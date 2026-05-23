from fastapi import APIRouter, Depends, Query

from app.middlewares.auth import get_current_user
from app.schemas.content_schema import (
    GenerateContentSchema,
    ContentUpdateSchema,
    ContentStatusSchema
)
from app.controllers.content_controller import content_controller

router = APIRouter(
    prefix="/content",
    tags=["Content"]
)


@router.post("/generate")
async def generate_content(
    body: GenerateContentSchema,
    user_id: str = Depends(get_current_user)
):
    """Generate new AI content and persist it as a draft."""
    return await content_controller.generate_content(user_id, body)


@router.get("/history")
async def get_history(
    platform: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user)
):
    """Return all generated content for the authenticated user."""
    return await content_controller.get_history(
        user_id=user_id,
        platform=platform,
        status=status,
        limit=limit,
        offset=offset
    )


@router.get("/{content_id}")
async def get_content(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Retrieve a single piece of generated content."""
    return await content_controller.get_content(content_id, user_id)


@router.patch("/{content_id}")
async def update_content(
    content_id: str,
    body: ContentUpdateSchema,
    user_id: str = Depends(get_current_user)
):
    """Edit the text / hashtags / CTA of a draft."""
    return await content_controller.update_content(
        content_id, user_id, body
    )


@router.patch("/{content_id}/status")
async def update_status(
    content_id: str,
    body: ContentStatusSchema,
    user_id: str = Depends(get_current_user)
):
    """Change the status: draft → scheduled → posted → archived."""
    return await content_controller.update_status(
        content_id, user_id, body
    )


@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    user_id: str = Depends(get_current_user)
):
    """Permanently delete a generated content record."""
    return await content_controller.delete_content(content_id, user_id)
