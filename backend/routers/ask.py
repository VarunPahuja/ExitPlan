"""
/ask router — RAG endpoint that answers natural-language immigration questions
using policy chunks and Gemini.

Returns a single JSON response (not SSE) for production reliability on Render.
"""

import json

from fastapi import APIRouter
from pydantic import BaseModel

from services import rag

router = APIRouter()


class AskRequest(BaseModel):
    query: str
    country_code: str = "GB"
    user_profile: dict = {}


@router.post("/")
async def ask_endpoint(body: AskRequest):
    """Run the RAG pipeline and return the full answer as JSON."""
    full_response = ""
    citations: list = []

    try:
        async for raw in rag.ask(body.query, body.country_code, body.user_profile or {}):
            # rag.ask() yields "data: {...}\n\n" formatted strings
            line = raw.strip()
            if line.startswith("data: "):
                line = line[6:]
            try:
                data = json.loads(line)
                if not data.get("done"):
                    full_response += data.get("chunk", "")
                else:
                    citations = data.get("citations", [])
            except Exception:
                pass
    except Exception as e:
        print(f"[ask] generation error: {e}")
        full_response = "I encountered an error. Please try again."

    return {
        "response": full_response or "No response received.",
        "citations": citations,
        "done": True,
    }
