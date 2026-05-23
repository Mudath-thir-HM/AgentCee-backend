from fastapi import APIRouter, Depends

from app.middlewares.auth import (
    get_current_user
)
from app.schemas.content_schema import (
    GenerateContentSchema
)
from app.controllers.content_controller import (
    content_controller
)

router = APIRouter(
    prefix="/content",
    tags=["Content"]
)


@router.post("/generate")
async def generate_content(
    body: GenerateContentSchema,
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        content_controller
        .generate_content(
            user_id,
            body
        )
    )