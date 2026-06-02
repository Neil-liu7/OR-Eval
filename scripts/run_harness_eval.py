"""Run multi-prompt Harness evaluation on SIRL benchmarks with GPT-4o."""
import json
import time
import re
import subprocess
import tempfile
from pathlib import Path
from openai import OpenAI

DATA_DIR = Path("/Users/neilliu/Desktop/OR-Benchmark/OPTEngine/SIRL/test_data")
OUTPUT_DIR = Path("/Users/neilliu/Desktop/OR-Benchmark/OR-Eval/results/gpt-4o-harness")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLIENT = OpenAI(
    base_url="https://ebill.baidu-int.com/v1",
    api_key="sk-bill-3848e0462172d0abf28a97e6644e322b",
)

# 5 semantically equivalent prompt variants
PROMPT_VARIANTS = [
    # V1: Original (baseline)
    """You are an Operations Research programmer. Solve the following optimization problem by writing Python code using the Gurobi (gurobipy) solver.

Problem:
{problem}

Requirements:
- Self-contained executable code using gurobipy.
- Print the optimal objective value as: OBJECTIVE_VALUE: <number>
- If infeasible: OBJECTIVE_VALUE: INFEASIBLE
- Wrap code in ```python ... ```""",

    # V2: Concise, direct instruction
    """Write executable Python code using gurobipy to solve this optimization problem. Print the result as OBJECTIVE_VALUE: <number>.

{problem}

Wrap code in ```python ... ```""",

    # V3: Step-by-step reasoning style
    """Solve the optimization problem below step by step:
1. Identify decision variables, objective, and constraints.
2. Implement in Python using gurobipy.
3. Print the optimal value as: OBJECTIVE_VALUE: <number>

Problem:
{problem}

Wrap your code in ```python ... ```""",

    # V4: Expert persona, formal tone
    """As a mathematical optimization expert, formulate and solve the following problem using Gurobi in Python. Your code must be self-contained and print exactly: OBJECTIVE_VALUE: <number>

Problem:
{problem}

```python""",

    # V5: Minimal instruction
    """Solve with gurobipy. Print OBJECTIVE_VALUE: <number>.

{problem}

```python""",
]


def call_gpt4o(prompt: str) -> str:
    for a in range(3):
        try:
            r = CLIENT.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}],
                temperature=0, max_tokens=2048,
            )
            return r.choices[0].message.content
        except Exception as e:
            time.sleep(2 ** a)
    return ""


def extract_code(t):
    m = re.search(r"```python\s*\n(.*?)```", t, re.DOTALL)
    return m.group(1).strip() if m else None


def run_code(code):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(["python3", tmp], capture_output=True, text=True, timeout=60)
        return r.stdout
    except:
        return ""
    finally:
        Path(tmp).unlink(missing_ok=True)


def extract_obj(t):
    m = re.search(r"OBJECTIVE_VALUE:\s*(.+)", t)
    if m:
        v = m.group(1).strip()
        if v.upper() in ("INFEASIBLE", "UNBOUNDED"):
            return v.upper()
        try:
            return float(v)
        except:
            pass
    for p in [r"[Oo]ptimal.*?[:=]\s*([\d.e+-]+)", r"[Oo]bjVal.*?[:=]\s*([\d.e+-]+)"]:
        m2 = re.search(p, t)
        if m2:
            try:
                return float(m2.group(1))
            except:
                pass
    return None


def judge(pred, gt, tol=0.05):
    if pred is None:
        return False
    if isinstance(gt, str):
        return str(pred).upper().strip() == gt.upper().strip()
    try:
        p, g = float(pred), float(gt)
    except:
        return False
    if g == 0:
        return abs(p) <= tol
    return abs((p - g) / g) <= tol


def parse_answer(ans):
    if ans in (None, "", "None"):
        return None
    if "No Best Solution" in str(ans):
        return "INFEASIBLE"
    try:
        return float(ans)
    except:
        return str(ans)


def eval_one(prompt, problem):
    resp = call_gpt4o(prompt)
    obj = None
    code = extract_code(resp)
    if code:
        stdout = run_code(code)
        if stdout:
            obj = extract_obj(stdout)
    if obj is None:
        obj = extract_obj(resp)
    return obj


def run_harness(filename: str, name: str, limit: int = 30):
    """Run multi-prompt evaluation on a subset."""
    print(f"\n{'='*60}")
    print(f"HARNESS: {name} ({filename}) | {len(PROMPT_VARIANTS)} variants | limit={limit}")
    print(f"{'='*60}")

    problems = [json.loads(l) for l in open(DATA_DIR / filename)][:limit]
    n_variants = len(PROMPT_VARIANTS)

    # results[variant_idx][problem_idx] = correct/incorrect
    variant_scores = [[] for _ in range(n_variants)]
    problem_consistency = []  # per-problem: how many variants got it right

    for i, p in enumerate(problems):
        gt = parse_answer(p.get("en_answer"))
        problem_correct_count = 0

        for v_idx, template in enumerate(PROMPT_VARIANTS):
            prompt = template.format(problem=p["en_question"])
            obj = eval_one(prompt, p)
            correct = judge(obj, gt) if gt is not None else False
            variant_scores[v_idx].append(correct)
            if correct:
                problem_correct_count += 1

        problem_consistency.append(problem_correct_count / n_variants)
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(problems)}] done")

    # Compute metrics
    variant_accs = [sum(s) / len(s) for s in variant_scores]
    import numpy as np
    accs = np.array(variant_accs)
    consistency = np.array(problem_consistency)

    result = {
        "benchmark": name,
        "n_problems": len(problems),
        "n_variants": n_variants,
        "per_variant_accuracy": {f"V{i+1}": round(a, 4) for i, a in enumerate(variant_accs)},
        "mean_accuracy": round(float(accs.mean()), 4),
        "std_accuracy": round(float(accs.std()), 4),
        "best_variant": round(float(accs.max()), 4),
        "worst_variant": round(float(accs.min()), 4),
        "prompt_robustness_score": round(float(1 - accs.std()), 4),
        "mean_problem_consistency": round(float(consistency.mean()), 4),
        "fully_robust_problems": int((consistency == 1.0).sum()),
        "fully_fragile_problems": int((consistency == 0.0).sum()),
    }

    print(f"\n  Results:")
    print(f"  Per-variant accuracy: {result['per_variant_accuracy']}")
    print(f"  Mean: {result['mean_accuracy']:.4f} | Std: {result['std_accuracy']:.4f}")
    print(f"  Best variant: {result['best_variant']:.4f} | Worst: {result['worst_variant']:.4f}")
    print(f"  Prompt Robustness Score: {result['prompt_robustness_score']:.4f}")
    print(f"  Problems always correct (all 5 variants): {result['fully_robust_problems']}/{len(problems)}")
    print(f"  Problems always wrong (all 5 variants): {result['fully_fragile_problems']}/{len(problems)}")

    (OUTPUT_DIR / f"{name}.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    benchmarks = [
        ("IndustryOR_fixedV2.json", "IndustryOR"),
        ("NL4OPT.jsonl", "NL4OPT"),
        ("MAMO_EasyLP_fixed.jsonl", "MAMO_EasyLP"),
        ("MAMO_ComplexLP_fixed.jsonl", "MAMO_ComplexLP"),
    ]

    all_results = {}
    for fname, name in benchmarks:
        r = run_harness(fname, name, limit=limit)
        all_results[name] = r

    print(f"\n{'='*60}")
    print("HARNESS SUMMARY")
    print(f"{'='*60}")
    print(f"{'Benchmark':<16} {'Mean':<8} {'Std':<8} {'Best':<8} {'Worst':<8} {'Robustness':<10}")
    print("-" * 58)
    for name, r in all_results.items():
        print(f"{name:<16} {r['mean_accuracy']:<8.4f} {r['std_accuracy']:<8.4f} {r['best_variant']:<8.4f} {r['worst_variant']:<8.4f} {r['prompt_robustness_score']:<10.4f}")

    (OUTPUT_DIR / "summary.json").write_text(json.dumps(all_results, indent=2))
