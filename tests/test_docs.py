import pytest
from src.groq_docs import get_groq_full_docs, get_groq_short_docs

def test_get_full_docs(mock_groq_api_key):
    """Test getting full Groq documentation"""
    result = get_groq_full_docs()
    assert result.type == "text"
    assert len(result.text) > 0
    assert "Groq" in result.text

def test_get_short_docs(mock_groq_api_key):
    """Test getting short Groq documentation"""
    result = get_groq_short_docs()
    assert result.type == "text"
    assert len(result.text) > 0
    assert "Groq" in result.text
    # Short docs should be shorter than full docs
    assert len(result.text) < len(get_groq_full_docs().text) 