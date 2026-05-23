from fastapi import HTTPException

from app.repositories.message_repository import message_repository
from app.agents.inbox_agent import inbox_agent
from app.agents.response_agent import response_agent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MessageService:

    async def get_messages(self, user_id: str):
        return await message_repository.get_messages(user_id)

    async def receive_message(
        self,
        user_id: str,
        platform: str,
        sender_name: str,
        message_text: str
    ):
        message = await message_repository.create_message(
            user_id=user_id,
            platform=platform,
            sender_name=sender_name,
            message_text=message_text
        )
        return dict(message)

    async def reply_message(
        self,
        message_id: str,
        user_id: str
    ):
        message = await message_repository.mark_replied(
            message_id, user_id
        )

        if not message:
            raise HTTPException(
                status_code=404,
                detail="Message not found"
            )

        return {"message": "Reply sent successfully"}

    async def get_ai_reply_suggestions(
        self,
        user_id: str,
        platform: str,
        message_text: str,
        sender_name: str,
        context: str = ""
    ):
        """
        Return AI-generated reply suggestions and sentiment
        for a given message.
        """
        suggestions = await inbox_agent.suggest_replies(
            platform=platform,
            message=message_text,
            author=sender_name,
            context=context
        )

        sentiment = await inbox_agent.classify_sentiment(message_text)

        return {
            "suggestions": suggestions,
            "sentiment": sentiment
        }

    async def auto_reply(
        self,
        user_id: str,
        platform: str,
        message_text: str,
        sender_name: str,
        interaction_type: str = "comment"
    ) -> str:
        """
        Generate a single auto-reply text via ResponseAgent.
        """
        return await response_agent.generate_auto_reply(
            platform=platform,
            interaction_type=interaction_type,
            content=message_text,
            author=sender_name
        )


message_service = MessageService()
