from fastapi import HTTPException

from app.repositories import auth_repository
from app.core.password import (
    hash_password,
    verify_password
)
from app.core.security import (
    create_access_token
)


class AuthService:

    async def register(
        self,
        email: str,
        password: str,
        company_name: str
    ):
        existing_profile = await (
            auth_repository
            .get_user_by_email(email)
        )

        if existing_profile:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        profile = await (
            auth_repository
            .create_user(
                email=email,
                password_hash=hash_password(
                    password
                ),
                company_name=company_name
            )
        )

        token = create_access_token(
            str(profile["id"])
        )

        return {
            "access_token": token,
            "user": dict(profile)
        }

    async def login(
        self,
        email: str,
        password: str
    ):
        profile = await (
            auth_repository
            .get_user_by_email(email)
        )

        if not profile:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        valid_password = (
            verify_password(
                password,
                profile["password_hash"]
            )
        )

        if not valid_password:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        token = create_access_token(
            str(profile["id"])
        )

        return {
            "access_token": token,
            "user": dict(profile)
        }


auth_service = AuthService()