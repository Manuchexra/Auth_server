from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Auth API"
    DEBUG: bool 

    # Database
    DATABASE_URL: str
    REDIS_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS : int

    # Email settings
    EMAIL_USER: str
    EMAIL_PORT: int
    EMAIL_HOST_USER: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"

    )


    @property
    def access_token_expire_delta(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
config = Settings()