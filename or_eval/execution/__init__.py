"""Solver execution engine: sandbox execution + result extraction."""
from or_eval.execution.sandbox import execute_code, ExecutionResult
from or_eval.execution.extractors import (
    ObjectiveExtraction,
    extract_code_block,
    extract_objective_record,
    extract_objective_value,
    extract_solver_status,
    extract_variable_values,
)
from or_eval.execution.solver_env import (
    detect_available_solvers,
    detect_solvers,
    primary_solver,
    solver_available,
    solver_availability_state,
    solver_environment_hash,
    solver_environment_snapshot,
)
