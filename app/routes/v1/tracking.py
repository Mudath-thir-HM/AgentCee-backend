from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional

from app.middlewares.auth import get_current_user
from app.schemas.tracking_schema import (
    CreateTrackingRuleSchema,
    IngestTrackedEventSchema
)
from app.controllers.tracking_controller import tracking_controller

router = APIRouter(
    prefix="/tracking",
    tags=["Tracking"]
)


# ── Rules ──────────────────────────────────────────────

@router.post("/rules")
async def create_tracking_rule(
    body: CreateTrackingRuleSchema,
    user_id: str = Depends(get_current_user)
):
    """Create a hashtag / mention / keyword tracking rule."""
    return await tracking_controller.create_rule(user_id, body)


@router.get("/rules")
async def get_tracking_rules(
    active_only: bool = Query(default=True),
    user_id: str = Depends(get_current_user)
):
    """List all tracking rules for the user."""
    return await tracking_controller.get_rules(user_id, active_only)


class ToggleBody(BaseModel):
    is_active: bool


@router.patch("/rules/{rule_id}")
async def toggle_tracking_rule(
    rule_id: str,
    body: ToggleBody,
    user_id: str = Depends(get_current_user)
):
    """Enable or disable a tracking rule."""
    return await tracking_controller.toggle_rule(
        rule_id, user_id, body.is_active
    )


@router.delete("/rules/{rule_id}")
async def delete_tracking_rule(
    rule_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a tracking rule."""
    return await tracking_controller.delete_rule(rule_id, user_id)


# ── Events ─────────────────────────────────────────────

@router.post("/events")
async def ingest_tracked_event(
    body: IngestTrackedEventSchema,
    user_id: str = Depends(get_current_user)
):
    """
    Ingest an incoming social event (webhook receiver).
    The system will match it against active tracking rules.
    """
    return await tracking_controller.ingest_event(user_id, body)


@router.get("/events")
async def get_tracked_events(
    platform: Optional[str] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    user_id: str = Depends(get_current_user)
):
    """List tracked events with optional filters."""
    return await tracking_controller.get_events(
        user_id=user_id,
        platform=platform,
        event_type=event_type,
        unread_only=unread_only,
        limit=limit
    )


@router.patch("/events/{event_id}/read")
async def mark_event_read(
    event_id: str,
    user_id: str = Depends(get_current_user)
):
    """Mark a single tracked event as read."""
    return await tracking_controller.mark_event_read(event_id, user_id)


@router.post("/events/read-all")
async def mark_all_events_read(
    user_id: str = Depends(get_current_user)
):
    """Mark all tracked events as read."""
    return await tracking_controller.mark_all_read(user_id)


# ── AI ─────────────────────────────────────────────────

class SuggestReplyBody(BaseModel):
    platform: str
    message: str
    author: str
    context: Optional[str] = ""


@router.post("/suggest-reply")
async def suggest_reply(
    body: SuggestReplyBody,
    user_id: str = Depends(get_current_user)
):
    """Get AI-generated reply suggestions for an incoming message."""
    return await tracking_controller.suggest_reply(user_id, body)
