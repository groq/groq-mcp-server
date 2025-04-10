#!/bin/bash

# Groq Vision script
# Usage: ./groq_vision.sh <image_file> [prompt] [temperature] [max_tokens] [output_directory]
# ./scripts/groq_vision.sh "./input/llama.jpg" "What is in this image?"

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

# Check if image file argument is provided
if [ -z "$1" ]; then
    echo "Error: No image file provided."
    echo "Usage: ./groq_vision.sh <image_file> [prompt] [temperature] [max_tokens] [output_directory]"
    exit 1
fi

# Check if the provided file exists
if [ ! -f "$1" ]; then
    echo "Error: Image file '$1' does not exist."
    exit 1
fi

IMAGE_FILE="$1"
PROMPT="${2:-What is in this image?}"  # Default prompt
TEMPERATURE="${3:-0.7}"  # Default temperature
MAX_TOKENS="${4:-1024}"  # Default max tokens
OUTPUT_DIR="${5:-}"  # Optional output directory, defaults to null (will use BASE_OUTPUT_PATH)

# Run the Groq vision analysis
python3 -c "
import sys
import os

# Add project root and parent directory to Python path
sys.path.insert(0, '$PROJECT_ROOT')
parent_dir = os.path.dirname('$PROJECT_ROOT')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.groq_vision import analyze_image
from mcp.types import TextContent

result = analyze_image(
    input_file_path='$IMAGE_FILE',
    prompt='$PROMPT',
    temperature=$TEMPERATURE,
    max_tokens=$MAX_TOKENS,
    output_directory='$OUTPUT_DIR' if '$OUTPUT_DIR' != '' else None,
    save_to_file=True
)

print(result.text)
"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Groq vision analysis failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi 