import json

from app.utils.openrouter import ask_openrouter
from app.utils.prompts import CONTENT_PROMPT


class ContentAgent:

    async def generate_content(
        self,
        platform: str,
        content_type: str,
        prompt: str,
        tone: str
    ):
        final_prompt = CONTENT_PROMPT.format(
            platform=platform,
            content_type=content_type,
            prompt=prompt,
            tone=tone
        )

        response = await ask_openrouter(
            prompt=final_prompt
        )

        try:
            return json.loads(response)

        except Exception:
            return {
                "generated_text": response,
                "hashtags": [],
                "call_to_action": ""
            }


content_agent = ContentAgent()