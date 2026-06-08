"""Statistical analysis utilities for publication-quality results.

Provides confidence intervals, significance tests, and item analysis
required by top-venue reviewers.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any


def bootstrap_ci(
    values: list[float | bool],
    statistic: str = "mean",
    n_bootstrap: int = 10000,
    confidence: float = 0.95,
    seed: int = 42,
) -> dict[str, float]:
    """Compute bootstrap confidence interval for a statistic."""
    if not values:
        return {"estimate": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "n": 0}
    rng = random.Random(seed)
    n = len(values)
    float_values = [float(v) for v in values]
    point = sum(float_values) / n

    bootstraps = []
    for _ in range(n_bootstrap):
        sample = [rng.choice(float_values) for _ in range(n)]
        bootstraps.append(sum(sample) / n)

    bootstraps.sort()
    alpha = 1 - confidence
    lower_idx = int(math.floor(alpha / 2 * n_bootstrap))
    upper_idx = int(math.ceil((1 - alpha / 2) * n_bootstrap)) - 1
    return {
        "estimate": point,
        "ci_lower": bootstraps[lower_idx],
        "ci_upper": bootstraps[upper_idx],
        "n": n,
        "confidence": confidence,
    }


def pairwise_significance(
    model_a_correct: list[bool],
    model_b_correct: list[bool],
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> dict[str, Any]:
    """Test whether model A is significantly better than model B (paired bootstrap).

    Uses the same problem set — each entry corresponds to the same problem.
    """
    if len(model_a_correct) != len(model_b_correct):
        raise ValueError("Lists must have equal length (same problem set)")
    n = len(model_a_correct)
    if n == 0:
        return {"delta": 0.0, "p_value": 1.0, "significant_at_05": False, "n": 0}

    observed_delta = sum(model_a_correct) / n - sum(model_b_correct) / n
    rng = random.Random(seed)
    count_ge = 0
    for _ in range(n_bootstrap):
        delta = 0.0
        for i in range(n):
            if rng.random() < 0.5:
                delta += float(model_a_correct[i]) - float(model_b_correct[i])
            else:
                delta += float(model_b_correct[i]) - float(model_a_correct[i])
        delta /= n
        if abs(delta) >= abs(observed_delta):
            count_ge += 1

    p_value = count_ge / n_bootstrap
    return {
        "delta": observed_delta,
        "p_value": p_value,
        "significant_at_05": p_value < 0.05,
        "significant_at_01": p_value < 0.01,
        "n": n,
    }


def rank_correlation(
    rankings_a: list[float],
    rankings_b: list[float],
) -> dict[str, float]:
    """Kendall's tau rank correlation between two model rankings."""
    n = len(rankings_a)
    if n != len(rankings_b) or n < 2:
        return {"tau": 0.0, "n": n}
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            diff_a = rankings_a[i] - rankings_a[j]
            diff_b = rankings_b[i] - rankings_b[j]
            product = diff_a * diff_b
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
    pairs = n * (n - 1) / 2
    tau = (concordant - discordant) / pairs if pairs > 0 else 0.0
    return {"tau": tau, "concordant": concordant, "discordant": discordant, "n": n}


def item_discrimination(
    results: list[dict],
    metric_key: str = "acc_5pct",
) -> list[dict]:
    """Compute item discrimination index for each problem.

    High discrimination = problem separates strong from weak models well.
    Low discrimination = all models get it right or all get it wrong (not useful).
    """
    by_problem: dict[str, list[bool]] = defaultdict(list)
    by_model: dict[str, list[bool]] = defaultdict(list)
    for row in results:
        pid = row.get("problem_id", "")
        model = row.get("model", "")
        correct = bool(row.get(metric_key, False))
        by_problem[pid].append(correct)
        by_model[model].append(correct)

    model_scores = {m: sum(v) / len(v) for m, v in by_model.items() if v}
    if not model_scores:
        return []
    median_score = sorted(model_scores.values())[len(model_scores) // 2]
    strong_models = {m for m, s in model_scores.items() if s >= median_score}
    weak_models = {m for m, s in model_scores.items() if s < median_score}

    items = []
    for row in results:
        pid = row.get("problem_id", "")
        if pid not in {r.get("problem_id") for r in items}:
            correct_list = by_problem[pid]
            p_value = sum(correct_list) / len(correct_list) if correct_list else 0

            strong_correct = [
                bool(r.get(metric_key, False))
                for r in results
                if r.get("problem_id") == pid and r.get("model") in strong_models
            ]
            weak_correct = [
                bool(r.get(metric_key, False))
                for r in results
                if r.get("problem_id") == pid and r.get("model") in weak_models
            ]
            p_strong = sum(strong_correct) / len(strong_correct) if strong_correct else 0
            p_weak = sum(weak_correct) / len(weak_correct) if weak_correct else 0
            discrimination = p_strong - p_weak
            items.append({
                "problem_id": pid,
                "difficulty": 1 - p_value,
                "discrimination": discrimination,
                "n_models": len(correct_list),
            })
    return sorted(items, key=lambda x: -x["discrimination"])


def extraction_confidence_analysis(results: list[dict]) -> dict[str, Any]:
    """Analyze accuracy stratified by extraction confidence level.

    Addresses reviewer concern: do low-confidence extractions produce
    false positives that inflate accuracy?
    """
    by_confidence: dict[str, list[bool]] = defaultdict(list)
    for row in results:
        extraction = row.get("objective_extraction") or {}
        confidence = extraction.get("confidence", "none")
        correct = bool(row.get("acc_5pct", False))
        by_confidence[confidence].append(correct)

    analysis = {}
    for level in ("high", "medium", "low", "very_low", "none"):
        values = by_confidence.get(level, [])
        if values:
            analysis[level] = {
                "n": len(values),
                "accuracy": sum(values) / len(values),
                "share": len(values),
            }
    total = sum(len(v) for v in by_confidence.values())
    for level_data in analysis.values():
        level_data["share"] = level_data["n"] / total if total else 0
    return analysis


def cross_dataset_rank_stability(results: list[dict]) -> dict[str, Any]:
    """Measure whether model rankings are stable across datasets.

    Returns Kendall's tau between every dataset pair.
    """
    by_dataset_model: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    for row in results:
        ds = row.get("dataset", "")
        model = row.get("model", "")
        correct = bool(row.get("acc_5pct", False))
        by_dataset_model[ds][model].append(correct)

    datasets = sorted(by_dataset_model.keys())
    models = sorted({m for ds_data in by_dataset_model.values() for m in ds_data})

    dataset_rankings: dict[str, list[float]] = {}
    for ds in datasets:
        scores = [sum(by_dataset_model[ds].get(m, [])) / max(len(by_dataset_model[ds].get(m, [])), 1) for m in models]
        dataset_rankings[ds] = scores

    pairwise_tau = {}
    for i, ds_a in enumerate(datasets):
        for ds_b in datasets[i + 1:]:
            tau = rank_correlation(dataset_rankings[ds_a], dataset_rankings[ds_b])
            pairwise_tau[f"{ds_a}_vs_{ds_b}"] = tau["tau"]

    taus = list(pairwise_tau.values())
    return {
        "pairwise_tau": pairwise_tau,
        "mean_tau": sum(taus) / len(taus) if taus else 0,
        "min_tau": min(taus) if taus else 0,
        "models": models,
        "datasets": datasets,
    }
