"""Production configuration demo with lazy instantiation.

This demonstrates:
- Loading configuration without instantiation
- Inspecting and modifying configurations
- Selective instantiation with overrides
- Factory pattern with configurations
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from examples.production_config_demo.settings_lazy import AppSettingsLazy
from frostbound.pydanticonf import instantiate


def demonstrate_lazy_configuration():
    """Demonstrate lazy configuration loading and instantiation."""

    print("🚀 Lazy Configuration Demo")
    print("=" * 60)

    # 1. Load settings WITHOUT instantiation
    print("\n1️⃣ Loading configuration (configs as data):")
    settings = AppSettingsLazy()

    # Show that we have config objects, not instantiated services
    print(f"\nApp: {settings.app_name} v{settings.version}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")

    print("\n📋 Service configurations (not instantiated):")
    print(f"  Database config type: {type(settings.database).__name__}")
    print(f"  Redis config type: {type(settings.redis).__name__}")
    print(f"  Storage config type: {type(settings.storage).__name__}")

    # 2. Inspect configurations before instantiation
    print("\n2️⃣ Inspecting configurations:")
    print("\nDatabase configuration:")
    print(f"  Host: {settings.database.host}")
    print(f"  Port: {settings.database.port}")
    print(f"  Database: {settings.database.database}")
    print(f"  Pool size: {settings.database.pool_size}")
    print(f"  Password: {'***' if settings.database.password else 'None'}")

    print("\nStorage configuration:")
    print(f"  Bucket: {settings.storage.bucket}")
    print(f"  Region: {settings.storage.region}")
    print(f"  Use SSL: {settings.storage.use_ssl}")
    print(f"  Access key: {'***' if settings.storage.access_key_id else 'None'}")

    # 3. Modify configuration before instantiation
    print("\n3️⃣ Modifying configurations before instantiation:")
    if settings.environment == "dev":
        print("  Adjusting pool size for development...")
        settings.database.pool_size = 2  # Smaller pool for dev
        print(f"  New pool size: {settings.database.pool_size}")

    # 4. Selective instantiation with overrides
    print("\n4️⃣ Selective instantiation with runtime overrides:")

    # Instantiate database with override
    print("\n  Creating database with custom timeout...")
    db = settings.instantiate_field("database", timeout=60)
    db.connect()

    # Instantiate storage as-is
    print("\n  Creating storage service...")
    storage = settings.instantiate_field("storage")
    url = storage.upload("demo/lazy.txt", b"Lazy instantiation demo")
    print(f"  Uploaded to: {url}")

    # 5. Factory pattern with configs
    print("\n5️⃣ Factory pattern with configurations:")

    def create_service(service_name: str, **overrides):
        """Factory function to create services with overrides."""
        config = getattr(settings, service_name)
        print(f"\n  Creating {service_name} with overrides: {overrides}")
        return instantiate(config, **overrides)

    # Create services with different configurations
    redis_primary = create_service("redis", db=0)
    redis_cache = create_service("redis", db=1, port=6380)

    redis_primary.set("key1", "value1")
    redis_cache.set("key2", "value2")

    # 6. Conditional instantiation
    print("\n6️⃣ Conditional instantiation:")
    if settings.monitoring.dsn:
        print("  Monitoring DSN found, creating monitoring service...")
        monitoring = settings.instantiate_field("monitoring")
        monitoring.initialize()
    else:
        print("  No monitoring DSN, skipping monitoring service")

    # 7. Bulk instantiation
    print("\n7️⃣ Alternative: Instantiate all services at once:")
    print("  Call settings.instantiate_all() to instantiate everything")
    print("  This would replace all config objects with instantiated services")

    print("\n✅ Lazy instantiation demo complete!")
    print("   Benefits demonstrated:")
    print("   - Configs inspected and modified before instantiation")
    print("   - Services created only when needed")
    print("   - Runtime overrides applied during instantiation")
    print("   - Conditional instantiation based on config values")


if __name__ == "__main__":
    demonstrate_lazy_configuration()
