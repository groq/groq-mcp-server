#!/bin/bash

# Groq Batch Processing script
# Usage: ./groq_batch.sh <input_file_or_directory> [completion_window]
# Example: ./scripts/groq_batch.sh "./input/test_batch.jsonl" 24h

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

# Check if GROQ_API_KEY is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "Error: GROQ_API_KEY environment variable is not set."
    echo "Please set it in your .env file or export it before running this script."
    exit 1
fi

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Check if input argument is provided
if [ -z "$1" ]; then
    echo "Error: No input file or directory provided."
    echo "Usage: ./groq_batch.sh <input_file_or_directory> [completion_window]"
    exit 1
fi

INPUT_PATH="$1"
COMPLETION_WINDOW="${2:-24h}"  # Default to 24h if not specified

# Run the batch processing
python3 -c "
import sys
import os

# Add project root and parent directory to Python path
sys.path.insert(0, '$PROJECT_ROOT')
parent_dir = os.path.dirname('$PROJECT_ROOT')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.groq_batch import process_batch

result = process_batch(
    requests='$INPUT_PATH',
    completion_window='$COMPLETION_WINDOW'
)

print(result.text)
"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Batch processing failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi 