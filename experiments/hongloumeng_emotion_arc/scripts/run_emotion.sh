#!/bin/bash
# Run emotional arc analysis
# Usage: bash experiments/hongloumeng_emotion_arc/scripts/run_emotion.sh

CONTINUATION_DIR="resources/corpora/hongloumeng/prepared/chapters/continuations"
ORIGINAL_DIR="resources/corpora/hongloumeng/prepared/chapters/original"
OUTPUT_DIR="experiments/hongloumeng_emotion_arc/runs/current"

mkdir -p "$OUTPUT_DIR"

echo "=== Emotion Arc Analysis ==="
echo "Original: $ORIGINAL_DIR"
echo "Continuation: $CONTINUATION_DIR"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Run with: stone-eval emotion --text <file> --reference <arc.json>"
