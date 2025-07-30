"""Configuration models using frostbound.pydanticonf."""

from typing import TYPE_CHECKING, Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from frostbound.pydanticonf import BaseSettingsWithInstantiation, DynamicConfig

if TYPE_CHECKING:
    pass


class DatabaseConfig(DynamicConfig["Database"]):
    """Database configuration with automatic target inference."""
    target_: Literal["services.Database"] = Field(
        default="services.Database",
        alias="_target_"
    )
    host: str = "localhost"
    port: int = 5432
    username: str = "admin"
    password: Optional[str] = None  # Will be loaded from env
    pool_size: int = 10


class RedisCacheConfig(DynamicConfig["RedisCache"]):
    """Redis cache configuration."""
    target_: Literal["services.RedisCache"] = Field(
        default="services.RedisCache",
        alias="_target_"
    )
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ttl: int = 3600
    max_connections: int = 50


class EmailServiceConfig(DynamicConfig["EmailService"]):
    """Email service configuration."""
    target_: Literal["services.EmailService"] = Field(
        default="services.EmailService",
        alias="_target_"
    )
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True


class APIClientConfig(DynamicConfig["APIClient"]):
    """API client configuration using positional args."""
    target_: Literal["services.APIClient"] = Field(
        default="services.APIClient",
        alias="_target_"
    )
    # Using _args_ for positional arguments
    args_: list[str] = Field(default_factory=list, alias="_args_")
    timeout: int = 30


class LoggerConfig(DynamicConfig["Logger"]):
    """Logger configuration for partial instantiation."""
    target_: Literal["services.Logger"] = Field(
        default="services.Logger",
        alias="_target_"
    )
    partial_: bool = Field(default=False, alias="_partial_")
    name: str = "app"
    level: str = "INFO"
    format: str = "json"


class ServiceConfig(DynamicConfig["Service"]):
    """Service configuration with nested dependencies."""
    target_: Literal["services.Service"] = Field(
        default="services.Service",
        alias="_target_"
    )
    name: str
    database: DatabaseConfig
    cache: RedisCacheConfig
    logger: Optional[LoggerConfig] = None


# Regular config without instantiation
class AppMetadata(BaseModel):
    """Application metadata - not instantiated."""
    app_name: str = "MyApp"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True


# Main application settings
class AppSettings(BaseSettingsWithInstantiation):
    """Main application settings with auto-instantiation."""

    model_config = SettingsConfigDict(
        yaml_file="config.yaml",
        env_file=".env",
        env_prefix="APP_",
        env_nested_delimiter="__",
        auto_instantiate=True  # Auto-instantiate on load
    )

    # Metadata (regular config, not instantiated)
    metadata: AppMetadata

    # Services to be instantiated
    database: DatabaseConfig
    cache: RedisCacheConfig
    email: EmailServiceConfig
    api_client: APIClientConfig

    # Optional service
    backup_database: Optional[DatabaseConfig] = None

    # Service with dependencies
    main_service: Optional[ServiceConfig] = None


class LazyAppSettings(BaseSettingsWithInstantiation):
    """Application settings with lazy instantiation."""

    model_config = SettingsConfigDict(
        yaml_file="config.yaml",
        env_file=".env",
        env_prefix="APP_",
        env_nested_delimiter="__",
        auto_instantiate=False  # Lazy mode - instantiate manually
    )

    # Same fields as AppSettings
    metadata: AppMetadata
    database: DatabaseConfig
    cache: RedisCacheConfig
    email: EmailServiceConfig
    api_client: APIClientConfig
    backup_database: Optional[DatabaseConfig] = None
    main_service: Optional[ServiceConfig] = None


# Multi-file configuration example
class MultiEnvSettings(BaseSettingsWithInstantiation):
    """Settings that support multiple environments with file merging."""

    model_config = SettingsConfigDict(
        yaml_file=["config/base.yaml", "config/{env}.yaml"],
        env_file=".env.{env}",
        env_prefix="APP_",
        env_nested_delimiter="__",
        auto_instantiate=True
    )

    metadata: AppMetadata
    database: DatabaseConfig
    cache: RedisCacheConfig
