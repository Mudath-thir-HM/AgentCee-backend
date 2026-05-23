from app.db.sql import (
    fetch_all,
    fetch_one,
    execute
)


class SocialRepository:

    async def connect_account(
        self,
        user_id: str,
        platform: str,
        account_name: str,
        account_id: str
    ):
        query = """
        INSERT INTO social_accounts (
            user_id,
            platform,
            account_name,
            account_id,
            access_token,
            is_active
        )
        VALUES (
            $1, $2, $3, $4, $5, TRUE
        )
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            platform,
            account_name,
            account_id,
            "mock_token"
        )

    async def get_accounts(
        self,
        user_id: str
    ):
        query = """
        SELECT *
        FROM social_accounts
        WHERE user_id = $1
        AND is_active = TRUE
        ORDER BY created_at DESC
        """

        return await fetch_all(
            query,
            user_id
        )

    async def disconnect_account(
        self,
        account_id: str,
        user_id: str
    ):
        query = """
        UPDATE social_accounts
        SET is_active = FALSE
        WHERE id = $1
        AND user_id = $2
        RETURNING *
        """

        return await fetch_one(
            query,
            account_id,
            user_id
        )

    async def create_interaction(
        self,
        user_id: str,
        platform: str,
        interaction_type: str,
        content: str,
        author_username: str,
        external_id: str | None
    ):
        query = """
        INSERT INTO social_interactions (
            user_id,
            platform,
            interaction_type,
            content,
            author_username,
            external_id
        )
        VALUES (
            $1, $2, $3, $4, $5, $6
        )
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            platform,
            interaction_type,
            content,
            author_username,
            external_id
        )


    async def get_interactions(
        self,
        user_id: str
    ):
        query = """
        SELECT *
        FROM social_interactions
        WHERE user_id = $1
        ORDER BY created_at DESC
        """

        return await fetch_all(
            query,
            user_id
        )

social_repository = SocialRepository()