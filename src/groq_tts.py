
"""
Groq TTS Module

⚠️ IMPORTANT: This module provides access to Groq API endpoints which may incur costs.
Each function that makes an API call is marked with a cost warning.

1. Only use functions when explicitly requested by the user
2. For functions that generate audio, consider the length of the text as it affects costs
"""

import os
import httpx
from typing import Literal
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

# Define available voices
ENGLISH_VOICES = [
    "Arista-PlayAI", "Atlas-PlayAI", "Basil-PlayAI", "Briggs-PlayAI", 
    "Calum-PlayAI", "Celeste-PlayAI", "Cheyenne-PlayAI", "Chip-PlayAI", 
    "Cillian-PlayAI", "Deedee-PlayAI", "Fritz-PlayAI", "Gail-PlayAI", 
    "Indigo-PlayAI", "Mamaw-PlayAI", "Mason-PlayAI", "Mikail-PlayAI", 
    "Mitch-PlayAI", "Quinn-PlayAI", "Thunder-PlayAI"
]

ARABIC_VOICES = ["Ahmad-PlayAI", "Amira-PlayAI", "Khalid-PlayAI", "Nasser-PlayAI"]

ALL_VOICES = ENGLISH_VOICES + ARABIC_VOICES

def text_to_speech(
    text: str,
    voice: str = "Arista-PlayAI",
    model: Literal["playai-tts", "playai-tts-arabic"] = "playai-tts",
    output_directory: str | None = None,
) -> TextContent:
    if text == "":
        make_error("Text is required.")
        
    if len(text) > 10000:
        make_error("Text length exceeds 10,000 characters limit.")
    
    # Validate voice selection
    if voice not in ALL_VOICES:
        available_voices = ENGLISH_VOICES + ARABIC_VOICES
        make_error(f"Voice '{voice}' not found. Available voices are: {', '.join(available_voices)}")
    
    # Check if Arabic model is selected with English voice or vice versa
    if model == "playai-tts-arabic" and voice not in ARABIC_VOICES:
        make_error(f"Voice '{voice}' is not available for Arabic TTS. Available Arabic voices are: {', '.join(ARABIC_VOICES)}")
    
    if model == "playai-tts" and voice in ARABIC_VOICES:
        make_error(f"Voice '{voice}' is an Arabic voice. For Arabic voices, use model='playai-tts-arabic'. Available English voices are: {', '.join(ENGLISH_VOICES)}")
    
    output_path = make_output_path(output_directory, base_path)
    output_file_path = make_output_file("groq-tts", text[:30], output_path, "wav")
    
    # Prepare the request to Groq API
    response = groq_client.post(
        "/audio/speech",
        json={
            "model": model,
            "input": text,
            "voice": voice,
            "response_format": "wav"
        },
    )
    
    if response.status_code != 200:
        error_data = response.json()
        error_message = error_data.get("error", {}).get("message", "Unknown error occurred")
        make_error(f"Groq API error: {error_message}")
    
    # Save the audio file
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file_path, "wb") as f:
        f.write(response.content)
    
    return TextContent(
        type="text",
        text=f"Success. File saved as: {output_file_path}. Voice used: {voice}"
    )

def list_voices(
    model: Literal["playai-tts", "playai-tts-arabic", "all"] = "all"
) -> TextContent:
    if model == "playai-tts":
        voices = ENGLISH_VOICES
        model_text = "English (playai-tts)"
    elif model == "playai-tts-arabic":
        voices = ARABIC_VOICES
        model_text = "Arabic (playai-tts-arabic)"
    else:  # "all"
        voices = ALL_VOICES
        model_text = "All Models"
    
    voice_list = ", ".join(voices)
    return TextContent(
        type="text",
        text=f"Available Groq TTS Voices for {model_text}:\n{voice_list}"
    )
