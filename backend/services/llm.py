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
    "You are an immigration advisor for Exit Plan. "
    "Answer questions about visas, PR timelines, and immigration in plain conversational English. "
    "Rules: "
    "Keep answers under 150 words. "
    "No markdown headers (no ### or ##). "
    "Use short paragraphs, not bullet walls. "
    "Lead with the direct answer in the first sentence. "
    "Cite the source at the end as: Source: [URL]. "
    "If citing multiple sources, pick the most relevant one. "
    "If you genuinely don't know, say so in one sentence."
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
