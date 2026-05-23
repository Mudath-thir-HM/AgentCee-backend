from app.repositories.social_repository import (
    social_repository
)
from app.repositories.profile_repository import (
    profile_repository
)


class SocialService:

    async def connect_account(
        self,
        user_id: str,
        platform: str,
        account_name: str,
        account_id: str | None
    ):
        account = await (
            social_repository
            .connect_account(
                user_id=user_id,
                platform=platform,
                account_name=account_name,
                account_id=account_id
            )
        )

        await (
            profile_repository
            .add_connected_platform(
                user_id,
                platform
            )
        )

        return account

    async def get_accounts(
        self,
        user_id: str
    ):
        return await (
            social_repository
            .get_accounts(user_id)
        )

    async def disconnect_account(
        self,
        account_id: str,
        user_id: str
    ):
        account = await (
            social_repository
            .disconnect_account(
                account_id,
                user_id
            )
        )

        if not account:
            return {
                "message":
                "Account not found"
            }

        await (
            profile_repository
            .refresh_connected_platforms(
                user_id
            )
        )

        return {
            "message":
            "Account disconnected"
        }
    
    async def receive_interaction(
        self,
        user_id: str,
        platform: str,
        interaction_type: str,
        content: str,
        author_username: str,
        external_id: str | None
    ):
        return await (
            social_repository
            .create_interaction(
                user_id=user_id,
                platform=platform,
                interaction_type=interaction_type,
                content=content,
                author_username=author_username,
                external_id=external_id
            )
        )

    async def get_interactions(
        self,
        user_id: str
    ):
        return await (
            social_repository
            .get_interactions(user_id)
        )


social_service = SocialService()