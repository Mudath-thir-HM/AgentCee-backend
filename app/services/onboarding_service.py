from fastapi import HTTPException

from app.repositories.onboarding_repository import (
    onboarding_repository
)


class OnboardingService:

    async def connect_platform(
        self,
        user_id: str,
        platform: str,
        account_name: str
    ):
        existing_accounts = await (
            onboarding_repository
            .get_connected_platforms(
                user_id
            )
        )

        for account in existing_accounts:
            if (
                account["platform"]
                == platform
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{platform}"
                        " already connected"
                    )
                )

        connected_account = await (
            onboarding_repository
            .connect_platform(
                user_id=user_id,
                platform=platform,
                account_name=account_name
            )
        )

        return {
            "message":
            (
                f"{platform}"
                " connected successfully"
            ),
            "account":
            dict(
                connected_account
            )
        }

    async def get_connected_platforms(
        self,
        user_id: str
    ):
        platforms = await (
            onboarding_repository
            .get_connected_platforms(
                user_id
            )
        )

        return [
            dict(platform)
            for platform in platforms
        ]


onboarding_service = (
    OnboardingService()
)