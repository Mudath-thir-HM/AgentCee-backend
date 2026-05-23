from app.db.sql import fetch_one, fetch_all, execute


class TrackingRepository:

    # ── Rules ──────────────────────────────────────────
    async def create_rule(
        self,
        user_id: str,
        type: str,
        value: str,
        platform: str | None
    ):
        query = """
        INSERT INTO tracking_rules (
            user_id, type, value, platform
        )
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (user_id, type, value, platform)
        DO UPDATE SET is_active = TRUE
        RETURNING *
        """
        return await fetch_one(query, user_id, type, value, platform)

    async def get_rules(
        self,
        user_id: str,
        active_only: bool = True
    ):
        query = """
        SELECT *
        FROM tracking_rules
        WHERE user_id = $1
        {filter}
        ORDER BY created_at DESC
        """.format(filter="AND is_active = TRUE" if active_only else "")

        return await fetch_all(query, user_id)

    async def toggle_rule(
        self,
        rule_id: str,
        user_id: str,
        is_active: bool
    ):
        query = """
        UPDATE tracking_rules
        SET is_active = $3
        WHERE id = $1
        AND user_id = $2
        RETURNING *
        """
        return await fetch_one(query, rule_id, user_id, is_active)

    async def delete_rule(self, rule_id: str, user_id: str):
        query = """
        DELETE FROM tracking_rules
        WHERE id = $1 AND user_id = $2
        RETURNING id
        """
        return await fetch_one(query, rule_id, user_id)

    async def find_matching_rules(
        self,
        user_id: str,
        content: str,
        platform: str
    ):
        """Return rules whose value appears in content."""
        query = """
        SELECT *
        FROM tracking_rules
        WHERE user_id = $1
        AND is_active = TRUE
        AND (platform IS NULL OR platform = $2)
        AND POSITION(value IN LOWER($3)) > 0
        """
        return await fetch_all(query, user_id, platform, content.lower())

    # ── Events ─────────────────────────────────────────
    async def create_event(
        self,
        user_id: str,
        rule_id: str | None,
        platform: str,
        event_type: str,
        content: str,
        author_username: str,
        external_id: str | None
    ):
        query = """
        INSERT INTO tracked_events (
            user_id,
            rule_id,
            platform,
            event_type,
            content,
            author_username,
            external_id
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7)
        RETURNING *
        """
        return await fetch_one(
            query,
            user_id,
            rule_id,
            platform,
            event_type,
            content,
            author_username,
            external_id
        )

    async def get_events(
        self,
        user_id: str,
        platform: str | None = None,
        event_type: str | None = None,
        unread_only: bool = False,
        limit: int = 50
    ):
        conditions = ["user_id = $1"]
        params: list = [user_id]
        idx = 2

        if platform:
            conditions.append(f"platform = ${idx}")
            params.append(platform)
            idx += 1

        if event_type:
            conditions.append(f"event_type = ${idx}")
            params.append(event_type)
            idx += 1

        if unread_only:
            conditions.append("is_read = FALSE")

        where = " AND ".join(conditions)

        query = f"""
        SELECT *
        FROM tracked_events
        WHERE {where}
        ORDER BY created_at DESC
        LIMIT ${idx}
        """
        params.append(limit)
        return await fetch_all(query, *params)

    async def mark_read(
        self,
        event_id: str,
        user_id: str
    ):
        query = """
        UPDATE tracked_events
        SET is_read = TRUE
        WHERE id = $1
        AND user_id = $2
        RETURNING *
        """
        return await fetch_one(query, event_id, user_id)

    async def mark_all_read(self, user_id: str):
        query = """
        UPDATE tracked_events
        SET is_read = TRUE
        WHERE user_id = $1
        AND is_read = FALSE
        """
        await execute(query, user_id)


tracking_repository = TrackingRepository()
