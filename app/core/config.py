from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    cors_origins: list[str] = ["http://localhost:5173"]
    use_stubs: bool = True

    exchange_base_url: str = "http://localhost:9000/api/v1"
    admin_token: str = "dev-admin-token"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()