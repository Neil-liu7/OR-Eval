# Contributing to OR-Eval

Thank you for your interest in contributing to OR-Eval! This document provides guidelines for development, testing, and submitting changes.

## Development Setup

```bash
git clone https://github.com/your-org/OR-Eval.git
cd OR-Eval
pip install -e ".[dev,all-providers]"
```

Verify your setup:

```bash
python -m unittest discover -s tests -v
python -m or_eval.cli fairness-smoke --output-dir /tmp/smoke
```

## Code Style

- Python 3.9+ with type annotations
- No external linter enforced; keep code consistent with existing style
- Prefer `pathlib.Path` over `os.path`
- Use `dataclass` for structured return types
- Keep functions focused — single responsibility

## Testing

Run the full test suite before submitting any PR:

```bash
python -m unittest discover -s tests -v
```

The test suite includes:
- `test_core.py` — solver detection, extraction, metrics, fairness audit, reporting
- `test_providers.py` — multi-provider routing, factory, response parsing

For changes that touch the fairness protocol:

```bash
python -m or_eval.cli fairness-smoke --output-dir /tmp/smoke
python -m or_eval.cli fairness-audit --results-dir /tmp/smoke --strict
```

## Architecture Principles

1. **Append-only JSONL** — evaluation results are never mutated; new runs append rows
2. **Hash-gated resume** — resuming only reuses rows with matching `prompt_hash`, `config_hash`, and `solver_env_hash`
3. **Solver neutrality** — the primary prompt must never name a specific solver
4. **Single-pass** — no self-debug, multi-turn, or agent interaction in the standard evaluation
5. **Deterministic** — `temperature=0`, seeded splits, reproducible environment hashes

## Adding a New Provider

1. Add a new class in `or_eval/inference/providers.py` extending `BaseProvider`
2. Implement the `generate(prompt, system_prompt) -> ModelResponse` method
3. Register it in `PROVIDER_REGISTRY`
4. Add auto-detection logic in `_detect_provider()` if applicable
5. Add tests in `tests/test_providers.py`

## Adding a New Dataset

1. Place the data file in `data/unified/` (JSONL or JSON format)
2. Add the filename mapping in `or_eval/data/loader.py::DATASET_FILES`
3. Ensure each row has `en_question` (or `question`) and `en_answer` (or `answer`) fields
4. If the format is non-standard, add an adapter in `or_eval/data/adapters/`
5. Update the dataset count in documentation

## Adding a New Solver

1. Add a `SolverSpec` entry in `or_eval/execution/solver_env.py::SOLVER_SPECS`
2. The AST-based import detection in `detect_solvers()` handles most cases automatically
3. Add test coverage in `tests/test_core.py::SolverDetectionTests`

## Submitting Changes

1. Create a feature branch from `main`
2. Make your changes with clear, atomic commits
3. Ensure all tests pass and fairness smoke check is green
4. Submit a PR with:
   - What changed and why
   - Test evidence (test output or fairness-audit result)
   - Any breaking changes noted

## Reporting Issues

- Include the output of `python -m or_eval.cli solver-env`
- Include the Python version and OS
- For evaluation issues, include the relevant JSONL row (redact API keys)

## Versioning

OR-Eval follows semantic versioning:
- **Major** — breaking changes to result schema or CLI interface
- **Minor** — new features, new providers, new datasets
- **Patch** — bug fixes, documentation updates
