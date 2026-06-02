"""Prompt variant registry for multi-prompt evaluation."""
from __future__ import annotations
from pathlib import Path

VARIANTS_DIR = Path(__file__).parent.parent / "prompts" / "variants"


class PromptVariantRegistry:
    def __init__(self):
        self._variants: dict[str, list[str]] = {}
        self._load_defaults()

    def _load_defaults(self):
        self._variants["code_gen"] = [
            "You are an Operations Research programmer. Solve the following optimization problem by writing Python code using the {{ solver_name }} solver.\n\nProblem:\n{{ problem_text }}\n\n{{ solver_instructions }}\n\nRequirements:\n- Self-contained executable code.\n- Print: OBJECTIVE_VALUE: <number>\n- Wrap in ```python ... ```",
            "Write a complete Python program using {{ solver_name }} to solve this optimization problem. Output the optimal value as OBJECTIVE_VALUE: <number>.\n\nProblem:\n{{ problem_text }}\n\n{{ solver_instructions }}\n\nWrap code in ```python ... ```",
            "As an optimization expert, implement a {{ solver_name }} solution for:\n\n{{ problem_text }}\n\n{{ solver_instructions }}\n\nOutput format: OBJECTIVE_VALUE: <number>\nWrap in ```python ... ```",
        ]
        self._variants["conceptual"] = [
            "You are an Operations Research expert. Given the following context and question, select the most appropriate answer.\n\nContext:\n{{ problem_text }}\n\nQuestion: {{ question }}\n{% for opt in mcq_options %}\n{{ ['A','B','C','D'][loop.index0] }}. {{ opt }}\n{% endfor %}\nAnswer with only the letter.",
            "Read the context below and answer the multiple-choice question.\n\nContext:\n{{ problem_text }}\n\nQuestion: {{ question }}\n{% for opt in mcq_options %}\n{{ ['A','B','C','D'][loop.index0] }}. {{ opt }}\n{% endfor %}\nRespond with a single letter: A, B, C, or D.",
        ]

    def get_variants(self, dimension: str) -> list[str]:
        return self._variants.get(dimension, [])

    def register(self, dimension: str, templates: list[str]):
        self._variants[dimension] = templates
