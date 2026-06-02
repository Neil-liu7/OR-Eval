"""Adapt ORQA dataset to unified format (Dimension A: conceptual QA)."""
import json
from pathlib import Path
from or_eval.data.schema import ORProblem


def adapt_orqa(data_path: Path) -> list[ORProblem]:
    problems = []
    with open(data_path) as f:
        for line in f:
            d = json.loads(line)
            problems.append(ORProblem(
                id=f"orqa_{len(problems)}",
                source="orqa",
                problem_text=d["CONTEXT"],
                problem_type="conceptual",
                difficulty="medium",
                dimensions=["A"],
                mcq_answer=["A", "B", "C", "D"][d["TARGET_ANSWER"]],
                mcq_options=d["OPTIONS"],
            ))
    return problems
