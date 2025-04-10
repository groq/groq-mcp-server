#!/bin/bash

# Groq Text to Speech script
# Usage: ./groq_tts.sh "Your text to convert to speech" [voice_name] [model] [output_directory]
# ./scripts/groq_tts.sh "Hello, how are you?"

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

# Check if text argument is provided
if [ -z "$1" ]; then
    echo "Error: No text provided."
    echo "Usage: ./groq_tts.sh \"Your text to convert to speech\" [voice_name] [model] [output_directory]"
    exit 1
fi

TEXT="$1"
VOICE="${2:-Arista-PlayAI}"  # Default voice is Arista-PlayAI
MODEL="${3:-playai-tts}"    # Default model is playai-tts (English)
OUTPUT_DIR="${4:-}"         # Optional output directory, defaults to null (will use Desktop)

# Run the Groq text-to-speech conversion
python3 -c "
import sys
import os

# Add project root and parent directory to Python path
sys.path.insert(0, '$PROJECT_ROOT')
parent_dir = os.path.dirname('$PROJECT_ROOT')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.groq_tts import text_to_speech
from mcp.types import TextContent

result = text_to_speech(
    text=\"\"\"$TEXT\"\"\",  # Using triple quotes to handle special characters in text
    voice='$VOICE',
    model='$MODEL',
    output_directory='$OUTPUT_DIR' if '$OUTPUT_DIR' != '' else None
)

print(result.text)
"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Groq text-to-speech conversion failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi 