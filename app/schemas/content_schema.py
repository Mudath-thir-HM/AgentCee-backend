from pydantic import BaseModel
from typing import Optional


class GenerateContentSchema(BaseModel):
    platform: str
    content_type: str
    prompt: str
    tone: str = "professional"


class ContentUpdateSchema(BaseModel):
    generated_text: Optional[str] = None
    hashtags: Optional[list[str]] = None
    call_to_action: Optional[str] = None


class ContentStatusSchema(BaseModel):
    status: str  # draft | scheduled | posted | archived


class ContentResponseSchema(BaseModel):
    id: str
    user_id: str
    platform: str
    content_type: str
    prompt: str
    generated_text: str
    hashtags: list[str]
    call_to_action: str
    status: str
    image_url: Optional[str]
    created_at: str
