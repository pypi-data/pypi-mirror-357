"""Comprehensive demo of frostbound.pydanticonf functionality."""

import os
import sys
from pathlib import Path

# Add parent directories to path so we can import frostbound
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import services
from config_models import AppSettings, DatabaseConfig, LazyAppSettings, MultiEnvSettings

from frostbound.pydanticonf import clear_dependencies, instantiate, register_dependency


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print("=" * 60)


def demo_auto_instantiation():
    """Demo 1: Auto-instantiation mode (default behavior)."""
    print_section("Demo 1: Auto-instantiation Mode")

    # Change to the demo directory to load config files
    os.chdir(Path(__file__).parent)

    # Load settings - objects are automatically instantiated
    settings = AppSettings()

    print("\nMetadata (not instantiated):")
    print(f"  App: {settings.metadata.app_name} v{settings.metadata.version}")
    print(f"  Environment: {settings.metadata.environment}")
    print(f"  Debug: {settings.metadata.debug}")

    print("\nDatabase (auto-instantiated):")
    print(f"  Type: {type(settings.database).__name__}")
    print(f"  Instance: {settings.database}")

    print("\nCache (auto-instantiated):")
    print(f"  Type: {type(settings.cache).__name__}")
    print(f"  Instance: {settings.cache}")

    print("\nEmail (auto-instantiated):")
    print(f"  Type: {type(settings.email).__name__}")
    print(f"  Instance: {settings.email}")

    print("\nAPI Client (with positional args):")
    print(f"  Type: {type(settings.api_client).__name__}")
    print(f"  Instance: {settings.api_client}")

    if settings.backup_database:
        print("\nBackup Database:")
        print(f"  Type: {type(settings.backup_database).__name__}")
        print(f"  Instance: {settings.backup_database}")

    if settings.main_service:
        print("\nMain Service (with nested dependencies):")
        print(f"  Type: {type(settings.main_service).__name__}")
        print(f"  Instance: {settings.main_service}")


def demo_lazy_instantiation():
    """Demo 2: Lazy instantiation mode."""
    print_section("Demo 2: Lazy Instantiation Mode")

    # Load settings - objects are NOT automatically instantiated
    settings = LazyAppSettings()

    print("\nDatabase config (not instantiated yet):")
    print(f"  Type: {type(settings.database).__name__}")
    print(f"  Host: {settings.database.host}")
    print(f"  Port: {settings.database.port}")
    print(f"  Password: {'***' if settings.database.password else 'None'}")

    # Modify configuration before instantiation
    print("\nModifying cache TTL before instantiation...")
    settings.cache.ttl = 9999

    # Instantiate specific field
    print("\nInstantiating database...")
    db = settings.instantiate_field("database")
    print(f"  Type: {type(db).__name__}")
    print(f"  Instance: {db}")

    # Instantiate with runtime overrides
    print("\nInstantiating cache with overrides...")
    cache = settings.instantiate_field("cache", max_connections=500)
    print(f"  Type: {type(cache).__name__}")
    print(f"  Instance: {cache}")
    print("  Note: max_connections overridden to 500")

    # Instantiate all at once
    print("\nInstantiating all configured objects...")
    instances = settings.instantiate_all()
    print(f"  Available: {list(vars(instances).keys())}")


def demo_dependency_injection():
    """Demo 3: Dependency injection with register_dependency."""
    print_section("Demo 3: Dependency Injection")

    # Clear any existing dependencies
    clear_dependencies()

    # Register shared dependencies by type
    shared_logger = services.Logger("shared", level="DEBUG")
    register_dependency(services.Logger, shared_logger)

    # Also register by name for explicit access
    register_dependency("shared_logger", shared_logger)

    # Create a service config without logger - dependency injection will provide it
    service_config = {
        "_target_": "services.Service",
        "name": "InjectedService",
        "database": {"_target_": "services.Database", "host": "injected-db.com", "port": 5432},
        "cache": {"_target_": "services.RedisCache", "host": "injected-redis.com"},
        # No logger specified - will be injected by type
    }

    # Instantiate with dependency injection
    service = instantiate(service_config)
    print("\nService created with type-based dependency injection:")
    print(f"  Service: {service}")
    print(f"  Logger: {service.logger}")
    print(f"  Logger is shared: {service.logger is shared_logger}")

    # Also demonstrate name-based injection
    service_config2 = {
        "_target_": "services.Service",
        "name": "NameBasedService",
        "database": {"_target_": "services.Database", "host": "name-based-db.com"},
        "cache": {"_target_": "services.RedisCache", "host": "name-based-redis.com"},
        "logger": {"_target_": "services.Logger", "name": "custom", "level": "INFO"},
    }

    service2 = instantiate(service_config2)
    print("\nService with explicit logger config:")
    print(f"  Service: {service2}")
    print(f"  Logger: {service2.logger}")
    print(f"  Logger is custom: {service2.logger is not shared_logger}")


def demo_standalone_instantiation():
    """Demo 4: Using instantiate() function directly."""
    print_section("Demo 4: Standalone Instantiation")

    # Create a config object
    db_config = DatabaseConfig(host="standalone-db.com", port=5433, username="standalone_user", password="secret123")

    print("\nConfig object:")
    print(f"  Type: {type(db_config).__name__}")
    print(f"  Target: {db_config.target_}")

    # Instantiate it
    db = instantiate(db_config)
    print("\nInstantiated object:")
    print(f"  Type: {type(db).__name__}")
    print(f"  Instance: {db}")

    # Direct dict instantiation
    cache_dict = {"_target_": "services.RedisCache", "host": "dict-redis.com", "ttl": 1800}

    cache = instantiate(cache_dict)
    print("\nFrom dict:")
    print(f"  Type: {type(cache).__name__}")
    print(f"  Instance: {cache}")


def demo_multi_environment():
    """Demo 5: Multi-environment configuration."""
    print_section("Demo 5: Multi-Environment Configuration")

    # Test development environment
    print("\nDevelopment Environment:")
    os.environ["ENV"] = "dev"
    dev_settings = MultiEnvSettings()

    print(f"  Environment: {dev_settings.metadata.environment}")
    print(f"  Debug: {dev_settings.metadata.debug}")
    print(f"  Database: {dev_settings.database}")
    print(f"  Cache: {dev_settings.cache}")

    # Test production environment
    print("\nProduction Environment:")
    os.environ["ENV"] = "prod"
    prod_settings = MultiEnvSettings()

    print(f"  Environment: {prod_settings.metadata.environment}")
    print(f"  Debug: {prod_settings.metadata.debug}")
    print(f"  Database: {prod_settings.database}")
    print(f"  Cache: {prod_settings.cache}")


def demo_partial_instantiation():
    """Demo 6: Partial instantiation for factory patterns."""
    print_section("Demo 6: Partial Instantiation")

    from functools import partial

    # Create a logger factory config
    logger_factory_config = {"_target_": "services.Logger", "_partial_": True, "level": "INFO", "format": "json"}

    # Instantiate to get a partial function
    logger_factory = instantiate(logger_factory_config)
    print("\nLogger factory:")
    print(f"  Type: {type(logger_factory).__name__}")
    print(f"  Is partial: {isinstance(logger_factory, partial)}")

    # Use the factory to create loggers
    app_logger = logger_factory(name="app")
    db_logger = logger_factory(name="database")

    print("\nCreated loggers:")
    print(f"  App Logger: {app_logger}")
    print(f"  DB Logger: {db_logger}")


def main():
    """Run all demos."""
    print("=" * 60)
    print("Frostbound PydantiConf - Comprehensive Demo")
    print("=" * 60)

    try:
        demo_auto_instantiation()
        demo_lazy_instantiation()
        demo_dependency_injection()
        demo_standalone_instantiation()
        demo_multi_environment()
        demo_partial_instantiation()

        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
