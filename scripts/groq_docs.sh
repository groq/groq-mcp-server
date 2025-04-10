#!/bin/bash

# Groq Documentation Fetcher script
# Usage: ./groq_docs.sh [full|summary]
# Example: ./scripts/groq_docs.sh full
# Example: ./scripts/groq_docs.sh summary

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

# Default to summary if no argument provided
DOC_TYPE="${1:-summary}"

# Validate doc type argument
if [[ "$DOC_TYPE" != "full" && "$DOC_TYPE" != "summary" ]]; then
    echo "Error: Invalid documentation type. Use 'full' or 'summary'."
    echo "Usage: ./groq_docs.sh [full|summary]"
    exit 1
fi

# Run the appropriate documentation fetcher
python3 -c "
import sys
import os

# Add project root and parent directory to Python path
sys.path.insert(0, '$PROJECT_ROOT')
parent_dir = os.path.dirname('$PROJECT_ROOT')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.groq_docs import get_groq_full_docs, get_groq_short_docs

if '$DOC_TYPE' == 'full':
    result = get_groq_full_docs()
else:
    result = get_groq_short_docs()

print(result.text)
"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Groq documentation fetch failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi