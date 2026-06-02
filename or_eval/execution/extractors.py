"""Extract code, numerical answers, and solver statuses from model/execution text."""
from __future__ import annotations

import math
import ast
import json
import re
from dataclasses import asdict, dataclass


NUMBER_RE = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"


@dataclass(frozen=True)
class ObjectiveExtraction:
    value: float | str | None
    source: str
    confidence: str

    def to_dict(self) -> dict:
        return asdict(self)


def extract_code_block(text: str) -> str:
    """Return the most likely Python code from an LLM response."""
    if not text:
        return ""
    match = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return _strip_code(match.group(1))
    return _strip_code(text)


def extract_objective_value(text: str) -> float | str | None:
    """Extract a scalar objective value from stdout or free-form text."""
    return extract_objective_record(text).value


def extract_objective_record(text: str, allow_fallback: bool = True) -> ObjectiveExtraction:
    """Extract a scalar objective value and record where it came from."""
    if not text:
        return ObjectiveExtraction(None, "none", "none")

    status = extract_solver_status(text)
    if status in {"infeasible", "unbounded"}:
        return ObjectiveExtraction(status.upper(), "solver_status", "high")

    labeled_patterns = [
        ("objective_value", rf"OBJECTIVE_VALUE\s*[:=]\s*({NUMBER_RE}|INFEASIBLE|UNBOUNDED)", "high"),
        ("objective_label", rf"(?:optimal\s+)?objective(?:\s+value)?\s*[:=]\s*({NUMBER_RE})", "medium"),
        ("solver_obj_label", rf"(?:objval|obj\s+value|best\s+objective)\s*[:=]\s*({NUMBER_RE})", "medium"),
        ("boxed", rf"\\boxed\{{\s*({NUMBER_RE})\s*\}}", "medium"),
    ]
    for source, pattern, confidence in labeled_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return ObjectiveExtraction(_coerce_number(match.group(1)), source, confidence)

    if not allow_fallback:
        return ObjectiveExtraction(None, "none", "none")

    # Prefer the last number from a line that appears answer-like.
    for line in reversed(text.splitlines()):
        if re.search(r"objective|optimal|answer|profit|cost|value|result", line, re.IGNORECASE):
            nums = re.findall(NUMBER_RE, line)
            if nums:
                return ObjectiveExtraction(_coerce_number(nums[-1]), "answer_like_line", "low")

    nums = re.findall(NUMBER_RE, text)
    if nums:
        return ObjectiveExtraction(_coerce_number(nums[-1]), "last_number", "very_low")
    return ObjectiveExtraction(None, "none", "none")


def extract_variable_values(text: str) -> dict | None:
    """Extract optional variable values printed by generated code."""
    if not text:
        return None
    match = re.search(r"VARIABLE_VALUES\s*[:=]\s*(\{.*?\})", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    payload = match.group(1).strip()
    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(payload)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def extract_solver_status(text: str) -> str:
    if not text:
        return "unknown"
    lowered = text.lower()
    status_patterns = [
        ("optimal", ("optimal solution", "status: optimal", "optimal objective", "solved to optimality", "getstatus() == optimal")),
        ("infeasible", ("infeasible", "no feasible", "status: infeasible")),
        ("unbounded", ("unbounded", "status: unbounded")),
        ("timeout", ("timeout", "timed out")),
        ("error", ("traceback", "error:", "exception", "modulenotfounderror")),
    ]
    for status, patterns in status_patterns:
        if any(p in lowered for p in patterns):
            return status
    if re.search(r"\boptimal\b", lowered):
        return "optimal"
    return "unknown"


def _strip_code(code: str) -> str:
    code = code.strip()
    # Some models prefix a language tag even without fenced markdown.
    code = re.sub(r"^\s*(python|py)\s*\n", "", code, flags=re.IGNORECASE)
    return code.strip()


def _coerce_number(value: str) -> float | str | None:
    upper = str(value).strip().upper()
    if upper in {"INFEASIBLE", "UNBOUNDED"}:
        return upper
    try:
        num = float(upper)
    except (TypeError, ValueError):
        return None
    return num if math.isfinite(num) else None
