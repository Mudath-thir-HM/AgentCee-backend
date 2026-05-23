from fastapi import APIRouter, Depends, Query

from app.middlewares.auth import get_current_user
from app.schemas.analytics_schema import RecordAnalyticsSchema
from app.controllers.analytics_controller import analytics_controller

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.post("/record")
async def record_analytics(
    body: RecordAnalyticsSchema,
    user_id: str = Depends(get_current_user)
):
    """
    Ingest analytics for a published post.
    Called by your platform webhooks or analytics worker.
    """
    return await analytics_controller.record(user_id, body)


@router.get("/overview")
async def get_overview(
    user_id: str = Depends(get_current_user)
):
    """Aggregate stats across all platforms."""
    return await analytics_controller.get_overview(user_id)


@router.get("/weekly-engagement")
async def get_weekly_engagement(
    user_id: str = Depends(get_current_user)
):
    """Daily engagement totals for the last 7 days (for the chart)."""
    return await analytics_controller.get_weekly_engagement(user_id)


@router.get("/platforms")
async def get_platform_breakdown(
    user_id: str = Depends(get_current_user)
):
    """Per-platform post count + engagement summary."""
    return await analytics_controller.get_platform_breakdown(user_id)


@router.get("/platforms/{platform}")
async def get_platform_analytics(
    platform: str,
    user_id: str = Depends(get_current_user)
):
    """Detailed analytics rows for a specific platform."""
    return await analytics_controller.get_platform_analytics(
        user_id, platform
    )


@router.get("/top-posts")
async def get_top_posts(
    limit: int = Query(default=5, ge=1, le=20),
    user_id: str = Depends(get_current_user)
):
    """Top performing posts ranked by total engagement."""
    return await analytics_controller.get_top_posts(user_id, limit)


@router.get("/suggestions")
async def get_suggestions(
    user_id: str = Depends(get_current_user)
):
    """AI-generated actionable suggestions based on performance data."""
    return await analytics_controller.get_suggestions(user_id)
