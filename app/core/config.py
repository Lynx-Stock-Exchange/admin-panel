from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    cors_origins: list[str] = ["http://localhost:5173"]
    use_stubs: bool = True

    exchange_base_url: str = "http://localhost:9000/api/v1"

    jwt_secret_key: str = "dev-secret-change-this"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    secure_cookies: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()