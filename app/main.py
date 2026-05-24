import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.cors import setup_cors
from app.db.connection import db
from app.middlewares.rate_limit import RateLimitMiddleware
from app.utils.logger import get_logger

from app.routes.v1 import (
    health,
    auth,
    profile,
    onboarding,
    social,
    messages,
    content,
    scheduler,
    analytics,
    tracking,
)

logger = get_logger("AgentCee.main")


# ── Lifespan ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up AgentCee AI API…")
    await db.connect()
    yield
    logger.info("Shutting down…")
    await db.disconnect()


# ── App ──────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan
)

app.add_middleware(RateLimitMiddleware)
setup_cors(app)


# ── Global error handler ─────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ── Routes ───────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(health.router,      prefix=PREFIX)
app.include_router(auth.router,        prefix=PREFIX)
app.include_router(profile.router,     prefix=PREFIX)
app.include_router(onboarding.router,  prefix=PREFIX)
app.include_router(social.router,      prefix=PREFIX)
app.include_router(messages.router,    prefix=PREFIX)
app.include_router(content.router,     prefix=PREFIX)
app.include_router(scheduler.router,   prefix=PREFIX)
app.include_router(analytics.router,   prefix=PREFIX)
app.include_router(tracking.router,    prefix=PREFIX)
