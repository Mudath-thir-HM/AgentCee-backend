from fastapi import HTTPException

from app.repositories.tracking_repository import tracking_repository
from app.agents.tracking_agent import tracking_agent
from app.agents.inbox_agent import inbox_agent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TrackingService:

    # ── Rules ──────────────────────────────────────────
    async def create_rule(
        self,
        user_id: str,
        type: str,
        value: str,
        platform: str | None
    ):
        row = await tracking_repository.create_rule(
            user_id=user_id,
            type=type,
            value=value,
            platform=platform
        )
        return dict(row)

    async def get_rules(self, user_id: str, active_only: bool = True):
        rows = await tracking_repository.get_rules(user_id, active_only)
        return [dict(r) for r in rows]

    async def toggle_rule(
        self,
        rule_id: str,
        user_id: str,
        is_active: bool
    ):
        row = await tracking_repository.toggle_rule(
            rule_id, user_id, is_active
        )
        if not row:
            raise HTTPException(
                status_code=404,
                detail="Rule not found"
            )
        return dict(row)

    async def delete_rule(self, rule_id: str, user_id: str):
        row = await tracking_repository.delete_rule(rule_id, user_id)
        if not row:
            raise HTTPException(
                status_code=404,
                detail="Rule not found"
            )
        return {"deleted": True, "id": rule_id}

    # ── Ingest ─────────────────────────────────────────
    async def ingest_event(
        self,
        user_id: str,
        platform: str,
        event_type: str,
        content: str,
        author_username: str,
        external_id: str | None
    ):
        event = await tracking_agent.process_event(
            user_id=user_id,
            platform=platform,
            event_type=event_type,
            content=content,
            author_username=author_username,
            external_id=external_id
        )
        return event

    # ── Read events ────────────────────────────────────
    async def get_events(
        self,
        user_id: str,
        platform: str | None = None,
        event_type: str | None = None,
        unread_only: bool = False,
        limit: int = 50
    ):
        rows = await tracking_repository.get_events(
            user_id=user_id,
            platform=platform,
            event_type=event_type,
            unread_only=unread_only,
            limit=limit
        )
        return [dict(r) for r in rows]

    async def mark_event_read(self, event_id: str, user_id: str):
        row = await tracking_repository.mark_read(event_id, user_id)
        if not row:
            raise HTTPException(status_code=404, detail="Event not found")
        return dict(row)

    async def mark_all_read(self, user_id: str):
        await tracking_repository.mark_all_read(user_id)
        return {"message": "All events marked as read"}

    # ── AI reply suggestions ───────────────────────────
    async def suggest_reply(
        self,
        user_id: str,
        platform: str,
        message: str,
        author: str,
        context: str = ""
    ):
        suggestions = await inbox_agent.suggest_replies(
            platform=platform,
            message=message,
            author=author,
            context=context
        )
        sentiment = await inbox_agent.classify_sentiment(message)
        return {
            "suggestions": suggestions,
            "sentiment": sentiment
        }


tracking_service = TrackingService()
