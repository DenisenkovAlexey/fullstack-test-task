from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path, PosixPath


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    storage_dir: PosixPath


app_settings = AppSettings()

app_settings.storage_dir.mkdir(parents=True, exist_ok=True)


