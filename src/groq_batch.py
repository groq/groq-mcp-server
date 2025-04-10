"""
Groq Batch Processing Module

This module provides functionality for batch processing using Groq's API, supporting both
JSONL file inputs and array-based inputs for better developer experience.
"""

import os
import json
import httpx
from pathlib import Path
from typing import List, Dict, Union, Optional
from dotenv import load_dotenv
from mcp.types import TextContent

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
base_path = os.getenv("BASE_OUTPUT_PATH")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is required")

# Create a custom httpx client with the Groq API key
groq_client = httpx.Client(
    base_url="https://api.groq.com/openai/v1",
    headers={
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    },
)

def create_batch_request(
    custom_id: str,
    model: str,
    messages: List[Dict[str, str]],
) -> Dict:
    """Helper function to create a batch request entry"""
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": messages
        }
    }

def upload_batch_data(requests_data: Union[str, List[Dict]]) -> Dict:
    """Upload batch data for processing, handling both file paths and request arrays"""
    headers = groq_client.headers.copy()
    headers.pop("Content-Type", None)
    
    if isinstance(requests_data, list):
        # Convert array to JSONL string in memory
        jsonl_content = "\n".join(json.dumps(request) for request in requests_data)
        
        response = httpx.post(
            "https://api.groq.com/openai/v1/files",
            headers=headers,
            files={
                "file": ("batch_requests.jsonl", jsonl_content, "application/x-jsonlines"),
                "purpose": ("", "batch")
            }
        )
    else:
        # Handle file path input
        with open(requests_data, 'rb') as f:
            response = httpx.post(
                "https://api.groq.com/openai/v1/files",
                headers=headers,
                files={
                    "file": (Path(requests_data).name, f, "application/x-jsonlines"),
                    "purpose": ("", "batch")
                }
            )
    
    if response.status_code != 200:
        raise Exception(f"Failed to upload file: {response.text}")
    
    return response.json()

def create_batch_job(
    file_id: str,
    completion_window: str = "24h"
) -> Dict:
    """Create a batch processing job"""
    response = groq_client.post(
        "/batches",
        json={
            "input_file_id": file_id,
            "endpoint": "/v1/chat/completions",
            "completion_window": completion_window
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to create batch job: {response.text}")
    
    return response.json()

def get_batch_status(batch_id: str) -> Dict:
    """Get the status of a batch job"""
    response = groq_client.get(f"/batches/{batch_id}")
    
    if response.status_code != 200:
        raise Exception(f"Failed to get batch status: {response.text}")
    
    return response.json()

def get_batch_results(file_id: str, output_path: Optional[str] = None) -> Union[str, TextContent]:
    """
    Retrieve batch results
    
    Args:
        file_id: The output file ID from the completed batch
        output_path: Optional path to save results
    
    Returns:
        Either a path to the saved results file or TextContent with the results
    """
    try:
        # Get the content
        response = groq_client.get(f"/files/{file_id}/content")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get batch results: {response.text}")

        # If output path is provided, try to save to file
        if output_path:
            try:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return str(output_path)
            except (OSError, PermissionError) as e:
                # If file save fails, return content as text
                return TextContent(
                    type="text",
                    text=f"Could not save to {output_path}, but here's the content:\n\n{response.text}"
                )
        
        # If no output path, just return the content
        return TextContent(
            type="text",
            text=response.text
        )
            
    except Exception as e:
        return TextContent(
            type="text",
            text=f"Error retrieving batch results: {str(e)}"
        )

def process_batch(
    requests: Union[str, List[Dict]],
    completion_window: str = "24h",
    output_path: Optional[str] = None
) -> TextContent:
    """
    Process a batch of requests, supporting both JSONL files and arrays
    
    Args:
        requests: Either a path to a JSONL file or a list of request dictionaries
        completion_window: Time window for batch completion (24h to 7d)
        output_path: Optional path to save results
    
    Returns:
        TextContent with batch processing information
    """
    # Upload data directly
    file_obj = upload_batch_data(requests)
    file_id = file_obj["id"]
    
    # Create batch job
    batch_job = create_batch_job(file_id, completion_window)
    batch_id = batch_job["id"]
    
    return TextContent(
        type="text",
        text=f"Batch job created successfully!\n"
             f"Batch ID: {batch_id}\n"
             f"Status: {batch_job['status']}\n"
             f"Monitor status using get_batch_status('{batch_id}')"
    )

def list_batches() -> Dict:
    """List all batch jobs"""
    response = groq_client.get("/batches")
    
    if response.status_code != 200:
        raise Exception(f"Failed to list batches: {response.text}")
    
    return response.json()

def format_batch_info(batch: Dict) -> str:
    """Helper to format batch information for display"""
    status = batch['status']
    created = batch['created_at']
    completed = batch.get('completed_at', 'Not completed')
    counts = batch['request_counts']
    
    return (
        f"Batch ID: {batch['id']}\n"
        f"Status: {status}\n"
        f"Requests: {counts['completed']}/{counts['total']} completed\n"
        f"Created: {created}\n"
        f"Completed: {completed}\n"
        f"{'Output File: ' + batch['output_file_id'] if batch.get('output_file_id') else ''}\n"
        f"{'Error File: ' + batch['error_file_id'] if batch.get('error_file_id') else ''}\n"
        "---"
    )

def list_batches_formatted() -> TextContent:
    """List all batch jobs with formatted output"""
    batches = list_batches()
    
    if not batches.get('data'):
        return TextContent(
            type="text",
            text="No batch jobs found."
        )
    
    batch_info = [format_batch_info(batch) for batch in batches['data']]
    
    return TextContent(
        type="text",
        text="Active Batch Jobs:\n\n" + "\n\n".join(batch_info)
    )