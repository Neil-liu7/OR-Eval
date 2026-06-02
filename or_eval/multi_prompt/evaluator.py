"""Multi-prompt evaluation engine with robustness scoring."""
from __future__ import annotations
import numpy as np
from jinja2 import Environment, BaseLoader

from or_eval.inference import GeminiStyleClient
from or_eval.execution.sandbox import execute_code
from or_eval.execution.extractors import extract_objective_value, extract_code_block
from or_eval.metrics.numerical_judge import numerical_judge
from or_eval.multi_prompt.registry import PromptVariantRegistry

_env = Environment(loader=BaseLoader())


def multi_prompt_evaluate(
    model: GeminiStyleClient,
    problems: list[dict],
    dimension: str,
    solver_id: str = None,
    tolerance: float = 0.05,
    registry: PromptVariantRegistry = None,
) -> dict:
    if registry is None:
        registry = PromptVariantRegistry()

    variants = registry.get_variants(dimension)
    if not variants:
        return {"error": f"No variants for dimension {dimension}"}

    from or_eval.prompts import SOLVERS
    solver_name = SOLVERS.get(solver_id, "") if solver_id else ""
    solver_instr_path = f"or_eval/prompts/solver_instructions/{solver_id}.j2" if solver_id else ""
    solver_instructions = ""
    if solver_id:
        from pathlib import Path
        instr_path = Path(__file__).parent.parent / "prompts" / "solver_instructions" / f"{solver_id}.j2"
        if instr_path.exists():
            solver_instructions = instr_path.read_text()

    per_variant_scores = []
    per_problem_results = {p["id"]: [] for p in problems}

    for v_idx, template_str in enumerate(variants):
        variant_correct = 0
        for p in problems:
            prompt = _env.from_string(template_str).render(
                solver_name=solver_name, solver_instructions=solver_instructions, **p
            )
            response = model.generate(prompt).text
            correct = _judge(response, p, dimension, tolerance)
            per_problem_results[p["id"]].append(correct)
            if correct:
                variant_correct += 1
        per_variant_scores.append(variant_correct / len(problems) if problems else 0)

    scores = np.array(per_variant_scores)
    per_problem_robustness = []
    for pid, results in per_problem_results.items():
        per_problem_robustness.append(sum(results) / len(results))

    return {
        "mean_accuracy": float(scores.mean()),
        "std_accuracy": float(scores.std()),
        "min_accuracy": float(scores.min()),
        "max_accuracy": float(scores.max()),
        "prompt_robustness": float(1 - scores.std()),
        "per_variant_scores": per_variant_scores,
        "n_variants": len(variants),
        "n_problems": len(problems),
    }


def _judge(response: str, problem: dict, dimension: str, tolerance: float) -> bool:
    if dimension == "A" or dimension == "conceptual":
        answer = response.strip().upper()[:1]
        return answer == problem.get("mcq_answer", "")
    else:
        code = extract_code_block(response)
        obj_value = None
        if code:
            result = execute_code(code, timeout=300)
            if result.success:
                obj_value = extract_objective_value(result.stdout)
        if obj_value is None:
            obj_value = extract_objective_value(response)
        gt = problem.get("optimal_value")
        return numerical_judge(obj_value, gt, tolerance) if gt is not None else False
