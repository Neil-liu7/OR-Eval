"""Tests for the task registry system."""
import unittest
from pathlib import Path

from or_eval.tasks import TaskConfig, get_task, list_tasks


class TaskRegistryTests(unittest.TestCase):
    def test_builtin_tasks_registered(self):
        tasks = list_tasks()
        expected = {"NL4OPT", "MAMO_EasyLP", "MAMO_ComplexLP", "OptiBench", "IndustryOR", "OptMATH_Bench", "ORQA"}
        self.assertTrue(expected.issubset(set(tasks.keys())))

    def test_task_metadata(self):
        t = get_task("NL4OPT")
        self.assertEqual(t.problem_type, "linear_programming")
        self.assertEqual(t.difficulty, "easy")
        self.assertIn("nl_understanding", t.capabilities)
        self.assertEqual(t.source, "Ramamonjison et al., 2023")

    def test_difficulty_gradient(self):
        tasks = list_tasks()
        levels = {"easy": 0, "medium": 1, "hard": 2, "expert": 3, "mixed": 1}
        self.assertLess(levels[tasks["NL4OPT"].difficulty], levels[tasks["IndustryOR"].difficulty])
        self.assertLess(levels[tasks["IndustryOR"].difficulty], levels[tasks["OptMATH_Bench"].difficulty])

    def test_task_config_fields(self):
        t = get_task("OptiBench")
        self.assertIsInstance(t.capabilities, list)
        self.assertEqual(t.evaluation_mode, "single_pass")
        self.assertEqual(t.dataset_file, "OptiBench.jsonl")

    def test_yaml_task_is_loadable_end_to_end(self):
        """A YAML-only task must be resolvable by the data loader (not just listed)."""
        from or_eval.tasks.registry import _REGISTRY, _discover_tasks, yaml_task_files
        from or_eval.data import load_datasets, DEFAULT_DATA_DIR

        _discover_tasks()
        data_file = "test_yaml_e2e.jsonl"
        (Path(DEFAULT_DATA_DIR) / data_file).write_text(
            '{"en_question": "Maximize x s.t. x <= 5", "en_answer": 5}\n', encoding="utf-8"
        )
        _REGISTRY["TestYAMLE2E"] = TaskConfig(
            name="TestYAMLE2E", dataset_file=data_file, problem_type="linear_programming",
        )
        try:
            self.assertIn("TestYAMLE2E", yaml_task_files())
            problems = load_datasets(["TestYAMLE2E"], DEFAULT_DATA_DIR)
            self.assertEqual(len(problems), 1)
            self.assertEqual(problems[0].answer, 5.0)
        finally:
            _REGISTRY.pop("TestYAMLE2E", None)
            (Path(DEFAULT_DATA_DIR) / data_file).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
