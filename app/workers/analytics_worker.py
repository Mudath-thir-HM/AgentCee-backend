"""
Analytics Worker
================
Periodically fetches post performance from connected platforms
and stores them in post_analytics.

Currently uses mock data; replace each platform section
with real API calls once OAuth tokens are stored (Step 9).

Usage:
    python -m app.workers.analytics_worker
"""

import asyncio
import random
from datetime import datetime, timezone

from app.db.connection import db
from app.db.sql import fetch_all
from app.services.analytics_service import analytics_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

POLL_INTERVAL_SECONDS = 3600   # every hour


async def fetch_platform_analytics(
    user_id: str,
    post_id: str,
    platform: str
) -> dict:
    """
    Stub: replace with real platform API call.
    Each platform SDK call goes here after OAuth is integrated.
    """
    # Simulated data — remove once real APIs are wired
    return {
        "likes":           random.randint(10, 500),
        "impressions":     random.randint(500, 10000),
        "reach":           random.randint(300, 8000),
        "engagement_rate": round(random.uniform(1.5, 12.0), 2),
        "clicks":          random.randint(5, 200),
        "shares":          random.randint(0, 100),
        "comments":        random.randint(0, 80)
    }


async def run_once():
    """Fetch analytics for all recently published posts."""
    # Get posts published in the last 24 hours
    query = """
    SELECT id, user_id, platform
    FROM scheduled_posts
    WHERE status = 'published'
    AND published_at >= NOW() - INTERVAL '24 hours'
    """

    posts = await fetch_all(query)

    if not posts:
        logger.info("Analytics worker: no recent posts to analyse")
        return

    for post in posts:
        try:
            stats = await fetch_platform_analytics(
                user_id=str(post["user_id"]),
                post_id=str(post["id"]),
                platform=post["platform"]
            )

            await analytics_service.record_analytics(
                user_id=str(post["user_id"]),
                scheduled_post_id=str(post["id"]),
                platform=post["platform"],
                **stats
            )

            logger.info(
                "Analytics recorded post=%s platform=%s",
                post["id"], post["platform"]
            )

        except Exception as exc:
            logger.error(
                "Failed analytics for post=%s: %s",
                post["id"], exc
            )


async def run():
    logger.info("Analytics worker starting…")
    await db.connect()

    try:
        while True:
            await run_once()
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    finally:
        await db.disconnect()
        logger.info("Analytics worker stopped.")


if __name__ == "__main__":
    asyncio.run(run())
