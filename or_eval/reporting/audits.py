"""Fairness and target audit logic for OR-Eval."""
from __future__ import annotations

import json
from pathlib import Path

from or_eval.evaluation import RESULT_SCHEMA_VERSION
from or_eval.execution.solver_env import solver_availability_state


def fairness_audit(
    full_rows: list[dict],
    ablation_rows: list[dict],
    summary: dict,
    ablation_prompt_bias: list[dict],
    solver_availability: list[dict],
) -> dict:
    checks = []

    def add(name: str, status: str, detail: str, value=None):
        checks.append({"name": name, "status": status, "detail": detail, "value": value})

    full_n = len(full_rows)
    ablation_n = len(ablation_rows)
    add("full_eval_rows", "pass" if full_n else "fail", "Full evaluation rows are available.", full_n)
    add("ablation_rows", "pass" if ablation_n else "warn", "Ablation rows are available for prompt-bias analysis.", ablation_n)

    if full_n:
        prompt_hash_rate = sum(1 for row in full_rows if row.get("prompt_hash")) / full_n
        config_hash_rate = sum(1 for row in full_rows if row.get("config_hash")) / full_n
        env_hash_rate = sum(1 for row in full_rows if row.get("solver_env_hash")) / full_n
        schema_rate = sum(1 for row in full_rows if row.get("schema_version") == RESULT_SCHEMA_VERSION) / full_n
        add("prompt_hash_coverage", _coverage_status(prompt_hash_rate), "Rows include prompt hashes for resume fairness.", prompt_hash_rate)
        add("config_hash_coverage", _coverage_status(config_hash_rate), "Rows include config hashes for resume fairness.", config_hash_rate)
        add("solver_env_hash_coverage", _coverage_status(env_hash_rate), "Rows include solver environment hashes.", env_hash_rate)
        add("schema_version_coverage", _coverage_status(schema_rate), f"Rows use current schema version {RESULT_SCHEMA_VERSION}.", schema_rate)

        failed_predictions = sum(1 for row in full_rows if not row.get("executable") and row.get("predicted") is not None)
        add(
            "failed_prediction_suppression",
            "pass" if failed_predictions == 0 else "fail",
            "Non-executable rows must not contribute predicted values.",
            failed_predictions,
        )

    available_count = sum(1 for row in solver_availability if row.get("available"))
    add(
        "solver_environment_reported",
        "pass" if solver_availability else "fail",
        "Solver availability matrix is reported.",
        {"available_solvers": available_count, "total_solvers": len(solver_availability)},
    )

    failure_types = (summary.get("failure_distribution") or {}).get("counts", {})
    add(
        "failure_taxonomy_reported",
        "pass" if failure_types else "fail",
        "Case-level failure taxonomy is available.",
        sorted(failure_types),
    )

    add(
        "objective_evaluable_metric",
        "pass" if "objective_evaluable_rate" in summary else "fail",
        "Objective-evaluable rate is tracked separately from solve rate.",
        summary.get("objective_evaluable_rate"),
    )

    variable_rate = summary.get("variable_output_rate")
    add(
        "variable_solution_evidence",
        "pass" if variable_rate and variable_rate > 0 else "warn",
        "Variable values are tracked; legacy runs may have zero coverage until rerun with the updated prompt.",
        variable_rate,
    )

    neutral_rows = [row for row in ablation_prompt_bias if str(row.get("prompt_id", "")).startswith("neutral")]
    specific_rows = [row for row in ablation_prompt_bias if str(row.get("prompt_id", "")).startswith("solver_specific")]
    specific_biased_count = sum(1 for row in specific_rows if (row.get("max_solver_share") or 0) >= 0.90)
    specific_biased = bool(specific_rows) and specific_biased_count >= len(specific_rows) * 0.6
    add(
        "solver_specific_bias_detected",
        "pass" if specific_biased else "warn",
        f"Solver-specific prompts should expose forced solver concentration (≥60% of rows with max_share≥0.90). {specific_biased_count}/{len(specific_rows)} pass.",
        {row.get("prompt_id"): row.get("max_solver_share") for row in specific_rows},
    )
    add(
        "neutral_prompt_bias_measured",
        "pass" if neutral_rows else "warn",
        "Neutral prompt concentration and unavailable-solver exposure are measured.",
        {row.get("model"): {"max_solver_share": row.get("max_solver_share"), "unavailable_solver_rate": row.get("unavailable_solver_rate")} for row in neutral_rows},
    )

    status_order = {"pass": 0, "warn": 1, "fail": 2}
    overall = max(checks, key=lambda item: status_order[item["status"]])["status"] if checks else "fail"
    return {"overall_status": overall, "checks": checks}


def result_status(audit: dict, summary: dict) -> dict:
    checks = {item["name"]: item for item in audit.get("checks", [])}

    framework_gate_names = {
        "failed_prediction_suppression",
        "solver_environment_reported",
        "failure_taxonomy_reported",
        "objective_evaluable_metric",
        "solver_specific_bias_detected",
        "neutral_prompt_bias_measured",
    }
    result_gate_names = {
        "schema_version_coverage",
        "prompt_hash_coverage",
        "config_hash_coverage",
        "solver_env_hash_coverage",
        "variable_solution_evidence",
    }

    framework_blockers = [
        name for name in sorted(framework_gate_names)
        if checks.get(name, {}).get("status") != "pass"
    ]
    result_blockers = [
        name for name in sorted(result_gate_names)
        if checks.get(name, {}).get("status") != "pass"
    ]
    legacy_results = any(
        checks.get(name, {}).get("status") != "pass"
        for name in ("schema_version_coverage", "prompt_hash_coverage", "config_hash_coverage", "solver_env_hash_coverage")
    )

    ready = audit.get("overall_status") == "pass"
    fw_ready = not framework_blockers
    msg = _result_status_message(fw_ready, ready, legacy_results)
    return {
        "framework_ready": fw_ready,
        "results_ready_for_paper": ready,
        "legacy_results": legacy_results,
        "audit_status": audit.get("overall_status"),
        "schema_version": RESULT_SCHEMA_VERSION,
        "framework_blockers": framework_blockers,
        "result_blockers": result_blockers,
        "n": summary.get("n", 0),
        "objective_evaluable_rate": summary.get("objective_evaluable_rate"),
        "variable_output_rate": summary.get("variable_output_rate"),
        "message": msg,
    }


def target_audit(
    results_dir: Path,
    output_dir: Path,
    full_rows: list[dict],
    ablation_rows: list[dict],
    ablation_prompt_bias: list[dict],
    solver_availability: list[dict],
) -> dict:
    checks = []

    def add(name: str, status: str, detail: str, value=None):
        checks.append({"name": name, "status": status, "detail": detail, "value": value})

    expected_total = 1961
    expected_datasets = {"IndustryOR", "MAMO_ComplexLP", "MAMO_EasyLP", "NL4OPT", "OptMATH_Bench", "OptiBench"}
    datasets = sorted({str(row.get("dataset")) for row in full_rows if row.get("dataset")})
    models = sorted({str(row.get("model")) for row in full_rows if row.get("model")})
    prompt_ids = sorted({str(row.get("prompt_id")) for row in full_rows if row.get("prompt_id")})
    row_count = len(full_rows)
    full_by_model = _rows_by(full_rows, "model")
    full_model_status = {
        model: {
            "rows": len(rows),
            "datasets": sorted({str(row.get("dataset")) for row in rows if row.get("dataset")}),
            "complete": len(rows) >= expected_total and expected_datasets.issubset({str(row.get("dataset")) for row in rows if row.get("dataset")}),
        }
        for model, rows in sorted(full_by_model.items())
    }
    complete_models = sorted(model for model, status in full_model_status.items() if status["complete"])

    add("six_dataset_full_eval", "pass" if expected_datasets.issubset(set(datasets)) and any(s["complete"] for s in full_model_status.values()) else "fail",
        "Full evaluation should cover all six SIRL datasets and at least one complete 1961-problem pass.",
        {"datasets": datasets, "rows": row_count, "complete_models": complete_models})
    add("five_model_full_eval", "pass" if len(complete_models) >= 5 else "fail",
        "Original acceptance requires at least five models on all six datasets.",
        {"models": models, "complete_models": complete_models, "complete_model_count": len(complete_models), "rows": row_count, "required_rows_per_model": expected_total, "per_model": full_model_status})
    add("neutral_full_eval_present", "pass" if any(pid.startswith("neutral") for pid in prompt_ids) else "fail",
        "Full evaluation should use the selected solver-neutral prompt.", prompt_ids)

    prompt_search_files = sorted(str(path.relative_to(results_dir)) for path in results_dir.rglob("prompt_search_summary.json"))
    best_prompt_files = sorted(str(path.relative_to(results_dir)) for path in results_dir.rglob("best_prompt*.txt"))
    add("prompt_search_artifacts", "pass" if prompt_search_files and best_prompt_files else "fail",
        "Prompt search artifacts should live under the audited result root.",
        {"prompt_search_summary": prompt_search_files, "best_prompt": best_prompt_files})

    ablation_status = _ablation_completion_status(ablation_rows, complete_models or models)
    add("ablation_validation_size", "pass" if len(ablation_status["complete_models"]) >= 5 else "fail",
        "Ablation should compare neutral, PySCIPOpt, Gurobi, and COPT prompts on 300 validation samples per model.",
        {"rows": len(ablation_rows), "complete_models": ablation_status["complete_models"], "required_complete_models": 5, "required_rows_per_prompt": 300, "per_model": ablation_status["per_model"]})

    specific_rows = [row for row in ablation_prompt_bias if str(row.get("prompt_id", "")).startswith("solver_specific")]
    neutral_rows = [row for row in ablation_prompt_bias if str(row.get("prompt_id", "")).startswith("neutral")]
    specific_biased_count = sum(1 for row in specific_rows if (row.get("max_solver_share") or 0.0) >= 0.90)
    specific_biased = bool(specific_rows) and specific_biased_count >= len(specific_rows) * 0.6
    neutral_below_count = sum(1 for row in neutral_rows if (row.get("max_solver_share") or 1.0) < 0.85)
    neutral_below_threshold = bool(neutral_rows) and neutral_below_count >= len(neutral_rows) * 0.6
    add("solver_specific_bias_demonstrated", "pass" if specific_biased else "fail",
        f"Solver-specific prompts should visibly concentrate generated code on the forced solver (≥60% of rows with max_share≥0.90). {specific_biased_count}/{len(specific_rows)} pass.",
        {row.get("prompt_id"): row.get("max_solver_share") for row in specific_rows})
    add("neutral_bias_mitigated", "pass" if neutral_below_threshold else "fail",
        f"Neutral prompt should keep top-solver concentration below 0.85 for majority of models (≥60% of rows). {neutral_below_count}/{len(neutral_rows)} pass.",
        {f"{row.get('model')}/{row.get('prompt_id')}": row.get("max_solver_share") for row in neutral_rows})

    total_solver_catalog = len(solver_availability)
    available_solvers = sum(1 for row in solver_availability if row.get("available"))
    add("solver_catalog_coverage", "pass" if total_solver_catalog >= 15 else "fail",
        "The solver layer should catalog the 15 requested solver families.",
        {"cataloged": total_solver_catalog, "available": available_solvers})
    add("solver_runtime_availability", "pass" if available_solvers >= 8 else "warn",
        "Commercial and optional solvers may be unavailable, but the runtime should report availability explicitly.",
        {"available": available_solvers, "cataloged": total_solver_catalog})

    report_files = {
        "tables_tex": (output_dir / "tables.tex").exists(),
        "report_md": (output_dir / "report.md").exists(),
        "model_accuracy_svg": (output_dir / "charts" / "model_accuracy.svg").exists(),
        "prompt_solver_concentration_svg": (output_dir / "charts" / "prompt_solver_concentration.svg").exists(),
    }
    add("paper_tables_and_charts", "pass" if all(report_files.values()) else "fail",
        "Paper-facing LaTeX tables and analysis charts should be generated.", report_files)

    verification_rows = [row for row in full_rows if row.get("solution_verification")]
    constraint_checked = [row for row in verification_rows if (row.get("solution_verification") or {}).get("constraint_feasibility") not in {None, "not_checked"}]
    add("equivalent_modeling_verifier", "pass" if constraint_checked else "fail",
        "Equivalent-modeling recognition should include real constraint feasibility evidence, not only objective matching.",
        {"rows_with_solution_verification": len(verification_rows), "rows_with_constraint_check": len(constraint_checked)})

    fail_count = sum(1 for check in checks if check["status"] == "fail")
    warning_count = sum(1 for check in checks if check["status"] == "warn")
    overall = "fail" if fail_count else "pass"
    return {"overall_status": overall, "warning_count": warning_count, "checks": checks}


def _result_status_message(framework_ready: bool, results_ready: bool, legacy_results: bool) -> str:
    if results_ready:
        return "Framework and results satisfy the strict OR-Eval fairness protocol."
    if framework_ready and legacy_results:
        return "Framework is ready, but current main results are legacy artifacts and should be rerun with the current schema for paper-ready claims."
    if framework_ready:
        return "Framework is ready, but current results do not satisfy all strict fairness gates."
    return "Framework fairness gates are not yet fully satisfied."


def _coverage_status(rate: float) -> str:
    if rate >= 0.999:
        return "pass"
    return "warn"


def _rows_by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        value = row.get(key)
        if value:
            grouped.setdefault(str(value), []).append(row)
    return grouped


def _ablation_completion_status(ablation_rows: list[dict], candidate_models: list[str]) -> dict:
    required_prompts = {
        "neutral": lambda prompt_id: prompt_id.startswith("neutral"),
        "solver_specific_pyscipopt": lambda prompt_id: prompt_id == "solver_specific_pyscipopt",
        "solver_specific_gurobipy": lambda prompt_id: prompt_id == "solver_specific_gurobipy",
        "solver_specific_coptpy": lambda prompt_id: prompt_id == "solver_specific_coptpy",
    }
    rows_by_model = _rows_by(ablation_rows, "model")
    per_model = {}
    complete_models = []
    for model in sorted(set(candidate_models) | set(rows_by_model)):
        rows = rows_by_model.get(model, [])
        prompt_counts = {label: sum(1 for row in rows if predicate(str(row.get("prompt_id", "")))) for label, predicate in required_prompts.items()}
        complete = all(count >= 300 for count in prompt_counts.values())
        per_model[model] = {"rows": len(rows), "prompt_counts": prompt_counts, "complete": complete}
        if complete:
            complete_models.append(model)
    return {"complete_models": complete_models, "per_model": per_model}
