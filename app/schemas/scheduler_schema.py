from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class CreateScheduledPostSchema(BaseModel):
    content_id: Optional[str] = None
    platform: str
    post_text: str
    scheduled_for: datetime

    @field_validator("scheduled_for")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        # Ensure tz-aware comparison
        if v.tzinfo is None:
            from datetime import timezone
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("scheduled_for must be in the future")
        return v


class UpdateScheduledPostSchema(BaseModel):
    post_text: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    status: Optional[str] = None   # pending | cancelled


class ScheduledPostResponseSchema(BaseModel):
    id: str
    user_id: str
    content_id: Optional[str]
    platform: str
    post_text: str
    scheduled_for: datetime
    status: str
    published_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
