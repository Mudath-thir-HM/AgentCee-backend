from app.services.scheduler_service import scheduler_service


class SchedulerController:

    async def schedule_post(self, user_id: str, body):
        return await scheduler_service.schedule_post(
            user_id=user_id,
            content_id=body.content_id,
            platform=body.platform,
            post_text=body.post_text,
            scheduled_for=body.scheduled_for
        )

    async def get_posts(
        self,
        user_id: str,
        status: str | None = None,
        platform: str | None = None
    ):
        return await scheduler_service.get_posts(
            user_id=user_id,
            status=status,
            platform=platform
        )

    async def get_post(self, post_id: str, user_id: str):
        return await scheduler_service.get_post(post_id, user_id)

    async def update_post(self, post_id: str, user_id: str, body):
        return await scheduler_service.update_post(
            post_id=post_id,
            user_id=user_id,
            post_text=body.post_text,
            scheduled_for=body.scheduled_for,
            status=body.status
        )

    async def delete_post(self, post_id: str, user_id: str):
        return await scheduler_service.delete_post(post_id, user_id)


scheduler_controller = SchedulerController()
