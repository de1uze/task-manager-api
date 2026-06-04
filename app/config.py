import os


class Settings:
    """Runtime configuration sourced from environment variables."""

    app_name: str = os.getenv("APP_NAME", "Task Manager API")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_json: bool = os.getenv("LOG_JSON", "false").lower() in {"1", "true", "yes"}
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))


settings = Settings()
