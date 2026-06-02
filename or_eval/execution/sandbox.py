"""Sandboxed execution for generated optimization code."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from or_eval.execution.extractors import extract_objective_record, extract_solver_status, extract_variable_values
from or_eval.execution.solver_env import primary_solver


@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    runtime: float
    returncode: int | None
    timed_out: bool = False
    memory_limit_mb: int | None = None
    solver: str = "unknown"
    solver_status: str = "unknown"
    objective_value: float | str | None = None
    objective_extraction: dict | None = None
    variable_values: dict | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def execute_code(code: str, timeout: int = 30, memory_limit_mb: int | None = 2048) -> ExecutionResult:
    """Run code in a subprocess with timeout and best-effort memory limits."""
    solver = primary_solver(code)
    wrapped_code = _wrap_code(code, memory_limit_mb)

    with tempfile.TemporaryDirectory(prefix="or_eval_") as tmp_dir:
        script_path = Path(tmp_dir) / "solution.py"
        script_path.write_text(wrapped_code, encoding="utf-8")

        env = os.environ.copy()
        env.update({
            "PYTHONUNBUFFERED": "1",
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        })
        start = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
            runtime = time.time() - start
            combined = f"{proc.stdout}\n{proc.stderr}"
            status = "error" if proc.returncode != 0 else extract_solver_status(combined)
            objective_record = extract_objective_record(proc.stdout, allow_fallback=proc.returncode == 0)
            return ExecutionResult(
                success=proc.returncode == 0,
                stdout=proc.stdout,
                stderr=proc.stderr,
                runtime=runtime,
                returncode=proc.returncode,
                timed_out=False,
                memory_limit_mb=memory_limit_mb,
                solver=solver,
                solver_status=status,
                objective_value=objective_record.value if proc.returncode == 0 else None,
                objective_extraction=objective_record.to_dict(),
                variable_values=extract_variable_values(proc.stdout),
            )
        except subprocess.TimeoutExpired as exc:
            runtime = time.time() - start
            stdout = _decode_timeout_payload(exc.stdout)
            stderr = _decode_timeout_payload(exc.stderr) or "Timeout"
            return ExecutionResult(
                success=False,
                stdout=stdout,
                stderr=stderr,
                runtime=runtime,
                returncode=None,
                timed_out=True,
                memory_limit_mb=memory_limit_mb,
                solver=solver,
                solver_status="timeout",
                objective_value=None,
                objective_extraction=extract_objective_record(stdout, allow_fallback=False).to_dict(),
                variable_values=extract_variable_values(stdout),
            )


def _wrap_code(code: str, memory_limit_mb: int | None) -> str:
    if memory_limit_mb is None:
        return code
    # resource is Unix-only; import failure is harmless on unsupported platforms.
    prefix = f"""
import os
try:
    import resource
    _or_eval_mem = int({memory_limit_mb}) * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (_or_eval_mem, _or_eval_mem))
except Exception:
    pass
"""
    return textwrap.dedent(prefix).strip() + "\n\n" + code


def _decode_timeout_payload(payload) -> str:
    if payload is None:
        return ""
    if isinstance(payload, bytes):
        return payload.decode("utf-8", errors="replace")
    return str(payload)
