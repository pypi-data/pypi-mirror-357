"""
Comprehensive Learning Guide for frostbound.pydanticonf._instantiate

This module is the HEART of the pydanticonf system - it enables dynamic object
instantiation from configuration. This is what makes it possible to create
complex object hierarchies from YAML/environment configuration.

Key Concepts:
1. DynamicConfig - Pydantic models that describe how to create objects
2. instantiate() - The main function that creates objects from configs
3. Dependency injection - Automatic injection of registered dependencies
4. Recursive instantiation - Nested configs are automatically instantiated
5. Partial instantiation - Create factory functions instead of objects

Fully typed with modern Python 3.12+ type annotations and rigorous type safety.
"""

from __future__ import annotations

import functools
import os
import tempfile
from pathlib import Path
from typing import Any, Protocol, TypeAlias

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint

from frostbound.pydanticonf import (
    ConfigLoader,
    DynamicConfig,
    instantiate,
    register_dependency,
)

console = Console()

# ============================================================================
# Type Definitions
# ============================================================================

# Configuration data types
ConfigValue: TypeAlias = str | int | bool | float | list[Any] | dict[str, Any]
ConfigDict: TypeAlias = dict[str, ConfigValue]
EnvVarsDict: TypeAlias = dict[str, str]

# Instantiation types
InstantiationConfig: TypeAlias = dict[str, Any] | DynamicConfig[Any] | BaseModel
PartialFunction: TypeAlias = functools.partial[Any]
FlexibleConfig: TypeAlias = dict[str, Any]


# Service protocol types
class LoggerProtocol(Protocol):
    """Protocol for logger-like objects."""

    def log(self, message: str) -> None: ...


class CacheProtocol(Protocol):
    """Protocol for cache-like objects."""

    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...


class DatabaseProtocol(Protocol):
    """Protocol for database-like objects."""

    def query(self, sql: str) -> str: ...
    def close(self) -> None: ...


def print_section(title: str) -> None:
    """Helper to print formatted sections."""
    console.print(Panel(title, style="bold blue"))
    console.print()


# ============================================================================
# Example Classes for Instantiation
# ============================================================================


class DatabaseConnection:
    """Example database connection class."""

    def __init__(self, host: str, port: int = 5432, username: str = "admin", password: str = "secret") -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connected = True
        console.print(f"🔌 Database connected to {host}:{port} as {username}")

    def query(self, sql: str) -> str:
        return f"Result from {self.host}: {sql}"

    def close(self) -> None:
        self.connected = False
        console.print(f"🔌 Database connection to {self.host} closed")


class Logger:
    """Example logger class."""

    def __init__(self, name: str, level: str = "INFO", format_style: str = "simple") -> None:
        self.name = name
        self.level = level
        self.format_style = format_style
        console.print(f"📝 Logger '{name}' created (level={level}, format={format_style})")

    def log(self, message: str) -> None:
        console.print(f"[{self.level}] {self.name}: {message}")


class CacheManager:
    """Example cache manager."""

    def __init__(self, backend: str = "memory", ttl: int = 3600) -> None:
        self.backend = backend
        self.ttl = ttl
        console.print(f"💾 Cache manager created (backend={backend}, ttl={ttl}s)")

    def get(self, key: str) -> str | None:
        return f"cached_value_for_{key}"

    def set(self, key: str, value: str) -> None:
        console.print(f"💾 Cached {key} = {value}")


class EmailService:
    """Example email service that depends on other services."""

    def __init__(self, smtp_host: str, logger: Logger, cache: CacheManager | None = None) -> None:
        self.smtp_host = smtp_host
        self.logger = logger
        self.cache = cache
        console.print(f"📧 Email service created (smtp={smtp_host})")

    def send_email(self, to: str, subject: str) -> None:
        self.logger.log(f"Sending email to {to}: {subject}")
        if self.cache:
            self.cache.set(f"last_email_{to}", subject)


class DataProcessor:
    """Example data processor with complex dependencies."""

    def __init__(self, name: str, database: DatabaseConnection, logger: Logger, batch_size: int = 100) -> None:
        self.name = name
        self.database = database
        self.logger = logger
        self.batch_size = batch_size
        console.print(f"⚙️  Data processor '{name}' created (batch_size={batch_size})")

    def process(self, data: list[str]) -> None:
        self.logger.log(f"Processing {len(data)} items in batches of {self.batch_size}")
        result = self.database.query("INSERT INTO processed_data VALUES (...)")
        self.logger.log(f"Database result: {result}")


class MLModel:
    """Example ML model with positional arguments."""

    def __init__(self, model_type: str, input_dim: int, output_dim: int, learning_rate: float = 0.001) -> None:
        self.model_type = model_type
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.learning_rate = learning_rate
        console.print(f"🤖 ML Model created: {model_type} ({input_dim}→{output_dim}, lr={learning_rate})")

    def train(self, epochs: int = 10) -> None:
        console.print(f"🤖 Training {self.model_type} for {epochs} epochs...")


# ============================================================================
# Configuration Models using DynamicConfig
# ============================================================================


class DatabaseConfig(DynamicConfig[DatabaseConnection]):
    """Configuration for database connection."""

    host: str
    port: int = 5432
    username: str = "admin"
    password: str = Field(default="secret", description="Database password")


class LoggerConfig(DynamicConfig[Logger]):
    """Configuration for logger."""

    name: str
    level: str = "INFO"
    format_style: str = "simple"


class CacheConfig(DynamicConfig[CacheManager]):
    """Configuration for cache manager."""

    backend: str = "memory"
    ttl: int = 3600


class EmailConfig(DynamicConfig[EmailService]):
    """Configuration for email service with dependencies."""

    smtp_host: str
    logger: LoggerConfig  # Nested config - will be instantiated recursively
    cache: CacheConfig | None = None  # Optional dependency


class DataProcessorConfig(DynamicConfig[DataProcessor]):
    """Configuration for data processor with multiple dependencies."""

    name: str
    database: DatabaseConfig  # Required dependency
    logger: LoggerConfig  # Required dependency
    batch_size: int = 100


class MLModelConfig(DynamicConfig[MLModel]):
    """Configuration for ML model."""

    model_type: str
    input_dim: int
    output_dim: int
    learning_rate: float = 0.001


# ============================================================================
# Learning Examples
# ============================================================================


def step_1_basic_instantiation() -> None:
    """Step 1: Basic object instantiation from DynamicConfig."""
    print_section("Step 1: Basic Object Instantiation")

    console.print("🎯 Creating a database connection from DynamicConfig:")

    # Create a DynamicConfig instance
    db_config = DatabaseConfig(  # type: ignore[call-arg]
        target_="__main__.DatabaseConnection",  # Full path to the class
        host="localhost",
        port=5432,
        username="admin",
        password="my_secret",
    )

    console.print("📋 Configuration object:")
    pprint(db_config)

    # Instantiate the actual object
    console.print("\n🔧 Instantiating object:")
    db = instantiate(db_config)

    console.print(f"\n✅ Created object of type: {type(db).__name__}")
    console.print(f"   Host: {db.host}")
    console.print(f"   Port: {db.port}")
    console.print(f"   Connected: {db.connected}")

    # Test the object
    result = db.query("SELECT * FROM users")
    console.print(f"   Query result: {result}")

    console.print("\n💡 Key insight: DynamicConfig describes HOW to create an object")
    console.print("   instantiate() actually CREATES the object using that description")
    console.print()


def step_2_dict_instantiation() -> None:
    """Step 2: Instantiation from plain dictionaries."""
    print_section("Step 2: Instantiation from Dictionaries")

    console.print("🎯 Creating objects from plain Python dictionaries:")

    # Dictionary with _target_ key
    logger_dict: FlexibleConfig = {
        "_target_": "__main__.Logger",
        "name": "app_logger",
        "level": "DEBUG",
        "format_style": "detailed",
    }

    console.print("📋 Configuration dictionary:")
    pprint(logger_dict)

    console.print("\n🔧 Instantiating object:")
    logger = instantiate(logger_dict)

    # Test the object
    logger.log("This is a test message")

    console.print("\n💡 Key insight: You don't need DynamicConfig - plain dicts work too!")
    console.print("   Just include '_target_' key with the full class path")
    console.print()


def step_3_parameter_overrides() -> None:
    """Step 3: Runtime parameter overrides."""
    print_section("Step 3: Runtime Parameter Overrides")

    console.print("🎯 Overriding configuration parameters at instantiation time:")

    # Base configuration
    cache_config = CacheConfig(  # type: ignore[call-arg]
        target_="__main__.CacheManager", backend="memory", ttl=3600
    )

    console.print("📋 Base configuration:")
    pprint(cache_config)

    # Instantiate with overrides
    console.print("\n🔧 Instantiating with overrides (backend='redis', ttl=7200):")
    cache = instantiate(cache_config, backend="redis", ttl=7200)

    console.print("\n✅ Final configuration:")
    console.print(f"   Backend: {cache.backend}")
    console.print(f"   TTL: {cache.ttl}")

    console.print("\n💡 Key insight: instantiate() accepts keyword arguments")
    console.print("   These override the values in the configuration")
    console.print()


def step_4_recursive_instantiation() -> None:
    """Step 4: Recursive instantiation of nested configurations."""
    print_section("Step 4: Recursive Instantiation")

    console.print("🎯 Creating objects with nested dependencies:")

    # Configuration with nested dependencies
    email_config = EmailConfig(  # type: ignore[call-arg]
        target_="__main__.EmailService",
        smtp_host="smtp.gmail.com",
        logger=LoggerConfig(  # type: ignore[call-arg]
            target_="__main__.Logger", name="email_logger", level="WARNING"
        ),
        cache=CacheConfig(  # type: ignore[call-arg]
            target_="__main__.CacheManager", backend="redis", ttl=1800
        ),
    )

    console.print("📋 Nested configuration:")
    pprint(email_config)

    console.print("\n🔧 Instantiating (notice recursive creation):")
    email_service = instantiate(email_config)

    console.print("\n✅ Created email service:")
    console.print(f"   SMTP Host: {email_service.smtp_host}")
    console.print(f"   Logger type: {type(email_service.logger).__name__}")
    console.print(f"   Cache type: {type(email_service.cache).__name__}")

    # Test the service
    console.print("\n🧪 Testing the service:")
    email_service.send_email("user@example.com", "Welcome!")

    console.print("\n💡 Key insight: Nested DynamicConfigs are automatically instantiated")
    console.print("   The entire object tree is built recursively")
    console.print()


def step_5_dependency_injection() -> None:
    """Step 5: Dependency injection system."""
    print_section("Step 5: Dependency Injection")

    console.print("🎯 Using dependency injection for shared objects:")

    # Create and register shared dependencies
    console.print("🔧 Creating shared dependencies:")
    shared_db = DatabaseConnection("shared-db.company.com", 5432, "shared_user", "shared_pass")
    shared_logger = Logger("global_logger", "INFO", "json")

    # Register dependencies (can be by type or by parameter name)
    register_dependency("database", shared_db)
    register_dependency("logger", shared_logger)

    console.print("\n📋 Registered dependencies:")
    console.print("   - database: shared DatabaseConnection")
    console.print("   - logger: shared Logger")

    # Create a processor that will use injected dependencies
    processor_config: FlexibleConfig = {
        "_target_": "__main__.DataProcessor",
        "name": "UserProcessor",
        "batch_size": 50,
        # Note: database and logger are NOT specified - they'll be injected!
    }

    console.print("\n📋 Processor configuration (missing dependencies):")
    pprint(processor_config)

    console.print("\n🔧 Instantiating with dependency injection:")
    processor = instantiate(processor_config)

    console.print("\n✅ Dependencies were injected:")
    console.print(f"   Database host: {processor.database.host}")
    console.print(f"   Logger name: {processor.logger.name}")

    # Test the processor
    console.print("\n🧪 Testing the processor:")
    processor.process(["data1", "data2", "data3"])

    console.print("\n💡 Key insight: register_dependency() enables automatic injection")
    console.print("   Missing required parameters are automatically filled")
    console.print()


def step_6_partial_instantiation() -> None:
    """Step 6: Partial instantiation for factory patterns."""
    print_section("Step 6: Partial Instantiation (Factory Pattern)")

    console.print("🎯 Creating factory functions with partial instantiation:")

    # Create a factory for loggers with specific settings
    console.print("🔧 Creating logger factory:")
    logger_factory_config: FlexibleConfig = {
        "_target_": "__main__.Logger",
        "_partial_": True,  # This is the key!
        "level": "ERROR",
        "format_style": "json",
    }

    logger_factory = instantiate(logger_factory_config)

    console.print(f"✅ Factory created: {type(logger_factory)}")
    console.print(f"   Type: {logger_factory}")

    # Use the factory to create multiple loggers
    console.print("\n🏭 Using factory to create loggers:")
    app_logger = logger_factory(name="app_errors")
    db_logger = logger_factory(name="db_errors")
    api_logger = logger_factory(name="api_errors")

    # Test the loggers
    console.print("\n🧪 Testing factory-created loggers:")
    app_logger.log("Application error occurred")
    db_logger.log("Database connection failed")
    api_logger.log("API rate limit exceeded")

    console.print("\n💡 Key insight: _partial_=True creates functools.partial objects")
    console.print("   These are factory functions that can be called later")
    console.print()


def step_7_positional_arguments() -> None:
    """Step 7: Using positional arguments with _args_."""
    print_section("Step 7: Positional Arguments with _args_")

    console.print("🎯 Using positional arguments for object creation:")

    # Some classes expect positional arguments
    model_config: FlexibleConfig = {
        "_target_": "__main__.MLModel",
        "_args_": ["neural_network", 784, 10],  # model_type, input_dim, output_dim
        "learning_rate": 0.001,
    }

    console.print("📋 Configuration with positional args:")
    pprint(model_config)

    console.print("\n🔧 Instantiating with positional arguments:")
    model = instantiate(model_config)

    console.print("\n✅ Model created:")
    console.print(f"   Type: {model.model_type}")
    console.print(f"   Input dim: {model.input_dim}")
    console.print(f"   Output dim: {model.output_dim}")
    console.print(f"   Learning rate: {model.learning_rate}")

    # Test the model
    console.print("\n🧪 Testing the model:")
    model.train(epochs=5)

    console.print("\n💡 Key insight: _args_ provides positional arguments")
    console.print("   Useful for classes that require positional parameters")
    console.print()


def step_8_integration_with_config_loader() -> None:
    """Step 8: Integration with ConfigLoader and real configuration files."""
    print_section("Step 8: Integration with ConfigLoader")

    console.print("🎯 Complete workflow: YAML → ConfigLoader → instantiate:")

    # Create a comprehensive YAML configuration
    yaml_config: ConfigDict = {
        "app_name": "DataPipeline",
        "debug": False,
        "components": {
            "database": {
                "_target_": "__main__.DatabaseConnection",
                "host": "prod-db.example.com",
                "port": 5432,
                "username": "pipeline_user",
                # password will come from environment
            },
            "logger": {
                "_target_": "__main__.Logger",
                "name": "pipeline_logger",
                "level": "INFO",
                "format_style": "json",
            },
            "processor": {
                "_target_": "__main__.DataProcessor",
                "name": "MainProcessor",
                "database": {
                    "_target_": "__main__.DatabaseConnection",
                    "host": "processing-db.example.com",
                    "port": 5432,
                    "username": "processor_user",
                },
                "logger": {"_target_": "__main__.Logger", "name": "processor_logger", "level": "DEBUG"},
                "batch_size": 1000,
            },
        },
    }

    # Write to temporary YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(yaml_config, f)
        yaml_path = Path(f.name)

    # Set environment variables for secrets
    original_env = dict(os.environ)
    env_vars: EnvVarsDict = {
        "APP_COMPONENTS__DATABASE__PASSWORD": "prod_secret_password",
        "APP_COMPONENTS__PROCESSOR__DATABASE__PASSWORD": "processor_secret",
    }
    os.environ.update(env_vars)

    try:
        console.print("📝 YAML configuration created")
        console.print("🌍 Environment variables set for secrets")

        # Define Pydantic model for the configuration
        class ComponentsConfig(BaseModel):
            database: dict[str, Any]
            logger: dict[str, Any]
            processor: dict[str, Any]

        class AppConfig(BaseSettings):
            app_name: str
            debug: bool
            components: ComponentsConfig

            model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__")

        # Load configuration using ConfigLoader
        console.print("\n🔧 Loading configuration with ConfigLoader:")
        config = ConfigLoader.from_yaml_with_env(AppConfig, yaml_path, env_prefix="APP")  # type: ignore[attr-defined]

        console.print("✅ Configuration loaded:")
        console.print(f"   App: {config.app_name}")
        console.print(f"   Debug: {config.debug}")

        # Instantiate components from the loaded configuration
        console.print("\n🔧 Instantiating components:")

        database = instantiate(config.components.database)
        logger = instantiate(config.components.logger)
        processor = instantiate(config.components.processor)

        console.print("\n✅ All components instantiated!")

        # Test the components
        console.print("\n🧪 Testing the pipeline:")
        logger.log("Pipeline starting")
        result = database.query("SELECT COUNT(*) FROM raw_data")
        logger.log(f"Found data: {result}")
        processor.process(["item1", "item2", "item3"])
        logger.log("Pipeline completed")

        console.print("\n💡 Key insight: ConfigLoader + instantiate = powerful combination")
        console.print("   Load structured config from YAML/env, then instantiate objects")

    finally:
        yaml_path.unlink()
        os.environ.clear()
        os.environ.update(original_env)

    console.print()


def step_9_advanced_patterns() -> None:
    """Step 9: Advanced patterns and best practices."""
    print_section("Step 9: Advanced Patterns")

    console.print("🎯 Advanced instantiation patterns:")

    # Pattern 1: Conditional instantiation
    console.print("📋 Pattern 1: Conditional instantiation")

    def create_cache_config(cache_type: str) -> FlexibleConfig:
        if cache_type == "redis":
            return {"_target_": "__main__.CacheManager", "backend": "redis", "ttl": 3600}
        else:
            return {"_target_": "__main__.CacheManager", "backend": "memory", "ttl": 1800}

    redis_cache = instantiate(create_cache_config("redis"))
    memory_cache = instantiate(create_cache_config("memory"))

    console.print(f"✅ Created {type(redis_cache).__name__} and {type(memory_cache).__name__}")

    # Pattern 2: List of instantiated objects
    console.print("\n📋 Pattern 2: List of instantiated objects")

    logger_configs: list[FlexibleConfig] = [
        {"_target_": "__main__.Logger", "name": f"worker_{i}", "level": "INFO"} for i in range(3)
    ]

    loggers = [instantiate(config) for config in logger_configs]

    console.print(f"✅ Created {len(loggers)} worker loggers")

    # Pattern 3: Dynamic target selection
    console.print("\n📋 Pattern 3: Dynamic target selection")

    model_type = "neural_network"  # Could come from config
    target_map: dict[str, str] = {
        "neural_network": "__main__.MLModel",
        "linear": "__main__.MLModel",  # Same class, different config
    }

    dynamic_model_config: FlexibleConfig = {
        "_target_": target_map[model_type],
        "_args_": [model_type, 100, 10],
        "learning_rate": 0.01,
    }

    dynamic_model = instantiate(dynamic_model_config)

    console.print(f"✅ Created dynamic {type(dynamic_model).__name__}: {dynamic_model.model_type}")
    console.print("\n💡 Advanced patterns enable flexible, dynamic object creation")
    console.print()


def step_10_error_handling() -> None:
    """Step 10: Error handling and debugging."""
    print_section("Step 10: Error Handling and Debugging")

    console.print("🎯 Understanding common errors and how to debug them:")

    # Error 1: Missing _target_
    console.print("❌ Error 1: Missing _target_")
    try:
        missing_target_config: FlexibleConfig = {"name": "test", "level": "INFO"}
        instantiate(missing_target_config)
    except Exception as e:
        console.print(f"   Exception: {type(e).__name__}: {e}")

    # Error 2: Invalid target path
    console.print("\n❌ Error 2: Invalid target path")
    try:
        invalid_target_config: FlexibleConfig = {"_target_": "nonexistent.module.Class"}
        instantiate(invalid_target_config)
    except Exception as e:
        console.print(f"   Exception: {type(e).__name__}: {e}")

    # Error 3: Missing required parameters
    console.print("\n❌ Error 3: Missing required parameters")
    try:
        missing_params_config: FlexibleConfig = {"_target_": "__main__.DatabaseConnection"}  # Missing required 'host'
        instantiate(missing_params_config)
    except Exception as e:
        console.print(f"   Exception: {type(e).__name__}: {e}")

    console.print("\n💡 Debugging tips:")
    console.print("   • Always check _target_ path is correct")
    console.print("   • Verify all required parameters are provided")
    console.print("   • Use dependency injection for complex dependencies")
    console.print("   • Check import paths match your module structure")
    console.print()


def main() -> None:
    """Run all learning steps."""
    console.print(
        Panel.fit(
            "🎓 Comprehensive Learning Guide\n"
            "frostbound.pydanticonf._instantiate\n\n"
            "This guide covers the powerful object instantiation\n"
            "system that enables creating complex object hierarchies\n"
            "from configuration files.",
            title="Instantiation Learning Guide",
            style="bold green",
        )
    )

    step_1_basic_instantiation()
    step_2_dict_instantiation()
    step_3_parameter_overrides()
    step_4_recursive_instantiation()
    step_5_dependency_injection()
    step_6_partial_instantiation()
    step_7_positional_arguments()
    step_8_integration_with_config_loader()
    step_9_advanced_patterns()
    step_10_error_handling()

    console.print(
        Panel.fit(
            "🎉 Instantiation Mastery Complete!\n\n"
            "You now understand:\n\n"
            "• DynamicConfig for describing object creation\n"
            "• instantiate() for creating objects from configs\n"
            "• Recursive instantiation for complex hierarchies\n"
            "• Dependency injection for shared objects\n"
            "• Partial instantiation for factory patterns\n"
            "• Integration with ConfigLoader for complete workflows\n\n"
            "This system enables powerful configuration-driven\n"
            "application architectures!",
            title="🎓 Learning Complete!",
            style="bold green",
        )
    )


if __name__ == "__main__":
    main()
