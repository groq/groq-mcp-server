import pytest
from pathlib import Path
from src.groq_tts import text_to_speech, list_voices
from src.utils import MCPError

@pytest.mark.unit
def test_text_to_speech(temp_dir, mock_groq_api_key, mock_httpx_client):
    """Test text to speech conversion"""
    text = "Hello, this is a test."
    result = text_to_speech(
        text=text,
        voice="Arista-PlayAI",
        model="playai-tts",
        output_directory=str(temp_dir)
    )
    
    # Check that the result is a TextContent object
    assert result.type == "text"
    assert "Success. File saved as:" in result.text
    assert "Voice used: Arista-PlayAI" in result.text
    
    # Extract file path from response
    file_path = result.text.split("File saved as: ")[1].split(".")[0] + ".wav"
    output_file = Path(file_path)
    assert output_file.exists()
    assert output_file.suffix == ".wav"

@pytest.mark.unit
def test_list_voices(mock_groq_api_key):
    """Test listing available voices"""
    result = list_voices("all")
    
    # Check that the result is a TextContent object
    assert result.type == "text"
    assert "Available Groq TTS Voices for All Models:" in result.text
    assert "Arista-PlayAI" in result.text  # Check for a known voice

@pytest.mark.unit
def test_list_voices_english(mock_groq_api_key):
    """Test listing English voices"""
    result = list_voices("playai-tts")
    
    # Check that the result is a TextContent object
    assert result.type == "text"
    assert "Available Groq TTS Voices for English (playai-tts):" in result.text
    assert "Arista-PlayAI" in result.text  # Check for a known English voice
    assert "Ahmad-PlayAI" not in result.text  # Should not include Arabic voices

@pytest.mark.unit
def test_list_voices_arabic(mock_groq_api_key):
    """Test listing Arabic voices"""
    result = list_voices("playai-tts-arabic")
    
    # Check that the result is a TextContent object
    assert result.type == "text"
    assert "Available Groq TTS Voices for Arabic (playai-tts-arabic):" in result.text
    assert "Ahmad-PlayAI" in result.text  # Check for a known Arabic voice
    assert "Arista-PlayAI" not in result.text  # Should not include English voices

@pytest.mark.parametrize("invalid_text", [
    "",  # Empty string
    "a" * 10001,  # Too long (over 10,000 characters)
])
@pytest.mark.unit
def test_text_to_speech_invalid_input(invalid_text, temp_dir, mock_groq_api_key, mock_httpx_client):
    """Test text to speech with invalid input"""
    with pytest.raises(MCPError):
        text_to_speech(
            text=invalid_text,
            voice="Arista-PlayAI",
            model="playai-tts",
            output_directory=str(temp_dir)
        ) 