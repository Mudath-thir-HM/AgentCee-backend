from fastapi import (
    APIRouter,
    Depends
)

from app.middlewares.auth import (
    get_current_user
)

from app.controllers.social_controller import (
    social_controller
)

from app.schemas.social_schema import (
    ConnectSocialSchema,
    ReceiveInteractionSchema
)

router = APIRouter(
    prefix="/social",
    tags=["Social"]
)


@router.post("/connect")
async def connect_account(
    data: ConnectSocialSchema,
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        social_controller
        .connect_account(
            user_id,
            data
        )
    )


@router.get("/accounts")
async def get_accounts(
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        social_controller
        .get_accounts(
            user_id
        )
    )


@router.delete("/{account_id}")
async def disconnect_account(
    account_id: str,
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        social_controller
        .disconnect_account(
            account_id,
            user_id
        )
    )

@router.post("/interactions")
async def receive_interaction(
    data: ReceiveInteractionSchema,
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        social_controller
        .receive_interaction(
            user_id=user_id,
            platform=data.platform,
            interaction_type=data.interaction_type,
            content=data.content,
            author_username=data.author_username,
            external_id=data.external_id
        )
    )


@router.get("/interactions")
async def get_interactions(
    user_id: str = Depends(
        get_current_user
    )
):
    return await (
        social_controller
        .get_interactions(user_id)
    )