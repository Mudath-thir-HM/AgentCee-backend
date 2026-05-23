from fastapi import HTTPException

from app.repositories.message_repository import (
    message_repository
)


class MessageService:

    async def get_messages(
        self,
        user_id: str
    ):
        return await (
            message_repository
            .get_messages(user_id)
        )

    async def receive_message(
        self,
        user_id: str,
        platform: str,
        sender_name: str,
        message_text: str
    ):
        return await (
            message_repository
            .create_message(
                user_id=user_id,
                platform=platform,
                sender_name=sender_name,
                message_text=message_text
            )
        )

    async def reply_message(
        self,
        message_id: str,
        user_id: str
    ):
        message = await (
            message_repository
            .mark_replied(
                message_id,
                user_id
            )
        )

        if not message:
            raise HTTPException(
                status_code=404,
                detail="Message not found"
            )

        return {
            "message":
            "Reply sent successfully"
        }


message_service = MessageService()