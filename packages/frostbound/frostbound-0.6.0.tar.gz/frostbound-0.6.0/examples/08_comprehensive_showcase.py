"""
Comprehensive ConfigLoader Showcase with Real Classes and DynamicConfig

This example demonstrates the FULL POWER of frostbound.pydanticonf with:
- Real component classes that can be instantiated
- Proper DynamicConfig models with _target_ fields
- Complex nested configurations
- Dependency injection
- Complete application execution
- Hybrid env_file approach

This is a production-ready example showing how to build configurable,
type-safe applications with frostbound.pydanticonf.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel

from frostbound.pydanticonf import ConfigLoader, DynamicConfig, instantiate, register_dependency

console = Console()


# ============================================================================
# Real Component Classes (The actual objects we want to instantiate)
# ============================================================================


class Database:
    """Production database connection."""

    def __init__(self, host: str, port: int = 5432, database: str = "app", pool_size: int = 10):
        self.host = host
        self.port = port
        self.database = database
        self.pool_size = pool_size
        self.connected = False

    def connect(self) -> None:
        """Simulate database connection."""
        console.print(f"🐘 Connecting to PostgreSQL at {self.host}:{self.port}/{self.database}")
        console.print(f"   Pool size: {self.pool_size}")
        self.connected = True

    def query(self, sql: str) -> dict[str, Any]:
        """Execute a query."""
        if not self.connected:
            raise RuntimeError("Database not connected")
        return {"result": f"Executed: {sql}", "rows": 42}


class RedisCache:
    """Redis cache for high-performance caching."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 3600):
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl
        self.connected = False

    def connect(self) -> None:
        """Connect to Redis."""
        console.print(f"🔴 Connecting to Redis at {self.host}:{self.port}/{self.db}")
        console.print(f"   Default TTL: {self.ttl}s")
        self.connected = True

    def get(self, key: str) -> str | None:
        """Get value from cache."""
        if not self.connected:
            raise RuntimeError("Cache not connected")
        return f"cached_value_for_{key}"

    def set(self, key: str, value: str) -> None:
        """Set value in cache."""
        if not self.connected:
            raise RuntimeError("Cache not connected")
        console.print(f"   Cached {key} = {value}")


class Logger:
    """Application logger with configurable levels."""

    def __init__(
        self, name: str, level: str = "INFO", format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ):
        self.name = name
        self.level = level
        self.format = format

    def info(self, message: str) -> None:
        """Log info message."""
        console.print(f"📝 [{self.level}] {self.name}: {message}")

    def error(self, message: str) -> None:
        """Log error message."""
        console.print(f"🚨 [ERROR] {self.name}: {message}")


class MLModel:
    """Machine learning model base class."""

    def __init__(self, name: str, learning_rate: float = 0.001):
        self.name = name
        self.learning_rate = learning_rate
        self.trained = False

    def train(self, data: dict[str, Any]) -> None:
        """Train the model."""
        console.print(f"🧠 Training {self.name} with lr={self.learning_rate}")
        self.trained = True

    def predict(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Make predictions."""
        if not self.trained:
            raise RuntimeError("Model not trained")
        return {"prediction": f"{self.name}_result", "confidence": 0.95}


class NeuralNetwork(MLModel):
    """Neural network implementation."""

    def __init__(self, name: str, learning_rate: float = 0.001, hidden_layers: int = 3, dropout: float = 0.1):
        super().__init__(name, learning_rate)
        self.hidden_layers = hidden_layers
        self.dropout = dropout

    def train(self, data: dict[str, Any]) -> None:
        """Train neural network."""
        console.print(f"🧠 Training Neural Network '{self.name}':")
        console.print(f"   Hidden layers: {self.hidden_layers}")
        console.print(f"   Dropout: {self.dropout}")
        console.print(f"   Learning rate: {self.learning_rate}")
        self.trained = True


class DataProcessor:
    """Data processing pipeline."""

    def __init__(self, name: str, database: Database, cache: RedisCache, logger: Logger):
        self.name = name
        self.database = database
        self.cache = cache
        self.logger = logger

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through the pipeline."""
        self.logger.info(f"Processing data in {self.name}")

        # Ensure connections are established
        if not self.database.connected:
            self.database.connect()
        if not self.cache.connected:
            self.cache.connect()

        # Check cache first
        cached = self.cache.get("processed_data")
        if cached:
            self.logger.info("Using cached result")
            return {"result": cached, "source": "cache"}

        # Process with database
        db_result = self.database.query("SELECT * FROM data")
        processed = {"processed": db_result, "timestamp": "2024-01-01"}

        # Cache result
        self.cache.set("processed_data", str(processed))

        self.logger.info("Data processing completed")
        return processed


class MLApplication:
    """Main ML application orchestrator."""

    def __init__(self, name: str, version: str, processor: DataProcessor, model: MLModel, logger: Logger):
        self.name = name
        self.version = version
        self.processor = processor
        self.model = model
        self.logger = logger

    def run(self) -> dict[str, Any]:
        """Run the complete ML pipeline."""
        self.logger.info(f"Starting {self.name} v{self.version}")

        # Connect all components
        self.processor.database.connect()
        self.processor.cache.connect()

        # Process data
        data = {"input": "sample_data"}
        processed_data = self.processor.process(data)

        # Train and predict
        self.model.train(processed_data)
        prediction = self.model.predict(processed_data)

        result = {
            "application": self.name,
            "version": self.version,
            "processed_data": processed_data,
            "prediction": prediction,
            "status": "success",
        }

        self.logger.info("Application run completed successfully")
        return result


# ============================================================================
# Configuration Models with DynamicConfig
# ============================================================================


class DatabaseConfig(DynamicConfig[Database]):
    """Configuration for Database instantiation."""

    host: str
    port: int = 5432
    database: str = "app"
    pool_size: int = 10


class RedisCacheConfig(DynamicConfig[RedisCache]):
    """Configuration for RedisCache instantiation."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ttl: int = 3600


class LoggerConfig(DynamicConfig[Logger]):
    """Configuration for Logger instantiation."""

    name: str
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class NeuralNetworkConfig(DynamicConfig[NeuralNetwork]):
    """Configuration for NeuralNetwork instantiation."""

    name: str
    learning_rate: float = 0.001
    hidden_layers: int = 3
    dropout: float = 0.1


class DataProcessorConfig(DynamicConfig[DataProcessor]):
    """Configuration for DataProcessor instantiation."""

    name: str
    database: DatabaseConfig
    cache: RedisCacheConfig
    logger: LoggerConfig


class MLApplicationConfig(DynamicConfig[MLApplication]):
    """Configuration for MLApplication instantiation."""

    name: str
    version: str = "1.0.0"
    processor: DataProcessorConfig
    model: NeuralNetworkConfig
    logger: LoggerConfig


# ============================================================================
# Pure Data Models (No instantiation)
# ============================================================================


class ServerConfig(BaseModel):
    """Server configuration data."""

    host: str = "localhost"
    port: int = 8000
    workers: int = 4
    timeout: int = 30


class SecurityConfig(BaseModel):
    """Security configuration data."""

    secret_key: str = Field(..., description="Secret key from environment")
    jwt_expiry: int = 3600
    rate_limit: int = 100


# ============================================================================
# Main Settings Class
# ============================================================================


class AppSettings(BaseSettings):
    """
    Main application settings combining data and instantiable configurations.

    This demonstrates the hybrid approach:
    - Pure data configs (server, security)
    - Instantiable configs with DynamicConfig
    - Environment variable loading
    - Type safety and validation
    """

    model_config = SettingsConfigDict(
        env_prefix="MLAPP_", env_nested_delimiter="__", case_sensitive=False, extra="allow"
    )

    # Pure data configuration
    app_name: str = "ML Showcase Application"
    debug: bool = False
    server: ServerConfig = ServerConfig()
    security: SecurityConfig

    # Instantiable configuration
    application: MLApplicationConfig


# ============================================================================
# Demonstration Functions
# ============================================================================


def demo_basic_instantiation():
    """Demo 1: Basic instantiation from DynamicConfig."""
    console.print(
        Panel.fit(
            "🔧 Demo 1: Basic Instantiation\n\n"
            "Creating individual components from DynamicConfig models.\n"
            "This shows the fundamental instantiate() functionality.",
            title="Basic Instantiation",
            style="bold green",
        )
    )

    # Create database config and instantiate
    db_config = DatabaseConfig(
        _target_="examples.08_comprehensive_showcase.Database",
        host="localhost",
        port=5432,
        database="showcase_db",
        pool_size=20,
    )

    database = instantiate(db_config)
    database.connect()
    result = database.query("SELECT COUNT(*) FROM users")
    console.print(f"   Query result: {result}")

    # Create cache config and instantiate
    cache_config = RedisCacheConfig(
        _target_="examples.08_comprehensive_showcase.RedisCache", host="localhost", port=6379, ttl=7200
    )

    cache = instantiate(cache_config)
    cache.connect()
    cache.set("demo_key", "demo_value")
    value = cache.get("demo_key")
    console.print(f"   Cached value: {value}")


def demo_nested_instantiation():
    """Demo 2: Nested instantiation with complex dependencies."""
    console.print(
        Panel.fit(
            "🏗️ Demo 2: Nested Instantiation\n\n"
            "Creating complex objects with nested dependencies.\n"
            "All dependencies are automatically instantiated recursively.",
            title="Nested Instantiation",
            style="bold blue",
        )
    )

    # Create complex nested configuration
    processor_config = DataProcessorConfig(
        _target_="examples.08_comprehensive_showcase.DataProcessor",
        name="Production Data Processor",
        database=DatabaseConfig(
            _target_="examples.08_comprehensive_showcase.Database",
            host="prod-db.company.com",
            database="production",
            pool_size=50,
        ),
        cache=RedisCacheConfig(
            _target_="examples.08_comprehensive_showcase.RedisCache", host="prod-cache.company.com", ttl=1800
        ),
        logger=LoggerConfig(_target_="examples.08_comprehensive_showcase.Logger", name="DataProcessor", level="INFO"),
    )

    # Instantiate - all nested components created automatically
    processor = instantiate(processor_config)

    # Use the processor
    data = {"input": "production_data"}
    result = processor.process(data)
    console.print(f"   Processing result: {result['source']}")


def demo_dependency_injection():
    """Demo 3: Dependency injection for shared resources."""
    console.print(
        Panel.fit(
            "💉 Demo 3: Dependency Injection\n\n"
            "Sharing common resources across multiple components\n"
            "using automatic dependency injection.",
            title="Dependency Injection",
            style="bold magenta",
        )
    )

    # Register shared dependencies
    shared_logger = Logger("SharedLogger", "DEBUG")
    shared_cache = RedisCache("shared-cache.company.com", ttl=3600)
    shared_cache.connect()

    register_dependency("logger", shared_logger)
    register_dependency("cache", shared_cache)

    # Create configs that will use injected dependencies
    processor1_config = {
        "_target_": "examples.08_comprehensive_showcase.DataProcessor",
        "name": "Processor1",
        "database": {"_target_": "examples.08_comprehensive_showcase.Database", "host": "db1.company.com"},
        # logger and cache will be injected automatically
    }

    processor2_config = {
        "_target_": "examples.08_comprehensive_showcase.DataProcessor",
        "name": "Processor2",
        "database": {"_target_": "examples.08_comprehensive_showcase.Database", "host": "db2.company.com"},
        # logger and cache will be injected automatically
    }

    # Instantiate - shared dependencies injected
    processor1 = instantiate(processor1_config)
    processor2 = instantiate(processor2_config)

    # Verify they share the same logger and cache
    console.print(f"   Processor1 logger: {processor1.logger.name}")
    console.print(f"   Processor2 logger: {processor2.logger.name}")
    console.print(f"   Same logger instance: {processor1.logger is processor2.logger}")
    console.print(f"   Same cache instance: {processor1.cache is processor2.cache}")


def demo_yaml_configuration():
    """Demo 4: Complete YAML-driven configuration."""
    console.print(
        Panel.fit(
            "📄 Demo 4: YAML Configuration\n\n"
            "Loading complete application configuration from YAML\n"
            "with environment variable overrides and instantiation.",
            title="YAML Configuration",
            style="bold cyan",
        )
    )

    # Create comprehensive YAML configuration
    yaml_content = """
app_name: "ML Showcase Application"
debug: false

server:
  host: "0.0.0.0"
  port: 8080
  workers: 8
  timeout: 60

security:
  secret_key: "yaml_secret_key"  # Will be overridden by env var
  jwt_expiry: 7200
  rate_limit: 1000

application:
  _target_: "examples.08_comprehensive_showcase.MLApplication"
  name: "Production ML Pipeline"
  version: "2.1.0"

  processor:
    _target_: "examples.08_comprehensive_showcase.DataProcessor"
    name: "Production Data Processor"

    database:
      _target_: "examples.08_comprehensive_showcase.Database"
      host: "yaml-db.company.com"
      port: 5432
      database: "ml_production"
      pool_size: 100

    cache:
      _target_: "examples.08_comprehensive_showcase.RedisCache"
      host: "yaml-cache.company.com"
      port: 6379
      ttl: 3600

    logger:
      _target_: "examples.08_comprehensive_showcase.Logger"
      name: "DataProcessor"
      level: "INFO"

  model:
    _target_: "examples.08_comprehensive_showcase.NeuralNetwork"
    name: "Production Neural Network"
    learning_rate: 0.001
    hidden_layers: 5
    dropout: 0.2

  logger:
    _target_: "examples.08_comprehensive_showcase.Logger"
    name: "MLApplication"
    level: "INFO"
"""

    # Create temporary YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_file = f.name

    # Set environment variables for overrides
    import os

    os.environ.update(
        {
            "MLAPP_SECURITY__SECRET_KEY": "super_secret_from_env",
            "MLAPP_APPLICATION__PROCESSOR__DATABASE__HOST": "env-override-db.company.com",
            "MLAPP_DEBUG": "true",
        }
    )

    try:
        # Load configuration using ConfigLoader
        settings = ConfigLoader.from_yaml_with_env(AppSettings, Path(yaml_file), env_prefix="MLAPP")

        console.print("   Configuration loaded successfully!")
        console.print(f"   App name: {settings.app_name}")
        console.print(f"   Debug: {settings.debug} (overridden by env)")
        console.print(f"   Secret key: {'***' if settings.security.secret_key != 'yaml_secret_key' else 'from_yaml'}")
        console.print(f"   DB host: {settings.application.processor.database.host} (env override)")

        # Instantiate the complete application
        app = instantiate(settings.application)

        # Run the application
        console.print("\n   🚀 Running the complete ML application...")
        result = app.run()
        console.print(f"   Application result: {result['status']}")

    finally:
        os.unlink(yaml_file)
        # Clean up environment variables
        for key in ["MLAPP_SECURITY__SECRET_KEY", "MLAPP_APPLICATION__PROCESSOR__DATABASE__HOST", "MLAPP_DEBUG"]:
            os.environ.pop(key, None)


def demo_hybrid_env_file():
    """Demo 5: Hybrid env_file approach."""
    console.print(
        Panel.fit(
            "🔄 Demo 5: Hybrid env_file Approach\n\n"
            "Demonstrating the new hybrid approach that respects\n"
            "Pydantic's env_file configuration while adding YAML capabilities.",
            title="Hybrid env_file",
            style="bold yellow",
        )
    )

    # Create .env file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("HYBRID_SECRET_KEY=secret_from_env_file\n")
        f.write("HYBRID_DEBUG=true\n")
        f.write("HYBRID_APPLICATION__NAME=App from env file\n")
        env_file = f.name

    # Create YAML override
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("""
application:
  name: "App from YAML"  # This will override .env
  version: "3.0.0"

server:
  port: 9000
""")
        yaml_file = f.name

    try:
        # Settings WITH env_file (uses hybrid Pydantic-native mode)
        class HybridSettings(BaseSettings):
            model_config = SettingsConfigDict(
                env_file=env_file, env_prefix="HYBRID_", env_nested_delimiter="__", extra="allow"
            )

            secret_key: str = "default_secret"
            debug: bool = False
            application_name: str = "default_app"
            application_version: str = "1.0.0"
            server_port: int = 8000

        # Load using hybrid approach - automatically detects env_file
        settings = ConfigLoader.from_yaml_with_env(HybridSettings, Path(yaml_file))

        console.print("   Hybrid approach results:")
        console.print(f"   Secret: {settings.secret_key} (from .env file)")
        console.print(f"   Debug: {settings.debug} (from .env file)")
        console.print(f"   App Name: {settings.application_name} (YAML overrides .env)")
        console.print(f"   App Version: {settings.application_version} (from YAML)")
        console.print(f"   Server Port: {settings.server_port} (from YAML)")

        console.print("\n   ✅ Hybrid approach automatically:")
        console.print("     • Detected env_file configuration")
        console.print("     • Used Pydantic's native .env loading")
        console.print("     • Applied YAML as intelligent overrides")

    finally:
        import os

        os.unlink(env_file)
        os.unlink(yaml_file)


def main():
    """Run the comprehensive showcase."""
    console.print(
        Panel.fit(
            "🎯 Comprehensive ConfigLoader Showcase\n\n"
            "This showcase demonstrates the FULL POWER of\n"
            "frostbound.pydanticonf with real classes, DynamicConfig,\n"
            "dependency injection, and complete applications.\n\n"
            "Perfect for understanding how to build production-ready,\n"
            "configurable applications with type safety and elegance!",
            title="🚀 Comprehensive Showcase",
            style="bold white on blue",
        )
    )

    try:
        demo_basic_instantiation()
        console.print("\n" + "=" * 80 + "\n")

        demo_nested_instantiation()
        console.print("\n" + "=" * 80 + "\n")

        demo_dependency_injection()
        console.print("\n" + "=" * 80 + "\n")

        demo_yaml_configuration()
        console.print("\n" + "=" * 80 + "\n")

        demo_hybrid_env_file()

        console.print(
            Panel.fit(
                "🎉 Comprehensive Showcase Complete!\n\n"
                "You've seen the full power of frostbound.pydanticonf:\n\n"
                "✅ Real component classes with proper instantiation\n"
                "✅ DynamicConfig models with _target_ fields\n"
                "✅ Complex nested configurations\n"
                "✅ Automatic dependency injection\n"
                "✅ YAML + environment variable loading\n"
                "✅ Hybrid env_file approach\n"
                "✅ Complete application execution\n"
                "✅ Type safety and validation throughout\n\n"
                "This is how you build sophisticated, configurable,\n"
                "production-ready applications with frostbound! 🚀",
                title="🏆 Mission Accomplished",
                style="bold green",
            )
        )

    except Exception as e:
        console.print(f"\n❌ [bold red]Showcase failed: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
