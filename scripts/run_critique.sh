#!/bin/bash
# Run NovelCritique-style quality evaluation
# Usage: bash scripts/run_critique.sh

CONTINUATION_DIR="../Stone/generations/prompt_baseline"
OUTPUT_DIR="outputs/critique"

mkdir -p "$OUTPUT_DIR"

echo "=== Quality Critique ==="
echo "Continuation: $CONTINUATION_DIR"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Run with: stone-eval critique --summary <file>"
