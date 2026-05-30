"""
Exit Plan — FastAPI application entry point.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Exit Plan API",
    description="AI-powered immigration country ranking platform",
    version="0.1.0",
)

# CORS must be registered before routers so preflight OPTIONS requests are handled
_frontend = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
_origins = [
    _frontend,
    "http://localhost:3000",
    "http://localhost:5173",
    "https://exit-plan-two.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import rank, ask, profile, alerts, outcomes, countries
from db.client import test_connection

app.include_router(rank.router,      prefix="/rank",     tags=["rank"])
app.include_router(ask.router,       prefix="/ask",      tags=["ask"])
app.include_router(profile.router,   prefix="/profile",  tags=["profile"])
app.include_router(alerts.router,    prefix="/alerts",   tags=["alerts"])
app.include_router(outcomes.router,  prefix="/outcomes", tags=["outcomes"])
app.include_router(countries.router, prefix="/country",  tags=["countries"])


@app.get("/health", tags=["meta"])
async def health_check():
    """Returns API status and a live DB connectivity check."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "db": test_connection(),
    }
