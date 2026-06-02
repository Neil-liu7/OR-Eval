"""Batch convert source benchmark data to unified JSONL format."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from or_eval.data.adapters import adapt_orqa, adapt_industryOR, adapt_optibench

SOURCE_DIR = Path(__file__).resolve().parent.parent.parent / "OR-Eval-摸底"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "unified"


def write_jsonl(problems, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for p in problems:
            f.write(p.to_jsonl() + "\n")
    print(f"  Written {len(problems)} problems to {output_path}")


def main():
    all_problems = {"A": [], "B": [], "C": [], "D": []}

    # ORQA
    orqa_path = SOURCE_DIR / "ORQA" / "dataset" / "ORQA_test.jsonl"
    if orqa_path.exists():
        problems = adapt_orqa(orqa_path)
        all_problems["A"].extend(problems)
        print(f"[ORQA] {len(problems)} problems (Dim A)")

    # IndustryOR
    indor_path = SOURCE_DIR / "orlm" / "results" / "IndustryOR.q2mc_en.ORLM-LLaMA-3-8B" / "executed.jsonl"
    if indor_path.exists():
        problems = adapt_industryOR(indor_path)
        for p in problems:
            for dim in p.dimensions:
                all_problems[dim].append(p)
        print(f"[IndustryOR] {len(problems)} problems (Dim C, D)")

    # OptiBench
    optibench_path = SOURCE_DIR / "ReSocratic" / "data" / "OptiBench.json"
    if optibench_path.exists():
        problems = adapt_optibench(optibench_path)
        for p in problems:
            for dim in p.dimensions:
                all_problems[dim].append(p)
        print(f"[OptiBench] {len(problems)} problems (Dim B, C, D)")

    # Write per-dimension JSONL
    dim_names = {"A": "conceptual", "B": "formulation", "C": "code_gen", "D": "end_to_end"}
    for dim, name in dim_names.items():
        if all_problems[dim]:
            write_jsonl(all_problems[dim], OUTPUT_DIR / f"{name}.jsonl")

    total = sum(len(v) for v in all_problems.values())
    print(f"\nTotal: {total} problem-dimension pairs across {len(dim_names)} dimensions")


if __name__ == "__main__":
    main()
