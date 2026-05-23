from app.db.sql import fetch_one, execute


class ProfileRepository:

    async def get_profile(self, user_id: str):
        query = """
        SELECT *
        FROM profiles
        WHERE id = $1
        """

        return await fetch_one(query, user_id)

    async def update_profile(
        self,
        user_id: str,
        company_name: str | None,
        avatar_url: str | None
    ):
        query = """
        UPDATE profiles
        SET
            company_name = COALESCE($2, company_name),
            avatar_url = COALESCE($3, avatar_url)
        WHERE id = $1
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            company_name,
            avatar_url
        )
        
    async def create_profile(
        self,
        user_id: str,
        company_name: str = None
    ):
        query = """
        INSERT INTO profiles (
            id,
            company_name
        )
        VALUES (
            $1,
            $2
        )
        ON CONFLICT (id)
        DO NOTHING
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            company_name
        )
    
    async def add_connected_platform(
        self,
        user_id: str,
        platform: str
    ):
        query = """
        UPDATE profiles
        SET connected_platforms =
            CASE
                WHEN NOT (
                    $2 = ANY(connected_platforms)
                )
                THEN array_append(
                    connected_platforms,
                    $2
                )
                ELSE connected_platforms
            END
        WHERE id = $1
        RETURNING connected_platforms
        """

        return await fetch_one(
            query,
            user_id,
            platform
        )


    async def refresh_connected_platforms(
        self,
        user_id: str
    ):
        query = """
        UPDATE profiles
        SET connected_platforms = COALESCE(
            (
                SELECT array_agg(
                    DISTINCT platform
                )
                FROM social_accounts
                WHERE user_id = $1
                AND is_active = TRUE
            ),
            ARRAY[]::TEXT[]
        )
        WHERE id = $1
        RETURNING connected_platforms
        """

        return await fetch_one(
            query,
            user_id
        )


profile_repository = ProfileRepository()