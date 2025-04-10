"""
Groq Speech to Text Module

⚠️ IMPORTANT: This module provides access to Groq API endpoints which may incur costs.
Each function that makes an API call is marked with a cost warning.

1. Only use functions when explicitly requested by the user
2. For functions that transcribe audio, consider the length of the audio as it affects costs
"""

import os
import json
import httpx
from pathlib import Path
from typing import Literal, Optional, List, Union
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
)

# Define available models
STT_MODELS = [
    "whisper-large-v3-turbo",  # Fast, multilingual transcription tasks
    "distil-whisper-large-v3-en",  # Fast, English-only
    "whisper-large-v3",  # High accuracy, multilingual
]

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
    # Validate model
    if model not in STT_MODELS:
        make_error(f"Model '{model}' not found. Available models are: {', '.join(STT_MODELS)}")
    
    # Validate temperature
    if temperature < 0.0 or temperature > 1.0:
        make_error("Temperature must be between 0.0 and 1.0")
    
    # Validate timestamp_granularities when using verbose_json
    if response_format != "verbose_json" and timestamp_granularities != ["segment"]:
        make_error("timestamp_granularities can only be used with response_format='verbose_json'")
    
    # Get the input file
    file_path = handle_input_file(input_file_path, audio_content_check=True)
    
    # Prepare the files for the multipart request
    files = {
        "file": (file_path.name, open(file_path, "rb"), "audio/mpeg"),
        "model": (None, model),
        "response_format": (None, response_format),
        "temperature": (None, str(temperature)),
    }
    
    # Add optional parameters
    if language:
        files["language"] = (None, language)
    if prompt:
        files["prompt"] = (None, prompt)
    if timestamp_granularities and response_format == "verbose_json":
        for granularity in timestamp_granularities:
            files["timestamp_granularities[]"] = (None, granularity)

    # Make the API request
    response = httpx.post(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {groq_api_key}"},
        files=files
    )
    
    # Check for errors
    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error occurred")
        except Exception:
            error_message = f"HTTP Error: {response.status_code}"
        make_error(f"Groq API error: {error_message}")
    
    # Process the response
    if response_format == "text":
        transcription = response.text
    else:
        transcription_data = response.json()
        if response_format == "json":
            transcription = transcription_data.get("text", "")
        else:  # verbose_json
            # For verbose_json, we'll save the full JSON but return the text
            transcription = transcription_data.get("text", "")
            
            # If saving to file, also save the full JSON response
            if save_to_file:
                output_path = make_output_path(output_directory, base_path)
                json_file_path = make_output_file("groq-stt-full", file_path.name, output_path, "json")
                with open(json_file_path, "w") as f:
                    json.dump(transcription_data, f, indent=2)
    
    # Save the transcription to a file if requested
    if save_to_file:
        output_path = make_output_path(output_directory, base_path)
        output_file_path = make_output_file("groq-stt", file_path.name, output_path, "txt")
        
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file_path, "w") as f:
            f.write(transcription)
        
        return TextContent(
            type="text",
            text=f"Success. Transcription saved as: {output_file_path}\nModel used: {model}"
        )
    else:
        return TextContent(
            type="text",
            text=transcription
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
    # Validate model - only whisper-large-v3 supports translation
    if model != "whisper-large-v3":
        make_error("Only 'whisper-large-v3' model supports translation. Other models can only transcribe.")
    
    # Get the input file
    file_path = handle_input_file(input_file_path, audio_content_check=True)
    
    # Prepare the files for the multipart request
    files = {
        "file": (file_path.name, open(file_path, "rb"), "audio/mpeg"),
        "model": (None, model),
        "response_format": (None, response_format),
        "temperature": (None, str(temperature)),
    }
    
    # Add optional parameters
    if prompt:
        files["prompt"] = (None, prompt)
    
    # Make the API request
    response = httpx.post(
        "https://api.groq.com/openai/v1/audio/translations",
        headers={"Authorization": f"Bearer {groq_api_key}"},
        files=files
    )
    
    # Check for errors
    if response.status_code != 200:
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error occurred")
        except Exception:
            error_message = f"HTTP Error: {response.status_code}"
        make_error(f"Groq API error: {error_message}")
    
    # Process the response
    if response_format == "text":
        translation = response.text
    else:  # json
        translation_data = response.json()
        translation = translation_data.get("text", "")
    
    # Save the translation to a file if requested
    if save_to_file:
        output_path = make_output_path(output_directory, base_path)
        output_file_path = make_output_file("groq-translation", file_path.name, output_path, "txt")
        
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file_path, "w") as f:
            f.write(translation)
        
        return TextContent(
            type="text",
            text=f"Success. Translation saved as: {output_file_path}\nModel used: {model}"
        )
    else:
        return TextContent(
            type="text",
            text=translation
        )

def list_stt_models() -> TextContent:
    models_info = {
        "whisper-large-v3-turbo": {
            "description": "A fine-tuned version of a pruned Whisper Large V3 designed for fast, multilingual transcription tasks.",
            "cost_per_hour": "$0.04",
            "languages": "Multilingual",
            "transcription": "Yes",
            "translation": "No",
            "speed_factor": "216",
            "word_error_rate": "12%"
        },
        "distil-whisper-large-v3-en": {
            "description": "A distilled version of Whisper, designed for faster, lower cost English speech recognition.",
            "cost_per_hour": "$0.02",
            "languages": "English only",
            "transcription": "Yes",
            "translation": "No",
            "speed_factor": "250",
            "word_error_rate": "13%"
        },
        "whisper-large-v3": {
            "description": "Provides state-of-the-art performance with high accuracy for multilingual transcription and translation tasks.",
            "cost_per_hour": "$0.111",
            "languages": "Multilingual",
            "transcription": "Yes",
            "translation": "Yes",
            "speed_factor": "189",
            "word_error_rate": "10.3%"
        }
    }
    
    # Format the model information
    model_details = []
    for model_id, info in models_info.items():
        model_details.append(
            f"Model: {model_id}\n"
            f"  Description: {info['description']}\n"
            f"  Cost: {info['cost_per_hour']} per hour\n"
            f"  Language Support: {info['languages']}\n"
            f"  Transcription: {info['transcription']}\n"
            f"  Translation: {info['translation']}\n"
            f"  Real-time Speed Factor: {info['speed_factor']}\n"
            f"  Word Error Rate: {info['word_error_rate']}"
        )
    
    return TextContent(
        type="text",
        text="Available Groq Speech-to-Text Models:\n\n" + "\n\n".join(model_details)
    ) 