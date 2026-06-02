import unittest
import tempfile
from pathlib import Path
from click.testing import CliRunner

from or_eval.data import DEFAULT_DATA_DIR, validation_split
from or_eval.evaluation import RESULT_SCHEMA_VERSION, fairness_smoke_check
from or_eval.cli import main
from or_eval.execution.extractors import extract_code_block, extract_objective_record, extract_objective_value, extract_solver_status, extract_variable_values
from or_eval.execution.solver_env import detect_solvers, primary_solver, solver_available, solver_availability_state, solver_environment_hash, solver_environment_snapshot
from or_eval.metrics import aggregate_results, classify_failure, numerical_judge, solution_verification_record, tolerance_flags, verification_status
from or_eval.reporting.reports import _fairness_audit, _prompt_bias_rows, _result_status


class SolverDetectionTests(unittest.TestCase):
    def test_detects_imported_solver_modules(self):
        code = """
import pulp
from scipy.optimize import linprog
import gurobipy as gp
"""
        self.assertEqual(detect_solvers(code), ["gurobipy", "pulp", "scipy.optimize"])
        self.assertEqual(primary_solver("import pulp\n"), "pulp")

    def test_unknown_when_no_solver_evidence(self):
        self.assertEqual(primary_solver("print(42)"), "unknown")


class ExtractionTests(unittest.TestCase):
    def test_extracts_python_fenced_code(self):
        text = "Here is code:\n```python\nprint('OBJECTIVE_VALUE:', 12.5)\n```"
        self.assertEqual(extract_code_block(text), "print('OBJECTIVE_VALUE:', 12.5)")

    def test_extracts_objective_and_status(self):
        output = "Status: Optimal\nOBJECTIVE_VALUE = 123.45"
        self.assertEqual(extract_solver_status(output), "optimal")
        self.assertEqual(extract_objective_value(output), 123.45)
        record = extract_objective_record(output)
        self.assertEqual(record.value, 123.45)
        self.assertEqual(record.source, "objective_value")

    def test_strict_objective_extraction_ignores_traceback_numbers(self):
        output = "Traceback line 49: AttributeError"
        self.assertEqual(extract_objective_record(output, allow_fallback=False).value, None)
        self.assertEqual(extract_objective_record(output, allow_fallback=True).value, 49.0)

    def test_extracts_optional_variable_values(self):
        output = 'OBJECTIVE_VALUE: 10\nVARIABLE_VALUES: {"x": 2, "y": 3.5}'
        self.assertEqual(extract_variable_values(output), {"x": 2, "y": 3.5})


class MetricsTests(unittest.TestCase):
    def test_tolerance_flags(self):
        flags = tolerance_flags(104.0, 100.0)
        self.assertTrue(flags["acc_5pct"])
        self.assertFalse(flags["acc_1pct"])
        self.assertFalse(flags["acc_1e-4"])
        self.assertTrue(numerical_judge("INFEASIBLE", "infeasible"))

    def test_aggregate_results(self):
        rows = [
            {"executable": True, "solve_success": True, "predicted": 100.1, "variable_values": {"x": 1}, "acc_5pct": True, "acc_1pct": True, "acc_1e-4": False, "solver": "pulp", "gap": 0.001, "latency": 1.0, "tokens_total": 100},
            {"executable": False, "solve_success": False, "acc_5pct": False, "acc_1pct": False, "acc_1e-4": False, "solver": "unknown", "gap": None, "latency": 3.0, "tokens_total": 200},
        ]
        metrics = aggregate_results(rows)
        self.assertEqual(metrics["n"], 2)
        self.assertEqual(metrics["accuracy"], 0.5)
        self.assertEqual(metrics["executable_rate"], 0.5)
        self.assertEqual(metrics["solve_rate"], 0.5)
        self.assertEqual(metrics["objective_evaluable_rate"], 0.5)
        self.assertEqual(metrics["variable_output_rate"], 0.5)
        self.assertEqual(metrics["avg_latency"], 2.0)
        self.assertEqual(metrics["avg_tokens"], 150.0)

    def test_solve_rate_requires_solve_success(self):
        rows = [
            {"executable": False, "solve_success": False, "solver_status": "optimal", "acc_5pct": False, "acc_1pct": False, "acc_1e-4": False, "solver": "pulp"},
            {"executable": True, "solve_success": True, "solver_status": "optimal", "acc_5pct": True, "acc_1pct": True, "acc_1e-4": True, "solver": "pulp"},
        ]
        self.assertEqual(aggregate_results(rows)["solve_rate"], 0.5)

    def test_classifies_common_failures(self):
        row = {
            "code": "import missing_package",
            "executable": False,
            "acc_5pct": False,
            "execution": {"stderr": "ModuleNotFoundError: No module named 'missing_package'"},
        }
        self.assertEqual(classify_failure(row), "missing_module")

    def test_verification_status_tracks_objective_and_variables(self):
        self.assertEqual(verification_status({"executable": False}), "not_executable")
        self.assertEqual(verification_status({"executable": True, "predicted": None}), "missing_objective")
        self.assertEqual(verification_status({"executable": True, "predicted": 1, "acc_5pct": True}), "objective_match")
        self.assertEqual(
            verification_status({"executable": True, "predicted": 1, "acc_5pct": False, "variable_values": {"x": 1}}),
            "objective_mismatch_with_variables",
        )

    def test_solution_verification_is_explicit_about_constraints(self):
        row = {"predicted": 10, "gap": 0.0, "acc_5pct": True, "variable_values": {"x": 2}}
        record = solution_verification_record(row)
        self.assertEqual(record["objective_status"], "match")
        self.assertEqual(record["variable_count"], 1)
        self.assertEqual(record["constraint_feasibility"], "not_checked")
        solved = solution_verification_record({**row, "solve_success": True})
        self.assertEqual(solved["constraint_feasibility"], "solver_reported_feasible")


class ReproducibilityTests(unittest.TestCase):
    def test_solver_environment_hash_is_stable(self):
        snapshot = solver_environment_snapshot()
        self.assertEqual(solver_environment_hash(snapshot), solver_environment_hash(snapshot))
        self.assertFalse(solver_available("unknown", {"pulp": True}))
        self.assertEqual(solver_availability_state("unknown", {"pulp": True}), "not_detected")
        self.assertEqual(solver_availability_state("pulp", {"pulp": True}), "available")
        self.assertEqual(solver_availability_state("cvxpy", {"cvxpy": False}), "unavailable")


class ReportingTests(unittest.TestCase):
    def test_prompt_bias_rows_track_unavailable_solver_exposure(self):
        rows = [
            {"model": "m", "prompt_id": "neutral", "solver": "pulp", "solver_available": True, "executable": True, "solve_success": True, "acc_5pct": True, "acc_1pct": True, "acc_1e-4": True},
            {"model": "m", "prompt_id": "neutral", "solver": "pulp", "solver_available": True, "executable": True, "solve_success": True, "acc_5pct": True, "acc_1pct": True, "acc_1e-4": True},
            {"model": "m", "prompt_id": "neutral", "solver": "cvxpy", "solver_available": False, "executable": False, "solve_success": False, "acc_5pct": False, "acc_1pct": False, "acc_1e-4": False},
        ]
        [row] = _prompt_bias_rows(rows)
        self.assertEqual(row["top_solver"], "pulp")
        self.assertAlmostEqual(row["max_solver_share"], 2 / 3)
        self.assertAlmostEqual(row["unavailable_solver_rate"], 1 / 3)

    def test_fairness_audit_flags_core_checks(self):
        rows = [
            {
                "run_key": "m|p|1",
                "schema_version": RESULT_SCHEMA_VERSION,
                "prompt_hash": "a",
                "config_hash": "b",
                "solver_env_hash": "c",
                "executable": True,
                "predicted": 1.0,
                "variable_values": {"x": 1},
                "acc_5pct": True,
                "acc_1pct": True,
                "acc_1e-4": True,
                "solve_success": True,
                "solver": "pulp",
                "failure_type": "correct",
            }
        ]
        summary = aggregate_results(rows)
        audit = _fairness_audit(rows, rows, summary, _prompt_bias_rows(rows), [{"solver": "pulp", "available": True}])
        checks = {item["name"]: item for item in audit["checks"]}
        self.assertEqual(checks["schema_version_coverage"]["status"], "pass")
        self.assertEqual(checks["failed_prediction_suppression"]["status"], "pass")
        self.assertEqual(checks["variable_solution_evidence"]["status"], "pass")
        status = _result_status(audit, summary)
        self.assertFalse(status["framework_ready"])
        self.assertFalse(status["results_ready_for_paper"])
        self.assertFalse(status["legacy_results"])

    def test_fairness_smoke_check_produces_pass_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = fairness_smoke_check(Path(tmp))
            self.assertEqual(report["fairness_audit"]["overall_status"], "pass")
            self.assertEqual(report["result"]["schema_version"], RESULT_SCHEMA_VERSION)
            self.assertEqual(report["summary"]["variable_output_rate"], 1.0)
            self.assertTrue((Path(tmp) / "report" / "fairness_audit.json").exists())

    def test_fairness_audit_cli_strict_passes_for_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            fairness_smoke_check(Path(tmp))
            result = CliRunner().invoke(main, ["fairness-audit", "--results-dir", tmp, "--strict"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn('"overall_status": "pass"', result.output)
            status = CliRunner().invoke(main, ["result-status", "--results-dir", tmp])
            self.assertEqual(status.exit_code, 0, status.output)
            self.assertIn('"results_ready_for_paper": true', status.output)

    def test_fairness_protocol_manifest_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "protocol.json"
            result = CliRunner().invoke(main, ["fairness-protocol", "--output-file", str(output)])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(output.exists())
            self.assertIn(RESULT_SCHEMA_VERSION, output.read_text(encoding="utf-8"))
            self.assertIn("schema_version_coverage", result.output)


class DataSplitTests(unittest.TestCase):
    def test_validation_split_is_seeded_and_balanced(self):
        split_a = validation_split(DEFAULT_DATA_DIR, per_dataset=2, seed=42)
        split_b = validation_split(DEFAULT_DATA_DIR, per_dataset=2, seed=42)
        self.assertEqual([p.id for p in split_a], [p.id for p in split_b])
        self.assertEqual(len(split_a), 12)
        self.assertEqual(sorted({p.dataset for p in split_a}), [
            "IndustryOR",
            "MAMO_ComplexLP",
            "MAMO_EasyLP",
            "NL4OPT",
            "OptMATH_Bench",
            "OptiBench",
        ])


if __name__ == "__main__":
    unittest.main()
