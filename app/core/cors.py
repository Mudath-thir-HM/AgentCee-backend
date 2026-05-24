# app/core/cors.py
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def setup_cors(app):
    # Always include both the env var and the known production URL
    origins = [
        "https://agentcee.netlify.app",
    ]
    
    if settings.FRONTEND_URL and settings.FRONTEND_URL not in origins:
        origins.append(settings.FRONTEND_URL.rstrip("/"))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )