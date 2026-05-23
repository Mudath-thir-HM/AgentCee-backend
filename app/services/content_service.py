from app.agents.content_agent import content_agent
from app.repositories.content_repository import (
    content_repository
)


class ContentService:

    async def generate_content(
        self,
        user_id: str,
        platform: str,
        content_type: str,
        prompt: str,
        tone: str
    ):
        try:
            ai_response = await (
                content_agent.generate_content(
                    platform=platform,
                    content_type=content_type,
                    prompt=prompt,
                    tone=tone
                )
            )

        except Exception:
            ai_response = {
                "generated_text":
                (
                    "AI content generation "
                    "temporarily unavailable"
                ),
                "hashtags": [],
                "call_to_action": ""
            }

        saved_content = await (
            content_repository
            .save_generated_content(
                user_id=user_id,
                platform=platform,
                content_type=content_type,
                prompt=prompt,
                generated_text=ai_response[
                    "generated_text"
                ],
                hashtags=ai_response[
                    "hashtags"
                ],
                call_to_action=ai_response[
                    "call_to_action"
                ]
            )
        )

        return saved_content


content_service = ContentService()