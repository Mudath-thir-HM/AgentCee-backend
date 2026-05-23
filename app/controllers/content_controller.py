from app.services.content_service import (
    content_service
)


class ContentController:

    async def generate_content(
        self,
        user_id: str,
        body
    ):
        return await (
            content_service
            .generate_content(
                user_id=user_id,
                platform=body.platform,
                content_type=body.content_type,
                prompt=body.prompt,
                tone=body.tone
            )
        )


content_controller = (
    ContentController()
)