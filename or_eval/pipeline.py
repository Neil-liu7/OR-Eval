"""Compatibility entry point for the formal OR-Eval pipeline."""
from __future__ import annotations

from pathlib import Path

from or_eval.data import DEFAULT_DATA_DIR
from or_eval.evaluation import run_model_evaluation
from or_eval.inference import DEFAULT_API_URL


def run_evaluation(config: dict, data_dir: Path | None = None, output_dir: Path | None = None):
    """Run evaluation from a config dictionary.

    This keeps older scripts working while delegating to the new JSONL pipeline.
    """
    data_dir = data_dir or DEFAULT_DATA_DIR
    output_dir = output_dir or Path("results/or_eval_pipeline")
    api_cfg = config.get("api", {})
    eval_cfg = config.get("evaluation", {})
    execution_cfg = config.get("execution", {})
    model_entries = config.get("models", ["deepseek-v3", "deepseek-v3.2"])
    datasets = config.get("datasets", "all")
    return run_model_evaluation(
        models=model_entries,
        datasets=datasets,
        output_dir=output_dir,
        data_dir=data_dir,
        api_url=config.get("api_url", DEFAULT_API_URL),
        api_key=api_cfg.get("api_key"),
        concurrency=eval_cfg.get("concurrency", 4),
        limit_per_dataset=eval_cfg.get("limit_per_dataset") or eval_cfg.get("limit"),
        timeout=execution_cfg.get("timeout", 30),
        memory_limit_mb=execution_cfg.get("memory_limit_mb", 2048),
        max_tokens=api_cfg.get("max_tokens", 4096),
    )
