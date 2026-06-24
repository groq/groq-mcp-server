"""
Groq Text-to-Text (Chat) Module

⚠️ IMPORTANT: This module provides access to Groq API endpoints which may incur costs.
Each function that makes an API call is marked with a cost warning.

1. Only use functions when explicitly requested by the user
2. For chat functions, consider the length of the messages as it affects costs
"""

import os
import json
import httpx
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any
from dotenv import load_dotenv
from mcp.types import TextContent
from src.utils import (
    make_error,
    make_output_path,
    make_output_file,
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
)

def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7,
    max_completion_tokens: Optional[int] = None,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    response_format: Optional[Dict[str, str]] = None,
    seed: Optional[int] = None,
    output_directory: Optional[str] = None,
    save_to_file: bool = True,
) -> TextContent:
    """
    Generate a chat completion using Groq's API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The model to use for completion
        temperature: Controls randomness (0.0-2.0)
        max_completion_tokens: Maximum tokens to generate
        top_p: Alternative to temperature for nucleus sampling
        frequency_penalty: Penalize frequent tokens (-2.0 to 2.0)
        presence_penalty: Penalize tokens based on presence (-2.0 to 2.0)
        response_format: Optional format specification (e.g., {"type": "json_object"})
        seed: Optional seed for deterministic results
        output_directory: Directory to save output (if save_to_file is True)
        save_to_file: Whether to save the response to a file
    
    Returns:
        TextContent object with the completion or file path
    """
    # ponytail: no local model whitelist — Groq's /chat/completions is the source of
    # truth and returns a clear error for unknown models. A hardcoded list only drifts.
    # Validate temperature
    if not 0.0 <= temperature <= 2.0:
        make_error("Temperature must be between 0.0 and 2.0")
    
    # Validate penalties
    if not -2.0 <= frequency_penalty <= 2.0:
        make_error("Frequency penalty must be between -2.0 and 2.0")
    if not -2.0 <= presence_penalty <= 2.0:
        make_error("Presence penalty must be between -2.0 and 2.0")
    
    # Validate messages
    if not messages:
        make_error("Messages list cannot be empty")
    for msg in messages:
        if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
            make_error("Each message must be a dictionary with 'role' and 'content' keys")
        if msg.get('role') not in {'system', 'user', 'assistant', 'tool'}:
            make_error(f"Invalid message role: {msg.get('role')}")
    
    # Prepare the request payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "stream": False
    }
    
    # Add optional parameters
    if max_completion_tokens is not None:
        payload["max_completion_tokens"] = max_completion_tokens
    if response_format is not None:
        payload["response_format"] = response_format
    if seed is not None:
        payload["seed"] = seed
    
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
    try:
        response_data = response.json()
        completion = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not completion:
            make_error("No completion was generated")
        
        # Save to file if requested
        if save_to_file:
            output_path = make_output_path(output_directory, base_path)
            # Use the first few words of the first message as part of the filename
            first_msg = messages[0]["content"][:30] if messages else "chat"
            output_file_path = make_output_file("groq-chat", first_msg, output_path, "txt")
            
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file_path, "w") as f:
                f.write(completion)
            
            # Also save the full response for reference
            json_file_path = make_output_file("groq-chat-full", first_msg, output_path, "json")
            with open(json_file_path, "w") as f:
                json.dump(response_data, f, indent=2)
            
            return TextContent(
                type="text",
                text=f"Success. Chat completion saved as: {output_file_path}\nModel used: {model}"
            )
        else:
            return TextContent(
                type="text",
                text=completion
            )
            
    except Exception as e:
        make_error(f"Error processing response: {str(e)}")

def list_chat_models() -> TextContent:
    """List models actually available to this account from Groq's /models endpoint."""
    try:
        response = groq_client.get("/models")
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        make_error(f"Groq API error listing models: HTTP {e.response.status_code}")
    except Exception as e:
        make_error(f"Error calling Groq API: {str(e)}")

    models = sorted(response.json().get("data", []), key=lambda m: m.get("id", ""))
    if not models:
        make_error("No models returned by Groq")

    lines = []
    for m in models:
        ctx = m.get("context_window")
        ctx_str = f"{ctx:,} tokens" if isinstance(ctx, int) else "n/a"
        lines.append(
            f"Model: {m.get('id')}\n"
            f"  Owned By: {m.get('owned_by', 'n/a')}\n"
            f"  Context Length: {ctx_str}\n"
            f"  Active: {m.get('active', 'n/a')}"
        )

    return TextContent(
        type="text",
        text=f"Available Groq Models ({len(models)}):\n\n" + "\n\n".join(lines)
    )