from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # MongoDB Settings
    MONGO_DB_URI: str
    MONGODB_DB: str = "Volvox"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "volvoxpersonalaiassistantresearc"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Volvox"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Collections
    USERS_COLLECTION: str = "users"

    # Optional keys present in .env or environment
    OPENAI_API_KEY: Optional[str] = None

    # pydantic-settings v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # ignore unknown env vars like OPENAI_API_KEY
    )

settings = Settings()
