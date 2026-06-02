"""
OR-Eval Harness Mode B: 主prompt选定 + 鲁棒性评测一体化
流程：
  Phase 1 (Harness前置): 用校准集从候选prompt中选出主prompt + 变体集
  Phase 2 (正式评测): 主prompt全量出分 + 变体集出鲁棒性指标
"""
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
OUTPUT_DIR = Path("/Users/neilliu/Desktop/OR-Benchmark/OR-Eval/results/gpt-4o-harness-B")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLIENT = OpenAI(
    base_url="https://ebill.baidu-int.com/v1",
    api_key="sk-bill-3848e0462172d0abf28a97e6644e322b",
)

# ============================================================
# 候选Prompt池（20个中选代表性的7个）
# ============================================================
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


# ============================================================
# 工具函数
# ============================================================
def call_api(prompt: str) -> str:
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


def eval_problem(prompt_template, problem):
    prompt = prompt_template.format(problem=problem["en_question"])
    resp = call_api(prompt)
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


# ============================================================
# Phase 1: Harness前置 — 用校准集选主prompt
# ============================================================
def phase1_calibration(calibration_problems, n_calibration=15):
    """从候选prompt中选出主prompt和变体集"""
    print("=" * 60)
    print("PHASE 1: Harness Calibration (selecting optimal prompt)")
    print(f"  Candidates: {len(CANDIDATE_PROMPTS)} prompts")
    print(f"  Calibration set: {n_calibration} problems")
    print("=" * 60)

    problems = calibration_problems[:n_calibration]
    scores = {}

    for pname, template in CANDIDATE_PROMPTS.items():
        correct = 0
        for p in problems:
            if eval_problem(template, p):
                correct += 1
        acc = correct / len(problems)
        scores[pname] = acc
        print(f"  {pname}: {acc:.3f} ({correct}/{len(problems)})")

    # Select main prompt: highest accuracy
    sorted_prompts = sorted(scores.items(), key=lambda x: -x[1])
    main_prompt_name = sorted_prompts[0][0]
    main_prompt_score = sorted_prompts[0][1]

    # Select variant set: top 5 (including main)
    variant_names = [name for name, _ in sorted_prompts[:5]]

    print(f"\n  Selected main prompt: {main_prompt_name} (acc={main_prompt_score:.3f})")
    print(f"  Variant set: {variant_names}")

    return main_prompt_name, variant_names, scores


# ============================================================
# Phase 2: 正式评测 — 主prompt出分 + 变体出鲁棒性
# ============================================================
def phase2_evaluation(problems, main_prompt_name, variant_names, benchmark_name):
    """主prompt全量评测 + 变体鲁棒性评测"""
    print(f"\n{'=' * 60}")
    print(f"PHASE 2: Formal Evaluation — {benchmark_name}")
    print(f"  Main prompt: {main_prompt_name}")
    print(f"  Problems: {len(problems)}")
    print(f"  Variants for robustness: {len(variant_names)}")
    print("=" * 60)

    main_template = CANDIDATE_PROMPTS[main_prompt_name]
    variant_templates = {name: CANDIDATE_PROMPTS[name] for name in variant_names}

    # Main evaluation
    main_results = []
    main_correct = 0
    for i, p in enumerate(problems):
        ok = eval_problem(main_template, p)
        main_results.append(ok)
        if ok:
            main_correct += 1
        if (i + 1) % 20 == 0:
            print(f"  [Main] {i+1}/{len(problems)} acc={main_correct/(i+1):.3f}")

    main_score = main_correct / len(problems)
    print(f"  Main Score: {main_score:.4f} ({main_correct}/{len(problems)})")

    # Robustness evaluation (all variants including main)
    variant_scores = {}
    per_problem_votes = [0] * len(problems)

    for vname, vtemplate in variant_templates.items():
        if vname == main_prompt_name:
            # Reuse main results
            variant_scores[vname] = main_score
            for i, ok in enumerate(main_results):
                if ok:
                    per_problem_votes[i] += 1
            continue

        v_correct = 0
        for i, p in enumerate(problems):
            ok = eval_problem(vtemplate, p)
            if ok:
                v_correct += 1
                per_problem_votes[i] += 1
            if (i + 1) % 20 == 0:
                print(f"  [{vname}] {i+1}/{len(problems)} acc={v_correct/(i+1):.3f}")
        variant_scores[vname] = v_correct / len(problems)
        print(f"  {vname}: {variant_scores[vname]:.4f}")

    # Compute robustness metrics
    accs = np.array(list(variant_scores.values()))
    consistency = np.array(per_problem_votes) / len(variant_names)

    result = {
        "benchmark": benchmark_name,
        "main_prompt": main_prompt_name,
        "main_score": round(main_score, 4),
        "variant_scores": {k: round(v, 4) for k, v in variant_scores.items()},
        "mean_across_variants": round(float(accs.mean()), 4),
        "std_across_variants": round(float(accs.std()), 4),
        "best_variant": round(float(accs.max()), 4),
        "worst_variant": round(float(accs.min()), 4),
        "prompt_robustness_score": round(float(1 - accs.std()), 4),
        "mean_problem_consistency": round(float(consistency.mean()), 4),
        "n_problems": len(problems),
        "n_variants": len(variant_names),
    }
    return result


# ============================================================
# Main
# ============================================================
def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    calibration_size = min(15, limit)

    benchmarks = [
        ("IndustryOR_fixedV2.json", "IndustryOR"),
        ("NL4OPT.jsonl", "NL4OPT"),
        ("MAMO_EasyLP_fixed.jsonl", "MAMO_EasyLP"),
        ("MAMO_ComplexLP_fixed.jsonl", "MAMO_ComplexLP"),
    ]

    all_results = {}

    for fname, name in benchmarks:
        problems = [json.loads(l) for l in open(DATA_DIR / fname)]

        # Phase 1: Calibration on first N problems
        calibration_set = problems[:calibration_size]
        main_prompt, variants, cal_scores = phase1_calibration(calibration_set, calibration_size)

        # Phase 2: Formal evaluation on full set (up to limit)
        eval_set = problems[:limit]
        result = phase2_evaluation(eval_set, main_prompt, variants, name)
        result["calibration_scores"] = {k: round(v, 4) for k, v in cal_scores.items()}
        all_results[name] = result

        (OUTPUT_DIR / f"{name}.json").write_text(json.dumps(result, indent=2))

    # Summary
    print(f"\n{'=' * 70}")
    print("FINAL REPORT: OR-Eval Harness Mode B")
    print(f"{'=' * 70}")
    print(f"{'Benchmark':<16} {'Score':<8} {'Mean':<8} {'Std':<8} {'Best':<8} {'Worst':<8} {'Robust':<8}")
    print("-" * 64)
    for name, r in all_results.items():
        print(f"{name:<16} {r['main_score']:<8.4f} {r['mean_across_variants']:<8.4f} "
              f"{r['std_across_variants']:<8.4f} {r['best_variant']:<8.4f} "
              f"{r['worst_variant']:<8.4f} {r['prompt_robustness_score']:<8.4f}")

    (OUTPUT_DIR / "summary.json").write_text(json.dumps(all_results, indent=2))
    print(f"\nResults saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
