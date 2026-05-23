from app.services.content_service import content_service


class ContentController:

    async def generate_content(self, user_id: str, body):
        return await content_service.generate_content(
            user_id=user_id,
            platform=body.platform,
            content_type=body.content_type,
            prompt=body.prompt,
            tone=body.tone
        )

    async def get_history(
        self,
        user_id: str,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0
    ):
        return await content_service.get_history(
            user_id=user_id,
            platform=platform,
            status=status,
            limit=limit,
            offset=offset
        )

    async def get_content(self, content_id: str, user_id: str):
        return await content_service.get_content_by_id(
            content_id, user_id
        )

    async def update_content(
        self, content_id: str, user_id: str, body
    ):
        return await content_service.update_content(
            content_id=content_id,
            user_id=user_id,
            generated_text=body.generated_text,
            hashtags=body.hashtags,
            call_to_action=body.call_to_action
        )

    async def update_status(
        self, content_id: str, user_id: str, body
    ):
        return await content_service.update_status(
            content_id=content_id,
            user_id=user_id,
            status=body.status
        )

    async def delete_content(self, content_id: str, user_id: str):
        return await content_service.delete_content(
            content_id, user_id
        )


content_controller = ContentController()
