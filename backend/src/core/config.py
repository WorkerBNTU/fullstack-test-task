from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "files"


class Settings(BaseSettings):
    """Single source of truth for environment configuration.

    Values are read once at process start instead of being scattered
    across ``os.environ.get(...)`` calls in service/task modules.
    """

    model_config = SettingsConfigDict(env_file=".env.dev", extra="ignore")

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "test"
    postgres_host: str = "backend-db"
    pgport: int = 5432

    celery_broker_url: str = "redis://backend-redis:6379/0"

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Threat-scan heuristics, kept configurable instead of hardcoded magic values.
    suspicious_extensions: set[str] = {".exe", ".bat", ".cmd", ".sh", ".js"}
    max_file_size_bytes: int = 10 * 1024 * 1024

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.pgport}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance -- read env / .env file exactly once."""
    return Settings()
