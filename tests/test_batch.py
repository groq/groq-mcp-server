import os
import json
from pathlib import Path
from src.groq_batch import process_batch, get_batch_status, get_batch_results

# Example requests
test_requests = [
    {
        "custom_id": "request-1",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is 2+2?"}
            ]
        }
    },
    {
        "custom_id": "request-2",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ]
        }
    }
]

def test_array_input():
    """Test batch processing with array input"""
    print("Testing batch processing with array input...")
    result = process_batch(test_requests)
    print(result.text)
    return result

def test_jsonl_input():
    """Test batch processing with JSONL file input"""
    # Create test JSONL file
    test_file = Path("tests/test_batch.jsonl")
    with open(test_file, 'w') as f:
        for request in test_requests:
            f.write(json.dumps(request) + '\n')
    
    print("\nTesting batch processing with JSONL input...")
    result = process_batch(str(test_file))
    print(result.text)
    return result

if __name__ == "__main__":
    # Test array input
    array_result = test_array_input()
    
    # Test JSONL input
    jsonl_result = test_jsonl_input()