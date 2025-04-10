#!/bin/bash

# example: ./scripts/test.sh
# example: ./scripts/test.sh --integration

# Load environment variables if .env file exists
if [ -f "../.env" ]; then
    source "../.env"
elif [ -f ".env" ]; then
    source ".env"
fi

# Set default variables
COVERAGE=true
VERBOSE=false
FAIL_FAST=false
RUN_INTEGRATION=false

# Process command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-coverage)
      COVERAGE=false
      shift
      ;;
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    --fail-fast|-f)
      FAIL_FAST=true
      shift
      ;;
    --integration|-i)
      RUN_INTEGRATION=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./test.sh [--no-coverage] [--verbose|-v] [--fail-fast|-f] [--integration|-i]"
      exit 1
      ;;
  esac
done

# Build the command
CMD="python -m pytest"

if [ "$COVERAGE" = true ]; then
  CMD="$CMD --cov=src"
fi

if [ "$VERBOSE" = true ]; then
  CMD="$CMD -v"
fi

if [ "$FAIL_FAST" = true ]; then
  CMD="$CMD -x"
fi

# Add marker based on integration flag
if [ "$RUN_INTEGRATION" = false ]; then
  CMD="$CMD -m \"not integration\""
fi

# Check if GROQ_API_KEY is set when running integration tests
if [ "$RUN_INTEGRATION" = true ] && [ -z "$GROQ_API_KEY" ]; then
  echo "Error: GROQ_API_KEY must be set to run integration tests"
  echo "Please ensure you have a .env file with GROQ_API_KEY or the environment variable is set"
  exit 1
fi

# Run the tests
echo "Running tests with command: $CMD"
eval "$CMD" 