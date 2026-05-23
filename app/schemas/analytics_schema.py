from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecordAnalyticsSchema(BaseModel):
    scheduled_post_id: Optional[str] = None
    platform: str
    likes: int = 0
    impressions: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    clicks: int = 0
    shares: int = 0
    comments: int = 0


class AnalyticsOverviewSchema(BaseModel):
    total_reach: int
    total_impressions: int
    avg_engagement_rate: float
    total_likes: int
    total_shares: int
    total_comments: int
    total_clicks: int
    posts_this_week: int
    top_platform: str
    growth_percentage: float


class PlatformBreakdownSchema(BaseModel):
    platform: str
    posts: int
    total_likes: int
    total_impressions: int
    avg_engagement_rate: float


class WeeklyEngagementPoint(BaseModel):
    day: str
    engagement: int


class AnalyticsSuggestionSchema(BaseModel):
    type: str           # tip | warning | insight
    message: str
    platform: Optional[str] = None
