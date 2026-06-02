"""Report and LaTeX table generation."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from or_eval.evaluation import RESULT_SCHEMA_VERSION
from or_eval.execution.solver_env import solver_available, solver_availability_state, solver_environment_snapshot
from or_eval.metrics import aggregate_results, classify_failure, compute_optimality_gap, cross_table, solution_verification_record, tolerance_flags, verification_status
from or_eval.reporting.audits import fairness_audit as _run_fairness_audit, result_status as _run_result_status, target_audit as _run_target_audit


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
    audit = _run_fairness_audit(full_rows, ablation_rows, summary, ablation_prompt_bias, solver_availability)
    status = _run_result_status(audit, summary)

    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "fairness_audit.json", audit)
    _write_json(output_dir / "result_status.json", status)
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
    (output_dir / "fairness_audit.md").write_text(_fairness_audit_markdown(audit), encoding="utf-8")
    (output_dir / "result_status.md").write_text(_result_status_markdown(status), encoding="utf-8")
    (output_dir / "tables.tex").write_text(_latex_tables(dataset_model_solver, dataset_model_prompt, dataset_model_solver_availability, failure_table, verification_table, ablation, ablation_prompt_bias, solver_availability), encoding="utf-8")
    _write_charts(output_dir, dataset_model_prompt, ablation_prompt_bias)
    ta = _run_target_audit(results_dir, output_dir, full_rows, ablation_rows, ablation_prompt_bias, solver_availability)
    _write_json(output_dir / "target_audit.json", ta)
    (output_dir / "target_audit.md").write_text(_target_audit_markdown(ta), encoding="utf-8")
    (output_dir / "report.md").write_text(_markdown_report(summary, dataset_model_solver, dataset_model_prompt, dataset_model_solver_availability, failure_table, verification_table, ablation, ablation_prompt_bias, solver_availability), encoding="utf-8")
    return {
        "summary": summary,
        "fairness_audit": audit,
        "result_status": status,
        "target_audit": ta,
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


def _fairness_audit_markdown(audit: dict) -> str:
    lines = ["# OR-Eval Fairness Audit", "", f"- Overall status: {audit.get('overall_status', 'unknown')}", "", "| check | status | value | detail |", "| --- | --- | --- | --- |"]
    for check in audit.get("checks", []):
        value = json.dumps(check.get("value"), ensure_ascii=False, sort_keys=True) if isinstance(check.get("value"), (dict, list)) else check.get("value")
        lines.append(f"| {check.get('name')} | {check.get('status')} | {_fmt(value)} | {check.get('detail')} |")
    return "\n".join(lines)


def _target_audit_markdown(audit: dict) -> str:
    lines = ["# OR-Eval Target Audit", "", f"- Overall status: {audit.get('overall_status', 'unknown')}", "", "| check | status | value | detail |", "| --- | --- | --- | --- |"]
    for check in audit.get("checks", []):
        value = json.dumps(check.get("value"), ensure_ascii=False, sort_keys=True) if isinstance(check.get("value"), (dict, list)) else check.get("value")
        lines.append(f"| {check.get('name')} | {check.get('status')} | {_fmt(value)} | {check.get('detail')} |")
    return "\n".join(lines)


def _result_status_markdown(status: dict) -> str:
    return "\n".join([
        "# OR-Eval Result Status", "",
        f"- Framework ready: {status.get('framework_ready')}",
        f"- Results ready for paper: {status.get('results_ready_for_paper')}",
        f"- Legacy results: {status.get('legacy_results')}",
        f"- Audit status: {status.get('audit_status')}",
        f"- Schema version: {status.get('schema_version')}",
        f"- Message: {status.get('message')}", "",
        "## Blockers", "",
        f"- Framework blockers: {', '.join(status.get('framework_blockers') or []) or '-'}",
        f"- Result blockers: {', '.join(status.get('result_blockers') or []) or '-'}",
    ])