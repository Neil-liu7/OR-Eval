"""Task registry: discover, validate, and load YAML-based task definitions."""
from __future__ import annotations

import importlib
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from or_eval.data.loader import BenchmarkProblem, load_dataset, DEFAULT_DATA_DIR


TASK_CONFIG_DIR = Path(__file__).parent / "configs"

_REGISTRY: dict[str, "TaskConfig"] = {}


@dataclass(frozen=True)
class TaskConfig:
    name: str
    dataset_file: str
    problem_type: str = "mixed"
    difficulty: str = "mixed"
    capabilities: list[str] = field(default_factory=lambda: ["formulation", "coding"])
    evaluation_mode: str = "single_pass"
    description: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def register_task(config: TaskConfig) -> None:
    _REGISTRY[config.name] = config


def get_task(name: str) -> TaskConfig:
    _discover_tasks()
    if name not in _REGISTRY:
        raise KeyError(f"Unknown task {name!r}. Available: {', '.join(sorted(_REGISTRY))}")
    return _REGISTRY[name]


def list_tasks() -> dict[str, TaskConfig]:
    _discover_tasks()
    return dict(sorted(_REGISTRY.items()))


def load_task_problems(
    name: str,
    data_dir: Path | str = DEFAULT_DATA_DIR,
    limit: int | None = None,
) -> list[BenchmarkProblem]:
    config = get_task(name)
    problems = load_dataset(name, data_dir)
    if limit is not None:
        problems = problems[:limit]
    return problems


def _discover_tasks() -> None:
    if _REGISTRY:
        return
    _register_builtin_tasks()
    _load_yaml_configs()


def _register_builtin_tasks() -> None:
    """Register the 6 original hardcoded datasets as TaskConfigs."""
    from or_eval.data.loader import DATASET_FILES

    builtin_meta = {
        "NL4OPT": {
            "problem_type": "linear_programming",
            "difficulty": "easy",
            "capabilities": ["formulation", "coding", "nl_understanding"],
            "description": "Natural language to LP formulation (NeurIPS 2022 competition)",
            "source": "Ramamonjison et al., 2023",
        },
        "MAMO_EasyLP": {
            "problem_type": "linear_programming",
            "difficulty": "easy",
            "capabilities": ["formulation", "coding"],
            "description": "Simple LP mathematical modeling",
            "source": "Huang et al., 2024",
        },
        "MAMO_ComplexLP": {
            "problem_type": "mixed_integer_programming",
            "difficulty": "medium",
            "capabilities": ["formulation", "coding", "constraint_modeling"],
            "description": "Complex LP/MIP mathematical modeling",
            "source": "Huang et al., 2024",
        },
        "OptiBench": {
            "problem_type": "mixed",
            "difficulty": "medium",
            "capabilities": ["formulation", "coding", "solver_selection"],
            "description": "Mixed LP/MIP/NLP optimization",
            "source": "Li et al., 2024",
        },
        "IndustryOR": {
            "problem_type": "mixed",
            "difficulty": "hard",
            "capabilities": ["formulation", "coding", "domain_knowledge", "constraint_modeling"],
            "description": "Real-world industrial optimization scenarios",
            "source": "Tang et al., 2024",
        },
        "OptMATH_Bench": {
            "problem_type": "mathematical_optimization",
            "difficulty": "expert",
            "capabilities": ["formulation", "coding", "mathematical_reasoning"],
            "description": "Mathematical reasoning for optimization",
            "source": "OptMATH, 2024",
        },
        "ORQA": {
            "problem_type": "multiple_choice_qa",
            "difficulty": "medium",
            "capabilities": ["conceptual_understanding", "constraint_identification", "model_reasoning"],
            "description": "OR expert-level multiple-choice QA (AAAI 2025)",
            "source": "Mostajabdaveh et al., AAAI 2025",
            "eval_mode": "mcq",
        },
    }

    for name, filename in DATASET_FILES.items():
        meta = builtin_meta.get(name, {})
        register_task(TaskConfig(
            name=name,
            dataset_file=filename,
            problem_type=meta.get("problem_type", "mixed"),
            difficulty=meta.get("difficulty", "mixed"),
            capabilities=meta.get("capabilities", ["formulation", "coding"]),
            description=meta.get("description", ""),
            source=meta.get("source", ""),
        ))


def _load_yaml_configs() -> None:
    """Load all YAML files from tasks/configs/ and register them."""
    if not TASK_CONFIG_DIR.exists():
        return
    for path in sorted(TASK_CONFIG_DIR.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(raw, dict) or "name" not in raw:
            continue
        if raw["name"] in _REGISTRY:
            continue
        config = TaskConfig(
            name=raw["name"],
            dataset_file=raw.get("dataset_file", f"{raw['name']}.jsonl"),
            problem_type=raw.get("problem_type", "mixed"),
            difficulty=raw.get("difficulty", "mixed"),
            capabilities=raw.get("capabilities", ["formulation", "coding"]),
            evaluation_mode=raw.get("evaluation_mode", "single_pass"),
            description=raw.get("description", ""),
            source=raw.get("source", ""),
            metadata=raw.get("metadata", {}),
        )
        register_task(config)
