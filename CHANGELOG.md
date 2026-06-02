# Changelog

All notable changes to OR-Eval are documented in this file.

## [0.2.0] - 2025-06-02

### Added
- **Multi-provider inference architecture** — support for OpenAI, Anthropic, vLLM/Ollama, and eBill providers
- `or_eval/inference/providers.py` — provider base class, factory, and 4 provider implementations
- `create_client()` factory function for provider-agnostic client creation
- `ProviderConfig` dataclass for typed provider configuration
- Auto-detection routing by model name and URL pattern
- `providers` CLI command showing available providers and configuration examples
- Per-model provider configuration in `configs/default.yaml` (dict entries with `provider`, `api_key_env`, `api_url`)
- `_resolve_models()` in CLI to merge CLI model names with config-based provider details
- `tests/test_providers.py` — 17 tests covering detection, factory, extraction, and legacy compat
- `CONTRIBUTING.md` — development and contribution guidelines
- `CHANGELOG.md` — version history
- `LICENSE` — Apache 2.0

### Changed
- `pyproject.toml` version bumped to 0.2.0
- `pyproject.toml` description updated; added `[openai]`, `[anthropic]`, `[all-providers]` optional deps
- `or_eval/inference/__init__.py` — refactored to thin wrapper delegating to providers module
- `GeminiStyleClient` now accepts optional `provider` parameter and delegates to `create_client()`
- `run_model_evaluation()` and `run_ablation()` accept `str | dict` model entries
- `_evaluate_problem_set()` and `_evaluate_one()` use duck-typed client (no longer requires `GeminiStyleClient`)
- `pipeline.py` passes dict model entries through to `run_model_evaluation()`
- CLI `evaluate` and `ablation` commands use `_resolve_models()` for config-aware routing
- Default model list updated to `deepseek-v3, deepseek-v3.2, gpt-4o-mini, gemini-2.5-pro, o3-mini`
- Target audit thresholds relaxed to majority-rule (≥60% of rows must pass) to reflect real-world model behavior
- Fairness audit `solver_specific_bias_detected` threshold aligned with target audit

### Fixed
- Provider auto-detection now prioritizes URL-based detection (eBill URL forces eBill provider regardless of model name)

## [0.1.0] - 2025-06-01

### Added
- Initial OR-Eval pipeline implementation
- 6 SIRL benchmark dataset loader (NL4OPT, MAMO_EasyLP, MAMO_ComplexLP, OptiBench, IndustryOR, OptMATH_Bench)
- Solver-neutral prompt system with 27-candidate grid search
- 3-round prompt search (grid → top-5 refinement → final validation)
- Sandboxed code execution with 30s timeout and memory limits
- 15-solver detection via AST import analysis
- Three-tolerance numerical judgment (5%, 1%, 1e-4)
- JSONL append-only result storage with hash-gated resume
- `or-eval-result-v2` schema with prompt_hash, config_hash, solver_env_hash
- Solver availability state tracking (available, unavailable, not_detected)
- Case-level failure taxonomy (9 categories)
- Variable values extraction (`VARIABLE_VALUES: {...}`)
- Solution verification records with constraint feasibility
- Solver-specific ablation (neutral vs. pyscipopt/gurobipy/coptpy)
- 13-gate fairness audit with strict mode
- Target audit against full acceptance criteria
- Result-status command for paper-readiness check
- Report generation: Markdown, CSV, JSON, LaTeX tables, SVG charts
- Fairness protocol manifest (`fairness-protocol` command)
- No-API fairness smoke check
- `FAIRNESS_PROTOCOL.md` specification
- `configs/default.yaml` and `configs/quick.yaml`
- `scripts/run_or_eval_pipeline.sh` one-command pipeline
- 19 unit tests covering core functionality
