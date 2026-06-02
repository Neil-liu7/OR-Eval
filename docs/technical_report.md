# OR-Eval: A Unified Solver-Neutral Evaluation Framework for Operations Research LLMs

## Abstract

We present OR-Eval, an open-source evaluation framework that addresses the reproducibility crisis in benchmarking large language models (LLMs) for operations research (OR) tasks. Existing benchmarks suffer from three fundamental problems: (1) solver-dependent prompts that produce incomparable results across environments, (2) lack of standardized execution and judgment criteria, and (3) absence of fairness guarantees that prevent prompt engineering from inflating reported metrics. OR-Eval introduces a solver-neutral evaluation protocol with cryptographic hash-based reproducibility, automated solver bias detection, and a 13-gate fairness audit. We evaluate 6 models across 1,961 problems from 6 benchmark datasets, demonstrating that solver-specific prompts can inflate accuracy by up to 12 percentage points and that solver unavailability accounts for 10.3% of failures. Our framework enables the first truly comparable cross-model evaluation in the OR+AI space.

## 1. Introduction

### 1.1 Problem Statement

The intersection of large language models and operations research has produced a growing body of benchmarks—NL4OPT, MAMO, OptiBench, IndustryOR, and others—each measuring LLM performance on optimization tasks. However, these benchmarks are fundamentally incomparable due to:

- **Solver lock-in**: Prompts that specify "use Gurobi" or "use PySCIPOpt" produce results that cannot be reproduced without commercial licenses
- **Inconsistent evaluation**: Different tolerance levels, extraction methods, and handling of execution failures
- **Prompt sensitivity**: Small prompt variations yield large accuracy differences, yet prompts are rarely disclosed or controlled
- **Environment dependence**: Solver availability, package versions, and timeout settings vary silently across machines

### 1.2 Contributions

OR-Eval makes four contributions:

1. **Solver-neutral evaluation protocol**: A standardized prompt and execution framework that does not prescribe a solver, while detecting and recording which solver each model actually selects
2. **Fairness audit system**: A 13-gate cryptographic audit ensuring that results are reproducible, correctly attributed, and free from systematic bias
3. **Solver bias quantification**: An ablation methodology that measures how much solver-specific prompts distort reported accuracy
4. **Multi-provider infrastructure**: A unified inference layer supporting 6 providers, enabling fair comparison across proprietary and open-source models

## 2. Related Work

### 2.1 OR Benchmarks

- **NL4OPT** (Ramamonjison et al., 2023): Natural language to linear programming, focusing on formulation accuracy
- **MAMO** (Huang et al., 2024): Mathematical modeling with Easy LP and Complex LP splits
- **OptiBench** (Li et al., 2024): Mixed optimization problems across LP, MIP, and nonlinear domains
- **IndustryOR** (Tang et al., 2024): Real-world industrial optimization scenarios
- **OptMATH_Bench**: Mathematical reasoning for optimization with high difficulty

### 2.2 Code Generation Benchmarks

HumanEval, MBPP, and SWE-bench evaluate code generation but lack OR-specific evaluation criteria (solver detection, numerical tolerance, constraint feasibility).

### 2.3 Gaps Addressed by OR-Eval

| Gap | Existing Approaches | OR-Eval Solution |
|-----|-------------------|------------------|
| Solver dependency | Hard-coded solver in prompt | Solver-neutral prompt + detection |
| Reproducibility | No environment tracking | Hash-based resume with solver_env_hash |
| Failure diagnosis | Binary pass/fail | 9-category failure taxonomy |
| Prompt sensitivity | Single prompt per paper | 3-round search + ablation |
| Execution fairness | Varied timeouts/limits | Standardized sandbox (30s, 2GB) |

## 3. Framework Design

### 3.1 Evaluation Protocol

```
Question → Prompt Template → LLM → Code Extraction → Sandboxed Execution
    → Objective Extraction → Numerical Judgment → Result Row (JSONL)
```

Each result row contains 30+ fields including the raw response, extracted code, execution output, detected solver, solver availability state, predicted value, ground truth, tolerance flags, failure type, and reproducibility hashes.

### 3.2 Solver-Neutral Prompting

The primary evaluation prompt instructs the model to:
1. Choose any suitable optimization library
2. Return self-contained executable Python code
3. Print `OBJECTIVE_VALUE: <number>` for machine-readable extraction
4. Optionally print `VARIABLE_VALUES: {...}` for decision variable evidence

The prompt is selected via a 3-round search:
- **Round 1**: 27 candidates from a grid over instruction style × solver mention × output format × reasoning style
- **Round 2**: Top-5 refined with 3 augmentations each (15 candidates)
- **Round 3**: Final validation on the full dataset or validation split

Scoring: `0.7 × accuracy + 0.2 × executable_rate + 0.1 × solver_uniformity − 0.25 × max(0, max_share − 0.80)`

### 3.3 Solver Detection

OR-Eval detects 15 solver families via AST-based import analysis:

```python
import pulp          → "pulp"
from scipy.optimize  → "scipy.optimize"
import gurobipy      → "gurobipy"
```

When multiple solvers are imported, the primary solver is recorded as `solver1+solver2`. The framework also records whether each detected solver is actually available in the local environment.

### 3.4 Execution Sandbox

Generated code runs in a subprocess with:
- 30-second timeout (configurable)
- 2GB memory limit via `resource.RLIMIT_AS`
- Single-threaded (OMP/MKL/OpenBLAS threads set to 1)
- Temporary directory isolation
- No network access from generated code

### 3.5 Numerical Judgment

Three tolerance levels compare predicted vs. ground truth:
- **@5%**: `|pred - gt| / |gt| ≤ 0.05` (primary metric)
- **@1%**: `|pred - gt| / |gt| ≤ 0.01`
- **@1e-4**: `|pred - gt| ≤ 1e-4` (near-exact)

Special cases: `gt = 0` uses absolute threshold; INFEASIBLE/UNBOUNDED are matched as strings.

### 3.6 Fairness Audit

The 13-gate audit checks:

| Gate | Requirement |
|------|-------------|
| full_eval_rows | Full evaluation data exists |
| ablation_rows | Ablation comparison data exists |
| schema_version_coverage | All rows use current schema |
| prompt_hash_coverage | All rows have prompt hashes |
| config_hash_coverage | All rows have config hashes |
| solver_env_hash_coverage | All rows have environment hashes |
| failed_prediction_suppression | Non-executable rows have no predictions |
| solver_environment_reported | Solver availability matrix is recorded |
| failure_taxonomy_reported | Failure types are classified |
| objective_evaluable_metric | Objective-evaluable rate is tracked |
| variable_solution_evidence | Variable values are captured |
| solver_specific_bias_detected | Solver prompts force concentration |
| neutral_prompt_bias_measured | Neutral prompt bias is measured |

## 4. Experimental Results

### 4.1 Setup

- **Models**: deepseek-v3, deepseek-v3.2, gpt-4o, gpt-4o-mini, gpt-4.1-mini, gemini-2.5-pro, o3-mini
- **Datasets**: 6 benchmarks, 1,961 problems total
- **Temperature**: 0 (deterministic)
- **Execution**: Single-pass, no self-repair

### 4.2 Main Results

| Model | Acc@5% | Acc@1% | Exec% | Solve% | Var% |
|-------|-------:|-------:|------:|-------:|-----:|
| o3-mini* | 86.8 | 85.4 | 96.5 | 90.6 | — |
| gpt-4.1-mini | 73.9 | 72.1 | 87.0 | 84.2 | 80.8 |
| deepseek-v3 | 66.4 | 64.2 | 85.8 | 80.4 | 77.2 |
| deepseek-v3.2 | 56.9 | 54.8 | 71.8 | 67.7 | 63.4 |
| gpt-4o-mini | 50.5 | 48.3 | 79.7 | 69.7 | 66.7 |
| gpt-4o | 39.8 | 38.1 | 43.2 | 42.4 | 40.5 |

*o3-mini: partial evaluation (288/1961 problems)

### 4.3 Per-Dataset Difficulty Gradient

| Dataset | Description | Best Acc | Avg Acc |
|---------|-------------|----------|---------|
| NL4OPT | Basic LP formulation | 86.1% | 75.2% |
| MAMO_EasyLP | Simple LP | 92.5% | 76.2% |
| MAMO_ComplexLP | Complex LP/MIP | 71.9% | 54.6% |
| OptiBench | Mixed optimization | 67.1% | 61.9% |
| IndustryOR | Industrial scenarios | 55.0% | 42.8% |
| OptMATH_Bench | Mathematical reasoning | 34.9% | 22.6% |

### 4.4 Failure Taxonomy

| Failure Type | Share | Description |
|-------------|------:|-------------|
| correct | 57.3% | Within 5% tolerance |
| wrong_numeric | 10.7% | Executes correctly but wrong answer |
| missing_module | 10.3% | Imports unavailable package |
| runtime_error | 6.3% | Execution crashes |
| syntax_error | 5.1% | Invalid Python generated |
| api_error | 4.8% | API call failed |
| infeasible_misclassification | 3.7% | Reports infeasible for feasible problem |
| name_error | 0.9% | Undefined variable |
| exec_no_solve | 0.8% | Runs but no solution found |
| timeout | 0.1% | Exceeds 30s limit |

### 4.5 Solver Bias Analysis

Key findings from the ablation study:

1. **Neutral prompt solver distribution**: Models naturally prefer PuLP (most models) or SciPy (gpt-4o-mini), with top-solver concentration between 0.43–0.87
2. **Solver-specific forcing**: Specifying a solver achieves 0.94–1.00 concentration
3. **COPT unavailability effect**: `solver_specific_coptpy` prompt produces 0% accuracy when COPT is not installed locally, demonstrating the reproducibility risk of solver-specific benchmarks
4. **Accuracy inflation**: For deepseek-v3, switching from neutral (60.3%) to `solver_specific_pyscipopt` (72.7%) inflates accuracy by 12.4 percentage points

## 5. Discussion

### 5.1 Why Solver Neutrality Matters

Our ablation demonstrates that solver-specific prompts create a confound: they measure the combination of (model capability + solver availability + solver-prompt alignment) rather than pure OR problem-solving ability. A benchmark that prescribes Gurobi will show 0% accuracy for any researcher without a Gurobi license.

### 5.2 The missing_module Problem

10.3% of all failures are `missing_module`—the model generates correct code that imports an unavailable package. This is not a model failure but an environment mismatch. OR-Eval reports this separately so researchers can distinguish model capability from environment limitations.

### 5.3 Limitations

- **Single-pass only**: Real-world usage often involves self-debugging; OR-Eval measures the one-shot baseline
- **Numerical comparison only**: Equivalent models with different formulations may have identical objective values; we track variables but cannot verify general constraint feasibility without structured problem data
- **Dataset coverage**: Current benchmarks skew toward LP/MIP; scheduling, routing, and stochastic programming are underrepresented

## 6. Conclusion

OR-Eval provides the first reproducible, solver-neutral, audit-certified evaluation framework for OR LLMs. Our results show that evaluation methodology choices (solver specification, tolerance level, failure handling) can swing reported accuracy by 10–15 percentage points. We release OR-Eval as an open-source tool to establish a common evaluation standard for the OR+AI research community.

## References

- Ramamonjison, R., et al. (2023). NL4Opt: Competition on Natural Language for Optimization.
- Huang, Y., et al. (2024). MAMO: Mathematical Modeling Benchmark for LLMs.
- Li, X., et al. (2024). OptiBench: Benchmarking LLMs for Optimization Problem Solving.
- Tang, Z., et al. (2024). IndustryOR: Industrial Operations Research Benchmark.
- Chen, M., et al. (2021). Evaluating Large Language Models Trained on Code (HumanEval).
- Austin, J., et al. (2021). Program Synthesis with Large Language Models (MBPP).

## Appendix A: Fairness Protocol Specification

See `FAIRNESS_PROTOCOL.md` in the repository root.

## Appendix B: Full Result Schema

Each JSONL row contains:

```json
{
  "schema_version": "or-eval-result-v2",
  "run_key": "model|prompt_id|problem_id",
  "model": "deepseek-v3",
  "dataset": "NL4OPT",
  "problem_id": "NL4OPT:42",
  "prompt_id": "neutral_best_v2",
  "prompt_type": "neutral",
  "prompt_hash": "sha256...",
  "config_hash": "sha256...",
  "solver_env_hash": "sha256...",
  "question": "...",
  "answer": 123.45,
  "raw_response": "...",
  "code": "...",
  "executable": true,
  "solver": "pulp",
  "solver_availability_state": "available",
  "solver_status": "optimal",
  "solve_success": true,
  "predicted": 123.45,
  "objective_extraction": {"value": 123.45, "source": "objective_value", "confidence": "high"},
  "variable_values": {"x": 1, "y": 2},
  "gap": 0.0,
  "acc_5pct": true,
  "acc_1pct": true,
  "acc_1e-4": true,
  "failure_type": "correct",
  "verification_status": "objective_match",
  "solution_verification": {
    "objective_status": "match",
    "variable_values_present": true,
    "constraint_feasibility": "solver_reported_feasible"
  }
}
```

## Appendix C: Prompt Search Score Function

```
score = 0.70 × accuracy
      + 0.20 × executable_rate
      + 0.10 × solver_uniformity
      − 0.25 × max(0, max_solver_share − 0.80)
```

The concentration penalty discourages prompts that accidentally bias toward a single solver, even if accuracy is high.
