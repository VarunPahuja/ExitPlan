"""
Exit Plan — FastAPI application entry point.

Initialises the app, registers all routers, configures CORS for the Lovable
frontend, and exposes a /health endpoint that includes a live DB connectivity
check.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import rank, ask, profile, alerts, outcomes, countries
from db.client import test_connection

app = FastAPI(
    title="Exit Plan API",
    description="AI-powered immigration country ranking platform",
    version="0.1.0",
)

# Allow local dev + production Vercel URL + whatever FRONTEND_URL is set to
_frontend = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
_origins = list({
    _frontend,
    _frontend + "/",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://exit-plan-two.vercel.app",
    "https://exit-plan-two.vercel.app/",
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rank.router,     prefix="/rank",     tags=["rank"])
app.include_router(ask.router,      prefix="/ask",      tags=["ask"])
app.include_router(profile.router,  prefix="/profile",  tags=["profile"])
app.include_router(alerts.router,   prefix="/alerts",   tags=["alerts"])
app.include_router(outcomes.router, prefix="/outcomes", tags=["outcomes"])
app.include_router(countries.router, prefix="/country", tags=["countries"])


@app.get("/health", tags=["meta"])
async def health_check():
    """Returns API status and a live DB connectivity check."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "db": test_connection(),
    }
