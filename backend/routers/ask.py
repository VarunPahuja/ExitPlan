"""
/ask router — streaming RAG endpoint that answers natural-language immigration
questions using policy chunks and Gemini.

Flow: mock retrieve → build prompt → Gemini SSE stream → forward chunks to client.
Week 4: mock retrieve will be replaced by pgvector search + FlashRank reranking.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services import rag

router = APIRouter()


class AskRequest(BaseModel):
    query: str
    country_code: str = "GB"
    user_profile: dict = {}


@router.post("/")
async def ask_question(body: AskRequest):
    """Accept a question, run RAG pipeline, stream the answer back as SSE."""
    return StreamingResponse(
        rag.ask(body.query, body.country_code, body.user_profile),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
