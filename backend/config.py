from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Financial Risk Intelligence Platform"
    database_url: str = "sqlite:///./risk_platform.db"
    redis_url: str = "redis://localhost:6379/0"
    model_path: str = "models/bankruptcy_model.pkl"
    feature_path: str = "models/bankruptcy_features.pkl"
    dataset_path: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def project_path(*parts: str) -> Path:
    return Path(__file__).resolve().parent.joinpath(*parts)
