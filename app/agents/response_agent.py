import json

from app.utils.openrouter import ask_openrouter
from app.utils.logger import get_logger

logger = get_logger(__name__)

AUTO_REPLY_PROMPT = """
You are a professional social media manager.

Compose a single, concise reply to the following social media interaction.

Platform: {platform}
Interaction type: {interaction_type}
Their message: "{content}"
Author: @{author}

Rules:
- Keep it under 280 characters for X/Twitter, 500 for others.
- Be warm, professional, and on-brand.
- Do NOT mention being an AI.
- End with a subtle CTA when appropriate.

Return ONLY the reply text. No quotes, no preamble.
"""


class ResponseAgent:

    async def generate_auto_reply(
        self,
        platform: str,
        interaction_type: str,
        content: str,
        author: str
    ) -> str:
        char_limit = 280 if platform.lower() in ("x", "twitter") else 500

        prompt = AUTO_REPLY_PROMPT.format(
            platform=platform,
            interaction_type=interaction_type,
            content=content,
            author=author,
            char_limit=char_limit
        )

        try:
            reply = await ask_openrouter(prompt=prompt)
            reply = reply.strip().strip('"').strip("'")
            return reply[:char_limit]

        except Exception as exc:
            logger.warning(
                "ResponseAgent.generate_auto_reply failed: %s", exc
            )
            return (
                "Thank you for your message! "
                "We'll get back to you soon. 🙌"
            )


response_agent = ResponseAgent()
