"""Numerical judgment and aggregate metrics for OR-Eval."""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any


TOLERANCES = {
    "acc_5pct": 0.05,
    "acc_1pct": 0.01,
    "acc_1e-4": 1e-4,
}


def numerical_judge(predicted: Any, ground_truth: Any, tolerance: float = 0.05) -> bool:
    if predicted is None or ground_truth is None:
        return False
    if isinstance(predicted, str) and predicted.upper() in {"INFEASIBLE", "UNBOUNDED"}:
        return str(ground_truth).upper() == predicted.upper()
    try:
        pred = float(predicted)
        gt = float(ground_truth)
    except (ValueError, TypeError):
        return str(predicted).strip().lower() == str(ground_truth).strip().lower()
    if not math.isfinite(pred) or not math.isfinite(gt):
        return False
    if gt == 0:
        return abs(pred) <= 1e-4
    if tolerance <= 1e-4:
        return abs(pred - gt) <= 1e-4
    return abs(pred - gt) / max(abs(gt), 1e-12) <= tolerance


def tolerance_flags(predicted: Any, ground_truth: Any) -> dict[str, bool]:
    return {name: numerical_judge(predicted, ground_truth, tol) for name, tol in TOLERANCES.items()}


def compute_optimality_gap(predicted: Any, ground_truth: Any) -> float | None:
    try:
        pred = float(predicted)
        gt = float(ground_truth)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(pred) or not math.isfinite(gt):
        return None
    if gt == 0:
        return abs(pred)
    return abs(pred - gt) / max(abs(gt), 1e-12)


def classify_failure(row: dict) -> str:
    """Classify an evaluation row for case-level error analysis."""
    if row.get("acc_5pct"):
        return "correct"
    if row.get("api_error"):
        return "api_error"
    if not row.get("code"):
        return "no_code"

    execution = row.get("execution") or {}
    stderr = str(execution.get("stderr") or execution.get("error") or "")
    solver_status = str(row.get("solver_status") or execution.get("solver_status") or "").lower()
    answer = row.get("answer")

    if not row.get("executable"):
        lowered = stderr.lower()
        if execution.get("timed_out") or "timeout" in lowered or "timed out" in lowered:
            return "timeout"
        if "modulenotfounderror" in lowered or "no module named" in lowered:
            return "missing_module"
        if "syntaxerror" in lowered:
            return "syntax_error"
        if "nameerror" in lowered:
            return "name_error"
        if stderr:
            return "runtime_error"
        return "other_exec_fail"

    if solver_status in {"infeasible", "unbounded"} and _is_numeric(answer):
        return "infeasible_unbounded_misclassification"
    if not row.get("solve_success"):
        return "exec_no_solve"
    if row.get("predicted") is None:
        return "missing_objective"
    return "wrong_numeric"


def verification_status(row: dict) -> str:
    """Return the strongest verification state available for this row."""
    if not row.get("executable"):
        return "not_executable"
    if row.get("predicted") is None:
        return "missing_objective"
    if row.get("acc_5pct"):
        return "objective_match"
    if row.get("variable_values"):
        return "objective_mismatch_with_variables"
    if row.get("solve_success"):
        return "objective_mismatch"
    return "executed_no_verified_solution"


def solution_verification_record(row: dict) -> dict:
    """Summarize objective and variable evidence for equivalent-modeling analysis.

    Natural-language OR benchmarks do not provide machine-readable constraints,
    so constraint feasibility is marked explicitly unless a future dataset
    adapter supplies structured checks. This avoids silently treating objective
    equality as full model equivalence.
    """
    variable_values = row.get("variable_values")
    constraint_feasibility = row.get("constraint_feasibility")
    if constraint_feasibility is None and row.get("solve_success"):
        constraint_feasibility = "solver_reported_feasible"
    if constraint_feasibility is None:
        constraint_feasibility = "not_checked"
    return {
        "objective_status": "match" if row.get("acc_5pct") else "mismatch" if row.get("predicted") is not None else "missing",
        "objective_gap": row.get("gap"),
        "variable_values_present": bool(variable_values),
        "variable_count": len(variable_values) if isinstance(variable_values, dict) else 0,
        "constraint_feasibility": constraint_feasibility,
        "constraint_violation_count": row.get("constraint_violation_count"),
        "note": "Constraint feasibility is solver-reported for the generated model; original-problem feasibility requires structured benchmark constraints or a dataset-specific verifier.",
    }


def solver_distribution(results: list[dict]) -> dict[str, Any]:
    counter = Counter(r.get("solver") or r.get("execution", {}).get("solver") or "unknown" for r in results)
    total = sum(counter.values())
    if total == 0:
        return {"counts": {}, "shares": {}, "max_share": 0.0, "entropy": 0.0, "uniformity": 0.0}
    shares = {k: v / total for k, v in sorted(counter.items())}
    entropy = -sum(p * math.log(p) for p in shares.values() if p > 0)
    max_entropy = math.log(len(shares)) if len(shares) > 1 else 1.0
    return {
        "counts": dict(sorted(counter.items())),
        "shares": shares,
        "max_share": max(shares.values()),
        "entropy": entropy,
        "uniformity": entropy / max_entropy if max_entropy else 0.0,
    }


def aggregate_results(results: list[dict]) -> dict[str, Any]:
    n = len(results)
    if n == 0:
        return {"n": 0}
    executable = sum(1 for r in results if r.get("executable"))
    solved = sum(1 for r in results if r.get("solve_success"))
    flags = {name: sum(1 for r in results if r.get(name)) / n for name in TOLERANCES}
    objective_evaluable = sum(1 for r in results if _objective_evaluable(r))
    variable_outputs = sum(1 for r in results if r.get("variable_values"))
    constraint_checked = sum(
        1 for r in results
        if (r.get("solution_verification") or {}).get("constraint_feasibility") not in {None, "not_checked"}
    )
    gaps = [r["gap"] for r in results if r.get("gap") is not None and _objective_evaluable(r)]
    latencies = [r["latency"] for r in results if r.get("latency") is not None]
    tokens = [r["tokens_total"] for r in results if r.get("tokens_total") is not None]
    metrics = {
        "n": n,
        "accuracy": flags["acc_5pct"],
        **flags,
        "executable_rate": executable / n,
        "solve_rate": solved / n,
        "objective_evaluable_rate": objective_evaluable / n,
        "variable_output_rate": variable_outputs / n,
        "constraint_checked_rate": constraint_checked / n,
        "mean_gap": sum(gaps) / len(gaps) if gaps else None,
        "avg_latency": sum(latencies) / len(latencies) if latencies else None,
        "avg_tokens": sum(tokens) / len(tokens) if tokens else None,
        "solver_distribution": solver_distribution(results),
        "failure_distribution": failure_distribution(results),
        "verification_distribution": verification_distribution(results),
    }
    return metrics


def failure_distribution(results: list[dict]) -> dict[str, Any]:
    counter = Counter(r.get("failure_type") or classify_failure(r) for r in results)
    total = sum(counter.values())
    if total == 0:
        return {"counts": {}, "shares": {}}
    return {
        "counts": dict(sorted(counter.items())),
        "shares": {k: v / total for k, v in sorted(counter.items())},
    }


def verification_distribution(results: list[dict]) -> dict[str, Any]:
    counter = Counter(r.get("verification_status") or verification_status(r) for r in results)
    total = sum(counter.values())
    if total == 0:
        return {"counts": {}, "shares": {}}
    return {
        "counts": dict(sorted(counter.items())),
        "shares": {k: v / total for k, v in sorted(counter.items())},
    }


def cross_table(results: list[dict], row_keys: tuple[str, ...] = ("dataset", "model", "solver")) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in results:
        key = tuple(row.get(k, "unknown") for k in row_keys)
        groups[key].append(row)
    table = []
    for key, rows in sorted(groups.items()):
        metrics = aggregate_results(rows)
        table.append({**dict(zip(row_keys, key)), **{k: v for k, v in metrics.items() if k not in {"solver_distribution", "failure_distribution", "verification_distribution"}}})
    return table


def _is_numeric(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _objective_evaluable(row: dict) -> bool:
    return bool(row.get("executable") and row.get("predicted") is not None)
