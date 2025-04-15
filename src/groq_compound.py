"""
Groq Compound-Beta Module

⚠️ IMPORTANT: This module provides access to Groq API endpoints which may incur costs.
Each function that makes an API call is marked with a cost warning.

1. Only use functions when explicitly requested by the user
2. For compound functions, consider the length of messages as it affects costs
"""

import os
import json
import httpx
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

# Create a custom httpx client with the Groq API key and increased timeouts
groq_client = httpx.Client(
    base_url="https://api.groq.com/openai/v1",
    headers={
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    },
    timeout=httpx.Timeout(60.0, read=300.0)  # 60s connect timeout, 300s read timeout
)

# Define available models
COMPOUND_MODELS = [
    "compound-beta",  # Default system using deepseek-r1-distill-llama-70b
    "compound-beta-mini",  # Mini version limited to one tool use
    "compound-beta-deep",  # Uses qwen-2.5-32b for core reasoning
]

def handle_stream_line(line: str, full_content: str, executed_tools: list, current_tool: Optional[dict]) -> tuple[str, list, Optional[dict]]:
    """Helper function to handle a single stream line"""
    if not line or line.startswith(":"):
        return full_content, executed_tools, current_tool
        
    if line.startswith("data: "):
        try:
            data = json.loads(line[6:])  # Skip "data: " prefix
            if "choices" in data:
                delta = data["choices"][0].get("delta", {})
                
                # Handle content
                if "content" in delta:
                    content = delta["content"]
                    print(content, end="", flush=True)
                    full_content += content
                
                # Handle reasoning
                if "reasoning" in delta:
                    reasoning = delta["reasoning"]
                    print(reasoning, end="", flush=True)
                    full_content += reasoning
                
                # Handle executed tools
                if "executed_tools" in delta:
                    tools = delta["executed_tools"]
                    for tool in tools:
                        if current_tool and "output" in tool:
                            # Update existing tool with output
                            current_tool.update(tool)
                            executed_tools.append(current_tool)
                            current_tool = None
                            print(f"\nTool output received: {tool['output']}\n", flush=True)
                        else:
                            # New tool execution started
                            current_tool = tool
                            print(f"\nExecuting tool: {tool['type']} with args: {tool['arguments']}\n", flush=True)
                            
        except json.JSONDecodeError:
            pass  # Skip invalid JSON lines
            
    return full_content, executed_tools, current_tool

def compound_chat(
    messages: List[Dict[str, str]],
    model: str = "compound-beta",
    stream: bool = False,
    output_directory: Optional[str] = None,
    save_to_file: bool = True,
) -> TextContent:
    """
    Send a chat request to Groq's Compound-Beta API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The compound model to use (compound-beta, compound-beta-mini, or compound-beta-deep)
        stream: Whether to stream the response
        output_directory: Optional directory to save output files
        save_to_file: Whether to save the response to a file
        
    Returns:
        TextContent object containing the response
    """
    # Validate model
    if model not in COMPOUND_MODELS:
        make_error(f"Model '{model}' not found. Available models are: {', '.join(COMPOUND_MODELS)}")
    
    # Validate messages format
    for msg in messages:
        if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
            make_error("Each message must be a dictionary with 'role' and 'content' keys")
    
    # Prepare the request payload
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream
    }
    
    try:
        # Create a client with appropriate timeout for streaming
        timeout = httpx.Timeout(60.0, read=300.0) if stream else httpx.Timeout(60.0)
        
        with httpx.Client(
            base_url="https://api.groq.com/openai/v1",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream" if stream else "application/json"
            },
            timeout=timeout
        ) as client:
            
            if stream:
                with client.stream("POST", "/chat/completions", json=payload) as response:
                    response.raise_for_status()
                    
                    # Handle streaming response
                    full_content = ""
                    executed_tools = []
                    current_tool = None
                    
                    try:
                        for line in response.iter_lines():
                            if not line or line.startswith(":"):
                                continue
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])  # Skip "data: " prefix
                                    if "choices" in data:
                                        delta = data["choices"][0].get("delta", {})
                                        
                                        # Handle content
                                        if "content" in delta:
                                            content = delta["content"]
                                            print(content, end="", flush=True)
                                            full_content += content
                                        
                                        # Handle reasoning
                                        if "reasoning" in delta:
                                            reasoning = delta["reasoning"]
                                            print(reasoning, end="", flush=True)
                                            full_content += reasoning
                                        
                                        # Handle executed tools
                                        if "executed_tools" in delta:
                                            tools = delta["executed_tools"]
                                            for tool in tools:
                                                if current_tool and "output" in tool:
                                                    # Update existing tool with output
                                                    current_tool.update(tool)
                                                    executed_tools.append(current_tool)
                                                    current_tool = None
                                                    print(f"\nTool output received: {tool['output']}\n", flush=True)
                                                else:
                                                    # New tool execution started
                                                    current_tool = tool
                                                    print(f"\nExecuting tool: {tool['type']} with args: {tool['arguments']}\n", flush=True)
                                                
                                except json.JSONDecodeError:
                                    continue
                        
                        print("\n")  # Add newline after streaming
                        
                    except httpx.ReadTimeout:
                        # If we timeout but have content, we can still return it
                        if full_content:
                            print("\n\nStream timed out, but partial response was received.", flush=True)
                        else:
                            make_error("Stream timed out before receiving any content")
                    except Exception as e:
                        make_error(f"Error processing stream: {str(e)}")
                    
                    # Format the final response
                    response_text = full_content
                    if executed_tools:
                        response_text += "\n\nExecuted Tools:\n"
                        for tool in executed_tools:
                            response_text += f"\n- Tool {tool.get('index')}: {tool.get('type')}"
                            response_text += f"\n  Arguments: {tool.get('arguments')}"
                            if 'output' in tool:
                                response_text += f"\n  Output: {tool.get('output')}"
            else:
                # Handle non-streaming response
                response = client.post("/chat/completions", json=payload)
                response.raise_for_status()
                response_data = response.json()
                
                assistant_message = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                executed_tools = response_data.get("executed_tools", [])
                
                # Format the response text
                response_text = assistant_message
                
                # If there were executed tools, append them to the response
                if executed_tools:
                    response_text += "\n\nExecuted Tools:\n"
                    for tool in executed_tools:
                        response_text += f"\n- Tool {tool.get('index')}: {tool.get('type')}"
                        response_text += f"\n  Arguments: {tool.get('arguments')}"
                        if 'output' in tool:
                            response_text += f"\n  Output: {tool.get('output')}"
            
            # Save to file if requested
            if save_to_file:
                output_path = make_output_path(output_directory, base_path)
                output_file_path = make_output_file("groq-compound", "response", output_path, "txt")
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file_path, "w") as f:
                    f.write(response_text)
                
                if not stream:
                    # Save the full JSON response for non-streaming requests
                    json_file_path = make_output_file("groq-compound-full", "response", output_path, "json")
                    with open(json_file_path, "w") as f:
                        json.dump(response_data, f, indent=2)
                    
                    return TextContent(
                        type="text",
                        text=f"Success. Response saved as: {output_file_path}\nFull JSON response saved as: {json_file_path}\nModel used: {model}"
                    )
                
                return TextContent(
                    type="text",
                    text=f"Success. Response saved as: {output_file_path}\nModel used: {model}"
                )
            else:
                return TextContent(
                    type="text",
                    text=response_text
                )
                    
    except httpx.HTTPStatusError as e:
        try:
            error_data = e.json()
            error_message = error_data.get("error", {}).get("message", f"HTTP Error: {e.response.status_code}")
        except Exception:
            error_message = f"HTTP Error: {e.response.status_code}"
        make_error(f"Groq API error: {error_message}")
    except httpx.ReadTimeout:
        make_error("Request timed out. For streaming responses, consider using the non-streaming version or try again.")
    except Exception as e:
        make_error(f"Error calling Groq API: {str(e)}")

def compound_chat_stream(
    messages: List[Dict[str, str]],
    model: str = "compound-beta",
    output_directory: Optional[str] = None,
    save_to_file: bool = True,
) -> TextContent:
    """
    Send a streaming chat request to Groq's Compound-Beta API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The compound model to use (compound-beta, compound-beta-mini, or compound-beta-deep)
        output_directory: Optional directory to save output files
        save_to_file: Whether to save the response to a file
        
    Returns:
        TextContent object containing the response
    """
    return compound_chat(
        messages=messages,
        model=model,
        stream=True,
        output_directory=output_directory,
        save_to_file=save_to_file
    )