from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # MongoDB Settings
    MONGO_DB_URI: str
    MONGODB_DB: str = "Volvox"
    
    JWT_SECRET_KEY: str = "volvoxpersonalaiassistantresearc"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Volvox"
    
    ALLOWED_ORIGINS: List[str] = ["*"]

    USERS_COLLECTION: str = "users"

    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  
    )

settings = Settings()
