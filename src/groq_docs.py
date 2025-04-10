"""
Groq Documentation Module

This module provides functions to fetch and return Groq documentation from their official sources.
"""

import httpx
from typing import Optional
from mcp.types import TextContent
from src.utils import make_error

# Documentation URLs
GROQ_FULL_DOCS_URL = "https://console.groq.com/llms-full.txt"
GROQ_SHORT_DOCS_URL = "https://console.groq.com/llms.txt"

def fetch_groq_docs(url: str) -> str:
    """
    Helper function to fetch documentation from a URL.
    """
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        make_error(f"Error fetching Groq documentation: {str(e)}")

def get_groq_full_docs() -> TextContent:
    """
    Fetch and return the full Groq documentation.
    """
    docs = fetch_groq_docs(GROQ_FULL_DOCS_URL)
    return TextContent(
        type="text",
        text=docs
    )

def get_groq_short_docs() -> TextContent:
    """
    Fetch and return the short/summary Groq documentation.
    """
    docs = fetch_groq_docs(GROQ_SHORT_DOCS_URL)
    return TextContent(
        type="text",
        text=docs
    )