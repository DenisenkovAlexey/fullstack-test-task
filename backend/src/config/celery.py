from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CELERY_")

    broker_url: str = "redis://localhost:6379/0"


celery_settings = CelerySettings()
