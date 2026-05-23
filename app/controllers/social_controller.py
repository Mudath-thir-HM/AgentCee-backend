from app.services.social_service import (
    social_service
)


class SocialController:

    async def connect_account(
        self,
        user_id: str,
        data
    ):
        account = await (
            social_service
            .connect_account(
                user_id=user_id,
                platform=data.platform,
                account_name=data.account_name,
                account_id=data.account_id
            )
        )

        return dict(account)

    async def get_accounts(
        self,
        user_id: str
    ):
        accounts = await (
            social_service
            .get_accounts(user_id)
        )

        return [
            dict(account)
            for account in accounts
        ]

    async def disconnect_account(
        self,
        account_id: str,
        user_id: str
    ):
        return await (
            social_service
            .disconnect_account(
                account_id,
                user_id
            )
        )
    
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
            social_service
            .receive_interaction(
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
            social_service
            .get_interactions(user_id)
        )



social_controller = (
    SocialController()
)