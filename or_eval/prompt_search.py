"""Three-round solver-neutral prompt search."""
from __future__ import annotations

import json
from pathlib import Path

from or_eval.data import BenchmarkProblem, load_datasets, validation_split
from or_eval.evaluation import _evaluate_problem_set, _run_metadata
from or_eval.execution.solver_env import solver_environment_hash, solver_environment_snapshot
from or_eval.inference import create_client
from or_eval.metrics import aggregate_results
from or_eval.prompts.neutral import PromptSpec, neutral_prompt_candidates, refine_prompt, solver_specific_prompts


def search_prompts(
    model: str,
    output_dir: Path,
    data_dir: Path,
    api_url: str,
    api_key: str | None,
    seed: int = 42,
    per_dataset: int = 50,
    concurrency: int = 4,
    timeout: int = 30,
    memory_limit_mb: int | None = 2048,
    final_full: bool = False,
    max_tokens: int = 4096,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    client = create_client(model=model, api_url=api_url, api_key=api_key, max_tokens=max_tokens, temperature=0)
    val_problems = validation_split(data_dir=data_dir, per_dataset=per_dataset, seed=seed)
    solver_env = solver_environment_snapshot()
    solver_env_digest = solver_environment_hash(solver_env)

    round1_specs = neutral_prompt_candidates()
    run_context = {
        "api_url": api_url,
        "max_tokens": max_tokens,
        "concurrency": concurrency,
        "solver_env": solver_env,
        "solver_env_hash": solver_env_digest,
    }
    round1 = _score_specs(client, val_problems, round1_specs, output_dir / "round1_grid", concurrency, timeout, memory_limit_mb, run_context)
    top5 = [item["prompt"] for item in sorted(round1, key=_prompt_score, reverse=True)[:5]]

    round2_specs: list[PromptSpec] = []
    for spec in top5:
        round2_specs.extend(refine_prompt(spec))
    round2 = _score_specs(client, val_problems, round2_specs, output_dir / "round2_refine", concurrency, timeout, memory_limit_mb, run_context)

    finalist = sorted([*round1, *round2], key=_prompt_score, reverse=True)[0]["prompt"]
    final_problems = load_datasets("all", data_dir) if final_full else val_problems
    round3 = _score_specs(client, final_problems, [finalist], output_dir / "round3_final", concurrency, timeout, memory_limit_mb, run_context)

    ablation = _score_specs(
        client,
        val_problems,
        [finalist, *solver_specific_prompts()],
        output_dir / "ablation_prompts",
        concurrency,
        timeout,
        memory_limit_mb,
        run_context,
    )
    report = {
        "model": model,
        "seed": seed,
        "per_dataset": per_dataset,
        "validation_size": len(val_problems),
        "final_full": final_full,
        "solver_env_hash": solver_env_digest,
        "solver_availability": {
            solver_id: data.get("available", False)
            for solver_id, data in solver_env.get("solvers", {}).items()
        },
        "best_prompt": _serializable_prompt(finalist),
        "round1": [_serializable_score(x) for x in round1],
        "round2": [_serializable_score(x) for x in round2],
        "round3": [_serializable_score(x) for x in round3],
        "ablation": [_serializable_score(x) for x in ablation],
    }
    (output_dir / "prompt_search_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "best_prompt.txt").write_text(finalist.text, encoding="utf-8")
    return report


def _score_specs(
    client,
    problems: list[BenchmarkProblem],
    specs: list[PromptSpec],
    output_dir: Path,
    concurrency: int,
    timeout: int,
    memory_limit_mb: int | None,
    run_context: dict | None = None,
) -> list[dict]:
    run_context = run_context or {}
    scores = []
    for spec in specs:
        metadata = _run_metadata(
            prompt_spec=spec,
            api_url=run_context.get("api_url", ""),
            timeout=timeout,
            memory_limit_mb=memory_limit_mb,
            max_tokens=run_context.get("max_tokens", 4096),
            concurrency=run_context.get("concurrency", concurrency),
            solver_env=run_context.get("solver_env", {}),
            solver_env_hash_value=run_context.get("solver_env_hash", ""),
        )
        spec_dir = output_dir / spec.id
        rows = _evaluate_problem_set(
            client=client,
            problems=problems,
            prompt_spec=spec,
            output_file=spec_dir / "results.jsonl",
            concurrency=concurrency,
            timeout=timeout,
            memory_limit_mb=memory_limit_mb,
            run_metadata=metadata,
        )
        metrics = aggregate_results(rows)
        scores.append({"prompt": spec, "metrics": metrics})
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "summary.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    return scores


def _prompt_score(item: dict) -> float:
    metrics = item["metrics"]
    dist = metrics.get("solver_distribution", {})
    max_share = dist.get("max_share", 1.0)
    concentration_penalty = max(0.0, max_share - 0.80)
    return (
        metrics.get("accuracy", 0.0) * 0.70
        + metrics.get("executable_rate", 0.0) * 0.20
        + dist.get("uniformity", 0.0) * 0.10
        - concentration_penalty * 0.25
    )


def _serializable_prompt(spec: PromptSpec) -> dict:
    return {
        "id": spec.id,
        "text": spec.text,
        "prompt_type": spec.prompt_type,
        "metadata": spec.metadata or {},
    }


def _serializable_score(item: dict) -> dict:
    return {
        "prompt": _serializable_prompt(item["prompt"]),
        "metrics": item["metrics"],
        "search_score": _prompt_score(item),
    }
