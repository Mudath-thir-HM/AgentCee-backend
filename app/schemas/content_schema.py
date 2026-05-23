from pydantic import BaseModel


class GenerateContentSchema(BaseModel):
    platform: str
    content_type: str
    prompt: str
    tone: str = "professional"


class ContentResponseSchema(BaseModel):
    generated_text: str
    hashtags: list[str]
    call_to_action: str