"""
Gemini streaming LLM client with tiered model routing.

Primary:  GEMINI_MODEL         (default: gemini-3.1-flash-lite) — 500 RPD free tier
Premium:  GEMINI_MODEL_PREMIUM (default: gemini-2.5-flash)      — 20 RPD free tier

The premium model is only used when the primary returns 429 or 503, preserving
the scarce 2.5-flash quota for cases where the lite tier is rate-limited.
"""

import json
import os
from collections.abc import AsyncGenerator

import httpx
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY", "")
_MODEL_PRIMARY = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
_MODEL_PREMIUM = os.getenv("GEMINI_MODEL_PREMIUM", "gemini-2.5-flash")

_SYSTEM_INSTRUCTION = (
    "You are an immigration advisor for Exit Plan. You are given "
    "excerpts from official government immigration documents. "
    "These may be dense legal texts. Extract and explain the "
    "relevant information in plain English. If the context "
    "contains relevant information even in legal language, "
    "interpret and explain it clearly. Always cite the source URL. "
    "If you truly cannot find relevant information, say so — but "
    "look carefully at the full legal text before concluding that."
)

_FALLBACK_ERROR = "I couldn't retrieve that information right now. Please try again."


def _url(model: str) -> str:
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models"
        f"/{model}:streamGenerateContent?key={_API_KEY}&alt=sse"
    )


async def _stream_model(
    model: str, payload: dict, client: httpx.AsyncClient
) -> AsyncGenerator[str, None]:
    """Stream chunks from one model. Raises httpx.HTTPStatusError on 4xx/5xx."""
    async with client.stream("POST", _url(model), json=payload) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if not line.startswith("data: "):
                continue
            raw = line[len("data: "):]
            if raw.strip() == "[DONE]":
                return
            try:
                data = json.loads(raw)
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    yield text
            except (KeyError, IndexError, json.JSONDecodeError):
                continue


async def generate(prompt: str, context: str) -> AsyncGenerator[str, None]:
    """Stream text chunks from Gemini using tiered model routing.

    Tries the primary (Flash Lite) model first. Falls back to premium
    (Flash 2.5) only on 429 or 503. Yields the error string if both fail.
    """
    payload = {
        "system_instruction": {"parts": [{"text": _SYSTEM_INSTRUCTION}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            async for chunk in _stream_model(_MODEL_PRIMARY, payload, client):
                yield chunk
            return
        except httpx.HTTPStatusError as e:
            if e.response.status_code not in (429, 503):
                yield _FALLBACK_ERROR
                return
        except Exception:
            yield _FALLBACK_ERROR
            return

        # Primary was rate-limited or unavailable — try premium
        try:
            async for chunk in _stream_model(_MODEL_PREMIUM, payload, client):
                yield chunk
        except Exception:
            yield _FALLBACK_ERROR
