"""
Tracking Worker
===============
Processes incoming platform webhooks for mentions, hashtags,
and comments and routes them through the tracking pipeline.

In production, replace the mock event loop below with:
  - Instagram Webhooks
  - Facebook Graph API webhooks
  - Twitter/X filtered stream
  - LinkedIn webhooks

Usage:
    python -m app.workers.tracking_worker
"""

import asyncio

from app.db.connection import db
from app.agents.tracking_agent import tracking_agent
from app.utils.logger import get_logger

logger = get_logger(__name__)

POLL_INTERVAL_SECONDS = 30


class TrackingWorker:
    """
    Consumes events from a queue (or webhooks) and processes them.
    Extend _pull_platform_events per platform once OAuth is in place.
    """

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()

    async def enqueue(self, event: dict):
        """Push an event onto the processing queue."""
        await self._queue.put(event)

    async def _process_event(self, event: dict):
        try:
            result = await tracking_agent.process_event(
                user_id=event["user_id"],
                platform=event["platform"],
                event_type=event["event_type"],
                content=event["content"],
                author_username=event["author_username"],
                external_id=event.get("external_id")
            )
            logger.info(
                "Processed tracking event id=%s",
                result.get("id") if result else "?"
            )
        except Exception as exc:
            logger.error("Failed processing tracking event: %s", exc)

    async def _consumer(self):
        """Continuously drain the queue."""
        while True:
            event = await self._queue.get()
            await self._process_event(event)
            self._queue.task_done()

    # ── Platform polling stubs ─────────────────────────
    async def _pull_instagram_events(self):
        """Replace with Instagram Webhooks / polling."""
        pass

    async def _pull_twitter_stream(self):
        """Replace with Twitter Filtered Stream API."""
        pass

    async def _pull_facebook_events(self):
        """Replace with Facebook Graph API webhooks."""
        pass

    async def run(self):
        logger.info("Tracking worker starting…")
        await db.connect()

        consumer = asyncio.create_task(self._consumer())

        try:
            while True:
                await asyncio.gather(
                    self._pull_instagram_events(),
                    self._pull_twitter_stream(),
                    self._pull_facebook_events(),
                    return_exceptions=True
                )
                await asyncio.sleep(POLL_INTERVAL_SECONDS)

        finally:
            consumer.cancel()
            await db.disconnect()
            logger.info("Tracking worker stopped.")


tracking_worker = TrackingWorker()


if __name__ == "__main__":
    asyncio.run(tracking_worker.run())
