from fastapi import FastAPI

from app.core.config import settings
from app.core.cors import setup_cors
from app.db.connection import db

from app.routes.v1 import (
    health,
    auth,
    profile,
    onboarding,
    social,
    messages,
    content
)

app = FastAPI(
    title=settings.PROJECT_NAME
)


setup_cors(app)


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


app.include_router(
    health.router,
    prefix="/api/v1"
)

app.include_router(
    auth.router,
    prefix="/api/v1"
)

app.include_router(
    profile.router,
    prefix="/api/v1"
)

app.include_router(
    onboarding.router,
    prefix="/api/v1"
)

app.include_router(
    social.router,
    prefix="/api/v1"
)

app.include_router(
    messages.router,
    prefix="/api/v1"
)

app.include_router(
    content.router,
    prefix="/api/v1"
)