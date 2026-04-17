"""Settings management for EvidenceAI.

All configuration is loaded from environment variables (or a .env file)
using pydantic-settings. Import the singleton ``settings`` object wherever
configuration is needed.

Example::

    from evidence_ai.config import settings

    print(settings.openai_model)  # "gpt-4o-mini"
    print(settings.database_url)  # "postgresql+asyncpg://..."
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_env: Literal["development", "production", "test"] = "development"
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for JWT signing. Must be changed in production.",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://evidence:evidence@localhost:5432/evidenceai",
        description="PostgreSQL connection string (asyncpg driver).",
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching.",
    )
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    cache_ttl_seconds: int = 3600

    # ── LLM Providers ─────────────────────────────────────────────────────────
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key. Required for triangulation and summarization.",
    )
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-haiku-20240307"

    # ── NCBI ──────────────────────────────────────────────────────────────────
    ncbi_api_key: str = Field(
        default="",
        description="NCBI API key. Without it: 3 req/s. With: 10 req/s.",
    )
    ncbi_email: str = Field(
        default="research@evidenceai.com",
        description="Email required by NCBI eUtils usage policy.",
    )

    # ── FDA Databases ─────────────────────────────────────────────────────────
    fda_openfda_api_key: str = ""

    # ── AWS ───────────────────────────────────────────────────────────────────
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "evidenceai-documents"
    s3_models_bucket: str = "evidenceai-models"

    # ── Authentication ────────────────────────────────────────────────────────
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # ── ML Models ─────────────────────────────────────────────────────────────
    picox_model_path: str = "sultan/BiomedNLP-PubMedBERT-large-uncased-abstract"
    evidence_outcomes_model_path: str = "sultan/BiomedNLP-BiomedBERT-base-uncased-abstract"
    medreview_model_path: str = "meta-llama/Llama-2-7b-hf"
    device: str = "cpu"
    model_cache_dir: str = "./.model_cache"

    # ── Feature Flags ─────────────────────────────────────────────────────────
    enable_synthetic_augmentation: bool = True
    enable_llm_summarization: bool = True
    enable_continuous_monitoring: bool = False
    require_human_review: bool = False

    # ── Computed properties ───────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        """Return True if running in production environment."""
        return self.app_env == "production"

    @property
    def ncbi_rate_limit(self) -> float:
        """Return NCBI rate limit (requests/second)."""
        return 10.0 if self.ncbi_api_key else 3.0

    @property
    def has_openai(self) -> bool:
        """Return True if OpenAI API key is configured."""
        return bool(self.openai_api_key)

    @property
    def has_anthropic(self) -> bool:
        """Return True if Anthropic API key is configured."""
        return bool(self.anthropic_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()


# Convenience alias
settings = get_settings()
