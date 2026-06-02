"""Unified data schema for OR-Eval."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
import json
from typing import Optional


@dataclass
class ORProblem:
    id: str
    source: str  # orqa / industryOR / optibench / nl4opt
    problem_text: str
    problem_type: str  # LP / IP / MIP / NLP / conceptual
    difficulty: str  # easy / medium / hard
    dimensions: list[str] = field(default_factory=list)  # subset of [A, B, C, D]
    optimal_value: float | None = None
    variable_values: dict | None = None
    mcq_answer: str | None = None
    mcq_options: list[str] | None = None
    tolerance: float = 0.05

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> "ORProblem":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
