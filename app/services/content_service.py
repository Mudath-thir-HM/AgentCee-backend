from fastapi import HTTPException

from app.agents.content_agent import content_agent
from app.repositories.content_repository import (
    content_repository
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ContentService:

    # ── Generate ───────────────────────────────────────
    async def generate_content(
        self,
        user_id: str,
        platform: str,
        content_type: str,
        prompt: str,
        tone: str
    ):
        try:
            ai_response = await content_agent.generate_content(
                platform=platform,
                content_type=content_type,
                prompt=prompt,
                tone=tone
            )

        except Exception as exc:
            logger.warning(
                "AI generation failed, using fallback: %s", exc
            )
            ai_response = {
                "generated_text": (
                    "AI content generation temporarily unavailable"
                ),
                "hashtags": [],
                "call_to_action": ""
            }

        saved = await content_repository.save_generated_content(
            user_id=user_id,
            platform=platform,
            content_type=content_type,
            prompt=prompt,
            generated_text=ai_response["generated_text"],
            hashtags=ai_response["hashtags"],
            call_to_action=ai_response["call_to_action"]
        )

        logger.info(
            "Content generated for user=%s platform=%s",
            user_id, platform
        )
        return dict(saved)

    # ── History ────────────────────────────────────────
    async def get_history(
        self,
        user_id: str,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0
    ):
        rows = await content_repository.get_all_content(
            user_id=user_id,
            platform=platform,
            status=status,
            limit=limit,
            offset=offset
        )
        return [dict(r) for r in rows]

    async def get_content_by_id(
        self,
        content_id: str,
        user_id: str
    ):
        row = await content_repository.get_content_by_id(
            content_id, user_id
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Content not found"
            )

        return dict(row)

    # ── Update ─────────────────────────────────────────
    async def update_content(
        self,
        content_id: str,
        user_id: str,
        generated_text: str | None,
        hashtags: list | None,
        call_to_action: str | None
    ):
        row = await content_repository.update_content(
            content_id=content_id,
            user_id=user_id,
            generated_text=generated_text,
            hashtags=hashtags,
            call_to_action=call_to_action
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Content not found"
            )

        return dict(row)

    async def update_status(
        self,
        content_id: str,
        user_id: str,
        status: str
    ):
        allowed = {"draft", "scheduled", "posted", "archived"}
        if status not in allowed:
            raise HTTPException(
                status_code=422,
                detail=f"status must be one of {allowed}"
            )

        row = await content_repository.update_content_status(
            content_id, user_id, status
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Content not found"
            )

        return dict(row)

    # ── Delete ─────────────────────────────────────────
    async def delete_content(
        self,
        content_id: str,
        user_id: str
    ):
        row = await content_repository.delete_content(
            content_id, user_id
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Content not found"
            )

        return {"deleted": True, "id": content_id}


content_service = ContentService()
