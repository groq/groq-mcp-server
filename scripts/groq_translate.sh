#!/bin/bash

# Groq Audio Translation script
# Usage: ./groq_translate.sh <audio_file> [response_format] [output_directory]
# ./scripts/groq_translate.sh "./input/chinese.wav"
# ./scripts/groq_translate.sh "./input/openai-french.wav"

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

# Check if audio file argument is provided
if [ -z "$1" ]; then
    echo "Error: No audio file provided."
    echo "Usage: ./groq_translate.sh <audio_file> [response_format] [output_directory]"
    exit 1
fi

# Check if the provided file exists
if [ ! -f "$1" ]; then
    echo "Error: Audio file '$1' does not exist."
    exit 1
fi

AUDIO_FILE="$1"
RESPONSE_FORMAT="${2:-json}"  # Default response format is json
OUTPUT_DIR="${3:-}"  # Optional output directory, defaults to null (will use BASE_OUTPUT_PATH)

# Run the Groq audio translation
python3 -c "
import sys
import os

# Add project root and parent directory to Python path
sys.path.insert(0, '$PROJECT_ROOT')
parent_dir = os.path.dirname('$PROJECT_ROOT')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.groq_stt import translate_audio
from mcp.types import TextContent

result = translate_audio(
    input_file_path='$AUDIO_FILE',
    model='whisper-large-v3',  # Only whisper-large-v3 supports translation
    response_format='$RESPONSE_FORMAT',
    output_directory='$OUTPUT_DIR' if '$OUTPUT_DIR' != '' else None,
    save_to_file=True
)

print(result.text)
"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Groq audio translation failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi 