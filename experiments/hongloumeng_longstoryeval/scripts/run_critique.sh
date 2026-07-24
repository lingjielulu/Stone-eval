#!/bin/bash
# Run NovelCritique-style quality evaluation
# Usage: bash experiments/hongloumeng_longstoryeval/scripts/run_critique.sh

CONTINUATION_DIR="resources/corpora/hongloumeng/prepared/longstoryeval/continuations/books_json"
OUTPUT_DIR="experiments/hongloumeng_longstoryeval/runs/current"

mkdir -p "$OUTPUT_DIR"

echo "=== Quality Critique ==="
echo "Continuation: $CONTINUATION_DIR"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Run with: stone-eval critique --summary <file>"
