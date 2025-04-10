#!/bin/bash

# Groq Speech to Text script
# Usage: ./groq_stt.sh <audio_file> [model] [language] [response_format] [output_directory]
# ./scripts/groq_stt.sh "./input/sample.wav"


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
    echo "Usage: ./groq_stt.sh <audio_file> [model] [language] [response_format] [output_directory]"
    exit 1
fi

# Check if the provided file exists
if [ ! -f "$1" ]; then
    echo "Error: Audio file '$1' does not exist."
    exit 1
fi

AUDIO_FILE="$1"
MODEL="${2:-whisper-large-v3-turbo}"  # Default model is whisper-large-v3-turbo
LANGUAGE="${3:-}"  # Optional language code, defaults to null
RESPONSE_FORMAT="${4:-verbose_json}"  # Default response format is verbose_json
OUTPUT_DIR="${5:-}"  # Optional output directory, defaults to null (will use BASE_OUTPUT_PATH)

# Run the Groq speech-to-text transcription
python3 -c "
import sys
import os

# Add project root and parent directory to Python path
sys.path.insert(0, '$PROJECT_ROOT')
parent_dir = os.path.dirname('$PROJECT_ROOT')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.groq_stt import transcribe_audio
from mcp.types import TextContent

result = transcribe_audio(
    input_file_path='$AUDIO_FILE',
    model='$MODEL',
    language='$LANGUAGE' if '$LANGUAGE' != '' else None,
    response_format='$RESPONSE_FORMAT',
    timestamp_granularities=['segment', 'word'] if '$RESPONSE_FORMAT' == 'verbose_json' else ['segment'],
    output_directory='$OUTPUT_DIR' if '$OUTPUT_DIR' != '' else None,
    save_to_file=True
)

print(result.text)
"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Groq speech-to-text transcription failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi 