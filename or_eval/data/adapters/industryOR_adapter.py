"""Adapt IndustryOR dataset to unified format (Dimensions C, D)."""
import json
from pathlib import Path
from or_eval.data.schema import ORProblem

TYPE_MAP = {"线性规划": "LP", "整数规划": "IP", "混合整数规划": "MIP", "非线性规划": "NLP"}
DIFF_MAP = {"简单": "easy", "中等": "medium", "困难": "hard"}


def adapt_industryOR(data_path: Path) -> list[ORProblem]:
    problems = []
    with open(data_path) as f:
        for line in f:
            d = json.loads(line)
            problems.append(ORProblem(
                id=f"industryOR_{len(problems)}",
                source="industryOR",
                problem_text=d["en_question"],
                problem_type=TYPE_MAP.get(d.get("type", ""), "LP"),
                difficulty=DIFF_MAP.get(d.get("difficulty", ""), "medium"),
                dimensions=["C", "D"],
                optimal_value=float(d["en_answer"]),
            ))
    return problems
