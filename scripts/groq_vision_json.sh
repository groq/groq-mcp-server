#!/bin/bash

# Groq Vision JSON script
# Usage: ./groq_vision_json.sh <image_file> [prompt] [temperature] [max_tokens] [output_directory]
# ./scripts/groq_vision_json.sh "./input/llama.jpg" "Extract key information as JSON"

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
    echo "Usage: ./groq_vision_json.sh <image_file> [prompt] [temperature] [max_tokens] [output_directory]"
    exit 1
fi

# Check if the provided file exists
if [ ! -f "$1" ]; then
    echo "Error: Image file '$1' does not exist."
    exit 1
fi

IMAGE_FILE="$1"
PROMPT="${2:-Extract key information from this image as JSON}"  # Default prompt
TEMPERATURE="${3:-0.2}"  # Default temperature
MAX_TOKENS="${4:-1024}"  # Default max tokens
OUTPUT_DIR="${5:-}"  # Optional output directory, defaults to null (will use BASE_OUTPUT_PATH)

# Create a temporary Python script
TEMP_SCRIPT=$(mktemp)

# Generate Python code using printf to handle special characters
printf "import sys\nimport os\n\n" > "$TEMP_SCRIPT"
printf "# Add project root and parent directory to Python path\n" >> "$TEMP_SCRIPT"
printf "sys.path.insert(0, '%s')\n" "$PROJECT_ROOT" >> "$TEMP_SCRIPT"
printf "parent_dir = os.path.dirname('%s')\n" "$PROJECT_ROOT" >> "$TEMP_SCRIPT"
printf "if parent_dir not in sys.path:\n    sys.path.insert(0, parent_dir)\n\n" >> "$TEMP_SCRIPT"
printf "from src.groq_vision import analyze_image_json\n" >> "$TEMP_SCRIPT"
printf "from mcp.types import TextContent\n\n" >> "$TEMP_SCRIPT"
printf "result = analyze_image_json(\n" >> "$TEMP_SCRIPT"
printf "    input_file_path='%s',\n" "$IMAGE_FILE" >> "$TEMP_SCRIPT"
printf "    prompt=\"%s\",\n" "$PROMPT" >> "$TEMP_SCRIPT"
printf "    temperature=%s,\n" "$TEMPERATURE" >> "$TEMP_SCRIPT"
printf "    max_tokens=%s,\n" "$MAX_TOKENS" >> "$TEMP_SCRIPT"
printf "    output_directory='%s' if '%s' != '' else None,\n" "$OUTPUT_DIR" "$OUTPUT_DIR" >> "$TEMP_SCRIPT"
printf "    save_to_file=True\n" >> "$TEMP_SCRIPT"
printf ")\n\n" >> "$TEMP_SCRIPT"
printf "print(result.text)\n" >> "$TEMP_SCRIPT"

# Run the script
python3 "$TEMP_SCRIPT"

# Clean up the temporary script
rm "$TEMP_SCRIPT"

# Exit status
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Groq vision JSON analysis failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi 