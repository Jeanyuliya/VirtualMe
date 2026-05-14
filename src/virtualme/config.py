from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: SecretStr
    claude_model: str = "claude-opus-4-7"
    line_channel_access_token: SecretStr | None = None
    line_channel_secret: SecretStr | None = None
    database_url: str = "sqlite:///./data/virtualme.db"
    session_max_minutes: int = 25
    energy_low_threshold: int = 3
    follow_up_max_depth: int = 3
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"


def sqlite_path(database_url: str) -> str:
    return database_url.removeprefix("sqlite:///")
