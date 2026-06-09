"""OR-Eval command line interface."""
from __future__ import annotations

import json
import os
from pathlib import Path

import click
import yaml

from or_eval.data import DATASET_FILES, DEFAULT_DATA_DIR, dataset_counts
from or_eval.execution import detect_available_solvers, solver_environment_hash, solver_environment_snapshot
from or_eval.prompts.neutral import PromptSpec, default_neutral_prompt


DEFAULT_API_URL = "http://ebill.baidu-int.com/v1/models/{model}"
DEFAULT_RESULTS_DIR = Path(__file__).resolve().parents[1] / "results" / "or_eval_pipeline"


@click.group()
def main():
    """OR-Eval: unified, solver-neutral OR LLM evaluation."""


@main.command("tasks")
@click.option("--verbose", "-v", is_flag=True, help="Show full task metadata.")
def tasks_cmd(verbose: bool):
    """Show registered task definitions (built-in + YAML-configured)."""
    from or_eval.tasks import list_tasks

    tasks = list_tasks()
    if verbose:
        output = {
            name: {
                "dataset_file": cfg.dataset_file,
                "problem_type": cfg.problem_type,
                "difficulty": cfg.difficulty,
                "capabilities": cfg.capabilities,
                "evaluation_mode": cfg.evaluation_mode,
                "description": cfg.description,
                "source": cfg.source,
            }
            for name, cfg in tasks.items()
        }
    else:
        output = {
            name: {"type": cfg.problem_type, "difficulty": cfg.difficulty, "description": cfg.description}
            for name, cfg in tasks.items()
        }
    click.echo(json.dumps(output, indent=2, ensure_ascii=False))


@main.command("data-info")
@click.option("--data-dir", type=click.Path(path_type=Path), default=DEFAULT_DATA_DIR)
def data_info(data_dir: Path):
    """Show dataset counts."""
    click.echo(json.dumps(dataset_counts(data_dir), indent=2, ensure_ascii=False))


@main.command("solvers")
def solvers():
    """Show importable local solver packages."""
    click.echo(json.dumps(detect_available_solvers(), indent=2, ensure_ascii=False))


@main.command("providers")
def providers_cmd():
    """Show available inference providers and their configuration."""
    from or_eval.inference.providers import PROVIDER_REGISTRY

    info = {
        "available_providers": sorted(PROVIDER_REGISTRY.keys()),
        "provider_details": {
            "ebill": {
                "description": "Baidu eBill proxy (Gemini-style + OpenAI fallback)",
                "default_url": "http://ebill.baidu-int.com/v1/models/{model}",
                "api_key_env": "OR_EVAL_API_KEY",
                "auto_models": ["deepseek-*", "any model not matching other providers"],
            },
            "openai": {
                "description": "OpenAI Chat Completions API (GPT-4o, o3, etc.)",
                "default_url": "https://api.openai.com/v1/chat/completions",
                "api_key_env": "OPENAI_API_KEY",
                "auto_models": ["gpt-*", "o3-*", "o4-*"],
            },
            "anthropic": {
                "description": "Anthropic Messages API (Claude)",
                "default_url": "https://api.anthropic.com/v1/messages",
                "api_key_env": "ANTHROPIC_API_KEY",
                "auto_models": ["claude-*"],
            },
            "vllm": {
                "description": "Local vLLM / Ollama / any OpenAI-compatible endpoint",
                "default_url": "http://localhost:8000/v1/chat/completions",
                "api_key_env": "OR_EVAL_API_KEY (optional)",
                "auto_models": ["any model with localhost/127.0.0.1 URL"],
                "aliases": ["ollama", "local"],
            },
        },
        "config_example": {
            "models": [
                "deepseek-v3",
                {"name": "gpt-4o", "provider": "openai", "api_key_env": "OPENAI_API_KEY"},
                {"name": "claude-sonnet-4-20250514", "provider": "anthropic", "api_key_env": "ANTHROPIC_API_KEY"},
                {"name": "my-local-model", "provider": "vllm", "api_url": "http://localhost:8000/v1/chat/completions"},
            ],
        },
    }
    click.echo(json.dumps(info, indent=2, ensure_ascii=False))


@main.command("solver-env")
def solver_env():
    """Show solver package availability, versions, and reproducibility hash."""
    snapshot = solver_environment_snapshot()
    click.echo(json.dumps({
        "solver_env_hash": solver_environment_hash(snapshot),
        **snapshot,
    }, indent=2, ensure_ascii=False))


@main.command("search-prompts")
@click.option("--model", default="deepseek-v3", show_default=True)
@click.option("--config", type=click.Path(path_type=Path), default=None)
@click.option("--data-dir", type=click.Path(path_type=Path), default=DEFAULT_DATA_DIR)
@click.option("--output-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR / "prompt_search")
@click.option("--per-dataset", type=int, default=50, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--concurrency", type=int, default=4, show_default=True)
@click.option("--final-full/--validation-final", default=False, show_default=True)
def search_prompts_cmd(model, config, data_dir, output_dir, per_dataset, seed, concurrency, final_full):
    """Run grid -> top-5 refinement -> final validation prompt search."""
    from or_eval.prompt_search import search_prompts

    cfg = _load_config(config)
    report = search_prompts(
        model=model,
        output_dir=output_dir,
        data_dir=data_dir,
        api_url=cfg.get("api_url", DEFAULT_API_URL),
        api_key=_api_key(cfg),
        seed=seed,
        per_dataset=per_dataset,
        concurrency=concurrency,
        final_full=final_full,
        timeout=cfg.get("execution", {}).get("timeout", 30),
        memory_limit_mb=cfg.get("execution", {}).get("memory_limit_mb", 2048),
        max_tokens=cfg.get("api", {}).get("max_tokens", 4096),
    )
    click.echo(f"Best prompt: {report['best_prompt']['id']}")
    click.echo(f"Summary: {output_dir / 'prompt_search_summary.json'}")


@main.command("evaluate")
@click.option("--models", default="deepseek-v3,deepseek-v3.2,gpt-4o-mini,gemini-2.5-pro,o3-mini", show_default=True, help="Comma-separated model names.")
@click.option("--datasets", default="all", show_default=True, help="Comma-separated datasets or all.")
@click.option("--config", type=click.Path(path_type=Path), default=None)
@click.option("--data-dir", type=click.Path(path_type=Path), default=DEFAULT_DATA_DIR)
@click.option("--output-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR / "full_eval")
@click.option("--prompt-file", type=click.Path(path_type=Path), default=None)
@click.option("--prompt-id", default="neutral_default", show_default=True)
@click.option("--limit-per-dataset", type=int, default=None)
@click.option("--concurrency", type=int, default=4, show_default=True)
@click.option("--mode", type=click.Choice(["single_pass", "self_debug", "reflexion"]), default="single_pass", show_default=True, help="Evaluation mode.")
@click.option("--max-turns", type=int, default=3, show_default=True, help="Max repair turns for multi-turn modes.")
def evaluate_cmd(models, datasets, config, data_dir, output_dir, prompt_file, prompt_id, limit_per_dataset, concurrency, mode, max_turns):
    """Run full model evaluation with JSONL resume."""
    from or_eval.evaluation import run_model_evaluation

    cfg = _load_config(config)
    prompt = _load_prompt(prompt_file, prompt_id)
    model_entries = _resolve_models(models, cfg)
    summary = run_model_evaluation(
        models=model_entries,
        datasets=_parse_datasets(datasets),
        output_dir=output_dir,
        data_dir=data_dir,
        api_url=cfg.get("api_url", DEFAULT_API_URL),
        api_key=_api_key(cfg),
        prompt=prompt,
        concurrency=concurrency,
        limit_per_dataset=limit_per_dataset,
        timeout=cfg.get("execution", {}).get("timeout", 30),
        memory_limit_mb=cfg.get("execution", {}).get("memory_limit_mb", 2048),
        max_tokens=cfg.get("api", {}).get("max_tokens", 4096),
        evaluation_mode=mode,
        max_turns=max_turns,
    )
    click.echo(json.dumps(summary, indent=2, ensure_ascii=False))


@main.command("ablation")
@click.option("--models", default="deepseek-v3,deepseek-v3.2,gpt-4o-mini,gemini-2.5-pro,o3-mini", show_default=True)
@click.option("--datasets", default="all", show_default=True)
@click.option("--config", type=click.Path(path_type=Path), default=None)
@click.option("--data-dir", type=click.Path(path_type=Path), default=DEFAULT_DATA_DIR)
@click.option("--output-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR / "ablation")
@click.option("--prompt-file", type=click.Path(path_type=Path), default=None)
@click.option("--limit-per-dataset", type=int, default=None)
@click.option("--validation-per-dataset", type=int, default=None, help="Use a seeded random validation sample per dataset.")
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--concurrency", type=int, default=4, show_default=True)
def ablation_cmd(models, datasets, config, data_dir, output_dir, prompt_file, limit_per_dataset, validation_per_dataset, seed, concurrency):
    """Compare neutral prompt against pyscipopt/gurobipy/coptpy prompts."""
    from or_eval.data import validation_split
    from or_eval.evaluation import run_ablation

    cfg = _load_config(config)
    model_entries = _resolve_models(models, cfg)
    problem_set = None
    if validation_per_dataset is not None:
        problem_set = validation_split(data_dir=data_dir, per_dataset=validation_per_dataset, seed=seed, datasets=_parse_datasets(datasets))
    summary = run_ablation(
        models=model_entries,
        datasets=_parse_datasets(datasets),
        output_dir=output_dir,
        data_dir=data_dir,
        api_url=cfg.get("api_url", DEFAULT_API_URL),
        api_key=_api_key(cfg),
        neutral_prompt=_load_prompt(prompt_file, "neutral_best") if prompt_file else default_neutral_prompt(),
        concurrency=concurrency,
        limit_per_dataset=limit_per_dataset,
        problem_set=problem_set,
        timeout=cfg.get("execution", {}).get("timeout", 30),
        memory_limit_mb=cfg.get("execution", {}).get("memory_limit_mb", 2048),
        max_tokens=cfg.get("api", {}).get("max_tokens", 4096),
    )
    click.echo(json.dumps(summary, indent=2, ensure_ascii=False))


@main.command("report")
@click.option("--results-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
def report_cmd(results_dir, output_dir):
    """Generate Markdown, CSV, JSON, and LaTeX report tables."""
    from or_eval.reporting import generate_report

    report = generate_report(results_dir, output_dir)
    click.echo(f"Report written to {report['output_dir']}")


@main.command("statistics")
@click.option("--results-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
def statistics_cmd(results_dir: Path, output_dir: Path | None):
    """Run publication-quality statistical analyses (CI, significance, item analysis)."""
    from or_eval.metrics.statistics import (
        bootstrap_ci,
        cross_dataset_rank_stability,
        extraction_confidence_analysis,
        item_discrimination,
        pairwise_significance,
    )
    from or_eval.reporting.reports import collect_result_rows

    output_dir = output_dir or results_dir / "report" / "statistics"
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = collect_result_rows(results_dir / "full_eval")
    if not rows:
        rows = collect_result_rows(results_dir)
    if not rows:
        raise click.ClickException("No result rows found.")

    models = sorted({str(r.get("model")) for r in rows if r.get("model")})
    model_ci = {}
    for model in models:
        model_rows = [r for r in rows if r.get("model") == model]
        correct = [bool(r.get("acc_5pct")) for r in model_rows]
        model_ci[model] = bootstrap_ci(correct)

    significance_matrix = {}
    for i, ma in enumerate(models):
        for mb in models[i + 1:]:
            rows_a = {r["problem_id"]: bool(r.get("acc_5pct")) for r in rows if r.get("model") == ma}
            rows_b = {r["problem_id"]: bool(r.get("acc_5pct")) for r in rows if r.get("model") == mb}
            common = sorted(set(rows_a) & set(rows_b))
            if common:
                sig = pairwise_significance(
                    [rows_a[p] for p in common],
                    [rows_b[p] for p in common],
                )
                significance_matrix[f"{ma}_vs_{mb}"] = sig

    rank_stability = cross_dataset_rank_stability(rows)
    confidence_analysis = extraction_confidence_analysis(rows)
    items = item_discrimination(rows)

    ablation_dir = results_dir / "ablation_validation"
    if not ablation_dir.exists():
        ablation_dir = results_dir / "ablation"
    ablation_rows = collect_result_rows(ablation_dir) if ablation_dir.exists() else []

    sensitivity = None
    if ablation_rows:
        from or_eval.metrics.sensitivity import full_methodology_sensitivity
        sensitivity = full_methodology_sensitivity(rows, ablation_rows)

    report = {
        "model_confidence_intervals": model_ci,
        "pairwise_significance": significance_matrix,
        "rank_stability": rank_stability,
        "extraction_confidence": confidence_analysis,
        "top_discriminating_items": items[:20] if items else [],
        "bottom_discriminating_items": items[-20:] if items else [],
        "methodology_sensitivity": sensitivity,
    }
    (output_dir / "statistical_analysis.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    click.echo(f"Statistical analysis → {output_dir / 'statistical_analysis.json'}")
    click.echo(f"Models: {len(models)}, Problems: {len(set(r.get('problem_id') for r in rows))}")
    for model, ci in model_ci.items():
        click.echo(f"  {model}: {ci['estimate']:.3f} [{ci['ci_lower']:.3f}, {ci['ci_upper']:.3f}]")
    if sensitivity:
        headline = sensitivity.get("headline_findings", {})
        click.echo(f"\nMethodology sensitivity: {headline.get('conclusion', 'N/A')}")


@main.command("fairness-smoke")
@click.option("--output-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR / "fairness_smoke")
def fairness_smoke_cmd(output_dir: Path):
    """Run a no-API local smoke check for fair-result schema and reporting."""
    from or_eval.evaluation import fairness_smoke_check

    report = fairness_smoke_check(output_dir)
    click.echo(json.dumps(report, indent=2, ensure_ascii=False))


@main.command("fairness-audit")
@click.option("--results-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--strict/--allow-warn", default=False, show_default=True, help="Fail unless the fairness audit status is pass.")
def fairness_audit_cmd(results_dir: Path, output_dir: Path | None, strict: bool):
    """Generate and check the fairness audit for existing results."""
    from or_eval.reporting import generate_report

    report = generate_report(results_dir, output_dir)
    audit = report["fairness_audit"]
    payload = {
        "overall_status": audit.get("overall_status"),
        "audit_path": str(Path(report["output_dir"]) / "fairness_audit.json"),
        "checks": audit.get("checks", []),
    }
    click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
    if strict and audit.get("overall_status") != "pass":
        raise click.ClickException(f"Fairness audit is {audit.get('overall_status')}; expected pass.")
    if audit.get("overall_status") == "fail":
        raise click.ClickException("Fairness audit failed.")


@main.command("fairness-protocol")
@click.option("--output-file", type=click.Path(path_type=Path), default=None)
def fairness_protocol_cmd(output_file: Path | None):
    """Print the machine-readable OR-Eval fairness protocol manifest."""
    protocol = _fairness_protocol()
    text = json.dumps(protocol, indent=2, ensure_ascii=False)
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(text + "\n", encoding="utf-8")
    click.echo(text)


@main.command("result-status")
@click.option("--results-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
def result_status_cmd(results_dir: Path, output_dir: Path | None):
    """Report whether the framework and current result artifacts are fairness-ready."""
    from or_eval.reporting import generate_report

    report = generate_report(results_dir, output_dir)
    click.echo(json.dumps(report["result_status"], indent=2, ensure_ascii=False))


@main.command("target-audit")
@click.option("--results-dir", type=click.Path(path_type=Path), default=DEFAULT_RESULTS_DIR)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--strict/--allow-warn", default=False, show_default=True, help="Fail unless the original target audit status is pass.")
def target_audit_cmd(results_dir: Path, output_dir: Path | None, strict: bool):
    """Check current artifacts against the original OR-Eval Pipeline target."""
    from or_eval.reporting import generate_report

    report = generate_report(results_dir, output_dir)
    audit = report["target_audit"]
    payload = {
        "overall_status": audit.get("overall_status"),
        "audit_path": str(Path(report["output_dir"]) / "target_audit.json"),
        "checks": audit.get("checks", []),
    }
    click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
    if strict and audit.get("overall_status") != "pass":
        raise click.ClickException(f"Target audit is {audit.get('overall_status')}; expected pass.")
    if audit.get("overall_status") == "fail":
        raise click.ClickException("Target audit failed.")


def _load_config(path: Path | None) -> dict:
    if path is None:
        default = Path(__file__).resolve().parents[1] / "configs" / "default.yaml"
        path = default if default.exists() else None
    if path is None or not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _api_key(cfg: dict) -> str | None:
    api_cfg = cfg.get("api", {})
    return api_cfg.get("api_key") or os.getenv(api_cfg.get("api_key_env", "OR_EVAL_API_KEY"))


def _load_prompt(path: Path | None, prompt_id: str) -> PromptSpec:
    if path is None:
        return default_neutral_prompt()
    return PromptSpec(id=prompt_id, text=path.read_text(encoding="utf-8"), prompt_type="neutral", metadata={"source": str(path)})


def _split(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _resolve_models(cli_models: str, cfg: dict) -> list[str | dict]:
    """Resolve model entries: merge CLI names with config-defined provider details.

    If the config has a models list with dicts (provider, api_key_env, etc.),
    those entries are used for matching CLI model names. CLI names not in config
    are passed through as plain strings (using auto provider detection).
    model_overrides from config (e.g. per-model max_tokens) are applied.
    """
    cli_names = _split(cli_models)
    config_models = cfg.get("models", [])
    overrides = cfg.get("model_overrides", {})
    config_by_name: dict[str, dict] = {}
    for entry in config_models:
        if isinstance(entry, dict):
            name = entry.get("name") or entry.get("model", "")
            if name:
                config_by_name[name] = entry
        elif isinstance(entry, str):
            config_by_name[entry] = entry

    resolved: list[str | dict] = []
    for name in cli_names:
        entry = config_by_name.get(name, name)
        override = overrides.get(name)
        if override and isinstance(override, dict):
            if isinstance(entry, str):
                entry = {"name": entry, **override}
            else:
                entry = {**entry, **override}
        resolved.append(entry)
    return resolved


def _parse_datasets(value: str):
    if value == "all":
        return "all"
    datasets = _split(value)
    unknown = [d for d in datasets if d not in DATASET_FILES]
    if unknown:
        raise click.ClickException(f"Unknown datasets: {', '.join(unknown)}")
    return datasets


def _fairness_protocol() -> dict:
    from or_eval.evaluation import RESULT_SCHEMA_VERSION

    return {
        "name": "OR-Eval fairness protocol",
        "schema_version": RESULT_SCHEMA_VERSION,
        "temperature": 0,
        "single_pass": True,
        "self_debug": False,
        "agent_interaction": False,
        "primary_prompt_policy": "solver-neutral",
        "required_result_fields": [
            "schema_version",
            "run_key",
            "model",
            "dataset",
            "problem_id",
            "prompt_id",
            "prompt_type",
            "question",
            "answer",
            "raw_response",
            "code",
            "execution",
            "predicted",
            "objective_extraction",
            "variable_values",
            "solution_verification",
            "prompt_hash",
            "config_hash",
            "solver_env_hash",
            "solver",
            "solver_availability_state",
            "solver_status",
            "solve_success",
            "failure_type",
            "verification_status",
            "acc_5pct",
            "acc_1pct",
            "acc_1e-4",
        ],
        "audit_gates": [
            "full_eval_rows",
            "ablation_rows",
            "schema_version_coverage",
            "prompt_hash_coverage",
            "config_hash_coverage",
            "solver_env_hash_coverage",
            "failed_prediction_suppression",
            "solver_environment_reported",
            "failure_taxonomy_reported",
            "objective_evaluable_metric",
            "variable_solution_evidence",
            "solver_specific_bias_detected",
            "neutral_prompt_bias_measured",
        ],
        "metrics": [
            "acc_5pct",
            "acc_1pct",
            "acc_1e-4",
            "executable_rate",
            "solve_rate",
            "objective_evaluable_rate",
            "variable_output_rate",
            "solver_distribution.max_share",
            "solver_distribution.uniformity",
            "failure_distribution",
            "verification_distribution",
        ],
        "commands": {
            "solver_environment": "python -m or_eval.cli solver-env",
            "fairness_smoke": "python -m or_eval.cli fairness-smoke --output-dir results/or_eval_pipeline/fairness_smoke",
            "full_eval": "python -m or_eval.cli evaluate --models deepseek-v3,deepseek-v3.2 --datasets all --config configs/default.yaml --prompt-file results/or_eval_pipeline/prompt_search_deepseek_v3/best_prompt.txt --prompt-id neutral_best --output-dir results/or_eval_pipeline/full_eval",
            "ablation": "python -m or_eval.cli ablation --models deepseek-v3,deepseek-v3.2 --datasets all --config configs/default.yaml --prompt-file results/or_eval_pipeline/prompt_search_deepseek_v3/best_prompt.txt --output-dir results/or_eval_pipeline/ablation_validation --validation-per-dataset 50 --seed 42",
            "report": "python -m or_eval.cli report --results-dir results/or_eval_pipeline --output-dir results/or_eval_pipeline/report",
            "strict_gate": "python -m or_eval.cli fairness-audit --results-dir results/or_eval_pipeline --output-dir results/or_eval_pipeline/report --strict",
            "result_status": "python -m or_eval.cli result-status --results-dir results/or_eval_pipeline --output-dir results/or_eval_pipeline/report",
        },
        "required_artifacts": [
            "full_eval/*/neutral_best/results.jsonl",
            "ablation_validation/*/*/results.jsonl",
            "report/summary.json",
            "report/fairness_audit.json",
            "report/result_status.json",
            "report/solver_availability.json",
            "report/dataset_model_solver_availability.json",
            "report/ablation_prompt_bias.json",
            "report/failure_taxonomy.json",
            "report/verification_status.json",
            "report/tables.tex",
        ],
    }


if __name__ == "__main__":
    main()
