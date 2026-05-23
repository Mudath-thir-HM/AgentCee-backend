from app.db.sql import fetch_one, fetch_all, execute


class AnalyticsRepository:

    async def record_analytics(
        self,
        user_id: str,
        scheduled_post_id: str | None,
        platform: str,
        likes: int,
        impressions: int,
        reach: int,
        engagement_rate: float,
        clicks: int,
        shares: int,
        comments: int
    ):
        query = """
        INSERT INTO post_analytics (
            user_id,
            scheduled_post_id,
            platform,
            likes,
            impressions,
            reach,
            engagement_rate,
            clicks,
            shares,
            comments
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
        RETURNING *
        """

        return await fetch_one(
            query,
            user_id,
            scheduled_post_id,
            platform,
            likes,
            impressions,
            reach,
            engagement_rate,
            clicks,
            shares,
            comments
        )

    async def get_overview(self, user_id: str):
        query = """
        SELECT
            COALESCE(SUM(reach), 0)::BIGINT           AS total_reach,
            COALESCE(SUM(impressions), 0)::BIGINT      AS total_impressions,
            COALESCE(AVG(engagement_rate), 0)::FLOAT   AS avg_engagement_rate,
            COALESCE(SUM(likes), 0)::BIGINT            AS total_likes,
            COALESCE(SUM(shares), 0)::BIGINT           AS total_shares,
            COALESCE(SUM(comments), 0)::BIGINT         AS total_comments,
            COALESCE(SUM(clicks), 0)::BIGINT           AS total_clicks,
            COUNT(*)::BIGINT                           AS total_records
        FROM post_analytics
        WHERE user_id = $1
        """

        return await fetch_one(query, user_id)

    async def get_platform_breakdown(self, user_id: str):
        query = """
        SELECT
            platform,
            COUNT(*)::BIGINT                           AS posts,
            COALESCE(SUM(likes), 0)::BIGINT            AS total_likes,
            COALESCE(SUM(impressions), 0)::BIGINT      AS total_impressions,
            COALESCE(AVG(engagement_rate), 0)::FLOAT   AS avg_engagement_rate
        FROM post_analytics
        WHERE user_id = $1
        GROUP BY platform
        ORDER BY total_likes DESC
        """

        return await fetch_all(query, user_id)

    async def get_weekly_engagement(self, user_id: str):
        """Returns daily engagement totals for the last 7 days."""
        query = """
        SELECT
            TO_CHAR(recorded_at AT TIME ZONE 'UTC', 'Dy') AS day,
            COALESCE(
                SUM(likes + shares + comments + clicks), 0
            )::BIGINT AS engagement
        FROM post_analytics
        WHERE user_id = $1
        AND recorded_at >= NOW() - INTERVAL '7 days'
        GROUP BY
            DATE_TRUNC('day', recorded_at AT TIME ZONE 'UTC'),
            TO_CHAR(recorded_at AT TIME ZONE 'UTC', 'Dy')
        ORDER BY
            DATE_TRUNC('day', recorded_at AT TIME ZONE 'UTC') ASC
        """

        return await fetch_all(query, user_id)

    async def get_platform_analytics(
        self,
        user_id: str,
        platform: str
    ):
        query = """
        SELECT *
        FROM post_analytics
        WHERE user_id = $1
        AND platform = $2
        ORDER BY recorded_at DESC
        LIMIT 100
        """

        return await fetch_all(query, user_id, platform)

    async def get_top_posts(
        self,
        user_id: str,
        limit: int = 5
    ):
        query = """
        SELECT
            pa.*,
            sp.post_text
        FROM post_analytics pa
        LEFT JOIN scheduled_posts sp ON sp.id = pa.scheduled_post_id
        WHERE pa.user_id = $1
        ORDER BY
            (pa.likes + pa.shares + pa.comments) DESC
        LIMIT $2
        """

        return await fetch_all(query, user_id, limit)

    async def get_posts_this_week(self, user_id: str) -> int:
        query = """
        SELECT COUNT(*)::INT AS cnt
        FROM scheduled_posts
        WHERE user_id = $1
        AND status = 'published'
        AND published_at >= NOW() - INTERVAL '7 days'
        """

        row = await fetch_one(query, user_id)
        return row["cnt"] if row else 0


analytics_repository = AnalyticsRepository()
