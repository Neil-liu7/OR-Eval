"""End-to-end evaluation runner."""
from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from or_eval.data import BenchmarkProblem, load_datasets
from or_eval.execution import execute_code, extract_code_block
from or_eval.execution.solver_env import detect_available_solvers, solver_available, solver_availability_state, solver_environment_hash, solver_environment_snapshot
from or_eval.metrics import aggregate_results, classify_failure, compute_optimality_gap, solution_verification_record, tolerance_flags, verification_status
from or_eval.prompts.neutral import PromptSpec, default_neutral_prompt, render_prompt, solver_specific_prompts


RESULT_SCHEMA_VERSION = "or-eval-result-v2"


def run_model_evaluation(
    models: Iterable[str | dict],
    datasets: Iterable[str] | str,
    output_dir: Path,
    data_dir: Path,
    api_url: str,
    api_key: str | None,
    prompt: PromptSpec | None = None,
    prompt_set: list[PromptSpec] | None = None,
    concurrency: int = 4,
    limit_per_dataset: int | None = None,
    problem_set: list[BenchmarkProblem] | None = None,
    timeout: int = 30,
    memory_limit_mb: int | None = 2048,
    max_tokens: int = 4096,
    evaluation_mode: str = "single_pass",
    max_turns: int = 3,
    few_shot: int = 0,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    problems = problem_set if problem_set is not None else load_datasets(datasets, data_dir, limit_per_dataset)
    prompts = prompt_set or [prompt or default_neutral_prompt()]
    few_shot_examples = _build_few_shot_examples(few_shot, problems) if few_shot > 0 else None
    summary: dict[str, dict] = {}
    solver_env = solver_environment_snapshot()
    solver_env_digest = solver_environment_hash(solver_env)

    for model_entry in models:
        from or_eval.inference import create_client

        model_name, client = _make_client(model_entry, api_url=api_url, api_key=api_key, max_tokens=max_tokens)
        for prompt_spec in prompts:
            run_metadata = _run_metadata(
                prompt_spec=prompt_spec,
                api_url=api_url,
                timeout=timeout,
                memory_limit_mb=memory_limit_mb,
                max_tokens=max_tokens,
                concurrency=concurrency,
                solver_env=solver_env,
                solver_env_hash_value=solver_env_digest,
            )
            run_dir = output_dir / model_name / prompt_spec.id
            run_dir.mkdir(parents=True, exist_ok=True)
            output_file = run_dir / "results.jsonl"
            results = _evaluate_problem_set(
                client=client,
                problems=problems,
                prompt_spec=prompt_spec,
                output_file=output_file,
                concurrency=concurrency,
                timeout=timeout,
                memory_limit_mb=memory_limit_mb,
                run_metadata=run_metadata,
                evaluation_mode=evaluation_mode,
                max_turns=max_turns,
                few_shot_examples=few_shot_examples,
            )
            metrics = aggregate_results(results)
            summary[f"{model_name}/{prompt_spec.id}"] = metrics
            (run_dir / "summary.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def run_ablation(
    models: Iterable[str | dict],
    datasets: Iterable[str] | str,
    output_dir: Path,
    data_dir: Path,
    api_url: str,
    api_key: str | None,
    neutral_prompt: PromptSpec | None = None,
    **kwargs,
) -> dict:
    prompts = [neutral_prompt or default_neutral_prompt(), *solver_specific_prompts()]
    return run_model_evaluation(
        models=models,
        datasets=datasets,
        output_dir=output_dir,
        data_dir=data_dir,
        api_url=api_url,
        api_key=api_key,
        prompt_set=prompts,
        **kwargs,
    )


def fairness_smoke_check(output_dir: Path) -> dict:
    """Run a deterministic local smoke check that does not call an LLM API."""
    from or_eval.reporting import generate_report

    output_dir.mkdir(parents=True, exist_ok=True)
    solver_env = solver_environment_snapshot()
    run_metadata = _run_metadata(
        prompt_spec=PromptSpec(
            id="neutral_smoke",
            text="Local fairness smoke prompt. Problem: {question}",
            prompt_type="neutral",
            metadata={"source": "fairness_smoke"},
        ),
        api_url="local://fairness-smoke",
        timeout=30,
        memory_limit_mb=2048,
        max_tokens=0,
        concurrency=1,
        solver_env=solver_env,
        solver_env_hash_value=solver_environment_hash(solver_env),
    )
    problem = BenchmarkProblem(
        id="FairnessSmoke:0",
        dataset="FairnessSmoke",
        question="Maximize x + y subject to x <= 1 and y <= 1.",
        answer=2.0,
        metadata={"source": "local_smoke"},
    )
    code = """
x = 1
y = 1
print("OBJECTIVE_VALUE:", x + y)
print('VARIABLE_VALUES: {"x": 1, "y": 1}')
"""
    full_row = _row_from_local_execution(
        model="local-smoke",
        prompt_spec=PromptSpec(id="neutral_smoke", text="Local fairness smoke prompt. Problem: {question}", prompt_type="neutral"),
        problem=problem,
        code=code,
        run_metadata=run_metadata,
    )
    full_dir = output_dir / "full_eval" / "local-smoke" / "neutral_smoke"
    full_dir.mkdir(parents=True, exist_ok=True)
    (full_dir / "results.jsonl").write_text(json.dumps(full_row, ensure_ascii=False) + "\n", encoding="utf-8")
    (full_dir / "summary.json").write_text(json.dumps(aggregate_results([full_row]), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "full_eval" / "summary.json").write_text(json.dumps({"local-smoke/neutral_smoke": aggregate_results([full_row])}, indent=2, ensure_ascii=False), encoding="utf-8")

    ablation_rows = _fairness_smoke_ablation_rows(problem, run_metadata)
    for row in ablation_rows:
        run_dir = output_dir / "ablation_validation" / row["model"] / row["prompt_id"]
        run_dir.mkdir(parents=True, exist_ok=True)
        with (run_dir / "results.jsonl").open("w", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        (run_dir / "summary.json").write_text(json.dumps(aggregate_results([row]), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "ablation_validation" / "summary.json").write_text(
        json.dumps({f'{row["model"]}/{row["prompt_id"]}': aggregate_results([row]) for row in ablation_rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report = generate_report(output_dir, output_dir / "report")
    return {
        "output_dir": str(output_dir),
        "result": full_row,
        "summary": report["summary"],
        "fairness_audit": report["fairness_audit"],
    }


def _evaluate_problem_set(
    client,
    problems: list[BenchmarkProblem],
    prompt_spec: PromptSpec,
    output_file: Path,
    concurrency: int,
    timeout: int,
    memory_limit_mb: int | None,
    run_metadata: dict | None = None,
    evaluation_mode: str = "single_pass",
    max_turns: int = 3,
    few_shot_examples: list[dict] | None = None,
) -> list[dict]:
    run_metadata = run_metadata or {}
    done = _load_existing(output_file)
    done = [_normalize_existing_row(row) for row in done if _matches_run_metadata(row, run_metadata)]
    done_keys = {row["run_key"] for row in done if "run_key" in row}
    pending = [p for p in problems if _run_key(client.model, prompt_spec.id, p) not in done_keys]
    lock = threading.Lock()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        futures = [
            pool.submit(
                _evaluate_one, client, problem, prompt_spec, timeout, memory_limit_mb,
                run_metadata, evaluation_mode, max_turns, few_shot_examples,
            )
            for problem in pending
        ]
        for fut in tqdm(as_completed(futures), total=len(futures), desc=f"{client.model}/{prompt_spec.id}"):
            row = fut.result()
            with lock:
                with output_file.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                done.append(row)
    return done


def _evaluate_one(
    client,
    problem: BenchmarkProblem,
    prompt_spec: PromptSpec,
    timeout: int,
    memory_limit_mb: int | None,
    run_metadata: dict | None = None,
    evaluation_mode: str = "single_pass",
    max_turns: int = 3,
    few_shot_examples: list[dict] | None = None,
) -> dict:
    run_metadata = run_metadata or {}
    eval_mode = problem.metadata.get("eval_mode", "code_gen")

    if eval_mode == "mcq":
        return _evaluate_mcq(client, problem, prompt_spec, run_metadata)

    prompt = render_prompt(prompt_spec.text, problem.question, few_shot_examples=few_shot_examples)
    response = client.generate(prompt)
    code = extract_code_block(response.text)
    execution = execute_code(code, timeout=timeout, memory_limit_mb=memory_limit_mb) if code else None

    row = _build_result_row(
        model=client.model,
        prompt_spec=prompt_spec,
        problem=problem,
        code=code,
        execution=execution,
        run_metadata=run_metadata,
        raw_response=response.text,
        api_error=response.error,
        latency=response.latency,
        tokens_prompt=response.tokens_prompt,
        tokens_completion=response.tokens_completion,
        tokens_total=response.tokens_total,
    )

    if evaluation_mode == "single_pass" or row.get("acc_5pct"):
        return row

    if evaluation_mode == "self_debug" and code and not row.get("executable"):
        from or_eval.evaluation_modes import self_debug_turns
        turns = self_debug_turns(
            client, problem.question, code, execution,
            max_turns=max_turns, timeout=timeout, memory_limit_mb=memory_limit_mb,
        )
        if turns:
            last = turns[-1]
            row["multi_turn"] = {
                "mode": "self_debug",
                "turns": len(turns),
                "final_success": last.success,
                "final_predicted": last.predicted,
            }
            if last.success and last.predicted is not None:
                from or_eval.metrics import tolerance_flags as _tflags
                row["multi_turn"]["acc_5pct"] = _tflags(last.predicted, problem.answer).get("acc_5pct", False)

    elif evaluation_mode == "reflexion":
        from or_eval.evaluation_modes import reflexion_turns
        turns = reflexion_turns(
            client, problem.question, code or "", execution,
            ground_truth=problem.answer,
            max_turns=max_turns, timeout=timeout, memory_limit_mb=memory_limit_mb,
        )
        if turns:
            last = turns[-1]
            row["multi_turn"] = {
                "mode": "reflexion",
                "turns": len(turns),
                "final_success": last.success,
                "final_predicted": last.predicted,
            }
            if last.success and last.predicted is not None:
                from or_eval.metrics import tolerance_flags as _tflags
                row["multi_turn"]["acc_5pct"] = _tflags(last.predicted, problem.answer).get("acc_5pct", False)

    return row


def _row_from_local_execution(
    model: str,
    prompt_spec: PromptSpec,
    problem: BenchmarkProblem,
    code: str,
    run_metadata: dict,
) -> dict:
    execution = execute_code(code, timeout=30, memory_limit_mb=2048)
    return _build_result_row(
        model=model,
        prompt_spec=prompt_spec,
        problem=problem,
        code=code,
        execution=execution,
        run_metadata=run_metadata,
        raw_response=f"```python\n{code}\n```",
        api_error=None,
        latency=0.0,
        tokens_prompt=0,
        tokens_completion=0,
        tokens_total=0,
    )


def _build_result_row(
    model: str,
    prompt_spec: PromptSpec,
    problem: BenchmarkProblem,
    code: str,
    execution,
    run_metadata: dict,
    raw_response: str,
    api_error: str | None,
    latency: float,
    tokens_prompt: int | None,
    tokens_completion: int | None,
    tokens_total: int | None,
) -> dict:
    pred = execution.objective_value if execution and execution.success else None
    solve_success = bool(
        execution
        and execution.success
        and pred is not None
        and execution.solver_status not in {"infeasible", "unbounded", "timeout", "error"}
    )
    flags = tolerance_flags(pred, problem.answer)
    availability = run_metadata.get("solver_availability") or detect_available_solvers()
    solver = execution.solver if execution else "unknown"
    row = {
        "run_key": _run_key(model, prompt_spec.id, problem),
        "schema_version": RESULT_SCHEMA_VERSION,
        "model": model,
        "dataset": problem.dataset,
        "problem_id": problem.id,
        "prompt_id": prompt_spec.id,
        "prompt_type": prompt_spec.prompt_type,
        "prompt_metadata": prompt_spec.metadata or {},
        "question": problem.question,
        "answer": problem.answer,
        "raw_response": raw_response,
        "code": code,
        "api_error": api_error,
        "latency": latency,
        "tokens_prompt": tokens_prompt,
        "tokens_completion": tokens_completion,
        "tokens_total": tokens_total,
        "executable": bool(execution and execution.success),
        "solver": solver,
        "solver_available": solver_available(solver, availability),
        "solver_availability_state": solver_availability_state(solver, availability),
        "solver_status": execution.solver_status if execution else "no_code",
        "solve_success": solve_success,
        "execution": execution.to_dict() if execution else None,
        "predicted": pred,
        "objective_extraction": execution.objective_extraction if execution else None,
        "variable_values": execution.variable_values if execution else None,
        "gap": compute_optimality_gap(pred, problem.answer),
        "prompt_hash": run_metadata.get("prompt_hash"),
        "config_hash": run_metadata.get("config_hash"),
        "solver_env_hash": run_metadata.get("solver_env_hash"),
        "run_metadata": run_metadata,
        **flags,
    }
    row["correct"] = row["acc_5pct"]
    row["failure_type"] = classify_failure(row)
    row["verification_status"] = verification_status(row)
    row["solution_verification"] = solution_verification_record(row)
    # Variable-level matching for OptiBench ReSocratic format
    expected_results = problem.metadata.get("expected_results")
    if expected_results and row.get("variable_values"):
        var_match = _check_variable_match(row["variable_values"], expected_results)
        row["variable_match"] = var_match
        row["solution_verification"]["variable_match"] = var_match
    return row


MCQ_PROMPT = """Answer the following multiple-choice question about operations research / optimization modeling.
Reply with ONLY the letter (A, B, C, or D) of the correct answer.

{question}

Answer:"""


def _evaluate_mcq(client, problem: BenchmarkProblem, prompt_spec: PromptSpec, run_metadata: dict) -> dict:
    """Evaluate a multiple-choice QA problem (ORQA-style)."""
    import re
    prompt = MCQ_PROMPT.format(question=problem.question)
    response = client.generate(prompt)
    raw = response.text.strip()
    match = re.search(r'\b([A-D])\b', raw)
    predicted = match.group(1) if match else raw[:1].upper()
    correct = predicted == problem.answer
    row = {
        "run_key": _run_key(client.model, prompt_spec.id, problem),
        "schema_version": RESULT_SCHEMA_VERSION,
        "model": client.model,
        "dataset": problem.dataset,
        "problem_id": problem.id,
        "prompt_id": prompt_spec.id,
        "prompt_type": prompt_spec.prompt_type,
        "prompt_metadata": prompt_spec.metadata or {},
        "question": problem.question,
        "answer": problem.answer,
        "raw_response": response.text,
        "code": None,
        "api_error": response.error,
        "latency": response.latency,
        "tokens_prompt": response.tokens_prompt,
        "tokens_completion": response.tokens_completion,
        "tokens_total": response.tokens_total,
        "executable": True,
        "solver": "mcq",
        "solver_available": True,
        "solver_availability_state": "not_detected",
        "solver_status": "optimal" if correct else "incorrect",
        "solve_success": correct,
        "execution": None,
        "predicted": predicted,
        "objective_extraction": {"value": predicted, "source": "mcq_answer", "confidence": "high"},
        "variable_values": None,
        "gap": 0.0 if correct else 1.0,
        "prompt_hash": run_metadata.get("prompt_hash"),
        "config_hash": run_metadata.get("config_hash"),
        "solver_env_hash": run_metadata.get("solver_env_hash"),
        "run_metadata": run_metadata,
        "acc_5pct": correct,
        "acc_1pct": correct,
        "acc_1e-4": correct,
        "eval_mode": "mcq",
        "question_type": problem.metadata.get("question_type"),
    }
    row["correct"] = correct
    row["failure_type"] = "correct" if correct else "wrong_answer"
    row["verification_status"] = "objective_match" if correct else "objective_mismatch"
    row["solution_verification"] = {"objective_status": "match" if correct else "mismatch", "constraint_feasibility": "not_applicable"}
    return row


def _fairness_smoke_ablation_rows(problem: BenchmarkProblem, base_metadata: dict) -> list[dict]:
    rows = []
    for prompt_id, solver, available in [
        ("neutral_smoke", "unknown", False),
        ("solver_specific_pyscipopt", "pyscipopt", True),
    ]:
        metadata = dict(base_metadata)
        metadata["solver_availability"] = {**base_metadata.get("solver_availability", {}), solver: available}
        row = {
            "run_key": f"local-smoke|{prompt_id}|{problem.id}",
            "schema_version": RESULT_SCHEMA_VERSION,
            "model": "local-smoke",
            "dataset": problem.dataset,
            "problem_id": problem.id,
            "prompt_id": prompt_id,
            "prompt_type": "neutral" if prompt_id == "neutral_smoke" else "solver_specific",
            "prompt_metadata": {},
            "question": problem.question,
            "answer": problem.answer,
            "raw_response": "",
            "code": "print('OBJECTIVE_VALUE:', 2)",
            "api_error": None,
            "latency": 0.0,
            "tokens_prompt": 0,
            "tokens_completion": 0,
            "tokens_total": 0,
            "executable": True,
            "solver": solver,
            "solver_available": solver_available(solver, metadata.get("solver_availability")),
            "solver_availability_state": solver_availability_state(solver, metadata.get("solver_availability")),
            "solver_status": "optimal",
            "solve_success": True,
            "execution": None,
            "predicted": 2.0,
            "objective_extraction": {"value": 2.0, "source": "objective_value", "confidence": "high"},
            "variable_values": {"x": 1, "y": 1},
            "gap": 0.0,
            "prompt_hash": base_metadata.get("prompt_hash"),
            "config_hash": base_metadata.get("config_hash"),
            "solver_env_hash": base_metadata.get("solver_env_hash"),
            "run_metadata": metadata,
            **tolerance_flags(2.0, problem.answer),
        }
        row["correct"] = row["acc_5pct"]
        row["failure_type"] = classify_failure(row)
        row["verification_status"] = verification_status(row)
        row["solution_verification"] = solution_verification_record(row)
        rows.append(row)
    return rows


def _build_few_shot_examples(n: int, problems: list[BenchmarkProblem]) -> list[dict] | None:
    """Build few-shot examples from the simplest problems in the set.

    Uses the first N problems as demonstrations with a trivial code template.
    These are NOT solved dynamically — they show the expected output format.
    """
    if n <= 0 or not problems:
        return None
    import random
    rng = random.Random(42)
    candidates = list(problems)
    rng.shuffle(candidates)
    examples = []
    for p in candidates[:n]:
        examples.append({
            "question": p.question[:500],
            "code": f'# Solve: {p.question[:80]}...\n# (formulate and solve with any optimizer)\nprint("OBJECTIVE_VALUE:", {p.answer})',
        })
    return examples


def _load_existing(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _run_key(model: str, prompt_id: str, problem: BenchmarkProblem) -> str:
    return f"{model}|{prompt_id}|{problem.id}"


def _run_metadata(
    prompt_spec: PromptSpec,
    api_url: str,
    timeout: int,
    memory_limit_mb: int | None,
    max_tokens: int,
    concurrency: int,
    solver_env: dict,
    solver_env_hash_value: str,
) -> dict:
    solver_availability = {
        solver_id: data.get("available", False)
        for solver_id, data in solver_env.get("solvers", {}).items()
    }
    config = {
        "api_url": api_url,
        "temperature": 0,
        "max_tokens": max_tokens,
        "timeout": timeout,
        "memory_limit_mb": memory_limit_mb,
        "concurrency": concurrency,
    }
    return {
        "prompt_hash": _stable_hash({"id": prompt_spec.id, "text": prompt_spec.text, "type": prompt_spec.prompt_type}),
        "config_hash": _stable_hash(_semantic_config(config)),
        "solver_env_hash": solver_env_hash_value,
        "schema_version": RESULT_SCHEMA_VERSION,
        "config": config,
        "solver_availability": solver_availability,
        "solver_environment": solver_env,
    }


def _stable_hash(value) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _matches_run_metadata(row: dict, run_metadata: dict) -> bool:
    if not run_metadata:
        return True
    if row.get("prompt_hash") != run_metadata.get("prompt_hash"):
        return False
    if row.get("solver_env_hash") != run_metadata.get("solver_env_hash"):
        return False
    if row.get("config_hash") == run_metadata.get("config_hash"):
        return True

    # Backward compatibility for rows written before concurrency was treated
    # as a scheduling-only parameter. Changing worker count must not invalidate
    # JSONL resume for the same model/prompt/data/execution configuration.
    row_config = (row.get("run_metadata") or {}).get("config") or {}
    new_config = run_metadata.get("config") or {}
    return _semantic_config(row_config) == _semantic_config(new_config)


def _semantic_config(config: dict) -> dict:
    return {key: value for key, value in config.items() if key != "concurrency"}


def _check_variable_match(actual: dict, expected: dict, tolerance: float = 0.05) -> dict:
    """Check if all expected variable values match actual values (OptiBench ReSocratic strict mode)."""
    matched = 0
    mismatched = []
    for key, expected_val in expected.items():
        actual_val = actual.get(key)
        if actual_val is None:
            mismatched.append({"key": key, "expected": expected_val, "actual": None})
            continue
        try:
            ev, av = float(expected_val), float(actual_val)
            if ev == 0:
                ok = abs(av) <= 1e-4
            else:
                ok = abs(ev - av) / max(abs(ev), 1e-12) <= tolerance
        except (ValueError, TypeError):
            ok = str(expected_val).strip() == str(actual_val).strip()
        if ok:
            matched += 1
        else:
            mismatched.append({"key": key, "expected": expected_val, "actual": actual_val})
    total = len(expected)
    return {
        "all_match": matched == total,
        "matched": matched,
        "total": total,
        "match_rate": matched / total if total else 0.0,
        "mismatched": mismatched[:5],
    }


def _normalize_existing_row(row: dict) -> dict:
    if "failure_type" not in row:
        row["failure_type"] = classify_failure(row)
    if "verification_status" not in row:
        row["verification_status"] = verification_status(row)
    if "solver_available" not in row:
        row["solver_available"] = solver_available(row.get("solver", "unknown"))
    if "solver_availability_state" not in row:
        row["solver_availability_state"] = solver_availability_state(row.get("solver", "unknown"))
    if "solution_verification" not in row:
        row["solution_verification"] = solution_verification_record(row)
    return row


def _make_client(model_entry, api_url: str, api_key: str | None, max_tokens: int):
    """Create a client from a model entry (string or dict with provider config)."""
    from or_eval.inference import create_client

    if isinstance(model_entry, str):
        client = create_client(
            model=model_entry,
            provider="auto",
            api_url=api_url,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=0,
        )
        return model_entry, client

    if isinstance(model_entry, dict):
        name = model_entry.get("name") or model_entry.get("model", "unknown")
        client = create_client(
            model=name,
            provider=model_entry.get("provider", "auto"),
            api_url=model_entry.get("api_url", api_url),
            api_key=model_entry.get("api_key", api_key),
            api_key_env=model_entry.get("api_key_env", "OR_EVAL_API_KEY"),
            max_tokens=model_entry.get("max_tokens", max_tokens),
            temperature=model_entry.get("temperature", 0),
            timeout=model_entry.get("timeout", 120),
            max_retries=model_entry.get("max_retries", 3),
        )
        return name, client

    raise ValueError(f"Invalid model entry: {model_entry!r}")
