from app.services.analytics_service import analytics_service
from app.schemas.analytics_schema import RecordAnalyticsSchema


class AnalyticsController:

    async def record(self, user_id: str, body: RecordAnalyticsSchema):
        return await analytics_service.record_analytics(
            user_id=user_id,
            scheduled_post_id=body.scheduled_post_id,
            platform=body.platform,
            likes=body.likes,
            impressions=body.impressions,
            reach=body.reach,
            engagement_rate=body.engagement_rate,
            clicks=body.clicks,
            shares=body.shares,
            comments=body.comments
        )

    async def get_overview(self, user_id: str):
        return await analytics_service.get_overview(user_id)

    async def get_weekly_engagement(self, user_id: str):
        return await analytics_service.get_weekly_engagement(user_id)

    async def get_platform_breakdown(self, user_id: str):
        return await analytics_service.get_platform_breakdown(user_id)

    async def get_platform_analytics(
        self, user_id: str, platform: str
    ):
        return await analytics_service.get_platform_analytics(
            user_id, platform
        )

    async def get_top_posts(self, user_id: str, limit: int = 5):
        return await analytics_service.get_top_posts(user_id, limit)

    async def get_suggestions(self, user_id: str):
        return await analytics_service.get_suggestions(user_id)


analytics_controller = AnalyticsController()
