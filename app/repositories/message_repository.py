from app.db.sql import (
    fetch_all,
    fetch_one
)


class MessageRepository:

    async def get_messages(
        self,
        user_id: str
    ):
        query = """
        SELECT *
        FROM messages
        WHERE user_id = $1
        ORDER BY created_at DESC
        """

        return await fetch_all(
            query,
            user_id
        )

    async def create_message(
        self,
        user_id: str,
        platform: str,
        sender_name: str,
        message_text: str
    ):
        query = """
        INSERT INTO messages (
            user_id,
            platform,
            sender_name,
            message_text
        )
        VALUES (
            $1, $2, $3, $4
        )
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            platform,
            sender_name,
            message_text
        )

    async def mark_replied(
        self,
        message_id: str,
        user_id: str
    ):
        query = """
        UPDATE messages
        SET is_replied = TRUE
        WHERE id = $1
        AND user_id = $2
        RETURNING *
        """

        return await fetch_one(
            query,
            message_id,
            user_id
        )


message_repository = MessageRepository()