from app.db.sql import fetch_one, fetch_all, execute


class ContentRepository:

    # ── Create ─────────────────────────────────────────
    async def save_generated_content(
        self,
        user_id: str,
        platform: str,
        content_type: str,
        prompt: str,
        generated_text: str,
        hashtags: list,
        call_to_action: str,
        image_url: str | None = None
    ):
        query = """
        INSERT INTO generated_assets (
            user_id,
            platform,
            content_type,
            prompt,
            generated_text,
            hashtags,
            call_to_action,
            image_url,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'draft')
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            platform,
            content_type,
            prompt,
            generated_text,
            hashtags,
            call_to_action,
            image_url
        )

    # ── Read ───────────────────────────────────────────
    async def get_all_content(
        self,
        user_id: str,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0
    ):
        conditions = ["user_id = $1"]
        params: list = [user_id]
        idx = 2

        if platform:
            conditions.append(f"platform = ${idx}")
            params.append(platform)
            idx += 1

        if status:
            conditions.append(f"status = ${idx}")
            params.append(status)
            idx += 1

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT *
        FROM generated_assets
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${idx} OFFSET ${idx + 1}
        """

        params += [limit, offset]
        return await fetch_all(query, *params)

    async def get_content_by_id(
        self,
        content_id: str,
        user_id: str
    ):
        query = """
        SELECT *
        FROM generated_assets
        WHERE id = $1
        AND user_id = $2
        """

        return await fetch_one(query, content_id, user_id)

    # ── Update ─────────────────────────────────────────
    async def update_content_status(
        self,
        content_id: str,
        user_id: str,
        status: str
    ):
        query = """
        UPDATE generated_assets
        SET status = $3
        WHERE id = $1
        AND user_id = $2
        RETURNING *
        """

        return await fetch_one(
            query,
            content_id,
            user_id,
            status
        )

    async def update_content(
        self,
        content_id: str,
        user_id: str,
        generated_text: str | None = None,
        hashtags: list | None = None,
        call_to_action: str | None = None
    ):
        query = """
        UPDATE generated_assets
        SET
            generated_text = COALESCE($3, generated_text),
            hashtags       = COALESCE($4, hashtags),
            call_to_action = COALESCE($5, call_to_action)
        WHERE id = $1
        AND user_id = $2
        RETURNING *
        """

        return await fetch_one(
            query,
            content_id,
            user_id,
            generated_text,
            hashtags,
            call_to_action
        )

    # ── Delete ─────────────────────────────────────────
    async def delete_content(
        self,
        content_id: str,
        user_id: str
    ):
        query = """
        DELETE FROM generated_assets
        WHERE id = $1
        AND user_id = $2
        RETURNING id
        """

        return await fetch_one(query, content_id, user_id)


content_repository = ContentRepository()
