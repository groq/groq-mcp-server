import os
import httpx
from typing import Literal, Optional, List, Dict, Union
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context, Image
from mcp.types import TextContent
from src.utils import play_audio as core_play_audio

# Import the pure TTS functions
from src.groq_tts import (
  text_to_speech as core_text_to_speech,
  list_voices as run_list_voices
)

# Import the pure STT functions
from src.groq_stt import (
  transcribe_audio as core_transcribe_audio,
  translate_audio as core_translate_audio,
  list_stt_models as core_list_stt_models
)

# Import the vision functions and models
from src.groq_vision import (
    analyze_image as core_analyze_image,
    analyze_image_json as core_analyze_image_json,
    VISION_MODELS,
    DEFAULT_MODEL
)

# Import the TTT functions
from src.groq_ttt import (
    chat_completion as core_chat_completion,
    list_chat_models as core_list_chat_models
)

from src.groq_docs import (
    get_groq_full_docs,
    get_groq_short_docs
)

# Import the batch functions
from src.groq_batch import (
    process_batch,
    get_batch_status,
    get_batch_results,
    list_batches_formatted
)

# Import the compound functions
from src.groq_compound import (
    compound_chat as core_compound_chat,
    compound_chat_stream as core_compound_chat_stream
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

# Create an MCP server
mcp = FastMCP("groq-mcp")



# TTS wrapper with MCP decoration
@mcp.tool(
    description="""Convert text to speech using Groq's TTS model and save the output audio file to a given directory.
    Directory is optional, if not provided, the output file will be saved to $HOME/Desktop.
    
    ⚠️ COST WARNING: This tool makes an API call to Groq which may incur costs. Only use when explicitly requested by the user.

    Args:
        text: The text to convert to speech (maximum 10,000 characters)
        voice: The voice to use for the audio generation
        model: The TTS model to use ("playai-tts" for English, "playai-tts-arabic" for Arabic)
        output_directory: Directory where files should be saved (defaults to $HOME/Desktop if not provided)

    Returns:
        Text content with the path to the output file and the voice used.
    """
)
def text_to_speech(
    text: str,
    voice: str = "Arista-PlayAI",
    model: Literal["playai-tts", "playai-tts-arabic"] = "playai-tts",
    output_directory: str | None = None,
) -> TextContent:
    # Call the core function from the imported module
    result = core_text_to_speech(text, voice, model, output_directory)
    return result  # The core function already returns TextContent


# Voice listing wrapper with MCP decoration
@mcp.tool(
    description="""List all available voices for Groq's TTS models.
    
    Args:
        model: Specify which model's voices to list ("playai-tts" for English, "playai-tts-arabic" for Arabic, or "all" for both)
        
    Returns:
        Text content with the list of available voices.
    """
)
def list_voices(
    model: Literal["playai-tts", "playai-tts-arabic", "all"] = "all"
) -> TextContent:
    # Call the core function from the imported module and return the TextContent object directly
    return run_list_voices(model)


@mcp.tool(
    description="""Transcribe speech from an audio file using Groq's speech-to-text API and save the output text file to a given directory.
    Directory is optional, if not provided, the output file will be saved to the configured base output path.
    
    ⚠️ COST WARNING: This tool makes an API call to Groq which may incur costs. Only use when explicitly requested by the user.

    Args:
        input_file_path: Path to the audio file to transcribe
        model: The model to use for transcription
        language: ISO-639-1 language code (e.g., "en" for English)
        response_format: Format of the response
        prompt: Optional prompt to guide the model's style or specify how to spell unfamiliar words
        timestamp_granularities: Level of detail for timestamps
        temperature: Controls randomness in the model's output (0.0 recommended for STT)
        output_directory: Directory where files should be saved
        save_to_file: Whether to save the transcript to a file
        
    Returns:
        Text content with the transcription or path to the output file
    """
)
def transcribe_audio(
    input_file_path: str,
    model: str = "whisper-large-v3-turbo",
    language: Optional[str] = None,
    response_format: Literal["json", "verbose_json", "text"] = "verbose_json",
    prompt: Optional[str] = None,
    timestamp_granularities: List[Literal["segment", "word"]] = ["segment"],
    temperature: float = 0.0,
    output_directory: Optional[str] = None,
    save_to_file: bool = True,
) -> TextContent:
    return core_transcribe_audio(
        input_file_path=input_file_path,
        model=model,
        language=language,
        response_format=response_format,
        prompt=prompt,
        timestamp_granularities=timestamp_granularities,
        temperature=temperature,
        output_directory=output_directory,
        save_to_file=save_to_file
    )

@mcp.tool(
    description="""Translate speech from an audio file to English text using Groq's speech-to-text API and save the output text file to a given directory.
    Directory is optional, if not provided, the output file will be saved to the configured base output path.
    
    ⚠️ COST WARNING: This tool makes an API call to Groq which may incur costs. Only use when explicitly requested by the user.

    Args:
        input_file_path: Path to the audio file to translate
        model: The model to use for translation (only whisper-large-v3 supports translation)
        response_format: Format of the response
        prompt: Optional prompt to guide the model's style or specify how to spell unfamiliar words
        temperature: Controls randomness in the model's output (0.0 recommended for translation)
        output_directory: Directory where files should be saved
        save_to_file: Whether to save the translation to a file
        
    Returns:
        Text content with the translation or path to the output file
    """
)
def translate_audio(
    input_file_path: str,
    model: str = "whisper-large-v3",
    response_format: Literal["json", "text"] = "json",
    prompt: Optional[str] = None,
    temperature: float = 0.0,
    output_directory: Optional[str] = None,
    save_to_file: bool = True,
) -> TextContent:
    return core_translate_audio(
        input_file_path=input_file_path,
        model=model,
        response_format=response_format,
        prompt=prompt,
        temperature=temperature,
        output_directory=output_directory,
        save_to_file=save_to_file
    )

@mcp.tool(
    description="""List all available models for Groq's STT service.
        
    Returns:
        Text content with the list of available models and their details.
    """
)
def list_stt_models() -> TextContent:
    return core_list_stt_models()

@mcp.tool(
    description="""Analyze an image using Groq's vision API with either Scout (default) or Maverick model and generate descriptive text.
    
    ⚠️ COST WARNING: This tool makes an API call to Groq which may incur costs. Only use when explicitly requested by the user.

    Args:
        image: Path to the image file to analyze, a resource reference from the client (e.g. file upload, clipboard, etc), base64-encoded image data, or raw image buffer
        prompt: Text prompt describing what you want to know about the image (e.g., "What's in this image?")
        model: Which model to use ("scout" for a smaller Scout 17B*16experts model (default) or "maverick" for a larger Maverick 17B*128experts model)
        temperature: Controls randomness in the model's output (0.0-1.0)
        max_tokens: Maximum number of tokens to generate in the response
        output_directory: Optional directory to save output file (only used if save_to_file is True)
        save_to_file: Whether to save the description to a file (defaults to False)
        ctx: (optional) MCP Context for resource access and progress reporting
        return_image: If True, return the image as a FastMCP Image object (default False)
    Returns:
        Text content with the direct image description, or FastMCP Image if return_image is True, or path to output file if save_to_file is True
    """
)
def analyze_image(
    image: str,
    prompt: str = "What's in this image?",
    model: Literal["scout", "maverick"] = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    output_directory: Optional[str] = None,
    save_to_file: bool = False,
    ctx: Context = None,
    return_image: bool = False,
) -> Union[TextContent, Image]:
    """
    Supports file paths, client-uploaded images/resources via ctx.read_resource(),
    base64-encoded image data, and raw image buffers.
    If return_image is True, returns a FastMCP Image object (for downstream use).
    """
    import os
    # Skip validation for base64 data since we now handle it in _prepare_image_content
    
    img_data = None
    if ctx is not None and isinstance(image, str) and image.startswith("resource://"):
        # Client resource (uploaded/clipboard image)
        img_data, mime_type = ctx.read_resource(image) if not hasattr(ctx, 'read_resource') or not callable(ctx.read_resource) else None
        if img_data is None:
            img_data, mime_type = ctx.read_resource(image)
        input_source = img_data
    else:
        # Handle file paths and base64/buffer data
        if isinstance(image, str) and image.startswith("~"):
            # Expand ~ to home directory if present
            input_source = os.path.expanduser(image)
        else:
            input_source = image
            
    result = core_analyze_image(
        input_source=input_source,
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        output_directory=output_directory,
        save_to_file=save_to_file
    )
    if return_image and img_data is not None:
        return Image(data=img_data, format=mime_type.split("/")[-1] if mime_type else "png")
    return result

@mcp.tool(
    description="""Analyze an image using Groq's vision API with either Scout (default) or Maverick model and generate a structured JSON response.
    
    ⚠️ COST WARNING: This tool makes an API call to Groq which may incur costs. Only use when explicitly requested by the user.

    Args:
        image: Path to the image file to analyze, a resource reference from the client (e.g. file upload, clipboard, etc), base64-encoded image data, or raw image buffer
        prompt: Text prompt describing what you want to know about the image (e.g., "Extract key information from this image as JSON")
        model: Which model to use ("scout" for Scout 17B or "maverick" for Maverick 17B)
        temperature: Controls randomness in the model's output (0.0-1.0)
        max_tokens: Maximum number of tokens to generate in the response
        output_directory: Optional directory to save output file (only used if save_to_file is True)
        save_to_file: Whether to save the JSON response to a file (defaults to False)
        ctx: (optional) MCP Context for resource access and progress reporting
        return_image: If True, return the image as a FastMCP Image object (default False)
    Returns:
        Text content with the direct JSON response, or FastMCP Image if return_image is True, or path to output file if save_to_file is True
    """
)
def analyze_image_json(
    image: str,
    prompt: str = "Extract key information from this image as JSON",
    model: Literal["scout", "maverick"] = DEFAULT_MODEL,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    output_directory: Optional[str] = None,
    save_to_file: bool = False,
    ctx: Context = None,
    return_image: bool = False,
) -> Union[TextContent, Image]:
    """
    Supports file paths, client-uploaded images/resources via ctx.read_resource(),
    base64-encoded image data, and raw image buffers.
    If return_image is True, returns a FastMCP Image object (for downstream use).
    """
    import os
    # Skip validation for base64 data since we now handle it in _prepare_image_content
    
    img_data = None
    if ctx is not None and isinstance(image, str) and image.startswith("resource://"):
        # Client resource (uploaded/clipboard image)
        img_data, mime_type = ctx.read_resource(image) if not hasattr(ctx, 'read_resource') or not callable(ctx.read_resource) else None
        if img_data is None:
            img_data, mime_type = ctx.read_resource(image)
        input_source = img_data
    else:
        # Handle file paths and base64/buffer data
        if isinstance(image, str) and image.startswith("~"):
            # Expand ~ to home directory if present
            input_source = os.path.expanduser(image)
        else:
            input_source = image
            
    result = core_analyze_image_json(
        input_source=input_source,
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        output_directory=output_directory,
        save_to_file=save_to_file
    )
    if return_image and img_data is not None:
        return Image(data=img_data, format=mime_type.split("/")[-1] if mime_type else "png")
    return result

@mcp.tool(
    description="""Generate a chat completion using Groq's API.
    
    ⚠️ COST WARNING: This tool makes an API call to Groq which may incur costs. Only use when explicitly requested by the user.

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
        output_directory: Optional directory to save output file (only used if save_to_file is True)
        save_to_file: Whether to save the response to a file (defaults to False)
        
    Returns:
        Text content with the direct completion response, or path to output file if save_to_file is True
    """
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
    save_to_file: bool = False,
) -> TextContent:
    return core_chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        response_format=response_format,
        seed=seed,
        output_directory=output_directory,
        save_to_file=save_to_file
    )

@mcp.tool(
    description="""List all available models for Groq's chat completion service.
        
    Returns:
        Text content with the list of available models and their details.
    """
)
def list_chat_models() -> TextContent:
    return core_list_chat_models()


@mcp.tool(
    description="""Play an audio file using the system's audio output.
    Supports WAV and other common audio formats.
    
    Args:
        input_file_path: Path to the audio file to play
        
    Returns:
        Text content with success message
    """
)
def play_audio(input_file_path: str) -> TextContent:
    return core_play_audio(input_file_path)


@mcp.tool(
    description="""Fetch and return the complete Groq LLM documentation.
    This documentation provides detailed information about Groq's language models,
    their capabilities, parameters, and best practices for building with them.
    
    Returns:
        Text content containing the full Groq documentation, useful for understanding
        model capabilities and building applications.
    """
)
def get_groq_documentation_full() -> TextContent:
    return get_groq_full_docs()

@mcp.tool(
    description="""Fetch and return the concise summary of Groq LLM documentation.
    This provides a quick overview of Groq's language models and their key features.
    Ideal for quick reference and understanding basic model capabilities.
    
    Returns:
        Text content containing the summarized Groq documentation, perfect for
        quick lookups and basic understanding of model capabilities.
    """
)
def get_groq_documentation_summary() -> TextContent:
    return get_groq_short_docs()

@mcp.tool(
    description="""Process a batch of requests using Groq's Batch API.
    Supports both JSONL files and arrays of requests.
    Batch processing offers 25% lower cost (50% off until April 2025) and higher rate limits.
    
    ⚠️ COST WARNING: This tool makes API calls to Groq which may incur costs.
    
    Args:
        requests: Either a path to a JSONL file or a list of request dictionaries
        completion_window: Time window for batch completion (e.g., "24h" or "7d")
        output_path: Optional path to save results
        
    Returns:
        Text content with batch job information and status
    """
)
def batch_process(
    requests: Union[str, List[Dict]],
    completion_window: str = "24h",
    output_path: Optional[str] = None
) -> TextContent:
    return process_batch(
        requests=requests,
        completion_window=completion_window,
        output_path=output_path
    )

@mcp.tool(
    description="""Check the status of a Groq batch processing job.
    Returns detailed information about the job's progress, including:
    - Status (validating/in_progress/completed/failed/expired)
    - Request counts (total/completed/failed)
    - File IDs for output and errors
    - Timestamps for various stages
    
    Args:
        batch_id: The ID of the batch job to check
        
    Returns:
        Text content with detailed batch status information
    """
)
def batch_status(batch_id: str) -> TextContent:
    status = get_batch_status(batch_id)
    return TextContent(
        type="text",
        text=f"Batch Status for {batch_id}:\n" + 
             f"Status: {status['status']}\n" +
             f"Requests: {status['request_counts']['completed']}/{status['request_counts']['total']} completed\n" +
             (f"Output File: {status['output_file_id']}\n" if status.get('output_file_id') else "") +
             (f"Error File: {status['error_file_id']}\n" if status.get('error_file_id') else "") +
             f"Created: {status['created_at']}\n" +
             (f"Completed: {status['completed_at']}" if status.get('completed_at') else "Not completed yet")
    )

@mcp.tool(
    description="""Retrieve results from a completed Groq batch job.
    Downloads and saves the results to a JSONL file.
    If saving to file fails, returns the content directly.
    
    Args:
        file_id: The output file ID from the completed batch
        output_path: Optional custom path to save results
        
    Returns:
        Text content with either the path to the saved results file or the actual content
    """
)
def batch_results(
    file_id: str,
    output_path: Optional[str] = None
) -> TextContent:
    result = get_batch_results(file_id, output_path)
    
    # If get_batch_results returned a TextContent object, it means it couldn't save to file
    if isinstance(result, TextContent):
        return result
    
    # Otherwise it returned a path string
    return TextContent(
        type="text",
        text=f"Batch results saved to: {result}"
    )

@mcp.tool(
    description="""List all active Groq batch processing jobs.
    Useful when you need to check all running batches or find a specific batch ID.
    Shows detailed information for each batch including:
    - Batch ID
    - Status
    - Request counts
    - Creation and completion times
    - Output and error file IDs
    
    Returns:
        Text content with a formatted list of all batch jobs
    """
)
def list_batches() -> TextContent:
    return list_batches_formatted()


@mcp.tool(
    description="""Use Groq's Compound-Beta API for advanced AI tasks involving web search and code execution.
    This tool is specifically designed for tasks that require real-time information lookup or code manipulation.
    It can autonomously:
    1. Search the web for current information
    2. Write and execute code
    3. Combine multiple tools to solve complex problems

    FOR ANY COMPLEX TASK, USE THIS TOOL. INCLUDING: WEB SEARCH, CODE EXECUTION, INTERNET SEARCH LIKE BITCOIN PRICES OR WEATHER LOOKUPS.
    
    ⚠️ COST WARNING: This tool makes API calls to Groq which may incur costs. Only use when explicitly requested by the user.
    
    The tool supports three models:
    - compound-beta-mini: Fastest, limited to one tool use (default)
    - compound-beta: Balanced performance with multiple tool uses
    - compound-beta-deep: Most thorough analysis with extensive tool use
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The compound model to use
        output_directory: Directory to save output (if save_to_file is True)
        save_to_file: Whether to save the response to a file
        
    Returns:
        Text content with the AI response, including any tool executions performed
    """
)
def compound_tool(
    messages: List[Dict[str, str]],
    model: str = "compound-beta-mini",
    output_directory: Optional[str] = None,
    save_to_file: bool = False,  # Default to False since we want to return content to client
) -> TextContent:
    return core_compound_chat(
        messages=messages,
        model=model,
        stream=False,  # Always use non-streaming mode
        output_directory=output_directory,
        save_to_file=save_to_file
    )


def main():
    print("Starting Groq TTS server")
    mcp.run()

if __name__ == "__main__":
    main()