#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

: "${OR_EVAL_API_KEY:?Set OR_EVAL_API_KEY before running.}"

RESULT_ROOT="${OR_EVAL_RESULT_ROOT:-results/or_eval_pipeline_v2}"
FULL_DIR="$RESULT_ROOT/full_eval"
ABLATION_DIR="$RESULT_ROOT/ablation_validation"
REPORT_DIR="$RESULT_ROOT/report"
CONCURRENCY="${OR_EVAL_CONCURRENCY:-8}"
PROMPT_FILE="$RESULT_ROOT/prompt_search_deepseek_v3/best_prompt_v2.txt"

SUPPLEMENT_MODELS="gpt-4.1,o4-mini,qwen-max,qwen3-235b-a22b,gemini-2.5-pro"

echo "=== OR-Eval Supplement Evaluation ==="
echo "Models: $SUPPLEMENT_MODELS"
echo "Concurrency: $CONCURRENCY"
echo "Prompt: $PROMPT_FILE"
echo ""

echo "[1/4] Full Evaluation (resume-safe, skips completed problems)"
python3 -m or_eval.cli evaluate \
  --models "$SUPPLEMENT_MODELS" \
  --datasets all \
  --config configs/default.yaml \
  --prompt-file "$PROMPT_FILE" \
  --prompt-id neutral_best_v2 \
  --output-dir "$FULL_DIR" \
  --concurrency "$CONCURRENCY"

echo ""
echo "[2/4] Ablation (neutral + 3 solver-specific, 300 validation samples)"
python3 -m or_eval.cli ablation \
  --models "$SUPPLEMENT_MODELS" \
  --datasets all \
  --config configs/default.yaml \
  --prompt-file "$PROMPT_FILE" \
  --output-dir "$ABLATION_DIR" \
  --validation-per-dataset 50 \
  --seed 42 \
  --concurrency "$CONCURRENCY"

echo ""
echo "[3/4] Report + Audit"
python3 -m or_eval.cli report \
  --results-dir "$RESULT_ROOT" \
  --output-dir "$REPORT_DIR"

python3 -m or_eval.cli fairness-audit \
  --results-dir "$RESULT_ROOT" \
  --output-dir "$REPORT_DIR"

python3 -m or_eval.cli target-audit \
  --results-dir "$RESULT_ROOT" \
  --output-dir "$REPORT_DIR"

echo ""
echo "[4/4] Statistical Analysis"
python3 -m or_eval.cli statistics \
  --results-dir "$RESULT_ROOT" \
  --output-dir "$REPORT_DIR/statistics"

echo ""
echo "=== Done. Check results at: $RESULT_ROOT ==="
