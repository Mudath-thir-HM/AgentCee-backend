from fastapi import APIRouter

from app.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema
)
from app.services.auth_service import (
    auth_service
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register(
    body: RegisterSchema
):
    return await (
        auth_service.register(
            body.email,
            body.password,
            body.company_name
        )
    )


@router.post("/login")
async def login(
    body: LoginSchema
):
    return await (
        auth_service.login(
            body.email,
            body.password
        )
    )