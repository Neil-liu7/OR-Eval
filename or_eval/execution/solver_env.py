"""Solver detection and execution-environment inspection."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
from dataclasses import dataclass
from importlib import metadata


@dataclass(frozen=True)
class SolverSpec:
    id: str
    packages: tuple[str, ...]
    display_name: str


SOLVER_SPECS: tuple[SolverSpec, ...] = (
    SolverSpec("pyscipopt", ("pyscipopt",), "SCIP / PySCIPOpt"),
    SolverSpec("gurobipy", ("gurobipy",), "Gurobi"),
    SolverSpec("coptpy", ("coptpy",), "COPT"),
    SolverSpec("pulp", ("pulp",), "PuLP"),
    SolverSpec("cvxpy", ("cvxpy",), "CVXPY"),
    SolverSpec("pyomo", ("pyomo", "pyomo.environ"), "Pyomo"),
    SolverSpec("ortools", ("ortools",), "OR-Tools"),
    SolverSpec("scipy.optimize", ("scipy.optimize",), "SciPy Optimize"),
    SolverSpec("docplex", ("docplex", "docplex.mp.model"), "DOcplex"),
    SolverSpec("mip", ("mip",), "Python-MIP"),
    SolverSpec("amplpy", ("amplpy",), "AMPLPy"),
    SolverSpec("xpress", ("xpress",), "FICO Xpress"),
    SolverSpec("highspy", ("highspy",), "HiGHS"),
    SolverSpec("mosek", ("mosek",), "MOSEK"),
    SolverSpec("linopy", ("linopy",), "Linopy"),
)

IMPORT_TO_SOLVER = {
    package: spec.id
    for spec in SOLVER_SPECS
    for package in spec.packages
}


def detect_available_solvers() -> dict[str, bool]:
    """Return whether each supported solver package is importable locally."""
    available: dict[str, bool] = {}
    for spec in SOLVER_SPECS:
        available[spec.id] = any(_safe_find_spec(pkg) for pkg in spec.packages)
    return available


def solver_environment_snapshot() -> dict:
    """Return a reproducible snapshot of local solver package availability."""
    solvers = {}
    for spec in SOLVER_SPECS:
        packages = {}
        installed = False
        for package in spec.packages:
            is_available = _safe_find_spec(package)
            packages[package] = {
                "available": is_available,
                "version": _safe_version(package) if is_available else None,
            }
            installed = installed or is_available
        solvers[spec.id] = {
            "display_name": spec.display_name,
            "available": installed,
            "packages": packages,
        }
    return {"solvers": solvers}


def solver_environment_hash(snapshot: dict | None = None) -> str:
    """Hash the availability matrix so resumed runs can detect env changes."""
    snapshot = snapshot or solver_environment_snapshot()
    payload = json.dumps(snapshot, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def detect_solvers(code: str) -> list[str]:
    """Detect solver libraries used by generated Python code.

    Detection prioritizes imports to avoid over-counting modeling words like
    ``Variable`` or ``Problem`` as solver evidence.
    """
    found: set[str] = set()
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    _add_import_match(alias.name, found)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    _add_import_match(node.module, found)
    except SyntaxError:
        pass

    lowered = code.lower()
    for spec in SOLVER_SPECS:
        for package in spec.packages:
            if re.search(rf"\b{re.escape(package.lower())}\b", lowered):
                found.add(spec.id)

    return sorted(found)


def primary_solver(code: str) -> str:
    solvers = detect_solvers(code)
    if not solvers:
        return "unknown"
    return solvers[0] if len(solvers) == 1 else "+".join(solvers)


def solver_available(solver_id: str, availability: dict[str, bool] | None = None) -> bool:
    """Return whether all detected solver packages are available locally."""
    return solver_availability_state(solver_id, availability) == "available"


def solver_availability_state(solver_id: str, availability: dict[str, bool] | None = None) -> str:
    """Classify detected solver availability without conflating unknown code."""
    if not solver_id or solver_id == "unknown":
        return "not_detected"
    availability = availability or detect_available_solvers()
    parts = solver_id.split("+")
    return "available" if all(availability.get(part, False) for part in parts) else "unavailable"


def _add_import_match(module_name: str, found: set[str]) -> None:
    parts = module_name.split(".")
    candidates = [module_name, parts[0], ".".join(parts[:2]) if len(parts) > 1 else parts[0]]
    for candidate in candidates:
        if candidate in IMPORT_TO_SOLVER:
            found.add(IMPORT_TO_SOLVER[candidate])


def _safe_find_spec(package: str) -> bool:
    try:
        return importlib.util.find_spec(package) is not None
    except (ImportError, ModuleNotFoundError, AttributeError, ValueError):
        return False


def _safe_version(package: str) -> str | None:
    try:
        return metadata.version(package.split(".")[0])
    except metadata.PackageNotFoundError:
        return None
    except Exception:
        return None
