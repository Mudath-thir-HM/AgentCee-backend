from app.repositories.profile_repository import (
    profile_repository
)


class ProfileService:

    async def get_profile(
        self,
        user_id: str
    ):
        return await profile_repository.get_profile(
            user_id
        )

    async def update_profile(
        self,
        user_id: str,
        company_name: str | None,
        avatar_url: str | None
    ):
        return await profile_repository.update_profile(
            user_id,
            company_name,
            avatar_url
        )
        
    async def create_profile(
        self,
        user_id: str,
        company_name: str = None
    ):
        return await profile_repository.create_profile(
            user_id,
            company_name
        )


profile_service = ProfileService()