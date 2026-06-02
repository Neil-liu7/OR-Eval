# OR-Eval Fairness Protocol v2

## Overview

OR-Eval evaluates single-pass optimization-code generation under a solver-neutral
primary prompt. The fairness protocol separates model behavior from prompt bias,
solver environment effects, code execution failures, and objective extraction
artifacts.

This protocol ensures that:
1. Results are reproducible across machines and time
2. Reported metrics cannot be inflated by prompt engineering or environment tricks
3. Failures are transparently categorized rather than silently dropped
4. Solver bias is measured and disclosed

## Design Principles

- **Solver neutrality**: The primary evaluation prompt must not name or prescribe any specific optimization solver
- **Single-pass**: No self-debug, Reflexion, or multi-turn agent interaction
- **Deterministic**: Temperature = 0, seeded validation splits
- **Append-only**: JSONL results are never mutated; new evaluations append rows
- **Hash-gated**: Resume only reuses rows with matching prompt, config, and environment hashes
- **Transparent failures**: Non-executable code is reported, not silently excluded

## Result Schema

Current result rows must use:

```text
schema_version = or-eval-result-v2
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Must be `or-eval-result-v2` |
| `run_key` | string | `model\|prompt_id\|problem_id` unique identifier |
| `model` | string | Model name used for inference |
| `dataset` | string | Source dataset name |
| `problem_id` | string | `Dataset:index` problem identifier |
| `prompt_id` | string | Prompt variant identifier |
| `prompt_type` | string | `neutral` or `solver_specific` |
| `question` | string | Original problem text |
| `answer` | number | Ground truth optimal value |
| `raw_response` | string | Full model response |
| `code` | string | Extracted Python code block |
| `executable` | boolean | Whether code ran without error |
| `solver` | string | Detected solver library |
| `solver_availability_state` | string | `available`, `unavailable`, or `not_detected` |
| `solver_status` | string | `optimal`, `infeasible`, `unbounded`, `timeout`, `error`, `unknown` |
| `solve_success` | boolean | Code produced a feasible solution |
| `predicted` | number\|null | Extracted objective value (null if not executable) |
| `objective_extraction` | object | Extraction source and confidence |
| `variable_values` | object\|null | Decision variable values if reported |
| `solution_verification` | object | Verification evidence record |
| `gap` | number\|null | Relative optimality gap |
| `prompt_hash` | string | SHA-256 of prompt content |
| `config_hash` | string | SHA-256 of execution config |
| `solver_env_hash` | string | SHA-256 of solver availability matrix |
| `failure_type` | string | Classified failure category |
| `verification_status` | string | Verification state |
| `acc_5pct` | boolean | Within 5% tolerance |
| `acc_1pct` | boolean | Within 1% tolerance |
| `acc_1e-4` | boolean | Within 1e-4 tolerance |

### Critical Invariants

- Non-executable rows MUST have `predicted = null` and `gap = null`
- The `failure_type` field MUST be populated for every row
- `solver_availability_state` MUST distinguish between "model chose an unavailable solver" and "no solver was detected in the code"

## Fairness Audit Gates

The audit system checks 13 gates:

| # | Gate | Pass Condition |
|---|------|----------------|
| 1 | `full_eval_rows` | Full evaluation rows exist |
| 2 | `ablation_rows` | Ablation comparison rows exist |
| 3 | `schema_version_coverage` | ≥99.9% of rows use current schema |
| 4 | `prompt_hash_coverage` | ≥99.9% of rows have prompt hashes |
| 5 | `config_hash_coverage` | ≥99.9% of rows have config hashes |
| 6 | `solver_env_hash_coverage` | ≥99.9% of rows have environment hashes |
| 7 | `failed_prediction_suppression` | Zero non-executable rows with predictions |
| 8 | `solver_environment_reported` | Solver availability matrix is present |
| 9 | `failure_taxonomy_reported` | Failure types are classified |
| 10 | `objective_evaluable_metric` | Objective-evaluable rate is tracked |
| 11 | `variable_solution_evidence` | Variable values capture rate > 0 |
| 12 | `solver_specific_bias_detected` | ≥60% of solver-specific ablation rows show max_share ≥ 0.90 |
| 13 | `neutral_prompt_bias_measured` | Neutral prompt concentration is measured |

### Strict Mode

In strict mode (`--strict`), all gates must pass. In normal mode, warnings are permitted for gates 11–13 (which depend on data completeness rather than framework correctness).

## Reproducibility Hashes

### prompt_hash

```python
sha256(json.dumps({"id": prompt_id, "text": prompt_text, "type": prompt_type}, sort_keys=True))
```

### config_hash

```python
sha256(json.dumps({
    "api_url": ..., "temperature": 0, "max_tokens": ...,
    "timeout": ..., "memory_limit_mb": ...
}, sort_keys=True))
```

Note: `concurrency` is excluded from config_hash (it affects scheduling, not results).

### solver_env_hash

```python
sha256(json.dumps(solver_environment_snapshot(), sort_keys=True))
```

The snapshot records every solver's availability status and package version.

## Resume Protocol

JSONL resume reuses existing rows ONLY when ALL THREE match:
1. `prompt_hash` — same prompt text and type
2. `config_hash` — same execution parameters
3. `solver_env_hash` — same solver availability (OR backward-compatible semantic match)

If any hash differs, the problem is re-evaluated from scratch.

## Failure Taxonomy

| Category | Condition |
|----------|-----------|
| `correct` | acc_5pct = true |
| `api_error` | API call failed |
| `no_code` | No code block extracted |
| `timeout` | Execution exceeded time limit |
| `missing_module` | ImportError / ModuleNotFoundError |
| `syntax_error` | SyntaxError in generated code |
| `name_error` | NameError (undefined variable) |
| `runtime_error` | Other execution error |
| `infeasible_unbounded_misclassification` | Reports infeasible/unbounded for a feasible problem |
| `exec_no_solve` | Executes but no solution found |
| `missing_objective` | Executes but no objective extracted |
| `wrong_numeric` | Objective extracted but outside tolerance |

## Running the Audit

```bash
# Normal mode (warnings allowed)
python -m or_eval.cli fairness-audit \
  --results-dir results/or_eval_pipeline_v2 \
  --output-dir results/or_eval_pipeline_v2/report

# Strict mode (all must pass)
python -m or_eval.cli fairness-audit \
  --results-dir results/or_eval_pipeline_v2 \
  --output-dir results/or_eval_pipeline_v2/report \
  --strict
```

## No-API Smoke Check

Before running expensive model calls, verify framework correctness locally:

```bash
python -m or_eval.cli fairness-smoke --output-dir /tmp/smoke
python -m or_eval.cli fairness-audit --results-dir /tmp/smoke --strict
```

The smoke check creates synthetic results that exercise all schema fields, variable output, and solver detection.

## Machine-Readable Manifest

```bash
python -m or_eval.cli fairness-protocol --output-file protocol.json
```

This outputs a JSON manifest listing the schema version, required fields, audit gates, metrics, commands, and expected artifacts.
