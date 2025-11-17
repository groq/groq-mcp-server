"""
AI Service - Leverages Groq API for AI-powered features
Uses the existing groq_ttt.py and groq_compound.py from the MCP server
"""

import sys
import os
from typing import List, Dict, Optional, Any

# Add parent directory to path to import existing Groq modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.groq_ttt import chat_completion
from src.groq_compound import compound_tool
from config import settings


class AIService:
    """
    AI Service for various AI-powered features using Groq
    """

    def __init__(self):
        self.chat_model = settings.GROQ_MODEL_CHAT
        self.compound_model = settings.GROQ_MODEL_COMPOUND
        self.compound_deep_model = settings.GROQ_MODEL_COMPOUND_DEEP

    async def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using Groq
        Returns a score between -1 (negative) and 1 (positive)
        """
        messages = [
            {
                "role": "system",
                "content": "You are a sentiment analysis expert. Analyze the sentiment of the given text and respond with ONLY a number between -1 (very negative) and 1 (very positive). No explanation needed."
            },
            {
                "role": "user",
                "content": f"Analyze the sentiment of this review:\n\n{text}"
            }
        ]

        try:
            result = chat_completion(
                messages=messages,
                model=self.chat_model,
                temperature=0.1,
                max_tokens=10
            )

            # Extract sentiment score from response
            sentiment_text = result.get("text", "0").strip()
            sentiment_score = float(sentiment_text)

            # Clamp to [-1, 1] range
            return max(-1.0, min(1.0, sentiment_score))

        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return 0.0  # Neutral on error

    async def extract_themes_from_reviews(self, reviews: List[str]) -> List[str]:
        """
        Extract common themes from a list of reviews using Groq
        """
        combined_reviews = "\n\n".join(reviews[:20])  # Limit to 20 reviews

        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing feedback and extracting common themes. Extract 5-10 common themes from the reviews provided. Return them as a JSON array of strings."
            },
            {
                "role": "user",
                "content": f"Extract common themes from these client reviews:\n\n{combined_reviews}"
            }
        ]

        try:
            result = chat_completion(
                messages=messages,
                model=self.chat_model,
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            import json
            themes_data = json.loads(result.get("text", "{}"))
            themes = themes_data.get("themes", [])

            return themes

        except Exception as e:
            print(f"Error extracting themes: {e}")
            return []

    async def detect_red_flags(
        self,
        client_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Detect red flags in client data using AI
        Returns list of red flags with type, severity, and description
        """
        messages = [
            {
                "role": "system",
                "content": """You are a fraud detection expert specializing in freelance platforms.
Analyze client data and identify red flags. Return a JSON array of objects with:
- flag_type: string (new_account, low_spend, cancelled_projects, off_platform, fake_reviews, etc.)
- severity: string (low, medium, high, critical)
- description: string (explanation)

Only return actual red flags, not positive indicators."""
            },
            {
                "role": "user",
                "content": f"Analyze this client data for red flags:\n\n{client_data}"
            }
        ]

        try:
            result = chat_completion(
                messages=messages,
                model=self.chat_model,
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            import json
            flags_data = json.loads(result.get("text", "{}"))
            red_flags = flags_data.get("red_flags", [])

            return red_flags

        except Exception as e:
            print(f"Error detecting red flags: {e}")
            return []

    async def generate_vetting_recommendation(
        self,
        trust_score: int,
        strengths: List[str],
        concerns: List[str],
        red_flags: List[str]
    ) -> str:
        """
        Generate a human-readable recommendation based on vetting data
        """
        messages = [
            {
                "role": "system",
                "content": "You are a freelance consultant. Provide a brief recommendation (1-2 sentences) on whether to work with this client based on their trust score, strengths, and concerns."
            },
            {
                "role": "user",
                "content": f"""Trust Score: {trust_score}/100

Strengths:
{chr(10).join(f'- {s}' for s in strengths)}

Concerns:
{chr(10).join(f'- {c}' for c in concerns)}

Red Flags:
{chr(10).join(f'- {r}' for r in red_flags)}

Provide a recommendation:"""
            }
        ]

        try:
            result = chat_completion(
                messages=messages,
                model=self.chat_model,
                temperature=0.5,
                max_tokens=150
            )

            recommendation = result.get("text", "Unable to generate recommendation")
            return recommendation.strip()

        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return "Unable to generate recommendation at this time."

    async def summarize_job_description(self, job_description: str) -> str:
        """
        Create a concise AI summary of a job description
        """
        messages = [
            {
                "role": "system",
                "content": "You are a job description summarizer. Provide a 2-3 sentence summary highlighting the key requirements, skills, and budget."
            },
            {
                "role": "user",
                "content": f"Summarize this job description:\n\n{job_description}"
            }
        ]

        try:
            result = chat_completion(
                messages=messages,
                model=self.chat_model,
                temperature=0.3,
                max_tokens=150
            )

            summary = result.get("text", job_description[:200] + "...")
            return summary.strip()

        except Exception as e:
            print(f"Error summarizing job: {e}")
            return job_description[:200] + "..."

    async def research_company(
        self,
        company_name: str,
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use Groq's compound-beta API to research a company
        This uses web search and data gathering capabilities
        """
        prompt = f"""Research the company "{company_name}" and provide:
1. LinkedIn profile URL (if found)
2. Official website URL
3. Social media presence (Twitter, Facebook, Instagram)
4. Employee count estimate
5. Recent news or articles (last 6 months)
6. Business registration verification

{f'Additional context: {additional_info}' if additional_info else ''}

Return the results in JSON format."""

        try:
            result = compound_tool(
                user_prompt=prompt,
                model=self.compound_deep_model,
                max_iterations=5
            )

            # Parse the result
            import json
            research_data = json.loads(result.get("text", "{}"))

            return research_data

        except Exception as e:
            print(f"Error researching company: {e}")
            return {}

    async def parse_natural_language_search(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        Parse natural language job search query into structured filters
        E.g., "find React jobs paying $50+/hour" -> {skills: ["React"], min_hourly_rate: 50}
        """
        messages = [
            {
                "role": "system",
                "content": """You are a search query parser. Convert natural language job search queries into structured filters.
Return a JSON object with these optional fields:
- skills: array of strings
- categories: array of strings
- min_hourly_rate: number
- max_hourly_rate: number
- min_fixed_price: number
- max_fixed_price: number
- experience_level: string (entry, intermediate, expert)
- job_type: string (hourly, fixed)
- location: string

Only include fields mentioned in the query."""
            },
            {
                "role": "user",
                "content": f"Parse this job search query:\n\n{query}"
            }
        ]

        try:
            result = chat_completion(
                messages=messages,
                model=self.chat_model,
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            import json
            filters = json.loads(result.get("text", "{}"))

            return filters

        except Exception as e:
            print(f"Error parsing search query: {e}")
            return {}
