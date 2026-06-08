"""Tests for the task registry system."""
from or_eval.tasks import TaskConfig, get_task, list_tasks


def test_builtin_tasks_registered():
    tasks = list_tasks()
    assert len(tasks) == 6
    expected = {"NL4OPT", "MAMO_EasyLP", "MAMO_ComplexLP", "OptiBench", "IndustryOR", "OptMATH_Bench"}
    assert set(tasks.keys()) == expected


def test_task_metadata():
    t = get_task("NL4OPT")
    assert t.problem_type == "linear_programming"
    assert t.difficulty == "easy"
    assert "nl_understanding" in t.capabilities
    assert t.source == "Ramamonjison et al., 2023"


def test_difficulty_gradient():
    tasks = list_tasks()
    levels = {"easy": 0, "medium": 1, "hard": 2, "expert": 3, "mixed": 1}
    assert levels[tasks["NL4OPT"].difficulty] < levels[tasks["IndustryOR"].difficulty]
    assert levels[tasks["IndustryOR"].difficulty] < levels[tasks["OptMATH_Bench"].difficulty]


def test_task_config_fields():
    t = get_task("OptiBench")
    assert isinstance(t.capabilities, list)
    assert t.evaluation_mode == "single_pass"
    assert t.dataset_file == "OptiBench.jsonl"
