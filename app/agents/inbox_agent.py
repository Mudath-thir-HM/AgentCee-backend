import json

from app.utils.openrouter import ask_openrouter
from app.utils.logger import get_logger

logger = get_logger(__name__)

REPLY_SUGGESTION_PROMPT = """
You are a social media community manager.

Someone has left the following comment/message on a post:

Platform: {platform}
Context (post they commented on): {context}
Their message: "{message}"
Author: @{author}

Suggest 3 short, friendly, on-brand reply options.

Return ONLY a JSON array of strings. No markdown, no preamble.
Example: ["Thanks so much! 🙌", "Glad you enjoyed it!", "Reach out to us at ..."]
"""

SENTIMENT_PROMPT = """
Classify the sentiment of the following social media message as one of:
positive | neutral | negative | question | spam

Message: "{message}"

Return ONLY the single word classification.
"""


class InboxAgent:

    async def suggest_replies(
        self,
        platform: str,
        message: str,
        author: str,
        context: str = ""
    ) -> list[str]:
        prompt = REPLY_SUGGESTION_PROMPT.format(
            platform=platform,
            message=message,
            author=author,
            context=context or "N/A"
        )

        try:
            response = await ask_openrouter(prompt=prompt)
            cleaned = (
                response.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            suggestions = json.loads(cleaned)
            if isinstance(suggestions, list):
                return suggestions[:3]
        except Exception as exc:
            logger.warning("InboxAgent.suggest_replies failed: %s", exc)

        return [
            "Thanks for reaching out! 😊",
            "We appreciate your comment!",
            "Feel free to DM us for more details."
        ]

    async def classify_sentiment(self, message: str) -> str:
        prompt = SENTIMENT_PROMPT.format(message=message)

        try:
            result = await ask_openrouter(prompt=prompt)
            sentiment = result.strip().lower()
            allowed = {"positive", "neutral", "negative", "question", "spam"}
            return sentiment if sentiment in allowed else "neutral"
        except Exception as exc:
            logger.warning("InboxAgent.classify_sentiment failed: %s", exc)
            return "neutral"


inbox_agent = InboxAgent()
