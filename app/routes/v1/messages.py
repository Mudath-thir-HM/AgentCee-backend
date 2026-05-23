from fastapi import (
    APIRouter,
    Depends
)

from app.middlewares.auth import (
    get_current_user
)

from app.controllers.message_controller import (
    message_controller
)

from app.schemas.message_schema import (
    ReceiveMessageSchema,
    ReplyMessageSchema
)

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.get("/")
async def get_messages(
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        message_controller
        .get_messages(user_id)
    )


@router.post("/receive")
async def receive_message(
    data: ReceiveMessageSchema,
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        message_controller
        .receive_message(
            user_id=user_id,
            platform=data.platform,
            sender_name=data.sender_name,
            message_text=data.message_text
        )
    )


@router.post("/reply")
async def reply_message(
    data: ReplyMessageSchema,
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        message_controller
        .reply_message(
            message_id=data.message_id,
            user_id=user_id
        )
    )