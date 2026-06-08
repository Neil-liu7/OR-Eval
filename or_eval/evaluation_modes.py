"""Multi-turn evaluation modes: self-debug and reflexion.

These complement the single-pass baseline. The single-pass result is always
recorded first, then additional turns attempt to repair failures.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from or_eval.execution import execute_code, extract_code_block
from or_eval.execution.extractors import ObjectiveExtraction


@dataclass
class TurnResult:
    turn: int
    code: str
    success: bool
    predicted: float | str | None
    error: str | None


SELF_DEBUG_PROMPT = """Your previous code produced an error. Fix it.

Error output:
{error}

Original problem:
{question}

Your previous code:
```python
{code}
```

Return only the corrected Python code in a fenced block. Print OBJECTIVE_VALUE: <number>."""


REFLEXION_PROMPT = """Your code ran but produced the wrong answer or no answer.

Execution output:
{stdout}

Original problem:
{question}

Your previous code:
```python
{code}
```

Reflect on what went wrong (constraint missed? wrong objective? indexing error?), then return corrected code in a fenced block. Print OBJECTIVE_VALUE: <number>."""


def self_debug_turns(
    client,
    question: str,
    first_code: str,
    first_execution,
    max_turns: int = 3,
    timeout: int = 30,
    memory_limit_mb: int | None = 2048,
) -> list[TurnResult]:
    """Iteratively fix code that fails to execute."""
    turns: list[TurnResult] = []
    code = first_code
    execution = first_execution

    for turn_idx in range(1, max_turns + 1):
        if execution and execution.success and execution.objective_value is not None:
            break

        error_text = ""
        if execution:
            error_text = execution.stderr or execution.stdout or "No output"
        else:
            error_text = "No code was generated"

        prompt = SELF_DEBUG_PROMPT.format(
            error=error_text[:2000],
            question=question,
            code=code[:3000],
        )
        response = client.generate(prompt)
        code = extract_code_block(response.text)
        if not code:
            turns.append(TurnResult(turn=turn_idx, code="", success=False, predicted=None, error="no_code"))
            break

        execution = execute_code(code, timeout=timeout, memory_limit_mb=memory_limit_mb)
        turns.append(TurnResult(
            turn=turn_idx,
            code=code,
            success=bool(execution and execution.success),
            predicted=execution.objective_value if execution and execution.success else None,
            error=execution.stderr[:500] if execution and not execution.success else None,
        ))

    return turns


def reflexion_turns(
    client,
    question: str,
    first_code: str,
    first_execution,
    ground_truth: float | str | None = None,
    max_turns: int = 2,
    timeout: int = 30,
    memory_limit_mb: int | None = 2048,
) -> list[TurnResult]:
    """Reflect on wrong-answer outputs and retry."""
    turns: list[TurnResult] = []
    code = first_code
    execution = first_execution

    for turn_idx in range(1, max_turns + 1):
        if execution and execution.success and execution.objective_value is not None:
            if ground_truth is not None:
                from or_eval.metrics import numerical_judge
                if numerical_judge(execution.objective_value, ground_truth):
                    break

        stdout_text = execution.stdout[:2000] if execution else "No output"
        prompt = REFLEXION_PROMPT.format(
            stdout=stdout_text,
            question=question,
            code=code[:3000],
        )
        response = client.generate(prompt)
        code = extract_code_block(response.text)
        if not code:
            turns.append(TurnResult(turn=turn_idx, code="", success=False, predicted=None, error="no_code"))
            break

        execution = execute_code(code, timeout=timeout, memory_limit_mb=memory_limit_mb)
        turns.append(TurnResult(
            turn=turn_idx,
            code=code,
            success=bool(execution and execution.success),
            predicted=execution.objective_value if execution and execution.success else None,
            error=execution.stderr[:500] if execution and not execution.success else None,
        ))

    return turns
