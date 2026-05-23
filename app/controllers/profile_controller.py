from fastapi import HTTPException

from app.services.profile_service import (
    profile_service
)


class ProfileController:

    async def get_me(
        self,
        user_id: str
    ):
        profile = await profile_service.get_profile(
            user_id
        )

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        return dict(profile)

    async def update_me(
        self,
        user_id: str,
        data
    ):
        profile = await profile_service.update_profile(
            user_id=user_id,
            company_name=data.company_name,
            avatar_url=data.avatar_url
        )

        return dict(profile)


profile_controller = ProfileController()