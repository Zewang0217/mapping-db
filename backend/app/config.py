from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://mapper:devpassword@localhost:5432/mapping"

    model_config = {"env_prefix": "", "env_file": ".env"}


settings = Settings()
