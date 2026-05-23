from app.services.onboarding_service import (
    onboarding_service
)


class OnboardingController:

    async def connect_platform(
        self,
        user_id: str,
        platform: str,
        account_name: str
    ):
        return await (
            onboarding_service
            .connect_platform(
                user_id=user_id,
                platform=platform,
                account_name=account_name
            )
        )

    async def get_connected_platforms(
        self,
        user_id: str
    ):
        return await (
            onboarding_service
            .get_connected_platforms(
                user_id=user_id
            )
        )


onboarding_controller = (
    OnboardingController()
)