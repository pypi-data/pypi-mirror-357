"""Production settings with lazy instantiation - configs as data.

This demonstrates the same production configuration but with lazy instantiation,
allowing you to inspect and manipulate configurations before instantiation.
"""

import os
from pathlib import Path

from pydantic import Field
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


class AppSettingsLazy(BaseSettingsWithInstantiation):
    """Production settings with lazy instantiation.

    Configurations are loaded but NOT instantiated automatically.
    This allows you to:
    - Inspect configurations before instantiation
    - Instantiate with runtime overrides
    - Selectively instantiate only what you need
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
        env_nested_delimiter="__",
        # Behavior
        case_sensitive=False,
        extra="allow",
        # IMPORTANT: Disable auto-instantiation!
        auto_instantiate=False,
    )

    # Application metadata
    app_name: str = Field("MyApp", description="Application name")
    version: str = Field("0.0.0", description="Application version")
    environment: str = Field(default=ENVIRONMENT, description="Current environment")
    debug: bool = Field(False, description="Debug mode")

    # Services as configuration objects (NOT instantiated)
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
