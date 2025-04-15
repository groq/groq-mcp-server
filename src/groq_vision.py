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
    MCPError
)
from datetime import datetime

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
VISION_MODELS = {
    "scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    "maverick": "meta-llama/llama-4-maverick-17b-128e-instruct"
}
DEFAULT_MODEL = "scout"

# Helper function to encode image bytes or read from path/URL
def _prepare_image_content(input_source: Union[str, bytes]) -> tuple[str, str]:
    """
    Prepares image content for the API (base64 encoding) and determines a filename.

    Args:
        input_source: Either a file path (str), URL (str), base64 string, or image bytes.

    Returns:
        Tuple: (base64_encoded_image, filename)
    """
    if isinstance(input_source, bytes):
        # Input is raw bytes
        try:
            base64_image = base64.b64encode(input_source).decode('utf-8')
            # TODO: Infer mime type properly if possible? Defaulting to jpeg for now.
            filename = f"uploaded_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}" 
            return f"data:image/jpeg;base64,{base64_image}", filename
        except Exception as e:
            make_error(f"Error encoding provided image bytes: {str(e)}")
            
    elif isinstance(input_source, str):
        # Check if input is already a base64 data URI
        if input_source.startswith('data:image/'):
            try:
                # Extract mime type and filename
                mime_type = input_source.split(';')[0].split(':')[1]
                extension = mime_type.split('/')[1]
                filename = f"base64_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
                return input_source, filename
            except Exception as e:
                make_error(f"Error processing base64 data URI: {str(e)}")
                
        # Check if input is a raw base64 string (without data URI prefix)
        elif len(input_source) > 100 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in input_source):
            try:
                # Default to JPEG for raw base64 strings
                filename = f"base64_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpeg"
                return f"data:image/jpeg;base64,{input_source}", filename
            except Exception as e:
                make_error(f"Error processing base64 string: {str(e)}")
                
        # Input is a URL
        elif input_source.startswith(('http://', 'https://')):
            # Return URL directly, API handles fetching
            filename = Path(input_source.split('?')[0]).name
            return input_source, filename # Return URL itself, not base64 data
            
        # Input is a file path
        else:
            # Handle local file path
            file_path = handle_input_file(input_source, image_content_check=True)
            try:
                with open(file_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                # TODO: Infer mime type from file extension? Defaulting to jpeg.
                mime_type = "image/jpeg" # Basic default
                if file_path.suffix.lower() == ".png":
                    mime_type = "image/png"
                elif file_path.suffix.lower() == ".gif":
                    mime_type = "image/gif"
                elif file_path.suffix.lower() == ".webp":
                    mime_type = "image/webp"
                elif file_path.suffix.lower() == ".bmp":
                    mime_type = "image/bmp"
                    
                return f"data:{mime_type};base64,{base64_image}", file_path.name
            except Exception as e:
                make_error(f"Error reading or encoding image file {file_path}: {str(e)}")
    else:
        make_error("Invalid input source type for image analysis.")

def analyze_image(
    input_source: Union[str, bytes],
    prompt: str = "What's in this image?",
    model: Literal["scout", "maverick"] = DEFAULT_MODEL,
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
    
    # Validate and get model
    if model not in VISION_MODELS:
        make_error(f"Invalid model. Must be one of: {', '.join(VISION_MODELS.keys())}")
    model_name = VISION_MODELS[model]

    # Prepare image data (handles path, URL, or bytes)
    try:
        image_url_data, file_name = _prepare_image_content(input_source)
    except Exception as e:
        make_error(f"Failed to prepare image content: {str(e)}")

    # Construct payload content
    content = [
        {"type": "text", "text": prompt}
    ]
    
    # Add the image data (either URL or base64 data URI)
    content.append({
        "type": "image_url",
        "image_url": {
            "url": image_url_data
        }
    })

    # Prepare the request payload
    payload = {
        "model": model_name,
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
            text=f"Success. Image analysis saved as: {output_file_path}\nModel used: {model_name}"
        )
    else:
        return TextContent(
            type="text",
            text=description
        )

def analyze_image_json(
    input_source: Union[str, bytes],
    prompt: str = "Extract key information from this image as JSON",
    model: Literal["scout", "maverick"] = DEFAULT_MODEL,
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
    
    # Validate and get model
    if model not in VISION_MODELS:
        make_error(f"Invalid model. Must be one of: {', '.join(VISION_MODELS.keys())}")
    model_name = VISION_MODELS[model]
    
    # Prepare image data (handles path, URL, or bytes)
    try:
        image_url_data, file_name = _prepare_image_content(input_source)
    except Exception as e:
        make_error(f"Failed to prepare image content: {str(e)}")

    # Construct payload content
    content = [
        {"type": "text", "text": prompt}
    ]

    # Add the image data (either URL or base64 data URI)
    content.append({
        "type": "image_url",
        "image_url": {
            "url": image_url_data
        }
    })

    # Prepare the request payload
    payload = {
        "model": model_name,
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
        output_file_path = make_output_file("groq-vision-json", file_name, output_path, "json")
        
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file_path, "w") as f:
            f.write(json_response)
        
        return TextContent(
            type="text",
            text=f"Success. JSON analysis saved as: {output_file_path}\nModel used: {model_name}"
        )
    else:
        return TextContent(
            type="text",
            text=json_response
        ) 
