from pydantic import BaseModel
from typing import Optional


class ProfileUpdateSchema(BaseModel):
    company_name: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileResponseSchema(BaseModel):
    id: str
    company_name: str | None
    avatar_url: str | None
    connected_platforms: list[str]