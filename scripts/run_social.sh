#!/bin/bash
# Run social network analysis on continuations
# Usage: bash scripts/run_social.sh

CONTINUATION_DIR="../Stone/generations/prompt_baseline"
CHARACTER_LIST="../Stone/Hongloumeng_card/cards"
OUTPUT_DIR="outputs/social"

mkdir -p "$OUTPUT_DIR"

echo "=== Social Network Analysis ==="
echo "Continuation: $CONTINUATION_DIR"
echo "Characters: $CHARACTER_LIST"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Run with: stone-eval social --text <file> --character-list <json>"
