#!/bin/bash
# Run consistency check on all continuation chapters vs original
# Usage: bash experiments/hongloumeng_constory_smoke/scripts/run_consistency.sh

SOURCE_DIR="resources/corpora/hongloumeng/prepared/chapters/original"
CONTINUATION_DIR="resources/corpora/hongloumeng/prepared/chapters/continuations"
OUTPUT_DIR="experiments/hongloumeng_constory_smoke/runs/current"

mkdir -p "$OUTPUT_DIR"

echo "=== Consistency Check ==="
echo "Source: $SOURCE_DIR"
echo "Continuation: $CONTINUATION_DIR"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Run with: stone-eval consistency --source <file> --continuation <file>"
