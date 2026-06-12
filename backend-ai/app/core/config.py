from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    internal_api_key: str = Field(default="change-me", alias="INTERNAL_API_KEY")
    spring_api_base_url: str = Field(
        default="http://localhost:8080",
        alias="SPRING_API_BASE_URL",
    )
    supabase_db_url: str = Field(
        default="postgresql://user:password@host:5432/postgres",
        alias="SUPABASE_DB_URL",
    )
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    gms_api_key: str = Field(default="", alias="GMS_API_KEY")
    llm_model: str = Field(default="", alias="LLM_MODEL")
    embedding_model: str = Field(default="", alias="EMBEDDING_MODEL")
    langsmith_tracing: bool = Field(default=False, alias="LANGSMITH_TRACING")
    langsmith_api_key: str = Field(default="", alias="LANGSMITH_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
