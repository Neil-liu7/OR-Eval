"""Solver-neutral and solver-specific prompt registry."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptSpec:
    id: str
    text: str
    prompt_type: str = "neutral"
    metadata: dict | None = None


BASE_OUTPUT_RULES = """Return only one fenced Python block.
The program must be self-contained and executable.
It must print the final optimal objective value exactly as:
OBJECTIVE_VALUE: <number>
When practical, also print decision variable values as one JSON object:
VARIABLE_VALUES: {"name": value}
If the model proves infeasible or unbounded, print OBJECTIVE_VALUE: INFEASIBLE or OBJECTIVE_VALUE: UNBOUNDED."""

NEUTRAL_HEADER = """Solve the optimization problem below with Python. Choose any suitable optimization library or exact algorithm yourself. Do not assume a required solver."""

MIXED_MINI_EXAMPLE = """Example output style:
```python
# build and solve the optimization model here
print("OBJECTIVE_VALUE:", value)
```"""


def render_prompt(template: str, question: str, few_shot_examples: list[dict] | None = None) -> str:
    prompt = template.replace("{question}", question.strip())
    if few_shot_examples:
        examples_text = "\n\n".join(
            f"Example {i+1}:\nProblem: {ex['question']}\n```python\n{ex['code']}\n```"
            for i, ex in enumerate(few_shot_examples)
            if "question" in ex and "code" in ex
        )
        prompt = prompt.replace("{examples}", examples_text)
        if "{examples}" not in template:
            prompt = f"{examples_text}\n\nNow solve:\n{prompt}"
    else:
        prompt = prompt.replace("{examples}", "")
    return prompt


def neutral_prompt_candidates() -> list[PromptSpec]:
    instruction_styles = {
        "direct": "Solve the optimization problem below with Python.",
        "expert": "You are an operations research expert writing a reproducible Python solution.",
        "careful": "Carefully translate the natural language optimization problem into decision variables, objective, and constraints, then solve it with Python.",
    }
    solver_mentions = {
        "none": "Choose the modeling approach yourself.",
        "anylib": "Use any appropriate Python optimization package or a clear exact algorithm.",
        "list": "You may use packages such as scipy.optimize, cvxpy, pulp, pyomo, gurobipy, pyscipopt, coptpy, ortools, highspy, or another suitable solver.",
    }
    output_styles = {
        "strict": BASE_OUTPUT_RULES,
        "compact": "Return only executable Python code in a fenced ```python block. Print exactly OBJECTIVE_VALUE: <number>.",
        "status": BASE_OUTPUT_RULES + "\nAlso print a short SOLVER_STATUS line when available.",
    }
    reasoning_styles = {
        "codeonly": "Do not include prose outside the code block.",
        "plan_in_comments": "Put any reasoning as concise comments inside the code only.",
        "parse_first": "Inside the code, define the data from the question explicitly before creating the model.",
    }

    candidates: list[PromptSpec] = []
    idx = 0
    for i_name, instruction in instruction_styles.items():
        for s_name, solver in solver_mentions.items():
            for o_name, output in output_styles.items():
                if len(candidates) >= 27:
                    break
                r_name = list(reasoning_styles)[idx % len(reasoning_styles)]
                template = f"""{instruction}
{solver}
{reasoning_styles[r_name]}

{output}

Problem:
{{question}}
"""
                candidates.append(PromptSpec(
                    id=f"neutral_grid_{i_name}_{s_name}_{o_name}_{r_name}",
                    text=template,
                    prompt_type="neutral",
                    metadata={"instruction": i_name, "solver_mention": s_name, "output": o_name, "reasoning": r_name},
                ))
                idx += 1
            if len(candidates) >= 27:
                break
        if len(candidates) >= 27:
            break
    return candidates


def refine_prompt(spec: PromptSpec) -> list[PromptSpec]:
    refinements = [
        ("numeric_guard", "When extracting the answer, print only the objective value, not variable values."),
        ("robust_status", "Suppress verbose solver logs when possible and handle non-optimal statuses explicitly."),
        ("scale_care", "Pay close attention to units, integer requirements, and whether the task asks to minimize or maximize."),
    ]
    return [
        PromptSpec(
            id=f"{spec.id}_refine_{suffix}",
            text=spec.text.rstrip() + "\n" + extra + "\n",
            prompt_type=spec.prompt_type,
            metadata={**(spec.metadata or {}), "refinement": suffix},
        )
        for suffix, extra in refinements
    ]


def solver_specific_prompts() -> list[PromptSpec]:
    templates = {
        "pyscipopt": """Solve the optimization problem below using Python with pyscipopt/SCIP only.
Return only one fenced Python block. Print exactly OBJECTIVE_VALUE: <number>.

Problem:
{question}
""",
        "gurobipy": """Solve the optimization problem below using Python with gurobipy/Gurobi only.
Return only one fenced Python block. Print exactly OBJECTIVE_VALUE: <number>.

Problem:
{question}
""",
        "coptpy": """Solve the optimization problem below using Python with coptpy/COPT only.
Return only one fenced Python block. Print exactly OBJECTIVE_VALUE: <number>.

Problem:
{question}
""",
    }
    return [PromptSpec(id=f"solver_specific_{name}", text=text, prompt_type="solver_specific", metadata={"solver": name}) for name, text in templates.items()]


def default_neutral_prompt() -> PromptSpec:
    return PromptSpec(
        id="neutral_default",
        text=f"""{NEUTRAL_HEADER}
Use any appropriate Python optimization package or exact algorithm. Keep the solution fair to all solvers by not relying on a prescribed library.
Pay close attention to units, integer requirements, and whether the problem asks for a minimum or maximum.

{BASE_OUTPUT_RULES}
{MIXED_MINI_EXAMPLE}

Problem:
{{question}}
""",
        prompt_type="neutral",
        metadata={"source": "built_in_default"},
    )
