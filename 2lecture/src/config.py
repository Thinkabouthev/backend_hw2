from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    database_url: str
    sync_database_url: str

    redis_url: str
    
    # Auth settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    
    # Celery settings
    celery_broker_url: str
    celery_result_backend: str
    
    # AI API settings
    openai_api_key: str
    gemini_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8"
    )


settings = Settings()
