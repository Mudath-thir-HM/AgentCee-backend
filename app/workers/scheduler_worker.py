"""
Scheduler Worker
================
Polls for due scheduled posts and publishes them.

Usage (run directly):
    python -m app.workers.scheduler_worker

Or integrate with APScheduler / Celery for production.
"""

import asyncio
from datetime import datetime, timezone

from app.db.connection import db
from app.services.scheduler_service import scheduler_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

POLL_INTERVAL_SECONDS = 60   # check every minute


async def run():
    logger.info("Scheduler worker starting…")
    await db.connect()

    try:
        while True:
            try:
                results = await scheduler_service.process_due_posts()

                if results["published"] or results["failed"]:
                    logger.info(
                        "Worker cycle complete — published=%d failed=%d",
                        results["published"],
                        results["failed"]
                    )

            except Exception as exc:
                logger.error("Worker cycle error: %s", exc)

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    finally:
        await db.disconnect()
        logger.info("Scheduler worker stopped.")


if __name__ == "__main__":
    asyncio.run(run())
