from pydantic import BaseModel


class ReceiveMessageSchema(BaseModel):
    platform: str
    sender_name: str
    message_text: str


class ReplyMessageSchema(BaseModel):
    message_id: str
    reply_text: str