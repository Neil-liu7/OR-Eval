"""Report and LaTeX table generation."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from or_eval.evaluation import RESULT_SCHEMA_VERSION
from or_eval.execution.solver_env import solver_available, solver_availability_state, solver_environment_snapshot
from or_eval.metrics import aggregate_results, classify_failure, compute_optimality_gap, cross_table, solution_verification_record, tolerance_flags, verification_status


def collect_result_rows(results_dir: Path) -> list[dict]:
    rows_by_key: dict[str, dict] = {}
    unkeyed: list[dict] = []
    for path in results_dir.rglob("results.jsonl"):
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    row = _normalize_row(json.loads(line))
                    key = row.get("run_key")
                    if key:
                        rows_by_key[key] = row
                    else:
                        unkeyed.append(row)
    return [*unkeyed, *rows_by_key.values()]


def generate_report(results_dir: Path, output_dir: Path | None = None) -> dict:
    output_dir = output_dir or results_dir / "report"
    output_dir.mkdir(parents=True, exist_ok=True)
    full_rows = collect_result_rows(results_dir / "full_eval")
    if not full_rows:
        full_rows = collect_result_rows(results_dir)
    ablation_dir = results_dir / "ablation_validation"
    if not ablation_dir.exists():
        ablation_dir = results_dir / "ablation"
    ablation_rows = collect_result_rows(ablation_dir) if ablation_dir.exists() else []

    summary = aggregate_results(full_rows)
    dataset_model_solver = cross_table(full_rows, ("dataset", "model", "solver"))
    dataset_model_prompt = cross_table(full_rows, ("dataset", "model", "prompt_id"))
    dataset_model_solver_availability = cross_table(full_rows, ("dataset", "model", "solver_availability_state"))
    failure_table = cross_table(full_rows, ("dataset", "model", "failure_type"))
    verification_table = cross_table(full_rows, ("dataset", "model", "verification_status"))
    ablation = cross_table(ablation_rows, ("model", "prompt_id", "solver"))
    ablation_prompt_bias = _prompt_bias_rows(ablation_rows)
    solver_availability = _solver_availability_rows(full_rows)
    fairness_audit = _fairness_audit(full_rows, ablation_rows, summary, ablation_prompt_bias, solver_availability)
    result_status = _result_status(fairness_audit, summary)

    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "fairness_audit.json", fairness_audit)
    _write_json(output_dir / "result_status.json", result_status)
    _write_json(output_dir / "dataset_model_solver.json", dataset_model_solver)
    _write_json(output_dir / "dataset_model_prompt.json", dataset_model_prompt)
    _write_json(output_dir / "dataset_model_solver_availability.json", dataset_model_solver_availability)
    _write_json(output_dir / "failure_taxonomy.json", failure_table)
    _write_json(output_dir / "verification_status.json", verification_table)
    _write_json(output_dir / "ablation_solver_bias.json", ablation)
    _write_json(output_dir / "ablation_prompt_bias.json", ablation_prompt_bias)
    _write_json(output_dir / "solver_availability.json", solver_availability)
    _write_csv(output_dir / "dataset_model_solver.csv", dataset_model_solver)
    _write_csv(output_dir / "dataset_model_prompt.csv", dataset_model_prompt)
    _write_csv(output_dir / "dataset_model_solver_availability.csv", dataset_model_solver_availability)
    _write_csv(output_dir / "failure_taxonomy.csv", failure_table)
    _write_csv(output_dir / "verification_status.csv", verification_table)
    _write_csv(output_dir / "ablation_solver_bias.csv", ablation)
    _write_csv(output_dir / "ablation_prompt_bias.csv", ablation_prompt_bias)
    _write_csv(output_dir / "solver_availability.csv", solver_availability)
    (output_dir / "fairness_audit.md").write_text(_fairness_audit_markdown(fairness_audit), encoding="utf-8")
    (output_dir / "result_status.md").write_text(_result_status_markdown(result_status), encoding="utf-8")
    (output_dir / "tables.tex").write_text(_latex_tables(dataset_model_solver, dataset_model_prompt, dataset_model_solver_availability, failure_table, verification_table, ablation, ablation_prompt_bias, solver_availability), encoding="utf-8")
    _write_charts(output_dir, dataset_model_prompt, ablation_prompt_bias)
    target_audit = _target_audit(results_dir, output_dir, full_rows, ablation_rows, ablation_prompt_bias, solver_availability)
    _write_json(output_dir / "target_audit.json", target_audit)
    (output_dir / "target_audit.md").write_text(_target_audit_markdown(target_audit), encoding="utf-8")
    (output_dir / "report.md").write_text(_markdown_report(summary, dataset_model_solver, dataset_model_prompt, dataset_model_solver_availability, failure_table, verification_table, ablation, ablation_prompt_bias, solver_availability), encoding="utf-8")
    return {
        "summary": summary,
        "fairness_audit": fairness_audit,
        "result_status": result_status,
        "target_audit": target_audit,
        "dataset_model_solver": dataset_model_solver,
        "dataset_model_prompt": dataset_model_prompt,
        "dataset_model_solver_availability": dataset_model_solver_availability,
        "failure_taxonomy": failure_table,
        "verification_status": verification_table,
        "ablation": ablation,
        "ablation_prompt_bias": ablation_prompt_bias,
        "solver_availability": solver_availability,
        "output_dir": str(output_dir),
    }


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_charts(output_dir: Path, prompt_table: list[dict], ablation_prompt_bias: list[dict]) -> None:
    """Write lightweight SVG charts without adding plotting dependencies."""
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    model_rows = [row for row in prompt_table if row.get("prompt_id")]
    by_model: dict[str, list[dict]] = {}
    for row in model_rows:
        by_model.setdefault(str(row.get("model", "unknown")), []).append(row)
    model_summary = []
    for model, rows in sorted(by_model.items()):
        total = sum(int(row.get("n") or 0) for row in rows)
        if total:
            acc = sum(float(row.get("accuracy") or 0) * int(row.get("n") or 0) for row in rows) / total
            exe = sum(float(row.get("executable_rate") or 0) * int(row.get("n") or 0) for row in rows) / total
            model_summary.append({"label": model, "accuracy": acc, "executable": exe})
    (charts_dir / "model_accuracy.svg").write_text(
        _bar_chart_svg(
            "Full Eval Accuracy by Model",
            [(row["label"], row["accuracy"]) for row in model_summary],
            value_label="accuracy",
        ),
        encoding="utf-8",
    )
    (charts_dir / "model_executable_rate.svg").write_text(
        _bar_chart_svg(
            "Full Eval Executable Rate by Model",
            [(row["label"], row["executable"]) for row in model_summary],
            value_label="executable",
        ),
        encoding="utf-8",
    )
    (charts_dir / "prompt_solver_concentration.svg").write_text(
        _bar_chart_svg(
            "Prompt Solver Concentration",
            [(f"{row.get('model')}:{row.get('prompt_id')}", float(row.get("max_solver_share") or 0)) for row in ablation_prompt_bias],
            value_label="max solver share",
            width=1100,
        ),
        encoding="utf-8",
    )


def _bar_chart_svg(
    title: str,
    values: list[tuple[str, float]],
    value_label: str,
    width: int = 900,
    bar_height: int = 28,
) -> str:
    if not values:
        values = [("no data", 0.0)]
    left = 230
    right = 40
    top = 56
    gap = 12
    height = top + len(values) * (bar_height + gap) + 44
    max_value = max(1.0, max(value for _, value in values))
    chart_width = width - left - right
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="24" y="32" font-family="Arial, sans-serif" font-size="20" font-weight="700">{_xml_escape(title)}</text>',
        f'<text x="{left}" y="{height - 14}" font-family="Arial, sans-serif" font-size="12" fill="#555">{_xml_escape(value_label)}</text>',
    ]
    for idx, (label, value) in enumerate(values):
        y = top + idx * (bar_height + gap)
        bar_w = max(1, int(chart_width * (value / max_value)))
        fill = "#2f6f73" if value < 0.8 else "#b24b3f"
        lines.extend([
            f'<text x="24" y="{y + 19}" font-family="Arial, sans-serif" font-size="12" fill="#222">{_xml_escape(label)}</text>',
            f'<rect x="{left}" y="{y}" width="{chart_width}" height="{bar_height}" fill="#edf2f2"/>',
            f'<rect x="{left}" y="{y}" width="{bar_w}" height="{bar_height}" fill="{fill}"/>',
            f'<text x="{left + bar_w + 8}" y="{y + 19}" font-family="Arial, sans-serif" font-size="12" fill="#222">{value:.3f}</text>',
        ])
    lines.append("</svg>")
    return "\n".join(lines)


def _xml_escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _markdown_report(
    summary: dict,
    solver_table: list[dict],
    prompt_table: list[dict],
    solver_availability_outcomes: list[dict],
    failure_table: list[dict],
    verification_table: list[dict],
    ablation_table: list[dict],
    ablation_prompt_bias: list[dict],
    availability_table: list[dict],
) -> str:
    lines = [
        "# OR-Eval Report",
        "",
        f"- Problems evaluated: {summary.get('n', 0)}",
        f"- Accuracy @5%: {_fmt(summary.get('acc_5pct'))}",
        f"- Accuracy @1%: {_fmt(summary.get('acc_1pct'))}",
        f"- Accuracy @1e-4: {_fmt(summary.get('acc_1e-4'))}",
        f"- Executable rate: {_fmt(summary.get('executable_rate'))}",
        f"- Solve rate: {_fmt(summary.get('solve_rate'))}",
        f"- Objective-evaluable rate: {_fmt(summary.get('objective_evaluable_rate'))}",
        f"- Variable-output rate: {_fmt(summary.get('variable_output_rate'))}",
        "",
        "## Solver Availability",
        "",
        _markdown_table(availability_table, ["solver", "available", "packages"]),
        "",
        "## Dataset x Model x Solver",
        "",
        _markdown_table(solver_table, ["dataset", "model", "solver", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate", "avg_tokens", "avg_latency"]),
        "",
        "## Dataset x Model x Prompt",
        "",
        _markdown_table(prompt_table, ["dataset", "model", "prompt_id", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate"]),
        "",
        "## Solver Availability Outcomes",
        "",
        _markdown_table(solver_availability_outcomes, ["dataset", "model", "solver_availability_state", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate"]),
        "",
        "## Failure Taxonomy",
        "",
        _markdown_table(failure_table, ["dataset", "model", "failure_type", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate"]),
        "",
        "## Verification Status",
        "",
        _markdown_table(verification_table, ["dataset", "model", "verification_status", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate"]),
        "",
        "## Ablation Prompt Bias",
        "",
        _markdown_table(ablation_prompt_bias, ["model", "prompt_id", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate", "max_solver_share", "top_solver", "unavailable_solver_rate"]),
        "",
        "## Ablation Solver Bias",
        "",
        _markdown_table(ablation_table, ["model", "prompt_id", "solver", "n", "accuracy", "executable_rate", "solve_rate"]),
    ]
    return "\n".join(lines)


def _markdown_table(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(_fmt(row.get(c)) for c in columns) + " |")
    return "\n".join(lines)


def _latex_tables(
    solver_table: list[dict],
    prompt_table: list[dict],
    solver_availability_outcomes: list[dict],
    failure_table: list[dict],
    verification_table: list[dict],
    ablation_table: list[dict],
    ablation_prompt_bias: list[dict],
    availability_table: list[dict],
) -> str:
    return "\n\n".join([
        latex_table(
            availability_table,
            ["solver", "available", "packages"],
            "Local solver package availability for OR-Eval.",
            "tab:or_eval_solver_availability",
        ),
        latex_table(
            solver_table,
            ["dataset", "model", "solver", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate"],
            "OR-Eval results by dataset, model, and solver.",
            "tab:or_eval_solver",
        ),
        latex_table(
            prompt_table,
            ["dataset", "model", "prompt_id", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate"],
            "OR-Eval results by dataset, model, and prompt.",
            "tab:or_eval_prompt",
        ),
        latex_table(
            solver_availability_outcomes,
            ["dataset", "model", "solver_availability_state", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate"],
            "OR-Eval results split by whether the generated solver is available locally.",
            "tab:or_eval_solver_availability_outcomes",
        ),
        latex_table(
            failure_table,
            ["dataset", "model", "failure_type", "n", "accuracy", "executable_rate", "solve_rate", "objective_evaluable_rate", "variable_output_rate"],
            "OR-Eval case-level failure taxonomy.",
            "tab:or_eval_failure",
        ),
        latex_table(
            verification_table,
            ["dataset", "model", "verification_status", "n", "accuracy", "objective_evaluable_rate", "variable_output_rate"],
            "OR-Eval verification status for objective and variable-solution evidence.",
            "tab:or_eval_verification_status",
        ),
        latex_table(
            ablation_prompt_bias,
            ["model", "prompt_id", "n", "accuracy", "objective_evaluable_rate", "variable_output_rate", "max_solver_share", "top_solver", "unavailable_solver_rate"],
            "Prompt-level solver concentration and unavailable-solver exposure.",
            "tab:or_eval_prompt_bias",
        ),
        latex_table(
            ablation_table,
            ["model", "prompt_id", "solver", "n", "accuracy", "executable_rate", "solve_rate"],
            "Validation prompt ablation solver distribution.",
            "tab:or_eval_ablation",
        ),
    ])


def latex_table(rows: Iterable[dict], columns: list[str], caption: str, label: str) -> str:
    align = "l" * len(columns)
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        f"\\begin{{tabular}}{{{align}}}",
        "\\toprule",
        " & ".join(_latex_escape(c) for c in columns) + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(_latex_escape(_fmt(row.get(c))) for c in columns) + " \\\\")
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        f"\\caption{{{_latex_escape(caption)}}}",
        f"\\label{{{label}}}",
        "\\end{table}",
    ])
    return "\n".join(lines)


def _fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _latex_escape(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def _normalize_row(row: dict) -> dict:
    if not row.get("executable"):
        row["predicted"] = None
        row["gap"] = None
        row.update({name: False for name in ("acc_5pct", "acc_1pct", "acc_1e-4")})
        row["correct"] = False
    else:
        if row.get("predicted") is not None:
            row.update(tolerance_flags(row.get("predicted"), row.get("answer")))
            row["gap"] = compute_optimality_gap(row.get("predicted"), row.get("answer"))
            row["correct"] = row.get("acc_5pct", False)
    row["failure_type"] = classify_failure(row)
    row["verification_status"] = verification_status(row)
    row["solution_verification"] = row.get("solution_verification") or solution_verification_record(row)
    row.setdefault("solver_availability_state", solver_availability_state(row.get("solver", "unknown")))
    if "solver_available" not in row:
        row["solver_available"] = solver_available(row.get("solver", "unknown"))
    return row


def _solver_availability_rows(rows: list[dict]) -> list[dict]:
    snapshot = None
    for row in rows:
        metadata = row.get("run_metadata") or {}
        if metadata.get("solver_environment"):
            snapshot = metadata["solver_environment"]
            break
    snapshot = snapshot or solver_environment_snapshot()
    table = []
    for solver, data in sorted((snapshot.get("solvers") or {}).items()):
        packages = []
        for package, package_data in sorted((data.get("packages") or {}).items()):
            version = package_data.get("version")
            marker = "yes" if package_data.get("available") else "no"
            packages.append(f"{package}:{marker}" + (f"@{version}" if version else ""))
        table.append({
            "solver": solver,
            "available": bool(data.get("available")),
            "packages": ", ".join(packages),
        })
    return table


def _prompt_bias_rows(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        key = (str(row.get("model", "unknown")), str(row.get("prompt_id", "unknown")))
        groups.setdefault(key, []).append(row)

    table = []
    for (model, prompt_id), group in sorted(groups.items()):
        metrics = aggregate_results(group)
        distribution = metrics.get("solver_distribution", {})
        counts = distribution.get("counts", {})
        top_solver = "-"
        if counts:
            top_solver = max(counts.items(), key=lambda item: item[1])[0]
        unavailable = sum(
            1
            for row in group
            if (row.get("solver_availability_state") or solver_availability_state(row.get("solver", "unknown"))) == "unavailable"
        )
        table.append({
            "model": model,
            "prompt_id": prompt_id,
            "n": metrics.get("n", 0),
            "accuracy": metrics.get("accuracy"),
            "executable_rate": metrics.get("executable_rate"),
            "solve_rate": metrics.get("solve_rate"),
            "objective_evaluable_rate": metrics.get("objective_evaluable_rate"),
            "variable_output_rate": metrics.get("variable_output_rate"),
            "max_solver_share": distribution.get("max_share"),
            "solver_uniformity": distribution.get("uniformity"),
            "top_solver": top_solver,
            "unavailable_solver_rate": unavailable / len(group) if group else 0.0,
        })
    return table


def _fairness_audit(
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


def _result_status(audit: dict, summary: dict) -> dict:
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

    return {
        "framework_ready": not framework_blockers,
        "results_ready_for_paper": audit.get("overall_status") == "pass",
        "legacy_results": legacy_results,
        "audit_status": audit.get("overall_status"),
        "schema_version": RESULT_SCHEMA_VERSION,
        "framework_blockers": framework_blockers,
        "result_blockers": result_blockers,
        "n": summary.get("n", 0),
        "objective_evaluable_rate": summary.get("objective_evaluable_rate"),
        "variable_output_rate": summary.get("variable_output_rate"),
        "message": _result_status_message(not framework_blockers, audit.get("overall_status") == "pass", legacy_results),
    }


def _result_status_message(framework_ready: bool, results_ready: bool, legacy_results: bool) -> str:
    if results_ready:
        return "Framework and results satisfy the strict OR-Eval fairness protocol."
    if framework_ready and legacy_results:
        return "Framework is ready, but current main results are legacy artifacts and should be rerun with the current schema for paper-ready claims."
    if framework_ready:
        return "Framework is ready, but current results do not satisfy all strict fairness gates."
    return "Framework fairness gates are not yet fully satisfied."


def _target_audit(
    results_dir: Path,
    output_dir: Path,
    full_rows: list[dict],
    ablation_rows: list[dict],
    ablation_prompt_bias: list[dict],
    solver_availability: list[dict],
) -> dict:
    """Audit the original OR-Eval Pipeline goal, not only the v2 fairness schema."""
    checks = []

    def add(name: str, status: str, detail: str, value=None):
        checks.append({"name": name, "status": status, "detail": detail, "value": value})

    expected_total = 1961
    expected_datasets = {
        "IndustryOR",
        "MAMO_ComplexLP",
        "MAMO_EasyLP",
        "NL4OPT",
        "OptMATH_Bench",
        "OptiBench",
    }
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

    add(
        "six_dataset_full_eval",
        "pass" if expected_datasets.issubset(set(datasets)) and any(status["complete"] for status in full_model_status.values()) else "fail",
        "Full evaluation should cover all six SIRL datasets and at least one complete 1961-problem pass.",
        {"datasets": datasets, "rows": row_count, "complete_models": complete_models},
    )
    add(
        "five_model_full_eval",
        "pass" if len(complete_models) >= 5 else "fail",
        "Original acceptance requires at least five models on all six datasets.",
        {
            "models": models,
            "complete_models": complete_models,
            "complete_model_count": len(complete_models),
            "rows": row_count,
            "required_rows_per_model": expected_total,
            "per_model": full_model_status,
        },
    )
    add(
        "neutral_full_eval_present",
        "pass" if any(pid.startswith("neutral") for pid in prompt_ids) else "fail",
        "Full evaluation should use the selected solver-neutral prompt.",
        prompt_ids,
    )

    prompt_search_files = sorted(str(path.relative_to(results_dir)) for path in results_dir.rglob("prompt_search_summary.json"))
    best_prompt_files = sorted(str(path.relative_to(results_dir)) for path in results_dir.rglob("best_prompt*.txt"))
    add(
        "prompt_search_artifacts",
        "pass" if prompt_search_files and best_prompt_files else "fail",
        "Prompt search artifacts should live under the audited result root.",
        {"prompt_search_summary": prompt_search_files, "best_prompt": best_prompt_files},
    )

    ablation_status = _ablation_completion_status(ablation_rows, complete_models or models)
    add(
        "ablation_validation_size",
        "pass" if len(ablation_status["complete_models"]) >= 5 else "fail",
        "Ablation should compare neutral, PySCIPOpt, Gurobi, and COPT prompts on 300 validation samples per model.",
        {
            "rows": len(ablation_rows),
            "complete_models": ablation_status["complete_models"],
            "required_complete_models": 5,
            "required_rows_per_prompt": 300,
            "per_model": ablation_status["per_model"],
        },
    )

    specific_rows = [row for row in ablation_prompt_bias if str(row.get("prompt_id", "")).startswith("solver_specific")]
    neutral_rows = [row for row in ablation_prompt_bias if str(row.get("prompt_id", "")).startswith("neutral")]
    specific_biased_count = sum(1 for row in specific_rows if (row.get("max_solver_share") or 0.0) >= 0.90)
    specific_biased = bool(specific_rows) and specific_biased_count >= len(specific_rows) * 0.6
    neutral_below_count = sum(1 for row in neutral_rows if (row.get("max_solver_share") or 1.0) < 0.85)
    neutral_below_threshold = bool(neutral_rows) and neutral_below_count >= len(neutral_rows) * 0.6
    add(
        "solver_specific_bias_demonstrated",
        "pass" if specific_biased else "fail",
        f"Solver-specific prompts should visibly concentrate generated code on the forced solver (≥60% of rows with max_share≥0.90). {specific_biased_count}/{len(specific_rows)} pass.",
        {row.get("prompt_id"): row.get("max_solver_share") for row in specific_rows},
    )
    add(
        "neutral_bias_mitigated",
        "pass" if neutral_below_threshold else "fail",
        f"Neutral prompt should keep top-solver concentration below 0.85 for majority of models (≥60% of rows). {neutral_below_count}/{len(neutral_rows)} pass.",
        {f"{row.get('model')}/{row.get('prompt_id')}": row.get("max_solver_share") for row in neutral_rows},
    )

    total_solver_catalog = len(solver_availability)
    available_solvers = sum(1 for row in solver_availability if row.get("available"))
    add(
        "solver_catalog_coverage",
        "pass" if total_solver_catalog >= 15 else "fail",
        "The solver layer should catalog the 15 requested solver families.",
        {"cataloged": total_solver_catalog, "available": available_solvers},
    )
    add(
        "solver_runtime_availability",
        "pass" if available_solvers >= 8 else "warn",
        "Commercial and optional solvers may be unavailable, but the runtime should report availability explicitly.",
        {"available": available_solvers, "cataloged": total_solver_catalog},
    )

    report_files = {
        "tables_tex": (output_dir / "tables.tex").exists(),
        "report_md": (output_dir / "report.md").exists(),
        "model_accuracy_svg": (output_dir / "charts" / "model_accuracy.svg").exists(),
        "prompt_solver_concentration_svg": (output_dir / "charts" / "prompt_solver_concentration.svg").exists(),
    }
    add(
        "paper_tables_and_charts",
        "pass" if all(report_files.values()) else "fail",
        "Paper-facing LaTeX tables and analysis charts should be generated.",
        report_files,
    )

    verification_rows = [row for row in full_rows if row.get("solution_verification")]
    constraint_checked = [
        row for row in verification_rows
        if (row.get("solution_verification") or {}).get("constraint_feasibility") not in {None, "not_checked"}
    ]
    add(
        "equivalent_modeling_verifier",
        "pass" if constraint_checked else "fail",
        "Equivalent-modeling recognition should include real constraint feasibility evidence, not only objective matching.",
        {"rows_with_solution_verification": len(verification_rows), "rows_with_constraint_check": len(constraint_checked)},
    )

    fail_count = sum(1 for check in checks if check["status"] == "fail")
    warning_count = sum(1 for check in checks if check["status"] == "warn")
    overall = "fail" if fail_count else "pass"
    return {"overall_status": overall, "warning_count": warning_count, "checks": checks}


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
        prompt_counts = {}
        for label, predicate in required_prompts.items():
            prompt_counts[label] = sum(1 for row in rows if predicate(str(row.get("prompt_id", ""))))
        complete = all(count >= 300 for count in prompt_counts.values())
        per_model[model] = {"rows": len(rows), "prompt_counts": prompt_counts, "complete": complete}
        if complete:
            complete_models.append(model)
    return {"complete_models": complete_models, "per_model": per_model}


def _coverage_status(rate: float) -> str:
    if rate >= 0.999:
        return "pass"
    if rate > 0:
        return "warn"
    return "warn"


def _fairness_audit_markdown(audit: dict) -> str:
    lines = [
        "# OR-Eval Fairness Audit",
        "",
        f"- Overall status: {audit.get('overall_status', 'unknown')}",
        "",
        "| check | status | value | detail |",
        "| --- | --- | --- | --- |",
    ]
    for check in audit.get("checks", []):
        value = json.dumps(check.get("value"), ensure_ascii=False, sort_keys=True) if isinstance(check.get("value"), (dict, list)) else check.get("value")
        lines.append(f"| {check.get('name')} | {check.get('status')} | {_fmt(value)} | {check.get('detail')} |")
    return "\n".join(lines)


def _target_audit_markdown(audit: dict) -> str:
    lines = [
        "# OR-Eval Target Audit",
        "",
        f"- Overall status: {audit.get('overall_status', 'unknown')}",
        "",
        "| check | status | value | detail |",
        "| --- | --- | --- | --- |",
    ]
    for check in audit.get("checks", []):
        value = json.dumps(check.get("value"), ensure_ascii=False, sort_keys=True) if isinstance(check.get("value"), (dict, list)) else check.get("value")
        lines.append(f"| {check.get('name')} | {check.get('status')} | {_fmt(value)} | {check.get('detail')} |")
    return "\n".join(lines)


def _result_status_markdown(status: dict) -> str:
    lines = [
        "# OR-Eval Result Status",
        "",
        f"- Framework ready: {status.get('framework_ready')}",
        f"- Results ready for paper: {status.get('results_ready_for_paper')}",
        f"- Legacy results: {status.get('legacy_results')}",
        f"- Audit status: {status.get('audit_status')}",
        f"- Schema version: {status.get('schema_version')}",
        f"- Message: {status.get('message')}",
        "",
        "## Blockers",
        "",
        f"- Framework blockers: {', '.join(status.get('framework_blockers') or []) or '-'}",
        f"- Result blockers: {', '.join(status.get('result_blockers') or []) or '-'}",
    ]
    return "\n".join(lines)
