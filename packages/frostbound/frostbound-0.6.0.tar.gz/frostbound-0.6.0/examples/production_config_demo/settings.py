"""Main application settings using BaseSettingsWithInstantiation.

This demonstrates:
- Type-safe configuration with DynamicConfig[T]
- Multi-layer configuration (base + environment overrides)
- Environment variables for secrets
- Automatic object instantiation
"""

import os
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from frostbound.pydanticonf import BaseSettingsWithInstantiation

from .config_models import (
    APIClientConfig,
    DatabaseConfig,
    LoggerConfig,
    RedisCacheConfig,
    S3StorageConfig,
    SentryMonitoringConfig,
)

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
CONFIG_DIR = Path(__file__).parent / "config"
ENV_DIR = Path(__file__).parent / "env"


class ModelConfig(BaseModel):
    """Model configuration."""

    temperature: float = Field(default=0.0, description="Temperature", ge=0.0, le=1.0)
    top_k: int = Field(default=0, description="Top K", ge=0, le=100)
    top_p: float = Field(default=0.0, description="Top P", ge=0.0, le=1.0)
    max_tokens: int = Field(default=0, description="Max Tokens", ge=0, le=10000)
    frequency_penalty: float = Field(default=0.0, description="Frequency Penalty", ge=0.0, le=1.0)
    presence_penalty: float = Field(default=0.0, description="Presence Penalty", ge=0.0, le=1.0)
    stop_sequences: list[str] = Field(default=[], description="Stop Sequences")


class AppSettings(BaseSettingsWithInstantiation):
    """Main application settings with automatic instantiation.

    Configuration precedence (highest to lowest):
    1. Environment variables (APP_*)
    2. .env file (.env.dev or .env.prod)
    3. Environment-specific YAML (dev.yaml or prod.yaml)
    4. Base YAML (base.yaml)
    5. Field defaults in this class
    """

    model_config = SettingsConfigDict(
        # YAML files - base + environment specific
        yaml_file=[
            str(CONFIG_DIR / "base.yaml"),
            str(CONFIG_DIR / f"{ENVIRONMENT}.yaml"),
        ],
        # Environment file
        env_file=str(ENV_DIR / f".env.{ENVIRONMENT}"),
        env_file_encoding="utf-8",
        # Environment variables
        # env_prefix=f"{ENVIRONMENT.upper()}",
        env_nested_delimiter="__",
        # Behavior
        case_sensitive=False,
        extra="allow",  # Fail on unknown fields
    )

    # Application metadata
    app_name: str = Field("MyApp", description="Application name")
    version: str = Field("0.0.0", description="Application version")
    environment: str = Field(default=ENVIRONMENT, description="Current environment")
    debug: bool = Field(False, description="Debug mode")

    llm_config: ModelConfig = Field(default_factory=ModelConfig, description="LLM configuration")

    # Services with type-safe configuration and auto-instantiation
    database: DatabaseConfig = Field(
        default=DatabaseConfig(_target_="examples.production_config_demo.models.Database"),
        description="PostgreSQL database configuration",
    )

    redis: RedisCacheConfig = Field(
        default=RedisCacheConfig(_target_="examples.production_config_demo.models.RedisCache"),
        description="Redis cache configuration",
    )

    storage: S3StorageConfig = Field(
        default=S3StorageConfig(_target_="examples.production_config_demo.models.S3Storage", bucket="default-bucket"),
        description="S3 storage configuration",
    )

    external_api: APIClientConfig = Field(
        default=APIClientConfig(
            _target_="examples.production_config_demo.models.APIClient", base_url="http://localhost"
        ),
        description="External API client configuration",
    )

    logger: LoggerConfig = Field(
        default=LoggerConfig(_target_="examples.production_config_demo.models.Logger"),
        description="Application logger configuration",
    )

    monitoring: SentryMonitoringConfig = Field(
        default=SentryMonitoringConfig(_target_="examples.production_config_demo.models.SentryMonitoring"),
        description="Sentry monitoring configuration",
    )
