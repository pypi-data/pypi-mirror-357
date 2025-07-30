"""
Example 09: Full ConfigLoader Showcase with Real Classes and Instantiation
Demonstrates ALL ConfigLoader features with production-ready patterns
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint

from frostbound.pydanticonf import ConfigLoader, DynamicConfig, instantiate, register_dependency

console = Console()


# =============================================================================
# Real Component Classes (like in production)
# =============================================================================


class Database:
    """Base database interface."""

    def __init__(self, host: str, port: int, **kwargs: Any) -> None:
        self.host = host
        self.port = port
        self.config = kwargs

    def connect(self) -> str:
        return f"Connected to {self.__class__.__name__} at {self.host}:{self.port}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.host}:{self.port})"


class PostgreSQL(Database):
    """PostgreSQL database implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        username: str = "postgres",
        password: str = "password",
        pool_size: int = 10,
        **kwargs: Any,
    ) -> None:
        super().__init__(host, port)
        self.database = database
        self.username = username
        self.password = password
        self.pool_size = pool_size
        self.extra = kwargs


class MongoDB(Database):
    """MongoDB database implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        database: str = "admin",
        auth_source: str = "admin",
        **kwargs: Any,
    ) -> None:
        super().__init__(host, port)
        self.database = database
        self.auth_source = auth_source
        self.extra = kwargs


class Cache:
    """Base cache interface."""

    def __init__(self, ttl: int = 3600):
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        return f"Cache miss for {key}"

    def set(self, key: str, value: Any) -> None:
        pass


class RedisCache(Cache):
    """Redis cache implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        ttl: int = 3600,
        max_connections: int = 100,
        **kwargs: Any,
    ) -> None:
        super().__init__(ttl)
        self.host = host
        self.port = port
        self.db = db
        self.max_connections = max_connections
        self.extra = kwargs

    def __repr__(self) -> str:
        return f"RedisCache({self.host}:{self.port}/db{self.db}, ttl={self.ttl})"


class MemcachedCache(Cache):
    """Memcached cache implementation."""

    def __init__(self, servers: Optional[list[str]] = None, ttl: int = 3600, **kwargs: Any) -> None:
        super().__init__(ttl)
        self.servers = servers or ["localhost:11211"]
        self.extra = kwargs

    def __repr__(self) -> str:
        return f"MemcachedCache(servers={len(self.servers)}, ttl={self.ttl})"


class Model:
    """Base ML model interface."""

    def __init__(self, name: str = "model"):
        self.name = name

    def predict(self, x: Any) -> str:
        return f"{self.name} prediction"


class NeuralNetwork(Model):
    """Neural network model."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        activation: str = "relu",
        dropout: float = 0.1,
        learning_rate: float = 0.001,
        name: str = "neural_net",
    ):
        super().__init__(name)
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.activation = activation
        self.dropout = dropout
        self.learning_rate = learning_rate

    def __repr__(self):
        return f"NeuralNetwork({self.input_dim}→{self.hidden_dim}→{self.output_dim}, {self.activation}, lr={self.learning_rate})"


class LinearRegression(Model):
    """Linear regression model."""

    def __init__(self, input_dim: int, regularization: float = 0.01, solver: str = "lbfgs", name: str = "linear_model"):
        super().__init__(name)
        self.input_dim = input_dim
        self.regularization = regularization
        self.solver = solver

    def __repr__(self):
        return f"LinearRegression(dim={self.input_dim}, reg={self.regularization}, {self.solver})"


class DataProcessor:
    """Data preprocessing component."""

    def __init__(
        self, normalize: bool = True, scale: bool = True, features: list[str] = None, cache: Optional[Cache] = None
    ):
        self.normalize = normalize
        self.scale = scale
        self.features = features or []
        self.cache = cache

    def process(self, data):
        actions = []
        if self.normalize:
            actions.append("normalized")
        if self.scale:
            actions.append("scaled")
        return f"Data {' & '.join(actions)} with {len(self.features)} features"

    def __repr__(self):
        cache_info = f", cache={type(self.cache).__name__}" if self.cache else ""
        return f"DataProcessor(normalize={self.normalize}, features={len(self.features)}{cache_info})"


class Pipeline:
    """ML pipeline combining model and processor."""

    def __init__(
        self, name: str, model: Model, processor: DataProcessor, database: Database, cache: Optional[Cache] = None
    ):
        self.name = name
        self.model = model
        self.processor = processor
        self.database = database
        self.cache = cache

    def run(self):
        db_status = self.database.connect()
        process_result = self.processor.process("input_data")
        prediction = self.model.predict("processed_data")
        return f"Pipeline '{self.name}': {db_status}, {process_result}, {prediction}"

    def __repr__(self):
        return f"Pipeline({self.name}, model={type(self.model).__name__}, processor={type(self.processor).__name__})"


class Application:
    """Main application orchestrating pipelines."""

    def __init__(
        self, name: str, version: str, pipelines: list[Pipeline], primary_database: Database, primary_cache: Cache
    ):
        self.name = name
        self.version = version
        self.pipelines = pipelines
        self.primary_database = primary_database
        self.primary_cache = primary_cache

    def run(self):
        console.print(f"\n🚀 Running {self.name} v{self.version}")
        console.print(f"   Database: {self.primary_database}")
        console.print(f"   Cache: {self.primary_cache}")

        for pipeline in self.pipelines:
            result = pipeline.run()
            console.print(f"   ✓ {result}")

        console.print(f"   ✅ {self.name} completed successfully!")


# =============================================================================
# Configuration Models with DynamicConfig
# =============================================================================


class DatabaseConfig(DynamicConfig[Database]):
    """Database configuration with instantiation support."""

    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    username: str = "user"
    password: str = "password"


class PostgreSQLConfig(DatabaseConfig):
    """PostgreSQL specific configuration."""

    target_: str = Field(default="__main__.PostgreSQL", alias="_target_")
    pool_size: int = 10
    ssl_mode: str = "prefer"


class MongoDBConfig(DatabaseConfig):
    """MongoDB specific configuration."""

    target_: str = Field(default="__main__.MongoDB", alias="_target_")
    port: int = 27017
    auth_source: str = "admin"
    replica_set: Optional[str] = None


class CacheConfig(DynamicConfig[Cache]):
    """Cache configuration with instantiation support."""

    ttl: int = 3600
    enabled: bool = True


class RedisCacheConfig(CacheConfig):
    """Redis cache configuration."""

    target_: str = Field(default="__main__.RedisCache", alias="_target_")
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    max_connections: int = 100


class MemcachedCacheConfig(CacheConfig):
    """Memcached cache configuration."""

    target_: str = Field(default="__main__.MemcachedCache", alias="_target_")
    servers: list[str] = Field(default_factory=lambda: ["localhost:11211"])


class ModelConfig(DynamicConfig[Model]):
    """ML model configuration."""

    name: str = "model"
    input_dim: int = 100


class NeuralNetworkConfig(ModelConfig):
    """Neural network configuration."""

    target_: str = Field(default="__main__.NeuralNetwork", alias="_target_")
    hidden_dim: int = 50
    output_dim: int = 10
    activation: str = "relu"
    dropout: float = 0.1
    learning_rate: float = 0.001


class LinearRegressionConfig(ModelConfig):
    """Linear regression configuration."""

    target_: str = Field(default="__main__.LinearRegression", alias="_target_")
    regularization: float = 0.01
    solver: str = "lbfgs"


class DataProcessorConfig(DynamicConfig[Any]):
    """Data processor configuration."""

    target_: str = Field(default="__main__.DataProcessor", alias="_target_")
    normalize: bool = True
    scale: bool = True
    features: list[str] = Field(default_factory=list)
    cache: Optional[CacheConfig] = None


class PipelineConfig(DynamicConfig[Any]):
    """Pipeline configuration."""

    target_: str = Field(default="__main__.Pipeline", alias="_target_")
    name: str
    model: ModelConfig
    processor: DataProcessorConfig
    database: Optional[DatabaseConfig] = None  # Can be injected
    cache: Optional[CacheConfig] = None


class ApplicationConfig(DynamicConfig[Any]):
    """Application configuration."""

    target_: str = Field(default="__main__.Application", alias="_target_")
    name: str = "ML Application"
    version: str = "1.0.0"
    pipelines: list[PipelineConfig] = Field(default_factory=list)
    primary_database: DatabaseConfig = Field(default_factory=PostgreSQLConfig)
    primary_cache: CacheConfig = Field(default_factory=RedisCacheConfig)


# =============================================================================
# Settings Classes (Different Modes)
# =============================================================================

# Get the directory for env files
_SCRIPT_DIR = Path(__file__).parent


class BasicAppSettings(BaseSettings):
    """Basic settings without env_file (source composition mode)."""

    model_config = SettingsConfigDict(
        extra="ignore"  # Ignore extra fields
    )

    # Simple configuration
    app_name: str = "BasicApp"
    debug: bool = False
    port: int = 8000
    log_level: str = "INFO"

    # Component configurations
    database: PostgreSQLConfig = Field(default_factory=PostgreSQLConfig)
    cache: RedisCacheConfig = Field(default_factory=RedisCacheConfig)
    model: NeuralNetworkConfig = Field(default_factory=NeuralNetworkConfig)
    processor: DataProcessorConfig = Field(default_factory=DataProcessorConfig)


class PydanticNativeAppSettings(BaseSettings):
    """Settings with Pydantic's env_file configured."""

    model_config = SettingsConfigDict(
        env_file=str(_SCRIPT_DIR / ".env"), env_prefix="APP_", env_nested_delimiter="__", extra="ignore"
    )

    # Simple configuration
    app_name: str = "PydanticApp"
    debug: bool = False
    port: int = 8000
    secret_key: str = "default-secret"
    log_level: str = "INFO"

    # Component configurations
    database: DatabaseConfig = Field(default_factory=PostgreSQLConfig)
    cache: CacheConfig = Field(default_factory=RedisCacheConfig)
    model: ModelConfig = Field(default_factory=NeuralNetworkConfig)
    processor: DataProcessorConfig = Field(default_factory=DataProcessorConfig)

    # Complex application config
    application: ApplicationConfig = Field(default_factory=ApplicationConfig)


class ProductionAppSettings(BaseSettings):
    """Production settings with multiple env files."""

    model_config = SettingsConfigDict(
        env_file=[str(_SCRIPT_DIR / ".env"), str(_SCRIPT_DIR / ".env.prod")], env_prefix="PROD_", extra="ignore"
    )

    app_name: str = "ProductionApp"
    environment: str = "production"
    debug: bool = False
    port: int = 443
    workers: int = 4

    # Production-grade components
    primary_db: PostgreSQLConfig = Field(default_factory=PostgreSQLConfig)
    secondary_db: MongoDBConfig = Field(default_factory=MongoDBConfig)
    cache: RedisCacheConfig = Field(default_factory=RedisCacheConfig)

    # ML components
    model_v1: NeuralNetworkConfig = Field(default_factory=NeuralNetworkConfig)
    model_v2: LinearRegressionConfig = Field(default_factory=LinearRegressionConfig)

    # Full application
    application: ApplicationConfig = Field(default_factory=ApplicationConfig)


# =============================================================================
# Comprehensive Showcase
# =============================================================================


def showcase_full_configloader():
    """Comprehensive showcase with real classes and instantiation."""

    console.print(
        Panel.fit(
            "🎯 Full ConfigLoader Showcase with Real Classes\n\n"
            "This example demonstrates the COMPLETE power of ConfigLoader:\n"
            "• 📄 All loading methods with real configuration models\n"
            "• 🏗️ DynamicConfig for automatic instantiation\n"
            "• 🔧 Real component classes (Database, Cache, ML Models)\n"
            "• 🔗 Dependency injection support\n"
            "• 🚀 Complete application execution\n"
            "• 🌍 Environment variable handling\n"
            "• 🎭 All modes: Pydantic-native, Source composition, Forced",
            title="Full ConfigLoader Showcase",
            style="bold blue",
        )
    )

    # ==========================================================================
    # PART 1: Source Composition Mode (No env_file)
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 1: Source Composition Mode[/bold cyan]")
    console.print("=" * 80)

    console.print("\n[yellow]1.1 Basic loading with YAML + Environment:[/yellow]")

    # Set some environment variables
    os.environ["BASIC_APP_NAME"] = "BasicAppFromEnv"
    os.environ["BASIC_DEBUG"] = "true"
    os.environ["BASIC_DATABASE__HOST"] = "env-db-host"
    os.environ["BASIC_DATABASE__PORT"] = "5433"
    os.environ["BASIC_CACHE__HOST"] = "env-redis-host"
    os.environ["BASIC_MODEL__LEARNING_RATE"] = "0.002"

    # Create a YAML configuration
    yaml_content = """
app_name: BasicAppFromYAML
port: 9000
database:
  database: yaml_database
  pool_size: 20
cache:
  ttl: 7200
  max_connections: 200
model:
  hidden_dim: 128
  activation: tanh
processor:
  features:
    - age
    - income
    - score
  cache:
    _target_: __main__.MemcachedCache
    servers:
      - cache1:11211
      - cache2:11211
"""

    yaml_path = _SCRIPT_DIR / "temp_config.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)

    try:
        # Load configuration
        settings = ConfigLoader.from_yaml_with_env(
            BasicAppSettings, yaml_path=yaml_path, env_prefix="BASIC_", env_nested_delimiter="__"
        )

        console.print("\nLoaded configuration:")
        pprint(settings)

        console.print("\n[bold]Precedence demonstration:[/bold]")
        console.print(f"  app_name: [green]{settings.app_name}[/green] (from env)")
        console.print(f"  port: [yellow]{settings.port}[/yellow] (from yaml)")
        console.print(f"  debug: [green]{settings.debug}[/green] (from env)")
        console.print(f"  database.host: [green]{settings.database.host}[/green] (from env)")
        console.print(f"  database.database: [yellow]{settings.database.database}[/yellow] (from yaml)")
        console.print(f"  model.learning_rate: [green]{settings.model.learning_rate}[/green] (from env)")
        console.print(f"  model.hidden_dim: [yellow]{settings.model.hidden_dim}[/yellow] (from yaml)")

        # Instantiate components
        console.print("\n[yellow]1.2 Instantiating components:[/yellow]")

        db = instantiate(settings.database)
        console.print(f"\nDatabase: {db}")
        console.print(f"  {db.connect()}")

        cache = instantiate(settings.cache)
        console.print(f"\nCache: {cache}")

        model = instantiate(settings.model)
        console.print(f"\nModel: {model}")

        processor = instantiate(settings.processor)
        console.print(f"\nProcessor: {processor}")
        console.print(f"  Features: {processor.features}")
        console.print(f"  Processor cache: {processor.cache}")

    finally:
        yaml_path.unlink()
        for key in list(os.environ.keys()):
            if key.startswith("BASIC_"):
                del os.environ[key]

    # ==========================================================================
    # PART 2: Pydantic-native Mode (With env_file)
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 2: Pydantic-native Mode[/bold cyan]")
    console.print("=" * 80)

    console.print("\n[yellow]2.1 Loading with .env file detection:[/yellow]")

    # Load with Pydantic handling .env
    settings_native = ConfigLoader.from_yaml_with_env(PydanticNativeAppSettings)
    console.print("\nLoaded from .env (Pydantic-native):")
    pprint(settings_native)

    # Create YAML for override
    yaml_content_override = """
app_name: PydanticAppWithYAMLOverride
database:
  _target_: __main__.MongoDB
  host: mongo-host
  port: 27017
  database: ml_database
model:
  _target_: __main__.LinearRegression
  input_dim: 50
  regularization: 0.001
application:
  name: ML Pipeline System
  version: 2.0.0
  pipelines:
    - name: neural_pipeline
      model:
        _target_: __main__.NeuralNetwork
        input_dim: 100
        hidden_dim: 64
        output_dim: 10
        learning_rate: 0.0001
      processor:
        normalize: true
        features: [feature1, feature2, feature3]
    - name: linear_pipeline
      model:
        _target_: __main__.LinearRegression
        input_dim: 100
        regularization: 0.1
      processor:
        normalize: false
        scale: true
        features: [feature1, feature2]
"""

    yaml_override_path = _SCRIPT_DIR / "override_config.yaml"
    with open(yaml_override_path, "w") as f:
        f.write(yaml_content_override)

    try:
        console.print("\n[yellow]2.2 Pydantic-native + YAML override:[/yellow]")
        settings_with_override = ConfigLoader.from_yaml_with_env(
            PydanticNativeAppSettings, yaml_path=yaml_override_path
        )

        console.print("\nAfter YAML override:")
        console.print(f"  app_name: {settings_with_override.app_name}")
        console.print(f"  database type: {settings_with_override.database.target_}")
        console.print(f"  model type: {settings_with_override.model.target_}")

        # Instantiate the full application
        console.print("\n[yellow]2.3 Instantiating complete application:[/yellow]")

        # First instantiate primary components
        primary_db = instantiate(settings_with_override.database)
        primary_cache = instantiate(settings_with_override.cache)

        console.print("\nPrimary components:")
        console.print(f"  Database: {primary_db}")
        console.print(f"  Cache: {primary_cache}")

        # Register for dependency injection
        register_dependency("database", primary_db)
        register_dependency("cache", primary_cache)

        # Update application config with instantiated components
        settings_with_override.application.primary_database = settings_with_override.database
        settings_with_override.application.primary_cache = settings_with_override.cache

        # Instantiate full application
        app = instantiate(settings_with_override.application)

        console.print(f"\nApplication: {app.name} v{app.version}")
        console.print(f"  Pipelines: {len(app.pipelines)}")
        for pipeline in app.pipelines:
            console.print(f"    - {pipeline}")

        # Run the application
        app.run()

    finally:
        yaml_override_path.unlink()

    # ==========================================================================
    # PART 3: Production Multi-env Example
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 3: Production Multi-env Configuration[/bold cyan]")
    console.print("=" * 80)

    console.print("\n[yellow]3.1 Loading from multiple env files:[/yellow]")

    settings_prod = ConfigLoader.from_yaml_with_env(ProductionAppSettings)
    console.print("\nProduction settings (from .env + .env.prod):")
    pprint(settings_prod)

    # Instantiate production components
    console.print("\n[yellow]3.2 Production components:[/yellow]")

    primary_db = instantiate(settings_prod.primary_db)
    secondary_db = instantiate(settings_prod.secondary_db)
    cache = instantiate(settings_prod.cache)
    model_v1 = instantiate(settings_prod.model_v1)
    model_v2 = instantiate(settings_prod.model_v2)

    console.print("\nDatabases:")
    console.print(f"  Primary: {primary_db}")
    console.print(f"  Secondary: {secondary_db}")
    console.print(f"\nCache: {cache}")
    console.print("\nModels:")
    console.print(f"  v1: {model_v1}")
    console.print(f"  v2: {model_v2}")

    # ==========================================================================
    # PART 4: Advanced Features
    # ==========================================================================

    console.print("\n" + "=" * 80)
    console.print("[bold cyan]PART 4: Advanced Features[/bold cyan]")
    console.print("=" * 80)

    # 4.1 Dependency Injection
    console.print("\n[yellow]4.1 Dependency Injection:[/yellow]")

    # Register shared components
    shared_cache = RedisCache(host="shared-redis", ttl=7200)
    shared_db = PostgreSQL(host="shared-db", database="shared")

    register_dependency("shared_cache", shared_cache)
    register_dependency("shared_database", shared_db)
    register_dependency("cache", shared_cache)  # Default cache
    register_dependency("database", shared_db)  # Default database

    console.print("\nRegistered dependencies:")
    console.print(f"  shared_cache: {shared_cache}")
    console.print(f"  shared_database: {shared_db}")

    # Create pipeline config without database (will be injected)
    pipeline_config = {
        "_target_": "__main__.Pipeline",
        "name": "injected_pipeline",
        "model": {"_target_": "__main__.NeuralNetwork", "input_dim": 128, "hidden_dim": 64, "output_dim": 10},
        "processor": {"_target_": "__main__.DataProcessor", "features": ["f1", "f2", "f3"]},
        # Note: database and cache are missing - will be injected!
    }

    pipeline = instantiate(pipeline_config)
    console.print(f"\nInjected pipeline: {pipeline}")
    console.print(f"  Database was injected: {pipeline.database}")
    console.print(f"  Cache was injected: {pipeline.cache}")
    console.print(f"  Result: {pipeline.run()}")

    # 4.2 Runtime overrides
    console.print("\n[yellow]4.2 Runtime parameter overrides:[/yellow]")

    # Create variant with overrides
    model_variant = instantiate(settings_prod.model_v1, name="variant_model", learning_rate=0.0001, hidden_dim=256)
    console.print(f"\nModel variant: {model_variant}")

    # ==========================================================================
    # Summary
    # ==========================================================================

    console.print(
        Panel.fit(
            "✅ Full ConfigLoader Showcase Complete!\n\n"
            "We demonstrated:\n"
            "• All ConfigLoader modes with real components\n"
            "• DynamicConfig for type-safe instantiation\n"
            "• Real classes: Database, Cache, ML Models, Pipelines\n"
            "• Dependency injection with register_dependency\n"
            "• Complex nested configurations\n"
            "• Multi-env file loading\n"
            "• YAML overrides with deep merging\n"
            "• Runtime parameter overrides\n"
            "• Complete application execution\n\n"
            "This showcases the FULL POWER of ConfigLoader for\n"
            "building production-ready, configurable applications!",
            title="🎯 Full Showcase Summary",
            style="bold green",
        )
    )


if __name__ == "__main__":
    showcase_full_configloader()
