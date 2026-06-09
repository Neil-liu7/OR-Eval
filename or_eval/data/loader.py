"""Unified loader for the six SIRL benchmark datasets."""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


DATASET_FILES = {
    "NL4OPT": "NL4OPT.jsonl",
    "MAMO_EasyLP": "MAMO_EasyLP_fixed.jsonl",
    "MAMO_ComplexLP": "MAMO_ComplexLP_fixed.jsonl",
    "OptiBench": "OptiBench.jsonl",
    "IndustryOR": "IndustryOR_fixedV2.json",
    "OptMATH_Bench": "OptMATH_Bench_166.jsonl",
    "ORQA": "ORQA_test.jsonl",
}

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_EXTERNAL_DATA_DIR = _PROJECT_ROOT.parent / "OPTEngine" / "SIRL" / "test_data"
_LOCAL_DATA_DIR = _PROJECT_ROOT / "data"

DEFAULT_DATA_DIR = _EXTERNAL_DATA_DIR if _EXTERNAL_DATA_DIR.exists() else _LOCAL_DATA_DIR


@dataclass(frozen=True)
class BenchmarkProblem:
    id: str
    dataset: str
    question: str
    answer: float | str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_dataset(dataset: str, data_dir: Path | str = DEFAULT_DATA_DIR) -> list[BenchmarkProblem]:
    data_dir = Path(data_dir)
    if dataset not in DATASET_FILES:
        raise KeyError(f"Unknown dataset {dataset!r}. Choose from: {', '.join(DATASET_FILES)}")
    path = data_dir / DATASET_FILES[dataset]
    rows = list(_read_json_or_jsonl(path))
    if dataset == "ORQA":
        return _load_orqa(rows, dataset)
    problems: list[BenchmarkProblem] = []
    for i, row in enumerate(rows):
        question = row.get("en_question") or row.get("question") or row.get("problem_text")
        answer = row.get("en_answer") if "en_answer" in row else row.get("answer")
        if question is None or answer is None:
            raise ValueError(f"{path}:{i + 1} is missing en_question/en_answer")
        metadata = {k: v for k, v in row.items() if k not in {"en_question", "question", "problem_text", "en_answer", "answer"}}
        raw_id = metadata.get("index", metadata.get("id", i))
        # OptiBench ReSocratic format: "results" dict with all variable values
        if "results" in row and isinstance(row["results"], dict):
            metadata["expected_results"] = row["results"]
            metadata["eval_mode"] = "variable_match"
        problems.append(BenchmarkProblem(
            id=f"{dataset}:{raw_id}",
            dataset=dataset,
            question=str(question),
            answer=_normalize_answer(answer),
            metadata=metadata,
        ))
    return problems


def load_datasets(
    datasets: Iterable[str] | str = "all",
    data_dir: Path | str = DEFAULT_DATA_DIR,
    limit_per_dataset: int | None = None,
) -> list[BenchmarkProblem]:
    selected = list(DATASET_FILES) if datasets == "all" else list(datasets)
    problems: list[BenchmarkProblem] = []
    for dataset in selected:
        items = load_dataset(dataset, data_dir)
        if limit_per_dataset is not None:
            items = items[:limit_per_dataset]
        problems.extend(items)
    return problems


def validation_split(
    data_dir: Path | str = DEFAULT_DATA_DIR,
    per_dataset: int = 50,
    seed: int = 42,
    datasets: Iterable[str] | str = "all",
) -> list[BenchmarkProblem]:
    selected = list(DATASET_FILES) if datasets == "all" else list(datasets)
    rng = random.Random(seed)
    validation: list[BenchmarkProblem] = []
    for dataset in selected:
        items = load_dataset(dataset, data_dir)
        sample_size = min(per_dataset, len(items))
        validation.extend(rng.sample(items, sample_size))
    return validation


def dataset_counts(data_dir: Path | str = DEFAULT_DATA_DIR) -> dict[str, int]:
    return {name: len(load_dataset(name, data_dir)) for name in DATASET_FILES}


def _read_json_or_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return [parsed]
    except json.JSONDecodeError:
        pass

    rows = []
    for line_no, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def _normalize_answer(answer: Any) -> float | str:
    if isinstance(answer, (int, float)):
        return float(answer)
    try:
        return float(str(answer).strip())
    except (TypeError, ValueError):
        return str(answer).strip()


def _load_orqa(rows: list[dict], dataset: str) -> list[BenchmarkProblem]:
    """Load ORQA multiple-choice QA format."""
    problems: list[BenchmarkProblem] = []
    for i, row in enumerate(rows):
        context = row.get("CONTEXT", "")
        question = row.get("QUESTION", "")
        options = row.get("OPTIONS", [])
        target = row.get("TARGET_ANSWER")
        qtype = row.get("QUESTION_TYPE", "")
        options_text = "\n".join(f"{chr(65+j)}. {opt}" for j, opt in enumerate(options))
        full_question = f"{context}\n\nQuestion: {question}\n\n{options_text}"
        answer_letter = chr(65 + target) if isinstance(target, int) else str(target)
        problems.append(BenchmarkProblem(
            id=f"{dataset}:{i}",
            dataset=dataset,
            question=full_question,
            answer=answer_letter,
            metadata={
                "question_type": qtype,
                "options": options,
                "target_index": target,
                "eval_mode": "mcq",
            },
        ))
    return problems
