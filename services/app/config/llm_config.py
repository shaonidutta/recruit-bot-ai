"""
LLM Configuration for AI Recruitment Agent
Handles OpenAI client setup and model configurations
"""

import os
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Default to GPT-3.5-turbo for cost efficiency
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))  # Low temperature for consistent results

if not OPENAI_API_KEY:
    raise ValueError(" OPENAI_API_KEY is not set. Please add it to your .env file.")

# Global OpenAI client
_openai_client: Optional[AsyncOpenAI] = None

def get_openai_client() -> AsyncOpenAI:
    """Get or create OpenAI client"""
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    return _openai_client

async def chat_completion(
    messages: list,
    model: str = OPENAI_MODEL,
    max_tokens: int = OPENAI_MAX_TOKENS,
    temperature: float = OPENAI_TEMPERATURE
) -> str:
    """
    Make a chat completion request to OpenAI
    """
    try:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"OpenAI API call failed: {e}")

# Model configurations for different tasks
MODEL_CONFIGS = {
    "job_parsing": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 800,
        "temperature": 0.1
    },
    "candidate_matching": {
        "model": "gpt-3.5-turbo", 
        "max_tokens": 500,
        "temperature": 0.2
    },
    "enrichment": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 300,
        "temperature": 0.1
    }
}
