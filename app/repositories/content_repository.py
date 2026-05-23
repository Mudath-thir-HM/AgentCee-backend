from app.db.sql import fetch_one


class ContentRepository:

    async def save_generated_content(
        self,
        user_id: str,
        platform: str,
        content_type: str,
        prompt: str,
        generated_text: str,
        hashtags: list,
        call_to_action: str
    ):
        query = """
        INSERT INTO generated_assets (
            user_id,
            platform,
            content_type,
            prompt,
            generated_text,
            hashtags,
            call_to_action
        )
        VALUES (
            $1,$2,$3,$4,$5,$6,$7
        )
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
            call_to_action
        )


content_repository = ContentRepository()