"""Run Harness Mode B for multiple models."""
import json
import time
import re
import subprocess
import tempfile
import sys
from pathlib import Path
from openai import OpenAI
import numpy as np

DATA_DIR = Path("/Users/neilliu/Desktop/OR-Benchmark/OPTEngine/SIRL/test_data")
BASE_OUTPUT = Path("/Users/neilliu/Desktop/OR-Benchmark/OR-Eval/results")

CLIENT = OpenAI(
    base_url="https://ebill.baidu-int.com/v1",
    api_key="sk-bill-3848e0462172d0abf28a97e6644e322b",
)

CANDIDATE_PROMPTS = {
    "P1_standard": """You are an Operations Research programmer. Solve the following optimization problem by writing Python code using the Gurobi (gurobipy) solver.

Problem:
{problem}

Requirements:
- Self-contained executable code using gurobipy.
- Print the optimal objective value as: OBJECTIVE_VALUE: <number>
- If infeasible: OBJECTIVE_VALUE: INFEASIBLE
- Wrap code in ```python ... ```""",
    "P2_concise": """Write executable Python code using gurobipy to solve this optimization problem. Print result as OBJECTIVE_VALUE: <number>.

{problem}

Wrap code in ```python ... ```""",
    "P3_stepbystep": """Solve the optimization problem below:
1. Identify decision variables, objective, and constraints.
2. Implement in Python using gurobipy.
3. Print optimal value as: OBJECTIVE_VALUE: <number>

Problem:
{problem}

Wrap code in ```python ... ```""",
    "P4_expert": """As a mathematical optimization expert, formulate and solve the following problem using Gurobi in Python. Your code must be self-contained and print exactly: OBJECTIVE_VALUE: <number>

Problem:
{problem}

Wrap code in ```python ... ```""",
    "P5_minimal": """Solve with gurobipy. Print OBJECTIVE_VALUE: <number>.

{problem}

```python""",
    "P6_structured": """Task: Solve an optimization problem using Gurobi.

Input: {problem}

Output format:
- Complete Python code using gurobipy
- Last line prints: OBJECTIVE_VALUE: <number>
- Code wrapped in ```python ... ```""",
    "P7_roleplay": """You are a senior OR consultant at a top firm. A client gives you this problem:

{problem}

Write production-ready Python code using gurobipy to solve it. Print the optimal objective value as OBJECTIVE_VALUE: <number>. Wrap in ```python ... ```""",
}


def call_api(model_name: str, prompt: str) -> str:
    for a in range(3):
        try:
            r = CLIENT.chat.completions.create(
                model=model_name, messages=[{"role": "user", "content": prompt}],
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
    for p in [r"[Oo]ptimal.*?[:=]\s*([\d.e+-]+)", r"ObjVal.*?[:=]\s*([\d.e+-]+)"]:
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


def eval_problem(model_name, prompt_template, problem):
    prompt = prompt_template.format(problem=problem["en_question"])
    resp = call_api(model_name, prompt)
    obj = None
    code = extract_code(resp)
    if code:
        stdout = run_code(code)
        if stdout:
            obj = extract_obj(stdout)
    if obj is None:
        obj = extract_obj(resp)
    gt = parse_answer(problem.get("en_answer"))
    return judge(obj, gt) if gt is not None else False


def run_model(model_name: str, limit: int = 30):
    output_dir = BASE_OUTPUT / f"{model_name}-harness-B"
    output_dir.mkdir(parents=True, exist_ok=True)

    benchmarks = [
        ("IndustryOR_fixedV2.json", "IndustryOR"),
        ("NL4OPT.jsonl", "NL4OPT"),
        ("MAMO_EasyLP_fixed.jsonl", "MAMO_EasyLP"),
        ("MAMO_ComplexLP_fixed.jsonl", "MAMO_ComplexLP"),
    ]

    all_results = {}
    for fname, name in benchmarks:
        problems = [json.loads(l) for l in open(DATA_DIR / fname)]
        cal_set = problems[:15]
        eval_set = problems[:limit]

        # Phase 1: Calibration
        print(f"\n[{model_name}] Phase 1: Calibrating {name} (15 problems × 7 prompts)")
        cal_scores = {}
        for pname, tmpl in CANDIDATE_PROMPTS.items():
            correct = sum(1 for p in cal_set if eval_problem(model_name, tmpl, p))
            cal_scores[pname] = correct / len(cal_set)
        sorted_p = sorted(cal_scores.items(), key=lambda x: -x[1])
        main_name = sorted_p[0][0]
        variants = [n for n, _ in sorted_p[:5]]
        print(f"  Main: {main_name} ({cal_scores[main_name]:.3f})")

        # Phase 2: Evaluation
        print(f"[{model_name}] Phase 2: Evaluating {name} ({limit} problems × 5 variants)")
        variant_accs = {}
        for vname in variants:
            correct = sum(1 for p in eval_set if eval_problem(model_name, CANDIDATE_PROMPTS[vname], p))
            acc = correct / len(eval_set)
            variant_accs[vname] = acc
            print(f"  {vname}: {acc:.4f}")

        accs = np.array(list(variant_accs.values()))
        result = {
            "benchmark": name,
            "main_prompt": main_name,
            "main_score": round(variant_accs[main_name], 4),
            "variant_scores": {k: round(v, 4) for k, v in variant_accs.items()},
            "mean": round(float(accs.mean()), 4),
            "std": round(float(accs.std()), 4),
            "best": round(float(accs.max()), 4),
            "worst": round(float(accs.min()), 4),
            "robustness": round(float(1 - accs.std()), 4),
        }
        all_results[name] = result
        (output_dir / f"{name}.json").write_text(json.dumps(result, indent=2))

    # Summary
    print(f"\n{'='*70}")
    print(f"[{model_name}] FINAL REPORT")
    print(f"{'='*70}")
    print(f"{'Benchmark':<16} {'Score':<8} {'Mean':<8} {'Std':<8} {'Best':<8} {'Worst':<8} {'Robust':<8}")
    print("-" * 64)
    for name, r in all_results.items():
        print(f"{name:<16} {r['main_score']:<8.4f} {r['mean']:<8.4f} {r['std']:<8.4f} {r['best']:<8.4f} {r['worst']:<8.4f} {r['robustness']:<8.4f}")

    (output_dir / "summary.json").write_text(json.dumps(all_results, indent=2))
    return all_results


if __name__ == "__main__":
    models = sys.argv[1].split(",") if len(sys.argv) > 1 else ["deepseek-v3"]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    for model in models:
        print(f"\n{'#'*70}")
        print(f"# MODEL: {model}")
        print(f"{'#'*70}")
        run_model(model, limit)
