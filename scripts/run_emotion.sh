#!/bin/bash
# Run emotional arc analysis
# Usage: bash scripts/run_emotion.sh

CONTINUATION_DIR="../Stone/generations/prompt_baseline"
ORIGINAL_DIR="../Stone/data/chapters"
OUTPUT_DIR="outputs/emotion"

mkdir -p "$OUTPUT_DIR"

echo "=== Emotion Arc Analysis ==="
echo "Original: $ORIGINAL_DIR"
echo "Continuation: $CONTINUATION_DIR"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Run with: stone-eval emotion --text <file> --reference <arc.json>"
