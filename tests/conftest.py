import pytest
from pathlib import Path
import tempfile
import os
import json
import httpx
from PIL import Image
import numpy as np

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_groq_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-api-key")

@pytest.fixture
def mock_httpx_client(monkeypatch):
    """Mock httpx client for non-integration tests"""
    class MockResponse:
        def __init__(self, status_code=200, json_data=None, text=""):
            self.status_code = status_code
            self._json_data = json_data or {}
            self._text = text

        def json(self):
            return self._json_data

        @property
        def text(self):
            return self._text

        def raise_for_status(self):
            if self.status_code != 200:
                raise httpx.HTTPStatusError("Error", request=None, response=self)

    def mock_post(*args, **kwargs):
        # Mock STT response
        if "audio/transcriptions" in args[0]:
            return MockResponse(
                json_data={
                    "text": "This is a mock transcription."
                }
            )
        # Mock translation response
        elif "audio/translations" in args[0]:
            return MockResponse(
                json_data={"text": "This is a test translation"},
                text="This is a test translation"
            )
        # Mock chat completion response (including vision)
        elif "chat/completions" in args[0]:
            # Check if this is a vision request
            if any(msg.get("content", [{}])[0].get("type") == "image_url" 
                  for msg in kwargs.get("json", {}).get("messages", [])):
                # Check if JSON response is requested
                if kwargs.get("json", {}).get("response_format", {}).get("type") == "json_object":
                    return MockResponse(
                        json_data={
                            "choices": [{
                                "message": {
                                    "content": {
                                        "description": "The image depicts a red square against a black background. The red square is centered in the image and is a solid, bright red color.",
                                        "colors": {
                                            "background": "black",
                                            "shape": "red"
                                        },
                                        "composition": {
                                            "shape": "square",
                                            "position": "centered"
                                        }
                                    }
                                }
                            }]
                        }
                    )
                # Regular vision response
                return MockResponse(
                    json_data={
                        "choices": [{
                            "message": {
                                "content": "The image depicts a red square against a black background. The red square is centered in the image and is a solid, bright red color. It has no other features or details. The background of the image is a solid black color, providing a stark contrast to the red square."
                            }
                        }]
                    }
                )
            # Regular chat completion
            return MockResponse(
                json_data={
                    "id": "mock-completion-id",
                    "object": "chat.completion",
                    "created": 1234567890,
                    "model": kwargs.get("json", {}).get("model", "default-model"),
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "This is a test response"
                        },
                        "finish_reason": "stop"
                    }]
                }
            )
        return MockResponse(status_code=404)

    monkeypatch.setattr(httpx, "post", mock_post)

@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a valid test audio file that meets minimum length requirements"""
    audio_file = temp_dir / "test.wav"
    
    # Create a WAV file with 1 second of silence (44100 samples)
    # WAV header for PCM format
    header = (
        b'RIFF'                  # ChunkID
        b'\x24\xA0\x00\x00'     # ChunkSize (41000 bytes)
        b'WAVE'                  # Format
        b'fmt '                  # Subchunk1ID
        b'\x10\x00\x00\x00'     # Subchunk1Size (16 bytes)
        b'\x01\x00'             # AudioFormat (1 = PCM)
        b'\x01\x00'             # NumChannels (1 = Mono)
        b'\x44\xAC\x00\x00'     # SampleRate (44100)
        b'\x44\xAC\x00\x00'     # ByteRate (44100)
        b'\x01\x00'             # BlockAlign (1)
        b'\x08\x00'             # BitsPerSample (8)
        b'data'                  # Subchunk2ID
        b'\x00\xA0\x00\x00'     # Subchunk2Size (40960 bytes)
    )
    
    # Create 1 second of silence (40960 bytes of zeros)
    silence = b'\x80' * 40960  # Use 0x80 for middle value in 8-bit audio
    
    with open(audio_file, "wb") as f:
        f.write(header + silence)
    
    return audio_file

@pytest.fixture
def sample_image_file(temp_dir):
    """Create a valid test image file"""
    image_file = temp_dir / "test.jpg"
    
    # Create a simple 100x100 RGB image with a colored rectangle
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    img_array[25:75, 25:75] = [255, 0, 0]  # Red rectangle
    
    # Convert numpy array to PIL Image and save
    img = Image.fromarray(img_array)
    img.save(image_file, format='JPEG')
    
    return image_file

@pytest.fixture
def sample_chat_messages():
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]

@pytest.fixture
def sample_batch_requests():
    return [
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
        }
    ] 