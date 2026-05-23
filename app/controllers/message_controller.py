from app.services.message_service import (
    message_service
)


class MessageController:

    async def get_messages(
        self,
        user_id: str
    ):
        return await (
            message_service
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
            message_service
            .receive_message(
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
        return await (
            message_service
            .reply_message(
                message_id,
                user_id
            )
        )


message_controller = MessageController()