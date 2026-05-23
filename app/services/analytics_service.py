from fastapi import HTTPException

from app.repositories.analytics_repository import (
    analytics_repository
)
from app.agents.analytics_agent import analytics_agent
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Mock data helpers (used when no real data exists) ──
_MOCK_WEEKLY = [
    {"day": "Mon", "engagement": 1400},
    {"day": "Tue", "engagement": 1560},
    {"day": "Wed", "engagement": 2200},
    {"day": "Thu", "engagement": 1700},
    {"day": "Fri", "engagement": 2500},
    {"day": "Sat", "engagement": 2980},
    {"day": "Sun", "engagement": 2820},
]

_MOCK_OVERVIEW = {
    "total_reach": 127500,
    "total_impressions": 280000,
    "avg_engagement_rate": 8.4,
    "total_likes": 9400,
    "total_shares": 1200,
    "total_comments": 870,
    "total_clicks": 3300,
    "posts_this_week": 7,
    "top_platform": "instagram",
    "growth_percentage": 12.5,
}

_MOCK_PLATFORMS = [
    {"platform": "instagram", "posts": 24, "total_likes": 4200,
     "total_impressions": 110000, "avg_engagement_rate": 9.1},
    {"platform": "facebook",  "posts": 18, "total_likes": 2800,
     "total_impressions": 95000,  "avg_engagement_rate": 7.2},
    {"platform": "x",         "posts": 32, "total_likes": 2400,
     "total_impressions": 75000,  "avg_engagement_rate": 6.8},
]


class AnalyticsService:

    # ── Record ──────────────────────────────────────────
    async def record_analytics(
        self,
        user_id: str,
        scheduled_post_id: str | None,
        platform: str,
        likes: int,
        impressions: int,
        reach: int,
        engagement_rate: float,
        clicks: int,
        shares: int,
        comments: int
    ):
        row = await analytics_repository.record_analytics(
            user_id=user_id,
            scheduled_post_id=scheduled_post_id,
            platform=platform,
            likes=likes,
            impressions=impressions,
            reach=reach,
            engagement_rate=engagement_rate,
            clicks=clicks,
            shares=shares,
            comments=comments
        )
        return dict(row)

    # ── Overview ────────────────────────────────────────
    async def get_overview(self, user_id: str):
        row = await analytics_repository.get_overview(user_id)
        posts_this_week = await analytics_repository.get_posts_this_week(
            user_id
        )
        platform_rows = await analytics_repository.get_platform_breakdown(
            user_id
        )

        # If no real data, return mock for demo purposes
        if not row or row["total_records"] == 0:
            return _MOCK_OVERVIEW

        platforms = [dict(r) for r in platform_rows]
        top_platform = (
            platforms[0]["platform"] if platforms else "—"
        )

        overview = dict(row)
        overview["posts_this_week"] = posts_this_week
        overview["top_platform"] = top_platform
        overview["growth_percentage"] = 0.0   # requires historical baseline
        return overview

    # ── Weekly trend ────────────────────────────────────
    async def get_weekly_engagement(self, user_id: str):
        rows = await analytics_repository.get_weekly_engagement(user_id)

        if not rows:
            return _MOCK_WEEKLY

        return [dict(r) for r in rows]

    # ── Platform ────────────────────────────────────────
    async def get_platform_breakdown(self, user_id: str):
        rows = await analytics_repository.get_platform_breakdown(user_id)

        if not rows:
            return _MOCK_PLATFORMS

        return [dict(r) for r in rows]

    async def get_platform_analytics(
        self,
        user_id: str,
        platform: str
    ):
        rows = await analytics_repository.get_platform_analytics(
            user_id, platform
        )
        return [dict(r) for r in rows]

    # ── Top posts ───────────────────────────────────────
    async def get_top_posts(self, user_id: str, limit: int = 5):
        rows = await analytics_repository.get_top_posts(user_id, limit)
        return [dict(r) for r in rows]

    # ── AI Suggestions ──────────────────────────────────
    async def get_suggestions(self, user_id: str):
        overview = await self.get_overview(user_id)
        platform_breakdown = await self.get_platform_breakdown(user_id)
        weekly_trend = await self.get_weekly_engagement(user_id)

        suggestions = await analytics_agent.generate_suggestions(
            overview=overview,
            platform_breakdown=platform_breakdown,
            weekly_trend=weekly_trend
        )

        logger.info(
            "Generated %d suggestions for user=%s",
            len(suggestions), user_id
        )
        return suggestions


analytics_service = AnalyticsService()
