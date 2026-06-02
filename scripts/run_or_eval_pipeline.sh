#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

: "${OR_EVAL_API_KEY:?Set OR_EVAL_API_KEY before running the full pipeline.}"

RESULT_ROOT="${OR_EVAL_RESULT_ROOT:-results/or_eval_pipeline_v2}"
SEARCH_DIR="${1:-$RESULT_ROOT/prompt_search_deepseek_v3}"
FULL_DIR="${2:-$RESULT_ROOT/full_eval}"
ABLATION_DIR="${3:-$RESULT_ROOT/ablation_validation}"
REPORT_DIR="${4:-$RESULT_ROOT/report}"
CONCURRENCY="${OR_EVAL_CONCURRENCY:-8}"
MODELS="${OR_EVAL_MODELS:-deepseek-v3,deepseek-v3.2,gpt-4o-mini,gemini-2.5-pro,o3-mini}"

python3 -m or_eval.cli search-prompts \
  --model deepseek-v3 \
  --config configs/default.yaml \
  --output-dir "$SEARCH_DIR" \
  --concurrency "$CONCURRENCY" \
  --final-full

python3 -m or_eval.cli evaluate \
  --models "$MODELS" \
  --datasets all \
  --config configs/default.yaml \
  --prompt-file "$SEARCH_DIR/best_prompt.txt" \
  --prompt-id neutral_best \
  --output-dir "$FULL_DIR" \
  --concurrency "$CONCURRENCY"

python3 -m or_eval.cli ablation \
  --models "$MODELS" \
  --datasets all \
  --config configs/default.yaml \
  --prompt-file "$SEARCH_DIR/best_prompt.txt" \
  --output-dir "$ABLATION_DIR" \
  --validation-per-dataset 50 \
  --seed 42 \
  --concurrency "$CONCURRENCY"

python3 -m or_eval.cli report \
  --results-dir "$RESULT_ROOT" \
  --output-dir "$REPORT_DIR"

AUDIT_ARGS=()
if [[ "${OR_EVAL_STRICT_AUDIT:-0}" == "1" ]]; then
  AUDIT_ARGS+=(--strict)
fi

python3 -m or_eval.cli fairness-audit \
  --results-dir "$RESULT_ROOT" \
  --output-dir "$REPORT_DIR" \
  "${AUDIT_ARGS[@]}"

python3 -m or_eval.cli target-audit \
  --results-dir "$RESULT_ROOT" \
  --output-dir "$REPORT_DIR" \
  "${AUDIT_ARGS[@]}"
