import pytest
from pathlib import Path
from src.groq_stt import (
    transcribe_audio,
    translate_audio,
    list_stt_models
)
from src.utils import MCPError

@pytest.mark.unit
def test_transcribe_audio(temp_dir, mock_groq_api_key, mock_httpx_client, sample_audio_file):
    """Test audio transcription"""
    result = transcribe_audio(
        input_file_path=str(sample_audio_file),
        model="whisper-large-v3-turbo",
        output_directory=str(temp_dir)
    )
    
    assert result.type == "text"
    assert len(result.text) > 0

@pytest.mark.unit
def test_translate_audio(temp_dir, mock_groq_api_key, mock_httpx_client, sample_audio_file):
    """Test audio translation"""
    result = translate_audio(
        input_file_path=str(sample_audio_file),
        model="whisper-large-v3",
        output_directory=str(temp_dir)
    )
    
    assert result.type == "text"
    assert len(result.text) > 0

@pytest.mark.unit
def test_list_stt_models(mock_groq_api_key):
    """Test listing available STT models"""
    result = list_stt_models()
    assert result.type == "text"
    assert "whisper-large-v3" in result.text
    assert "whisper-large-v3-turbo" in result.text

@pytest.mark.unit
def test_invalid_audio_file(temp_dir, mock_groq_api_key, mock_httpx_client):
    """Test that invalid audio file raises error"""
    with pytest.raises(MCPError):
        transcribe_audio(
            input_file_path="nonexistent.wav",
            output_directory=str(temp_dir)
        )

@pytest.mark.unit
@pytest.mark.parametrize("invalid_model", [
    "invalid-model",
    "whisper-invalid",
    "gpt-4"  # Valid Groq model but not for STT
])
def test_invalid_model(temp_dir, mock_groq_api_key, mock_httpx_client, sample_audio_file, invalid_model):
    """Test that invalid model raises error"""
    with pytest.raises(MCPError):
        transcribe_audio(
            input_file_path=str(sample_audio_file),
            model=invalid_model,
            output_directory=str(temp_dir)
        )

# Add integration tests that use real API
@pytest.mark.integration
def test_transcribe_audio_integration(temp_dir, mock_groq_api_key, sample_audio_file):
    """Integration test for audio transcription"""
    result = transcribe_audio(
        input_file_path=str(sample_audio_file),
        model="whisper-large-v3-turbo",
        output_directory=str(temp_dir)
    )
    
    assert result.type == "text"
    assert len(result.text) > 0

@pytest.mark.integration
def test_translate_audio_integration(temp_dir, mock_groq_api_key, sample_audio_file):
    """Integration test for audio translation"""
    result = translate_audio(
        input_file_path=str(sample_audio_file),
        model="whisper-large-v3",
        output_directory=str(temp_dir)
    )
    
    assert result.type == "text"
    assert len(result.text) > 0 