from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Demo mode - set to True to use mock data (no API keys required)
    demo_mode: bool = False

    # API keys (optional when demo_mode=True)
    anthropic_api_key: Optional[str] = None
    youtube_api_key: Optional[str] = None
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "ResearchAI/0.1.0"
    producthunt_api_token: Optional[str] = None
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
