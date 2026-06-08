"""Methodology sensitivity analysis: how evaluation choices swing model rankings.

This module produces the key finding for a benchmark methodology paper:
showing that prompt choice, tolerance level, solver environment, and
failure handling each independently affect which model "wins."
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from or_eval.metrics.statistics import rank_correlation


def tolerance_sensitivity(results: list[dict]) -> dict[str, Any]:
    """Show how model rankings change across tolerance levels.

    Key insight: if rankings shift significantly between @5% and @1%,
    the tolerance choice is a hidden confound in reported results.
    """
    models = sorted({r.get("model") for r in results if r.get("model")})
    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        if r.get("model"):
            by_model[r["model"]].append(r)

    tolerances = {"acc_5pct": 0.05, "acc_1pct": 0.01, "acc_1e-4": 1e-4}
    rankings: dict[str, list[float]] = {}
    for tol_name in tolerances:
        scores = []
        for m in models:
            rows = by_model[m]
            if rows:
                scores.append(sum(1 for r in rows if r.get(tol_name)) / len(rows))
            else:
                scores.append(0.0)
        rankings[tol_name] = scores

    pairwise = {}
    tol_names = list(tolerances)
    for i, t1 in enumerate(tol_names):
        for t2 in tol_names[i + 1:]:
            tau = rank_correlation(rankings[t1], rankings[t2])
            pairwise[f"{t1}_vs_{t2}"] = tau["tau"]

    return {
        "models": models,
        "rankings_by_tolerance": {t: dict(zip(models, scores)) for t, scores in rankings.items()},
        "rank_correlation": pairwise,
        "rank_stable": all(v > 0.8 for v in pairwise.values()),
    }


def failure_handling_sensitivity(results: list[dict]) -> dict[str, Any]:
    """Show how different failure handling policies change accuracy.

    Policies:
    - "include_all": count failed rows as incorrect (current default)
    - "exclude_non_executable": only score rows where code ran
    - "exclude_unavailable_solver": exclude solver-unavailability failures
    """
    models = sorted({r.get("model") for r in results if r.get("model")})
    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        if r.get("model"):
            by_model[r["model"]].append(r)

    policies = {
        "include_all": lambda rows: rows,
        "exclude_non_executable": lambda rows: [r for r in rows if r.get("executable")],
        "exclude_unavailable_solver": lambda rows: [
            r for r in rows
            if r.get("solver_availability_state") != "unavailable" or r.get("executable")
        ],
    }

    results_by_policy: dict[str, dict[str, float]] = {}
    for policy_name, filter_fn in policies.items():
        model_scores = {}
        for m in models:
            filtered = filter_fn(by_model[m])
            if filtered:
                model_scores[m] = sum(1 for r in filtered if r.get("acc_5pct")) / len(filtered)
            else:
                model_scores[m] = 0.0
        results_by_policy[policy_name] = model_scores

    ranking_vecs = {p: [scores[m] for m in models] for p, scores in results_by_policy.items()}
    tau_include_vs_exclude_exec = rank_correlation(
        ranking_vecs["include_all"], ranking_vecs["exclude_non_executable"]
    )
    tau_include_vs_exclude_solver = rank_correlation(
        ranking_vecs["include_all"], ranking_vecs["exclude_unavailable_solver"]
    )

    max_swing = {}
    for m in models:
        scores = [results_by_policy[p][m] for p in policies]
        max_swing[m] = max(scores) - min(scores)

    return {
        "models": models,
        "accuracy_by_policy": results_by_policy,
        "max_accuracy_swing": max_swing,
        "rank_correlation_include_vs_exclude_exec": tau_include_vs_exclude_exec["tau"],
        "rank_correlation_include_vs_exclude_solver": tau_include_vs_exclude_solver["tau"],
    }


def prompt_sensitivity(
    full_results: list[dict],
    ablation_results: list[dict],
) -> dict[str, Any]:
    """Quantify how prompt choice (neutral vs solver-specific) affects rankings.

    This is the core finding: solver-specific prompts can swap model rankings.
    """
    models = sorted({r.get("model") for r in ablation_results if r.get("model")})
    by_model_prompt: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in ablation_results:
        m = r.get("model", "")
        p = r.get("prompt_id", "")
        if m and p:
            by_model_prompt[(m, p)].append(r)

    prompt_ids = sorted({r.get("prompt_id") for r in ablation_results if r.get("prompt_id")})

    accuracy_matrix: dict[str, dict[str, float]] = {}
    for pid in prompt_ids:
        model_scores = {}
        for m in models:
            rows = by_model_prompt.get((m, pid), [])
            if rows:
                model_scores[m] = sum(1 for r in rows if r.get("acc_5pct")) / len(rows)
            else:
                model_scores[m] = 0.0
        accuracy_matrix[pid] = model_scores

    ranking_vecs = {p: [scores.get(m, 0) for m in models] for p, scores in accuracy_matrix.items()}
    neutral_prompts = [p for p in prompt_ids if "neutral" in p]
    specific_prompts = [p for p in prompt_ids if "solver_specific" in p]

    cross_prompt_tau = {}
    for np in neutral_prompts:
        for sp in specific_prompts:
            if np in ranking_vecs and sp in ranking_vecs:
                tau = rank_correlation(ranking_vecs[np], ranking_vecs[sp])
                cross_prompt_tau[f"{np}_vs_{sp}"] = tau["tau"]

    inflation = {}
    for m in models:
        neutral_scores = [accuracy_matrix.get(p, {}).get(m, 0) for p in neutral_prompts if p in accuracy_matrix]
        specific_scores = [accuracy_matrix.get(p, {}).get(m, 0) for p in specific_prompts if p in accuracy_matrix]
        if neutral_scores and specific_scores:
            best_neutral = max(neutral_scores)
            best_specific = max(specific_scores)
            inflation[m] = best_specific - best_neutral

    return {
        "models": models,
        "prompt_ids": prompt_ids,
        "accuracy_matrix": accuracy_matrix,
        "cross_prompt_rank_tau": cross_prompt_tau,
        "accuracy_inflation_by_model": inflation,
        "max_inflation": max(inflation.values()) if inflation else 0,
        "mean_inflation": sum(inflation.values()) / len(inflation) if inflation else 0,
    }


def full_methodology_sensitivity(
    full_results: list[dict],
    ablation_results: list[dict],
) -> dict[str, Any]:
    """Run all sensitivity analyses and produce a summary finding."""
    tol = tolerance_sensitivity(full_results)
    fail = failure_handling_sensitivity(full_results)
    prompt = prompt_sensitivity(full_results, ablation_results)

    return {
        "tolerance_sensitivity": tol,
        "failure_handling_sensitivity": fail,
        "prompt_sensitivity": prompt,
        "headline_findings": {
            "tolerance_rank_stable": tol["rank_stable"],
            "max_prompt_inflation": prompt["max_inflation"],
            "mean_prompt_inflation": prompt["mean_inflation"],
            "max_failure_policy_swing": max(fail["max_accuracy_swing"].values()) if fail["max_accuracy_swing"] else 0,
            "conclusion": _conclusion(tol, fail, prompt),
        },
    }


def _conclusion(tol: dict, fail: dict, prompt: dict) -> str:
    issues = []
    if not tol["rank_stable"]:
        issues.append("tolerance choice affects model ranking")
    if prompt["max_inflation"] > 0.05:
        issues.append(f"solver-specific prompts inflate accuracy by up to {prompt['max_inflation']:.1%}")
    max_swing = max(fail["max_accuracy_swing"].values()) if fail["max_accuracy_swing"] else 0
    if max_swing > 0.05:
        issues.append(f"failure handling policy swings accuracy by up to {max_swing:.1%}")
    if not issues:
        return "Evaluation methodology choices do not significantly affect model rankings in this benchmark."
    return "Evaluation methodology is a confound: " + "; ".join(issues) + "."
