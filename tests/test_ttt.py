import pytest
from pathlib import Path
import json
from src.groq_ttt import chat_completion, list_chat_models
from src.utils import MCPError

@pytest.fixture
def sample_messages():
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ]

@pytest.mark.unit
def test_chat_completion(temp_dir, mock_groq_api_key, mock_httpx_client):
    """Test basic chat completion functionality"""
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    
    result = chat_completion(
        messages=messages,
        model="gemma2-9b-it",
        output_directory=str(temp_dir)
    )
    
    # Test response structure only
    assert result.type == "text"
    assert "Success" in result.text
    assert "saved as:" in result.text
    assert "Model used:" in result.text
    
    # Get the base filename from the text file path
    output_file = Path(result.text.split("saved as: ")[1].split("\n")[0])
    assert output_file.exists()
    
    # Check the corresponding JSON file - the pattern is groq-chat-full_{first_few_words}_{timestamp}.json
    json_file = output_file.parent / f"groq-chat-full_{output_file.stem.split('_', 1)[1]}.json"
    assert json_file.exists()
    with open(json_file) as f:
        content = json.load(f)
        assert isinstance(content, dict)
        assert "choices" in content
        assert isinstance(content["choices"], list)
        assert len(content["choices"]) > 0
        assert "message" in content["choices"][0]
        assert "content" in content["choices"][0]["message"]
        assert isinstance(content["choices"][0]["message"]["content"], str)
        assert len(content["choices"][0]["message"]["content"]) > 0

@pytest.mark.unit
def test_chat_completion_with_system(temp_dir, mock_groq_api_key, mock_httpx_client):
    """Test chat completion with system message"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hi"}
    ]
    
    result = chat_completion(
        messages=messages,
        model="gemma2-9b-it",
        output_directory=str(temp_dir)
    )
    
    assert result.type == "text"
    assert "Success" in result.text

@pytest.mark.unit
def test_invalid_messages(temp_dir, mock_groq_api_key, mock_httpx_client):
    """Test various invalid message formats"""
    invalid_messages = [
        [],  # Empty messages
        [{"wrong": "format"}],  # Missing role/content
        [{"role": "invalid", "content": "test"}],  # Invalid role
        [{"role": "user"}],  # Missing content
        None,  # None value
    ]
    
    for messages in invalid_messages:
        with pytest.raises(MCPError):
            chat_completion(
                messages=messages,
                model="gemma2-9b-it",
                output_directory=str(temp_dir)
            )

@pytest.mark.unit
def test_invalid_temperature(temp_dir, mock_groq_api_key, mock_httpx_client):
    """Test invalid temperature values"""
    messages = [{"role": "user", "content": "test"}]
    
    with pytest.raises(MCPError):
        chat_completion(
            messages=messages,
            temperature=-1,
            output_directory=str(temp_dir)
        )
    
    with pytest.raises(MCPError):
        chat_completion(
            messages=messages,
            temperature=2.1,
            output_directory=str(temp_dir)
        )

@pytest.mark.unit
def test_list_chat_models(mock_groq_api_key, mock_httpx_client):
    """Test listing available chat models"""
    result = list_chat_models()
    
    assert result.type == "text"
    assert "Available Groq Chat Models" in result.text
    # Check for current models but don't be too specific about exact ones
    assert any(model in result.text for model in [
        "gemma2-9b-it",
        "llama-3.3-70b-versatile",
        "meta-llama/llama-4-scout-17b-16e-instruct"
    ])

@pytest.mark.integration
def test_chat_completion_integration(temp_dir, mock_groq_api_key):
    """Integration test for chat completion"""
    messages = [
        {"role": "user", "content": "Write a one-word greeting"}
    ]
    
    result = chat_completion(
        messages=messages,
        model="gemma2-9b-it",
        temperature=0,  # Use 0 for more consistent results
        output_directory=str(temp_dir)
    )
    
    # Only test structural aspects
    assert result.type == "text"
    assert "Success" in result.text
    assert "saved as:" in result.text
    
    # Get the base filename from the text file path
    output_file = Path(result.text.split("saved as: ")[1].split("\n")[0])
    assert output_file.exists()
    
    # Check the corresponding JSON file - the pattern is groq-chat-full_{first_few_words}_{timestamp}.json
    json_file = output_file.parent / f"groq-chat-full_{output_file.stem.split('_', 1)[1]}.json"
    assert json_file.exists()
    with open(json_file) as f:
        content = json.load(f)
        assert isinstance(content, dict)
        assert "choices" in content
        assert len(content["choices"]) > 0
        assert isinstance(content["choices"][0]["message"]["content"], str) 