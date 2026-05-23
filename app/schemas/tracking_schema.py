from pydantic import BaseModel, field_validator
from typing import Optional, Literal


class CreateTrackingRuleSchema(BaseModel):
    type: Literal["hashtag", "mention", "keyword"]
    value: str
    platform: Optional[str] = None   # None = all platforms

    @field_validator("value")
    @classmethod
    def normalise_value(cls, v: str) -> str:
        v = v.strip().lower()
        # Strip leading # or @ — we store the bare value
        v = v.lstrip("#@")
        if not v:
            raise ValueError("value cannot be empty")
        return v


class TrackingRuleResponseSchema(BaseModel):
    id: str
    user_id: str
    type: str
    value: str
    platform: Optional[str]
    is_active: bool


class IngestTrackedEventSchema(BaseModel):
    platform: str
    event_type: str       # comment | mention | hashtag | dm
    content: str
    author_username: str
    external_id: Optional[str] = None


class TrackedEventResponseSchema(BaseModel):
    id: str
    user_id: str
    rule_id: Optional[str]
    platform: str
    event_type: str
    content: str
    author_username: str
    external_id: Optional[str]
    is_read: bool
