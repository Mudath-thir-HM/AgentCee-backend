from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str
    API_VERSION: str

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    DATABASE_URL: str
    
    SUPABASE_JWT_SECRET: str

    FRONTEND_URL: str

    OPENROUTER_API_KEY: str

    DEEPSEEK_MODEL: str
    GEMMA_MODEL: str
    FLUX_MODEL: str
    
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()