from app.db.sql import (
    fetch_all,
    fetch_one,
    execute
)


class OnboardingRepository:

    async def connect_platform(
        self,
        user_id: str,
        platform: str,
        account_name: str
    ):
        query = """
        INSERT INTO social_accounts (
            user_id,
            platform,
            account_name,
            is_active
        )
        VALUES (
            $1, $2, $3, TRUE
        )
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            platform,
            account_name
        )

    async def get_connected_platforms(
        self,
        user_id: str
    ):
        query = """
        SELECT
            id,
            platform,
            account_name,
            is_active,
            created_at
        FROM social_accounts
        WHERE user_id = $1
        ORDER BY created_at DESC
        """

        return await fetch_all(
            query,
            user_id
        )


onboarding_repository = (
    OnboardingRepository()
)