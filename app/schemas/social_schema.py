from pydantic import BaseModel
from typing import Optional


class ConnectSocialSchema(BaseModel):
    platform: str
    account_name: str
    account_id: str


class SocialResponseSchema(BaseModel):
    id: str
    platform: str
    account_name: Optional[str]
    account_id: Optional[str]
    is_active: bool
    
class ReceiveInteractionSchema(
    BaseModel
):
    platform: str
    interaction_type: str
    content: str
    author_username: str
    external_id: Optional[str] = None