from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.middlewares.auth import get_current_user
from app.controllers.message_controller import message_controller
from app.schemas.message_schema import (
    ReceiveMessageSchema,
    ReplyMessageSchema
)

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.get("/")
async def get_messages(
    user_id: str = Depends(get_current_user)
):
    return await message_controller.get_messages(user_id)


@router.post("/receive")
async def receive_message(
    data: ReceiveMessageSchema,
    user_id: str = Depends(get_current_user)
):
    return await message_controller.receive_message(
        user_id=user_id,
        platform=data.platform,
        sender_name=data.sender_name,
        message_text=data.message_text
    )


@router.post("/reply")
async def reply_message(
    data: ReplyMessageSchema,
    user_id: str = Depends(get_current_user)
):
    return await message_controller.reply_message(
        message_id=data.message_id,
        user_id=user_id
    )


# ── AI ──────────────────────────────────────────────────

class AISuggestBody(BaseModel):
    platform: str
    message_text: str
    sender_name: str
    context: Optional[str] = ""


@router.post("/ai-suggest")
async def get_ai_suggestions(
    body: AISuggestBody,
    user_id: str = Depends(get_current_user)
):
    """
    Return AI-generated reply suggestions and sentiment analysis
    for an incoming message. Feeds the "AI Suggest Reply" button.
    """
    return await message_controller.get_ai_suggestions(user_id, body)


class AutoReplyBody(BaseModel):
    platform: str
    message_text: str
    sender_name: str
    interaction_type: Optional[str] = "comment"


@router.post("/auto-reply")
async def auto_reply(
    body: AutoReplyBody,
    user_id: str = Depends(get_current_user)
):
    """Generate a single ready-to-send AI reply."""
    return await message_controller.auto_reply(user_id, body)
