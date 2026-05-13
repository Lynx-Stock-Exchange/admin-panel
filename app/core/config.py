from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    cors_origins: list[str] = ["http://localhost:8087"]
    use_stubs: bool = False

    exchange_base_url: str = "http://rest-api:8085/api/v1"
    api_gateway_url: str = "http://rest-api:8085/api/v1"
    exchange_admin_token: str = "test-token"
    rest_api_platform_key: str = "test-key"
    rest_api_platform_secret: str = "test-secret"

    rest_api_url: str = "http://rest-api:8085"
    kafka_bootstrap_servers: str = "localhost:9092"

    jwt_secret_key: str = "dev-secret-change-this"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    secure_cookies: bool = False

    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///./admin_panel.db"


settings = Settings()
