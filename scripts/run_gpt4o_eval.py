"""Run OR-Eval on SIRL fixed benchmarks with GPT-4o via ebill API."""
import json
import time
import re
import sys
from pathlib import Path
from openai import OpenAI

DATA_DIR = Path("/Users/neilliu/Desktop/OR-Benchmark/OPTEngine/SIRL/test_data")
OUTPUT_DIR = Path("/Users/neilliu/Desktop/OR-Benchmark/OR-Eval/results/gpt-4o")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLIENT = OpenAI(
    base_url="https://ebill.baidu-int.com/v1",
    api_key="sk-bill-3848e0462172d0abf28a97e6644e322b",
)

PROMPT_TEMPLATE = """You are an Operations Research programmer. Solve the following optimization problem by writing Python code using the Gurobi (gurobipy) solver.

Problem:
{problem}

Solver: Gurobi (gurobipy)
- Import: `import gurobipy as gp` and `from gurobipy import GRB`
- Create model: `model = gp.Model()`
- Solve: `model.optimize()`
- Get objective: `model.ObjVal`

Requirements:
- Self-contained executable code.
- Print the optimal objective value in this exact format: OBJECTIVE_VALUE: <number>
- If infeasible, print: OBJECTIVE_VALUE: INFEASIBLE
- Wrap your code in ```python ... ```"""

BENCHMARKS = [
    ("IndustryOR_fixedV2.json", "IndustryOR"),
    ("NL4OPT.jsonl", "NL4OPT"),
    ("MAMO_EasyLP_fixed.jsonl", "MAMO_EasyLP"),
    ("MAMO_ComplexLP_fixed.jsonl", "MAMO_ComplexLP"),
    ("OptiBench.jsonl", "OptiBench"),
]


def call_gpt4o(prompt: str) -> str:
    for attempt in range(3):
        try:
            resp = CLIENT.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=2048,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"  Retry {attempt+1}: {e}")
            time.sleep(2 ** attempt)
    return ""


def extract_obj(text: str):
    m = re.search(r"OBJECTIVE_VALUE:\s*(.+)", text)
    if m:
        val = m.group(1).strip()
        if val.upper() in ("INFEASIBLE", "UNBOUNDED"):
            return val.upper()
        try:
            return float(val)
        except ValueError:
            pass
    # Fallback patterns
    for pat in [r"[Oo]ptimal.*?[:=]\s*([\d.e+-]+)", r"[Oo]bjective.*?[:=]\s*([\d.e+-]+)"]:
        m2 = re.search(pat, text)
        if m2:
            try:
                return float(m2.group(1))
            except ValueError:
                pass
    return None


def extract_code(text: str) -> str:
    m = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def run_code(code: str, timeout: int = 60) -> str:
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(["python3", tmp], capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except Exception:
        return ""
    finally:
        Path(tmp).unlink(missing_ok=True)


def judge(predicted, ground_truth, tolerance=0.05) -> bool:
    if predicted is None:
        return False
    if isinstance(ground_truth, str):
        return str(predicted).upper() == ground_truth.upper()
    try:
        pred, gt = float(predicted), float(ground_truth)
    except (ValueError, TypeError):
        return False
    if gt == 0:
        return abs(pred) <= tolerance
    return abs((pred - gt) / gt) <= tolerance


def load_benchmark(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    problems = []
    with open(path) as f:
        for line in f:
            problems.append(json.loads(line))
    return problems


def run_benchmark(filename: str, name: str, limit: int = None):
    print(f"\n{'='*60}")
    print(f"Benchmark: {name} ({filename})")
    print(f"{'='*60}")

    problems = load_benchmark(filename)
    if limit:
        problems = problems[:limit]

    results = []
    correct = 0
    for i, p in enumerate(problems):
        prompt = PROMPT_TEMPLATE.format(problem=p["en_question"])
        response = call_gpt4o(prompt)

        # Try to extract and execute code
        obj_value = None
        code = extract_code(response)
        if code:
            exec_result = run_code(code)
            if exec_result:
                obj_value = extract_obj(exec_result)
        # Fallback: extract from response text
        if obj_value is None:
            obj_value = extract_obj(response)

        gt = float(p["en_answer"]) if p["en_answer"] not in (None, "", "None") else None
        is_correct = judge(obj_value, gt) if gt is not None else False
        if is_correct:
            correct += 1
        results.append({
            "id": p.get("id", i),
            "correct": is_correct,
            "predicted": obj_value,
            "expected": gt,
        })
        if (i + 1) % 10 == 0 or i == len(problems) - 1:
            print(f"  [{i+1}/{len(problems)}] acc={correct/(i+1):.3f}")

    acc = correct / len(problems) if problems else 0
    print(f"\n  RESULT: {name} pass@1 = {acc:.4f} ({correct}/{len(problems)})")

    out_path = OUTPUT_DIR / f"{name}.json"
    out_path.write_text(json.dumps({"benchmark": name, "pass@1": acc, "n": len(problems), "results": results}, indent=2))
    return name, acc, len(problems)


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    summary = []
    for filename, name in BENCHMARKS:
        result = run_benchmark(filename, name, limit=limit)
        summary.append(result)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Benchmark':<20} {'pass@1':<10} {'N':<6}")
    print("-" * 36)
    for name, acc, n in summary:
        print(f"{name:<20} {acc:<10.4f} {n:<6}")

    (OUTPUT_DIR / "summary.json").write_text(json.dumps(
        {name: {"pass@1": acc, "n": n} for name, acc, n in summary}, indent=2
    ))


if __name__ == "__main__":
    main()
