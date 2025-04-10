#!/bin/bash

# List Groq Speech-to-Text Models script
# Usage: ./list_groq_stt_models.sh

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

# Run the list STT models function
python3 -c "
import sys
import os

# Add project root and parent directory to Python path
sys.path.insert(0, '$PROJECT_ROOT')
parent_dir = os.path.dirname('$PROJECT_ROOT')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.groq_stt import list_stt_models
from mcp.types import TextContent

result = list_stt_models()
print(result.text)
"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Listing Groq STT models failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi 