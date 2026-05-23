from fastapi import (
    APIRouter,
    Depends
)

from app.middlewares.auth import (
    get_current_user
)

from app.schemas.onboarding import (
    ConnectPlatformSchema
)

from app.controllers.onboarding_controller import (
    onboarding_controller
)

router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding"]
)


@router.post("/connect")
async def connect_platform(
    payload: ConnectPlatformSchema,
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        onboarding_controller
        .connect_platform(
            user_id=user_id,
            platform=payload.platform,
            account_name=payload.account_name
        )
    )


@router.get("/platforms")
async def get_connected_platforms(
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        onboarding_controller
        .get_connected_platforms(
            user_id=user_id
        )
    )