"""Adapt OptiBench dataset to unified format (Dimensions B, C, D)."""
import json
from pathlib import Path
from or_eval.data.schema import ORProblem

TYPE_MAP = {
    "linear-notable": "LP", "linear-table": "LP",
    "nonlinear-notable": "NLP", "nonlinear-table": "NLP",
}


def adapt_optibench(data_path: Path) -> list[ORProblem]:
    with open(data_path) as f:
        data = json.load(f)

    problems = []
    for item in data:
        results = item.get("results", {})
        obj_key = next((k for k in results if "objective" in k.lower() or "profit" in k.lower() or "cost" in k.lower()), None)
        optimal_value = float(results[obj_key]) if obj_key else None

        problems.append(ORProblem(
            id=f"optibench_{item['index']}",
            source="optibench",
            problem_text=item["question"],
            problem_type=TYPE_MAP.get(item.get("type", ""), "LP"),
            difficulty="medium",
            dimensions=["B", "C", "D"],
            optimal_value=optimal_value,
            variable_values={k: float(v) for k, v in results.items() if k != obj_key} if obj_key else results,
            tolerance=1e-4,
        ))
    return problems
