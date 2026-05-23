from app.repositories.tracking_repository import tracking_repository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TrackingAgent:
    """
    Routes incoming social events to matching tracking rules
    and stores them as tracked_events.
    """

    async def process_event(
        self,
        user_id: str,
        platform: str,
        event_type: str,
        content: str,
        author_username: str,
        external_id: str | None = None
    ) -> dict | None:
        """
        Check if the event matches any active tracking rule.
        If yes, record it and return the event record.
        """
        matching_rules = await tracking_repository.find_matching_rules(
            user_id=user_id,
            content=content,
            platform=platform
        )

        rule_id = str(matching_rules[0]["id"]) if matching_rules else None

        # Always store — even unmatched events are useful for the inbox
        event = await tracking_repository.create_event(
            user_id=user_id,
            rule_id=rule_id,
            platform=platform,
            event_type=event_type,
            content=content,
            author_username=author_username,
            external_id=external_id
        )

        if rule_id:
            logger.info(
                "Tracked event matched rule=%s user=%s platform=%s",
                rule_id, user_id, platform
            )

        return dict(event)

    async def scan_content_for_rules(
        self,
        user_id: str,
        content: str,
        platform: str
    ) -> list[dict]:
        """Return which tracking rules match a given piece of content."""
        rows = await tracking_repository.find_matching_rules(
            user_id, content, platform
        )
        return [dict(r) for r in rows]


tracking_agent = TrackingAgent()
