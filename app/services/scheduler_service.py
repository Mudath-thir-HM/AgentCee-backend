from datetime import datetime, timezone
from fastapi import HTTPException

from app.repositories.scheduler_repository import (
    scheduler_repository
)
from app.repositories.content_repository import (
    content_repository
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SchedulerService:

    # ── Create ──────────────────────────────────────────
    async def schedule_post(
        self,
        user_id: str,
        content_id: str | None,
        platform: str,
        post_text: str,
        scheduled_for: datetime
    ):
        # If content_id supplied, verify ownership
        if content_id:
            asset = await content_repository.get_content_by_id(
                content_id, user_id
            )
            if not asset:
                raise HTTPException(
                    status_code=404,
                    detail="Content asset not found"
                )

        post = await scheduler_repository.create_scheduled_post(
            user_id=user_id,
            content_id=content_id,
            platform=platform,
            post_text=post_text,
            scheduled_for=scheduled_for
        )

        # Mark the linked content as "scheduled"
        if content_id:
            await content_repository.update_content_status(
                content_id, user_id, "scheduled"
            )

        logger.info(
            "Post scheduled user=%s platform=%s for=%s",
            user_id, platform, scheduled_for
        )
        return dict(post)

    # ── Read ────────────────────────────────────────────
    async def get_posts(
        self,
        user_id: str,
        status: str | None = None,
        platform: str | None = None
    ):
        rows = await scheduler_repository.get_scheduled_posts(
            user_id=user_id,
            status=status,
            platform=platform
        )
        return [dict(r) for r in rows]

    async def get_post(self, post_id: str, user_id: str):
        row = await scheduler_repository.get_post_by_id(
            post_id, user_id
        )
        if not row:
            raise HTTPException(
                status_code=404,
                detail="Scheduled post not found"
            )
        return dict(row)

    # ── Update ──────────────────────────────────────────
    async def update_post(
        self,
        post_id: str,
        user_id: str,
        post_text: str | None,
        scheduled_for: datetime | None,
        status: str | None
    ):
        allowed_statuses = {"pending", "cancelled"}
        if status and status not in allowed_statuses:
            raise HTTPException(
                status_code=422,
                detail=f"Allowed statuses: {allowed_statuses}"
            )

        # Cannot edit published / failed posts
        existing = await self.get_post(post_id, user_id)
        if existing["status"] not in {"pending"}:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Only pending posts can be modified. "
                    f"Current status: {existing['status']}"
                )
            )

        row = await scheduler_repository.update_post(
            post_id=post_id,
            user_id=user_id,
            post_text=post_text,
            scheduled_for=scheduled_for,
            status=status
        )
        return dict(row)

    # ── Delete ──────────────────────────────────────────
    async def delete_post(self, post_id: str, user_id: str):
        row = await scheduler_repository.delete_post(
            post_id, user_id
        )
        if not row:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Scheduled post not found or "
                    "cannot be deleted (non-pending)"
                )
            )
        return {"deleted": True, "id": post_id}

    # ── Worker hook ─────────────────────────────────────
    async def process_due_posts(self):
        """
        Called by the scheduler worker.
        Picks up all pending posts whose time has come,
        attempts to publish them, and updates status.
        """
        now = datetime.now(timezone.utc)
        due_posts = await scheduler_repository.get_due_posts(now)

        results = {"published": 0, "failed": 0}

        for post in due_posts:
            try:
                await self._publish_post(post)
                await scheduler_repository.mark_published(
                    str(post["id"]), now
                )
                # Keep content status in sync
                if post["content_id"]:
                    await content_repository.update_content_status(
                        str(post["content_id"]),
                        str(post["user_id"]),
                        "posted"
                    )
                results["published"] += 1
                logger.info(
                    "Published post id=%s platform=%s",
                    post["id"], post["platform"]
                )

            except Exception as exc:
                await scheduler_repository.mark_failed(
                    str(post["id"]), str(exc)
                )
                results["failed"] += 1
                logger.error(
                    "Failed to publish post id=%s: %s",
                    post["id"], exc
                )

        return results

    async def _publish_post(self, post: dict):
        """
        Platform publishing stub.
        Replace each branch with real OAuth API calls
        once Step 9 (OAuth) is implemented.
        """
        platform = post["platform"].lower()

        if platform == "instagram":
            await self._publish_instagram(post)
        elif platform == "facebook":
            await self._publish_facebook(post)
        elif platform in ("x", "twitter"):
            await self._publish_twitter(post)
        elif platform == "linkedin":
            await self._publish_linkedin(post)
        elif platform == "tiktok":
            await self._publish_tiktok(post)
        else:
            # Generic mock — always succeeds
            logger.warning(
                "No publisher for platform=%s, mock-publishing",
                platform
            )

    # ── Platform stubs (replace with real SDK calls) ────
    async def _publish_instagram(self, post: dict):
        logger.info("[MOCK] Instagram publish post=%s", post["id"])

    async def _publish_facebook(self, post: dict):
        logger.info("[MOCK] Facebook publish post=%s", post["id"])

    async def _publish_twitter(self, post: dict):
        logger.info("[MOCK] Twitter/X publish post=%s", post["id"])

    async def _publish_linkedin(self, post: dict):
        logger.info("[MOCK] LinkedIn publish post=%s", post["id"])

    async def _publish_tiktok(self, post: dict):
        logger.info("[MOCK] TikTok publish post=%s", post["id"])


scheduler_service = SchedulerService()
