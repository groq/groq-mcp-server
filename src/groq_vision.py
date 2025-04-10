"""
Groq Vision Module

⚠️ IMPORTANT: This module provides access to Groq API endpoints which may incur costs.
Each function that makes an API call is marked with a cost warning.

1. Only use functions when explicitly requested by the user
2. For functions that process images, consider the size of the image as it affects costs
"""

import os
import json
import base64
import httpx
from pathlib import Path
from typing import Literal, Optional, List, Union, Dict, Any
from dotenv import load_dotenv
from mcp.types import TextContent
from src.utils import (
    make_error,
    make_output_path,
    make_output_file,
    handle_input_file,
)

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
    timeout=60.0,  # vision models may take longer to process
)

# Supported models
VISION_MODEL_SCOUT = "meta-llama/llama-4-scout-17b-16e-instruct"
VISION_MODEL_MAVERICK = "meta-llama/llama-4-maverick-17b-128e-instruct"
VISION_MODEL = VISION_MODEL_SCOUT  # Default to Scout

def analyze_image(
    input_file_path: str,
    prompt: str = "What's in this image?",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    output_directory: Optional[str] = None,
    save_to_file: bool = True,
) -> TextContent:
    # Validate prompt
    if not prompt or not prompt.strip():
        make_error("Prompt is required")
    
    # Validate temperature
    if temperature < 0.0 or temperature > 1.0:
        make_error("Temperature must be between 0.0 and 1.0")
    
    # Check if input is a URL
    is_url = input_file_path.startswith(('http://', 'https://'))
    
    content = [
        {"type": "text", "text": prompt}
    ]

    if is_url:
        # For URLs, use them directly
        content.append({
            "type": "image_url",
            "image_url": {
                "url": input_file_path
            }
        })
        file_name = Path(input_file_path.split('?')[0]).name  # Get filename from URL
    else:
        # Handle local files as before
        file_path = handle_input_file(input_file_path, image_content_check=True)
        try:
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
            file_name = file_path.name
        except Exception as e:
            make_error(f"Error reading or encoding image: {str(e)}")

    # Prepare the request payload
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
        "stream": False
    }

    # Make the API request
    try:
        response = groq_client.post("/chat/completions", json=payload)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        try:
            error_data = e.response.json()
            error_message = error_data.get("error", {}).get("message", f"HTTP Error: {e.response.status_code}")
        except Exception:
            error_message = f"HTTP Error: {e.response.status_code}"
        make_error(f"Groq API error: {error_message}")
    except Exception as e:
        make_error(f"Error calling Groq API: {str(e)}")
    
    # Process the response
    response_data = response.json()
    description = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    if not description:
        make_error("No description was generated")
    
    # Save the description to a file if requested
    if save_to_file:
        output_path = make_output_path(output_directory, base_path)
        output_file_path = make_output_file("groq-vision", file_name, output_path, "txt")
        
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file_path, "w") as f:
            f.write(description)
        
        # Also save the full response for reference
        json_file_path = make_output_file("groq-vision-full", file_name, output_path, "json")
        with open(json_file_path, "w") as f:
            json.dump(response_data, f, indent=2)
        
        return TextContent(
            type="text",
            text=f"Success. Image analysis saved as: {output_file_path}\nModel used: {VISION_MODEL}"
        )
    else:
        return TextContent(
            type="text",
            text=description
        )

def analyze_image_json(
    input_file_path: str,
    prompt: str = "Extract key information from this image as JSON",
    temperature: float = 0.2,
    max_tokens: int = 1024,
    output_directory: Optional[str] = None,
    save_to_file: bool = True,
) -> TextContent:
    # Validate prompt
    if not prompt or not prompt.strip():
        make_error("Prompt is required")
    
    # Validate temperature
    if temperature < 0.0 or temperature > 1.0:
        make_error("Temperature must be between 0.0 and 1.0")
    
    # Get the input file
    file_path = handle_input_file(input_file_path, image_content_check=True)
    
    # Read and encode the image
    try:
        with open(file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        make_error(f"Error reading or encoding image: {str(e)}")
    
    # Create the message content
    content = [
        {"type": "text", "text": prompt},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }
    ]

    # Prepare the request payload
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "stream": False
    }

    # Make the API request
    try:
        response = groq_client.post("/chat/completions", json=payload)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        try:
            error_data = e.response.json()
            error_message = error_data.get("error", {}).get("message", f"HTTP Error: {e.response.status_code}")
        except Exception:
            error_message = f"HTTP Error: {e.response.status_code}"
        make_error(f"Groq API error: {error_message}")
    except Exception as e:
        make_error(f"Error calling Groq API: {str(e)}")
    
    # Process the response
    response_data = response.json()
    json_response = response_data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    
    # Validate JSON response
    try:
        parsed_json = json.loads(json_response)
        json_response = json.dumps(parsed_json, indent=2)
    except json.JSONDecodeError:
        make_error("Invalid JSON response received from the model")
    
    # Save the JSON response to a file if requested
    if save_to_file:
        output_path = make_output_path(output_directory, base_path)
        output_file_path = make_output_file("groq-vision-json", file_path.name, output_path, "json")
        
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file_path, "w") as f:
            f.write(json_response)
        
        return TextContent(
            type="text",
            text=f"Success. JSON analysis saved as: {output_file_path}\nModel used: {VISION_MODEL}"
        )
    else:
        return TextContent(
            type="text",
            text=json_response
        ) 
