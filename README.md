# OR-Eval

**Unified, solver-neutral, reproducible evaluation framework for Operations Research LLMs.**

OR-Eval addresses the critical gap in OR+AI research: existing benchmarks produce incomparable results due to differing prompts, solver dependencies, execution environments, and evaluation criteria. OR-Eval standardizes the entire pipeline so that any researcher can reproduce and fairly compare LLM performance on optimization tasks.

## Key Features

- **Solver-neutral evaluation** — prompts do not prescribe a solver; the framework detects which of 15 solver libraries the model actually chose
- **Fairness protocol** — cryptographic hashes (prompt, config, solver environment) ensure reproducibility; a 13-gate audit certifies results
- **6 benchmark datasets** — NL4OPT, MAMO (Easy/Complex LP), OptiBench, IndustryOR, OptMATH_Bench (1,961 problems total)
- **Multi-provider inference** — OpenAI, Anthropic, vLLM/Ollama, or any OpenAI-compatible endpoint
- **Three-round prompt search** — automated grid search → refinement → validation to find the best solver-neutral prompt
- **Solver bias ablation** — quantifies how much solver-specific prompts distort results
- **Failure taxonomy** — classifies every error (syntax, missing module, timeout, wrong numeric, etc.)
- **Paper-ready output** — LaTeX tables, SVG charts, Markdown report, CSV, and JSON

## Quick Start

```bash
pip install -e .
export OR_EVAL_API_KEY="your-api-key"

# Verify framework locally (no API calls)
python -m or_eval.cli fairness-smoke --output-dir /tmp/smoke
python -m or_eval.cli fairness-audit --results-dir /tmp/smoke --strict

# Run full pipeline
./scripts/run_or_eval_pipeline.sh
```

## Installation

**Requirements:** Python ≥ 3.9

```bash
git clone https://github.com/your-org/OR-Eval.git
cd OR-Eval
pip install -e .
```

Optional provider SDKs:

```bash
pip install -e ".[openai]"          # OpenAI SDK
pip install -e ".[anthropic]"       # Anthropic SDK
pip install -e ".[all-providers]"   # Both
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
  - deepseek-v3                              # auto-detect provider
  - deepseek-v3.2
  - name: gpt-4o                             # explicit provider
    provider: openai
    api_key_env: OPENAI_API_KEY
  - name: claude-sonnet-4-20250514
    provider: anthropic
    api_key_env: ANTHROPIC_API_KEY
  - name: my-local-model                     # local vLLM/Ollama
    provider: vllm
    api_url: http://localhost:8000/v1/chat/completions

datasets:
  - NL4OPT
  - MAMO_EasyLP
  - MAMO_ComplexLP
  - OptiBench
  - IndustryOR
  - OptMATH_Bench

execution:
  timeout: 30
  memory_limit_mb: 2048
```

### Supported Providers

| Provider | Models | Default URL |
|----------|--------|-------------|
| `ebill` | Any model via Baidu eBill proxy | `http://ebill.baidu-int.com/v1/models/{model}` |
| `openai` | GPT-4o, o3, o4, etc. | `https://api.openai.com/v1/chat/completions` |
| `anthropic` | Claude family | `https://api.anthropic.com/v1/messages` |
| `vllm` | Any local model | `http://localhost:8000/v1/chat/completions` |

Auto-detection: `gpt-*`/`o3-*` → openai, `claude-*` → anthropic, `localhost` URL → vllm, otherwise → ebill.

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        OR-Eval Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. PROMPT SEARCH                                               │
│     27 candidates → grid eval → top-5 refinement → final       │
│     Score = 0.7×accuracy + 0.2×exec_rate + 0.1×uniformity      │
│                                                                 │
│  2. FULL EVALUATION                                             │
│     N models × 1961 problems × solver-neutral prompt            │
│     Single-pass, temperature=0, JSONL resume                    │
│                                                                 │
│  3. ABLATION                                                    │
│     Neutral vs. pyscipopt/gurobipy/coptpy prompts               │
│     300 validation samples, seed=42                             │
│                                                                 │
│  4. REPORT + AUDIT                                              │
│     Markdown / LaTeX / CSV / JSON / SVG                         │
│     13-gate fairness audit + target audit                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## CLI Reference

```bash
python -m or_eval.cli COMMAND [OPTIONS]
```

| Command | Description |
|---------|-------------|
| `data-info` | Show dataset problem counts |
| `solvers` | Show locally importable solver packages |
| `solver-env` | Show solver versions and reproducibility hash |
| `providers` | Show available inference providers |
| `search-prompts` | Run 3-round prompt search |
| `evaluate` | Run full model evaluation (JSONL resume) |
| `ablation` | Compare neutral vs. solver-specific prompts |
| `report` | Generate Markdown, CSV, JSON, LaTeX tables |
| `fairness-smoke` | Local no-API framework verification |
| `fairness-audit` | Validate results against fairness protocol |
| `target-audit` | Check against full acceptance criteria |
| `result-status` | Paper-readiness status check |
| `fairness-protocol` | Print machine-readable protocol manifest |

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| `accuracy@5%` | Primary: predicted within 5% relative error of ground truth |
| `accuracy@1%` | Stricter tolerance |
| `accuracy@1e-4` | Near-exact match |
| `executable_rate` | Code runs without error |
| `solve_rate` | Code produces a solver-feasible solution |
| `objective_evaluable_rate` | Predicted value is extractable |
| `variable_output_rate` | Decision variable values are reported |
| `solver_distribution.max_share` | Concentration of dominant solver |

## Fairness Protocol

OR-Eval enforces a strict fairness protocol to ensure reproducibility:

1. **Schema version** — every result row is tagged `or-eval-result-v2`
2. **Hash-based resume** — JSONL resume requires matching `prompt_hash`, `config_hash`, and `solver_env_hash`
3. **Failed prediction suppression** — non-executable rows cannot contribute predictions
4. **Solver environment reporting** — full availability matrix is recorded
5. **Failure taxonomy** — every non-correct row is classified
6. **Solver bias detection** — ablation quantifies prompt-induced solver concentration
7. **Variable evidence** — decision variables tracked for equivalent-modeling analysis

Run the audit:

```bash
python -m or_eval.cli fairness-audit --results-dir results/ --strict
```

## Results (Current Run)

| Model | N | Acc@5% | Executable | Solve | Variable Output |
|-------|--:|-------:|-----------:|------:|----------------:|
| o3-mini | 288 | 86.8% | 96.5% | 90.6% | — |
| gpt-4.1-mini | 1961 | 73.9% | 87.0% | 84.2% | 80.8% |
| deepseek-v3 | 1961 | 66.4% | 85.8% | 80.4% | 77.2% |
| deepseek-v3.2 | 1961 | 56.9% | 71.8% | 67.7% | 63.4% |
| gpt-4o-mini | 1961 | 50.5% | 79.7% | 69.7% | 66.7% |
| gpt-4o | 1961 | 39.8% | 43.2% | 42.4% | 40.5% |

## Project Structure

```
OR-Eval/
├── or_eval/
│   ├── cli.py                   # Click CLI entry point
│   ├── evaluation.py            # Core evaluation loop
│   ├── pipeline.py              # Legacy compat wrapper
│   ├── prompt_search.py         # 3-round prompt search
│   ├── inference/
│   │   ├── __init__.py          # Public API (create_client, GeminiStyleClient)
│   │   └── providers.py         # Multi-provider adapters
│   ├── execution/
│   │   ├── sandbox.py           # Subprocess execution with timeout
│   │   ├── extractors.py        # Code/objective/variable extraction
│   │   └── solver_env.py        # Solver detection & environment hash
│   ├── metrics/
│   │   └── numerical_judge.py   # Tolerance-based numerical judgment
│   ├── prompts/
│   │   ├── neutral.py           # Prompt registry & generation
│   │   ├── templates/           # Jinja2 prompt templates
│   │   └── solver_instructions/ # Per-solver instruction templates
│   ├── data/
│   │   ├── loader.py            # Unified dataset loader
│   │   ├── schema.py            # Data schema definitions
│   │   └── adapters/            # Per-dataset format adapters
│   ├── reporting/
│   │   └── reports.py           # Report, audit, LaTeX generation
│   └── multi_prompt/
│       ├── evaluator.py         # Multi-prompt robustness scoring
│       └── registry.py          # Prompt variant registry
├── configs/
│   ├── default.yaml             # Default pipeline configuration
│   └── quick.yaml               # Fast local testing config
├── scripts/
│   └── run_or_eval_pipeline.sh  # One-command full pipeline
├── tests/
│   ├── test_core.py             # Core functionality tests
│   └── test_providers.py        # Provider system tests
├── data/unified/                # Pre-converted dataset files
├── results/                     # Evaluation output artifacts
├── FAIRNESS_PROTOCOL.md         # Fairness protocol specification
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Version history
├── LICENSE                      # Apache 2.0
└── pyproject.toml               # Package metadata
```

## Reproducibility Guarantees

- Temperature fixed at `0` for all API calls
- Single-pass generation only (no self-debug, no Reflexion, no agent loops)
- Deterministic validation splits: `seed=42`, 50 samples per dataset
- JSONL append-only with hash-gated resume
- Non-executable rows normalized to `predicted=None`
- Solver environment hash ensures consistent execution context

## Supported Solvers (15)

PySCIPOpt, Gurobi, COPT, PuLP, CVXPY, Pyomo, OR-Tools, SciPy Optimize, DOcplex, Python-MIP, AMPLPy, FICO Xpress, HiGHS, MOSEK, Linopy

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and PR guidelines.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Citation

```bibtex
@software{or_eval_2025,
  title={OR-Eval: Unified Solver-Neutral Evaluation Framework for Operations Research LLMs},
  author={OR-Eval Contributors},
  year={2025},
  url={https://github.com/your-org/OR-Eval}
}
```
