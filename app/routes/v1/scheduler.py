from fastapi import APIRouter, Depends, Query

from app.middlewares.auth import get_current_user
from app.schemas.scheduler_schema import (
    CreateScheduledPostSchema,
    UpdateScheduledPostSchema
)
from app.controllers.scheduler_controller import scheduler_controller

router = APIRouter(
    prefix="/scheduler",
    tags=["Scheduler"]
)


@router.post("/")
async def schedule_post(
    body: CreateScheduledPostSchema,
    user_id: str = Depends(get_current_user)
):
    """Schedule a post for future publishing."""
    return await scheduler_controller.schedule_post(user_id, body)


@router.get("/")
async def get_scheduled_posts(
    status: str | None = Query(default=None),
    platform: str | None = Query(default=None),
    user_id: str = Depends(get_current_user)
):
    """List all scheduled posts, optionally filtered by status/platform."""
    return await scheduler_controller.get_posts(
        user_id=user_id,
        status=status,
        platform=platform
    )


@router.get("/{post_id}")
async def get_scheduled_post(
    post_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a single scheduled post."""
    return await scheduler_controller.get_post(post_id, user_id)


@router.patch("/{post_id}")
async def update_scheduled_post(
    post_id: str,
    body: UpdateScheduledPostSchema,
    user_id: str = Depends(get_current_user)
):
    """Update text / time / cancel a pending post."""
    return await scheduler_controller.update_post(
        post_id, user_id, body
    )


@router.delete("/{post_id}")
async def delete_scheduled_post(
    post_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a pending scheduled post."""
    return await scheduler_controller.delete_post(post_id, user_id)
