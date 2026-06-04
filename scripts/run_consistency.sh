#!/bin/bash
# Run consistency check on all continuation chapters vs original
# Usage: bash scripts/run_consistency.sh

SOURCE_DIR="../Stone/data/chapters"
CONTINUATION_DIR="../Stone/generations/prompt_baseline"
OUTPUT_DIR="outputs/consistency"

mkdir -p "$OUTPUT_DIR"

echo "=== Consistency Check ==="
echo "Source: $SOURCE_DIR"
echo "Continuation: $CONTINUATION_DIR"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Run with: stone-eval consistency --source <file> --continuation <file>"
