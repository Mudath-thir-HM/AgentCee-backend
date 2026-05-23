from fastapi import HTTPException
from supabase import create_client

from app.core.config import settings


supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY
)


class AuthController:

    async def login(
        self,
        email: str,
        password: str
    ):
        try:
            response = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password
                }
            )

            session = response.session

            return {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "user": response.user
            }

        except Exception:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )


auth_controller = AuthController()