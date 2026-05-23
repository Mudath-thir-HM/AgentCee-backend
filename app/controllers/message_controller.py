from app.services.message_service import message_service


class MessageController:

    async def get_messages(self, user_id: str):
        return await message_service.get_messages(user_id)

    async def receive_message(
        self, user_id, platform, sender_name, message_text
    ):
        return await message_service.receive_message(
            user_id=user_id,
            platform=platform,
            sender_name=sender_name,
            message_text=message_text
        )

    async def reply_message(self, message_id, user_id):
        return await message_service.reply_message(message_id, user_id)

    async def get_ai_suggestions(self, user_id: str, body):
        return await message_service.get_ai_reply_suggestions(
            user_id=user_id,
            platform=body.platform,
            message_text=body.message_text,
            sender_name=body.sender_name,
            context=getattr(body, "context", "")
        )

    async def auto_reply(self, user_id: str, body):
        text = await message_service.auto_reply(
            user_id=user_id,
            platform=body.platform,
            message_text=body.message_text,
            sender_name=body.sender_name,
            interaction_type=getattr(body, "interaction_type", "comment")
        )
        return {"reply": text}


message_controller = MessageController()
