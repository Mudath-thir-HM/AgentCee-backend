from datetime import datetime
from app.db.sql import fetch_one, fetch_all, execute


class SchedulerRepository:

    async def create_scheduled_post(
        self,
        user_id: str,
        content_id: str | None,
        platform: str,
        post_text: str,
        scheduled_for: datetime
    ):
        query = """
        INSERT INTO scheduled_posts (
            user_id,
            content_id,
            platform,
            post_text,
            scheduled_for,
            status
        )
        VALUES ($1, $2, $3, $4, $5, 'pending')
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            content_id,
            platform,
            post_text,
            scheduled_for
        )

    async def get_scheduled_posts(
        self,
        user_id: str,
        status: str | None = None,
        platform: str | None = None
    ):
        conditions = ["user_id = $1"]
        params: list = [user_id]
        idx = 2

        if status:
            conditions.append(f"status = ${idx}")
            params.append(status)
            idx += 1

        if platform:
            conditions.append(f"platform = ${idx}")
            params.append(platform)
            idx += 1

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT *
        FROM scheduled_posts
        WHERE {where_clause}
        ORDER BY scheduled_for ASC
        """

        return await fetch_all(query, *params)

    async def get_post_by_id(
        self,
        post_id: str,
        user_id: str
    ):
        query = """
        SELECT *
        FROM scheduled_posts
        WHERE id = $1
        AND user_id = $2
        """
        return await fetch_one(query, post_id, user_id)

    async def get_due_posts(self, now: datetime):
        """Fetch all pending posts whose scheduled_for <= now."""
        query = """
        SELECT *
        FROM scheduled_posts
        WHERE status = 'pending'
        AND scheduled_for <= $1
        ORDER BY scheduled_for ASC
        LIMIT 100
        """
        return await fetch_all(query, now)

    async def update_post(
        self,
        post_id: str,
        user_id: str,
        post_text: str | None,
        scheduled_for: datetime | None,
        status: str | None
    ):
        query = """
        UPDATE scheduled_posts
        SET
            post_text    = COALESCE($3, post_text),
            scheduled_for = COALESCE($4, scheduled_for),
            status       = COALESCE($5, status),
            updated_at   = NOW()
        WHERE id = $1
        AND user_id = $2
        RETURNING *
        """

        return await fetch_one(
            query,
            post_id,
            user_id,
            post_text,
            scheduled_for,
            status
        )

    async def mark_published(
        self,
        post_id: str,
        published_at: datetime
    ):
        query = """
        UPDATE scheduled_posts
        SET
            status       = 'published',
            published_at = $2,
            updated_at   = NOW()
        WHERE id = $1
        RETURNING *
        """
        return await fetch_one(query, post_id, published_at)

    async def mark_failed(
        self,
        post_id: str,
        error_message: str
    ):
        query = """
        UPDATE scheduled_posts
        SET
            status        = 'failed',
            error_message = $2,
            updated_at    = NOW()
        WHERE id = $1
        RETURNING *
        """
        return await fetch_one(query, post_id, error_message)

    async def delete_post(
        self,
        post_id: str,
        user_id: str
    ):
        query = """
        DELETE FROM scheduled_posts
        WHERE id = $1
        AND user_id = $2
        AND status = 'pending'
        RETURNING id
        """
        return await fetch_one(query, post_id, user_id)


scheduler_repository = SchedulerRepository()
