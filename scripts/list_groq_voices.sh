#!/bin/bash

# List Groq Voices script
# Usage: ./list_groq_voices.sh [model]

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Load environment variables if .env file exists
if [ -f "../.env" ]; then
    source "../.env"
elif [ -f ".env" ]; then
    source ".env"
fi

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Default model is "all"
MODEL="${1:-all}"

# Valid models check
if [[ "$MODEL" != "all" && "$MODEL" != "playai-tts" && "$MODEL" != "playai-tts-arabic" ]]; then
    echo "Error: Invalid model specified."
    echo "Valid options are: all, playai-tts, or playai-tts-arabic"
    exit 1
fi

# Run the list voices function
python3 -c "
import sys
import os

# Add project root and parent directory to Python path
sys.path.insert(0, '$PROJECT_ROOT')
parent_dir = os.path.dirname('$PROJECT_ROOT')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.groq_tts import list_voices
from mcp.types import TextContent

result = list_voices(model='$MODEL')
print(result.text)
"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Listing Groq voices failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi 