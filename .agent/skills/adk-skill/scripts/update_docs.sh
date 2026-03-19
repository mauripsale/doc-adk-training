#!/bin/bash
# Script to update the ADK documentation
# Uses paths relative to the script location to remain portable.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REFS_DIR="$SKILL_DIR/references"

echo "Creating references directory if it doesn't exist..."
mkdir -p "$REFS_DIR"

echo "Downloading the latest ADK guidelines from https://github.com/google/adk-python/blob/main/llms-full.txt..."
curl -sL "https://raw.githubusercontent.com/google/adk-python/main/llms-full.txt" -o "$REFS_DIR/adk-docs.txt"

echo "Update complete. Documentation saved to: $REFS_DIR/adk-docs.txt"
