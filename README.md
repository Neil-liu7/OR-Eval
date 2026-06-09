# OR-Eval

[![CI](https://github.com/Neil-liu7/OR-Eval/actions/workflows/ci.yml/badge.svg)](https://github.com/Neil-liu7/OR-Eval/actions/workflows/ci.yml)

**Unified, solver-neutral, reproducible evaluation framework for Operations Research LLMs.**

OR-Eval addresses the critical gap in OR+AI research: existing benchmarks produce incomparable results due to differing prompts, solver dependencies, execution environments, and evaluation criteria. OR-Eval standardizes the entire pipeline so that any researcher can reproduce and fairly compare LLM performance on optimization tasks.

## Key Findings

Our evaluation of 11 models across 1,961 problems reveals:

- **Solver-specific prompts inflate accuracy by up to 37%** — making cross-paper comparisons meaningless
- **13.4% of failures are environment issues** (missing packages), not model failures
- **Failure handling policy can swing accuracy by 71%** — the same model ranks #2 or #8 depending on how you count
- **Model rankings are unstable across datasets** (mean Kendall's τ = 0.54)

## Results (11 Models, 6 Datasets, 1,961 Problems)

| # | Model | Acc@5% | Exec% | Solve% | CI (95%) |
|---|-------|-------:|------:|-------:|----------|
| 1 | o4-mini | **77.9%** | 90.6% | 88.8% | [76.1%, 79.7%] |
| 2 | gpt-4.1-mini | 73.9% | 87.0% | 84.2% | [72.0%, 75.9%] |
| 3 | qwen3-235b-a22b | 71.1% | 85.0% | 81.9% | [69.0%, 73.1%] |
| 4 | gpt-4.1 | 69.4% | 79.6% | 77.1% | [67.3%, 71.4%] |
| 5 | deepseek-v3 | 66.5% | 85.9% | 80.6% | [64.4%, 68.5%] |
| 6 | deepseek-v3.2 | 56.9% | 71.8% | 67.7% | [54.7%, 59.2%] |
| 7 | gpt-4o-mini | 50.5% | 79.7% | 69.7% | [48.2%, 52.7%] |
| 8 | gpt-4o | 39.8% | 43.2% | 42.4% | [37.6%, 42.0%] |
| 9 | qwen-max | 32.0% | 39.6% | 37.0% | [30.0%, 34.1%] |
| 10 | gemini-2.5-pro | 22.0% | 23.6% | 23.2% | [20.2%, 23.8%] |

*All results: single-pass, temperature=0, solver-neutral prompt, 95% bootstrap CI.*

## Key Features

- **Solver-neutral evaluation** — prompts do not prescribe a solver; the framework detects which of 15 solver libraries the model chose
- **Fairness protocol** — cryptographic hashes (prompt, config, solver environment) ensure reproducibility; a 13-gate audit certifies results
- **6 benchmark datasets** — NL4OPT, MAMO (Easy/Complex LP), OptiBench, IndustryOR, OptMATH_Bench (1,961 problems)
- **Multi-provider inference** — OpenAI, Anthropic, vLLM/Ollama, or any OpenAI-compatible endpoint
- **Prompt search** — automated 3-round grid search to find the best solver-neutral prompt
- **Solver bias ablation** — quantifies how solver-specific prompts distort results
- **Failure taxonomy** — classifies every error (syntax, missing module, timeout, wrong answer, etc.)
- **Statistical analysis** — bootstrap CI, pairwise significance tests, rank stability, sensitivity analysis
- **Multi-turn evaluation** — optional self-debug and reflexion modes
- **Paper-ready output** — LaTeX tables, SVG charts, Markdown report, CSV, and JSON

## Quick Start

```bash
pip install -e ".[solvers]"    # includes cvxpy, pyomo, networkx
export OR_EVAL_API_KEY="your-api-key"

# Verify framework locally (no API calls)
or-eval fairness-smoke --output-dir /tmp/smoke
or-eval fairness-audit --results-dir /tmp/smoke --strict

# Evaluate a model
or-eval evaluate --models deepseek-v3 --datasets NL4OPT --limit-per-dataset 10

# Full pipeline
bash scripts/run_or_eval_pipeline.sh
```

## Installation

**Requirements:** Python >= 3.9

```bash
git clone https://github.com/Neil-liu7/OR-Eval.git
cd OR-Eval
pip install -e "."
```

Optional dependencies:

```bash
pip install -e ".[solvers]"        # cvxpy, pyomo, networkx (recommended)
pip install -e ".[openai]"         # OpenAI SDK
pip install -e ".[anthropic]"      # Anthropic SDK
pip install -e ".[all]"            # Everything
```

## Configuration

### API Keys

```bash
export OR_EVAL_API_KEY="..."        # Default (eBill proxy)
export OPENAI_API_KEY="sk-..."      # OpenAI direct
export ANTHROPIC_API_KEY="sk-..."   # Anthropic direct
```

### Model Configuration (`configs/default.yaml`)

```yaml
api_url: "http://ebill.baidu-int.com/v1/models/{model}"

models:
  - deepseek-v3
  - gpt-4.1-mini
  - name: claude-4-sonnet
    provider: anthropic
    api_key_env: ANTHROPIC_API_KEY
  - name: my-local-model
    provider: vllm
    api_url: http://localhost:8000/v1/chat/completions

# Per-model overrides (e.g., higher token limit for reasoning models)
model_overrides:
  gemini-2.5-pro:
    max_tokens: 16384
```

### Adding a New Benchmark

1. Place the data file under the data directory (rows use `en_question` / `en_answer`).
2. Drop a YAML file in `or_eval/tasks/configs/`:

```yaml
name: MyBenchmark
dataset_file: my_benchmark.jsonl
problem_type: mixed_integer_programming
difficulty: hard
capabilities: [formulation, coding, constraint_modeling]
```

No code changes needed — the loader resolves the task through the registry,
so `python -m or_eval.cli evaluate --datasets MyBenchmark` works directly.

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        OR-Eval Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. PROMPT SEARCH                                               │
│     27 candidates → grid eval → top-5 refinement → final       │
│                                                                 │
│  2. FULL EVALUATION                                             │
│     N models × 1961 problems × solver-neutral prompt            │
│     Single-pass, temperature=0, JSONL resume                    │
│                                                                 │
│  3. ABLATION                                                    │
│     Neutral vs. solver-specific prompts (bias quantification)   │
│                                                                 │
│  4. STATISTICAL ANALYSIS                                        │
│     Bootstrap CI, pairwise significance, rank stability,        │
│     methodology sensitivity, item discrimination                │
│                                                                 │
│  5. REPORT + AUDIT                                              │
│     Markdown / LaTeX / CSV / JSON / SVG                         │
│     13-gate fairness audit                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## CLI Reference

```bash
or-eval COMMAND [OPTIONS]
```

| Command | Description |
|---------|-------------|
| `evaluate` | Run model evaluation (JSONL resume, multi-turn, few-shot) |
| `ablation` | Compare neutral vs. solver-specific prompts |
| `search-prompts` | Run 3-round prompt search |
| `statistics` | Bootstrap CI, significance tests, sensitivity analysis |
| `report` | Generate Markdown, CSV, JSON, LaTeX tables |
| `fairness-smoke` | Local no-API framework verification |
| `fairness-audit` | Validate results against fairness protocol |
| `tasks` | Show registered benchmarks and metadata |
| `solvers` | Show locally importable solver packages |
| `providers` | Show available inference providers |

## Evaluation Modes

```bash
# Default: single-pass (fair baseline)
or-eval evaluate --models gpt-4.1 --mode single_pass

# Self-debug: retry on execution failure
or-eval evaluate --models gpt-4.1 --mode self_debug --max-turns 3

# Reflexion: retry on wrong answer
or-eval evaluate --models gpt-4.1 --mode reflexion --max-turns 2

# Few-shot
or-eval evaluate --models gpt-4.1 --few-shot 3
```

## Metrics

| Metric | Description |
|--------|-------------|
| `accuracy@5%` | Primary: predicted within 5% relative error |
| `accuracy@1%` | Stricter tolerance |
| `env_corrected_accuracy` | Accuracy excluding environment failures (missing packages) |
| `executable_rate` | Code runs without error |
| `solve_rate` | Code produces a feasible solution |
| `solver_distribution` | Which solvers models naturally prefer |

## Fairness Protocol

OR-Eval enforces reproducibility through:

1. **Triple hashing** — prompt_hash + config_hash + solver_env_hash gate JSONL resume
2. **Failed prediction suppression** — non-executable rows cannot contribute predictions
3. **Solver bias detection** — ablation quantifies prompt-induced solver concentration
4. **13-gate audit** — all results must pass before publication claims

```bash
or-eval fairness-audit --results-dir results/ --strict
```

## Project Structure

```
OR-Eval/
├── or_eval/
│   ├── cli.py                   # Click CLI (15 commands)
│   ├── evaluation.py            # Core evaluation loop
│   ├── evaluation_modes.py      # Self-debug, reflexion
│   ├── prompt_search.py         # 3-round prompt optimization
│   ├── inference/providers.py   # Multi-provider adapters
│   ├── execution/
│   │   ├── sandbox.py           # Subprocess + timeout + memory limit
│   │   ├── extractors.py        # Code/objective/variable extraction
│   │   └── solver_env.py        # 15-solver detection & hashing
│   ├── metrics/
│   │   ├── numerical_judge.py   # Tolerance-based judgment + aggregation
│   │   ├── statistics.py        # CI, significance, rank correlation
│   │   └── sensitivity.py       # Methodology sensitivity analysis
│   ├── tasks/
│   │   ├── registry.py          # YAML-driven task discovery
│   │   └── configs/             # Drop-in benchmark definitions
│   ├── prompts/neutral.py       # Prompt registry & generation
│   └── reporting/               # Report, audit, LaTeX generation
├── configs/default.yaml
├── scripts/
│   ├── run_or_eval_pipeline.sh
│   └── run_supplement_eval.sh
├── tests/
└── results/
```

## Supported Solvers (15)

PySCIPOpt, Gurobi, COPT, PuLP, CVXPY, Pyomo, OR-Tools, SciPy Optimize, DOcplex, Python-MIP, AMPLPy, FICO Xpress, HiGHS, MOSEK, Linopy

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and PR guidelines.

```bash
pip install -e ".[dev,solvers]"
python -m pytest tests/ -v
or-eval fairness-smoke --output-dir /tmp/smoke
```

## Citation

```bibtex
@software{or_eval_2025,
  title={OR-Eval: Unified Solver-Neutral Evaluation Framework for Operations Research LLMs},
  author={OR-Eval Contributors},
  year={2025},
  url={https://github.com/Neil-liu7/OR-Eval}
}
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
