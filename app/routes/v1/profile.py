from fastapi import APIRouter, Depends

from app.controllers.profile_controller import (
    profile_controller
)

from app.schemas.profile import (
    ProfileUpdateSchema
)

from app.middlewares.auth import (
    get_current_user
)

router = APIRouter()


@router.get("/me")
async def get_me(
    user_id: str = Depends(
        get_current_user
    )
):
    return await profile_controller.get_me(
        user_id
    )


@router.patch("/me")
async def update_me(
    data: ProfileUpdateSchema,
    user_id: str = Depends(
        get_current_user
    )
):
    return await profile_controller.update_me(
        user_id,
        data
    )