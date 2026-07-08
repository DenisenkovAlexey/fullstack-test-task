from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    user: str
    password: str
    db: str
    host: str
    port: str = Field(validation_alias=AliasChoices("PGPORT"))

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


database_settings = DatabaseSettings()
