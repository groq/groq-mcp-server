#!/bin/bash

# Groq Compound-Beta script
# Usage: ./groq_compound.sh "Your message" [model] [stream] [output_directory]
# Example: ./scripts/groq_compound.sh "What is Groq's Compound Beta?" compound-beta true
# Example: ./scripts/groq_compound.sh "Please retrieve the current Bitcoin price from CoinGecko API and calculate the value of 0.38474 bitcoins.?" compound-beta-deep


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

# Check if message argument is provided
if [ -z "$1" ]; then
    echo "Error: No message provided."
    echo "Usage: ./groq_compound.sh \"Your message\" [model] [stream] [output_directory]"
    exit 1
fi

MESSAGE="$1"
MODEL="${2:-compound-beta}"  # Default model is compound-beta
STREAM="${3:-false}"        # Default stream is false
OUTPUT_DIR="${4:-}"         # Optional output directory

# Create a temporary Python script to handle special characters properly
TEMP_SCRIPT=$(mktemp)

# Generate Python code using printf to handle special characters
printf "import sys\nimport os\n\n" > "$TEMP_SCRIPT"
printf "# Add project root and parent directory to Python path\n" >> "$TEMP_SCRIPT"
printf "sys.path.insert(0, '%s')\n" "$PROJECT_ROOT" >> "$TEMP_SCRIPT"
printf "parent_dir = os.path.dirname('%s')\n" "$PROJECT_ROOT" >> "$TEMP_SCRIPT"
printf "if parent_dir not in sys.path:\n    sys.path.insert(0, parent_dir)\n\n" >> "$TEMP_SCRIPT"
printf "from src.groq_compound import compound_chat, compound_chat_stream\n" >> "$TEMP_SCRIPT"
printf "from mcp.types import TextContent\n\n" >> "$TEMP_SCRIPT"

# Choose the appropriate function based on stream parameter
if [ "$STREAM" = "true" ]; then
    printf "result = compound_chat_stream(\n" >> "$TEMP_SCRIPT"
else
    printf "result = compound_chat(\n" >> "$TEMP_SCRIPT"
fi

printf "    messages=[{\n" >> "$TEMP_SCRIPT"
printf "        'role': 'user',\n" >> "$TEMP_SCRIPT"
printf "        'content': \"\"\"%s\"\"\"\n" "$MESSAGE" >> "$TEMP_SCRIPT"
printf "    }],\n" >> "$TEMP_SCRIPT"
printf "    model='%s',\n" "$MODEL" >> "$TEMP_SCRIPT"
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
    echo "Error: Groq compound chat failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi