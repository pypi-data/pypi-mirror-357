"""Type-safe configuration models using DynamicConfig.

These models define the configuration structure with full type safety
and automatic instantiation to the actual component classes.
"""

from frostbound.pydanticonf import DynamicConfig

from .models import (
    APIClient,
    Database,
    Logger,
    RedisCache,
    S3Storage,
    SentryMonitoring,
)


class DatabaseConfig(DynamicConfig[Database]):
    """Type-safe database configuration."""

    # Connection settings
    host: str = "localhost"
    port: int = 5432
    database: str = "app_db"
    username: str = "postgres"
    password: str | None = None  # From environment

    # Performance settings
    pool_size: int = 10
    timeout: int = 30


class RedisCacheConfig(DynamicConfig[RedisCache]):
    """Type-safe Redis cache configuration."""

    # Connection settings
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None  # From environment

    # Security settings
    ssl: bool = False
    cluster_mode: bool = False


class S3StorageConfig(DynamicConfig[S3Storage]):
    """Type-safe S3 storage configuration."""

    # Bucket settings
    bucket: str
    region: str = "us-east-1"

    # Credentials (from environment)
    access_key_id: str | None = None
    secret_access_key: str | None = None

    # Optional settings
    endpoint_url: str | None = None  # For MinIO, etc.
    use_ssl: bool = True


class APIClientConfig(DynamicConfig[APIClient]):
    """Type-safe API client configuration."""

    # API settings
    base_url: str
    api_key: str | None = None  # From environment
    api_secret: str | None = None  # From environment

    # Client behavior
    timeout: int = 30
    retry_count: int = 3
    rate_limit: int = 100  # requests per minute


class LoggerConfig(DynamicConfig[Logger]):
    """Type-safe logger configuration."""

    name: str = "app"
    level: str = "INFO"
    format: str = "json"
    output: str = "stdout"
    buffer_size: int = 1000


class SentryMonitoringConfig(DynamicConfig[SentryMonitoring]):
    """Type-safe Sentry monitoring configuration."""

    dsn: str | None = None  # From environment
    environment: str = "development"
    release: str | None = None

    # Performance settings
    sample_rate: float = 1.0
    traces_sample_rate: float = 0.1
    debug: bool = False
