"""Prompt template rendering engine using Jinja2."""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from or_eval.prompts.neutral import (
    PromptSpec,
    default_neutral_prompt,
    neutral_prompt_candidates,
    refine_prompt,
    render_prompt as render_neutral_prompt,
    solver_specific_prompts,
)

PROMPTS_DIR = Path(__file__).parent

_env = Environment(
    loader=FileSystemLoader([
        str(PROMPTS_DIR / "templates"),
        str(PROMPTS_DIR / "solver_instructions"),
        str(PROMPTS_DIR / "variants"),
    ]),
    keep_trailing_newline=True,
)

SOLVERS = {
    "gurobi": "Gurobi (gurobipy)",
    "copt": "COPT (coptpy)",
    "pulp": "PuLP",
    "scip": "SCIP (pyscipopt)",
}


def render_prompt(dimension: str, problem: dict, solver_id: str = None, variant: str = None) -> str:
    template_name = variant if variant else f"{dimension}.j2"
    template = _env.get_template(template_name)

    solver_instructions = ""
    solver_name = ""
    if solver_id and solver_id in SOLVERS:
        solver_name = SOLVERS[solver_id]
        instr_template = _env.get_template(f"{solver_id}.j2")
        solver_instructions = instr_template.render()

    return template.render(
        solver_name=solver_name,
        solver_id=solver_id,
        solver_instructions=solver_instructions,
        **problem,
    )
