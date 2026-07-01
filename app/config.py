from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    challonge_api_key: str = ""
    challonge_username: str = ""
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_prefix": "SF_", "env_file": ".env"}


settings = Settings()
