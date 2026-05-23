import json

from app.utils.openrouter import ask_openrouter
from app.utils.logger import get_logger

logger = get_logger(__name__)

ANALYTICS_PROMPT = """
You are an expert social media analyst.

Analyse the following performance data and return actionable suggestions.

Platform breakdown:
{platform_data}

Weekly engagement trend:
{weekly_trend}

Overview metrics:
{overview}

Return a JSON array of suggestion objects. Maximum 5 suggestions.
Each object must have:
{{
  "type": "tip" | "warning" | "insight",
  "message": "Concise actionable message (max 2 sentences)",
  "platform": "instagram" | "facebook" | "x" | "linkedin" | "tiktok" | null
}}

Return only the JSON array. No markdown, no preamble.
"""


class AnalyticsAgent:

    async def generate_suggestions(
        self,
        overview: dict,
        platform_breakdown: list[dict],
        weekly_trend: list[dict]
    ) -> list[dict]:
        prompt = ANALYTICS_PROMPT.format(
            overview=json.dumps(overview, default=str),
            platform_data=json.dumps(platform_breakdown, default=str),
            weekly_trend=json.dumps(weekly_trend, default=str)
        )

        try:
            response = await ask_openrouter(prompt=prompt)
            # Strip possible markdown fences
            cleaned = (
                response
                .strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            suggestions = json.loads(cleaned)
            if isinstance(suggestions, list):
                return suggestions
        except Exception as exc:
            logger.warning("AnalyticsAgent failed: %s", exc)

        # Fallback: rule-based suggestions
        return self._rule_based_suggestions(
            overview, platform_breakdown
        )

    def _rule_based_suggestions(
        self,
        overview: dict,
        platform_breakdown: list[dict]
    ) -> list[dict]:
        suggestions: list[dict] = []

        avg_eng = overview.get("avg_engagement_rate", 0)
        if avg_eng < 2.0:
            suggestions.append({
                "type": "warning",
                "message": (
                    "Your average engagement rate is below 2%. "
                    "Try using more questions and calls-to-action in your posts."
                ),
                "platform": None
            })
        elif avg_eng > 8.0:
            suggestions.append({
                "type": "insight",
                "message": (
                    f"Excellent! Your engagement rate of {avg_eng:.1f}% "
                    "is well above the industry average. Keep up this content style."
                ),
                "platform": None
            })

        if platform_breakdown:
            top = max(
                platform_breakdown,
                key=lambda x: x.get("avg_engagement_rate", 0)
            )
            suggestions.append({
                "type": "tip",
                "message": (
                    f"{top['platform'].capitalize()} is your best-performing platform. "
                    "Consider posting more frequently there."
                ),
                "platform": top["platform"]
            })

        reach = overview.get("total_reach", 0)
        if reach == 0:
            suggestions.append({
                "type": "tip",
                "message": (
                    "No reach data yet. Start scheduling and publishing posts "
                    "to see your analytics populate."
                ),
                "platform": None
            })

        if not suggestions:
            suggestions.append({
                "type": "tip",
                "message": (
                    "Post consistently at least 3-5 times per week "
                    "to build engagement momentum."
                ),
                "platform": None
            })

        return suggestions


analytics_agent = AnalyticsAgent()
