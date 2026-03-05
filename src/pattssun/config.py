from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        # .env file wins over shell environment variables
        return (init_settings, dotenv_settings, env_settings, file_secret_settings)

    x_bearer_token: str = ""
    x_user_id: str = ""
    output_dir: Path = Path("output")
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    bookmarks_path: Path = Path("bookmarks/bookmarks.json")
