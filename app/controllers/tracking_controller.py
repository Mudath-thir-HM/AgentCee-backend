from app.services.tracking_service import tracking_service


class TrackingController:

    # ── Rules ──────────────────────────────────────────
    async def create_rule(self, user_id: str, body):
        return await tracking_service.create_rule(
            user_id=user_id,
            type=body.type,
            value=body.value,
            platform=body.platform
        )

    async def get_rules(self, user_id: str, active_only: bool = True):
        return await tracking_service.get_rules(user_id, active_only)

    async def toggle_rule(self, rule_id: str, user_id: str, is_active: bool):
        return await tracking_service.toggle_rule(rule_id, user_id, is_active)

    async def delete_rule(self, rule_id: str, user_id: str):
        return await tracking_service.delete_rule(rule_id, user_id)

    # ── Events ─────────────────────────────────────────
    async def ingest_event(self, user_id: str, body):
        return await tracking_service.ingest_event(
            user_id=user_id,
            platform=body.platform,
            event_type=body.event_type,
            content=body.content,
            author_username=body.author_username,
            external_id=body.external_id
        )

    async def get_events(
        self,
        user_id: str,
        platform=None,
        event_type=None,
        unread_only=False,
        limit=50
    ):
        return await tracking_service.get_events(
            user_id=user_id,
            platform=platform,
            event_type=event_type,
            unread_only=unread_only,
            limit=limit
        )

    async def mark_event_read(self, event_id: str, user_id: str):
        return await tracking_service.mark_event_read(event_id, user_id)

    async def mark_all_read(self, user_id: str):
        return await tracking_service.mark_all_read(user_id)

    # ── AI ─────────────────────────────────────────────
    async def suggest_reply(self, user_id: str, body):
        return await tracking_service.suggest_reply(
            user_id=user_id,
            platform=body.platform,
            message=body.message,
            author=body.author,
            context=getattr(body, "context", "")
        )


tracking_controller = TrackingController()
