"""Production configuration demo showing BaseSettingsWithInstantiation.

This demonstrates:
- Loading configuration from multiple sources
- Environment-specific settings
- Secure handling of secrets
- Automatic object instantiation
- Type safety throughout

Usage:
    # Development mode (default)
    python main.py

    # Production mode
    ENVIRONMENT=prod python main.py

    # With custom env file
    ENVIRONMENT=staging python main.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich.pretty import pprint

from examples.production_config_demo.settings import AppSettings


def demonstrate_configuration():
    """Demonstrate the configuration system."""

    # Load settings - everything is automatically configured and instantiated!
    print(f"Loading configuration for environment: {os.getenv('ENVIRONMENT', 'dev')}")

    try:
        settings = AppSettings()  # type: ignore
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return

    pprint(settings)
    pprint(settings.model_config)

    print("\n🔧 Demonstrating instantiated services:\n")

    # 1. Database is already instantiated and ready to use
    print("1. Database Operations:")
    settings.database.connect()
    results = settings.database.query("SELECT * FROM users LIMIT 1")
    print(f"   Query returned: {results}\n")

    # 2. Redis cache is ready
    print("2. Redis Cache Operations:")
    settings.redis.set("demo_key", "demo_value", ttl=300)
    value = settings.redis.get("demo_key")
    print(f"   Retrieved: {value}\n")

    # 3. S3 storage is configured
    print("3. S3 Storage Operations:")
    url = settings.storage.upload("demo/test.txt", b"Hello, World!")
    print(f"   Uploaded to: {url}\n")

    # 4. External API client is ready
    print("4. External API Operations:")
    response = settings.external_api.request("/users/123")
    print(f"   API response: {response}\n")

    # 5. Logger is configured
    print("5. Logging Operations:")
    settings.logger.info("Application started successfully")
    settings.logger.error("Demo error for testing")
    # 6. Monitoring is set up
    print("\n6. Monitoring Setup:")
    settings.monitoring.initialize()
    try:
        raise ValueError("Demo exception")
    except Exception as e:
        settings.monitoring.capture_exception(e)

    print("\n✨ All services are instantiated and ready to use!")
    print("   No manual setup required - just use them!")


def show_configuration_layers():
    """Show how configuration layers work."""
    print("\n📚 Configuration Layers Demo")
    print("=" * 60)

    # Create settings to inspect
    settings = AppSettings()

    print("\nConfiguration sources (in precedence order):")
    print("1. Environment variables (APP_*)")
    print("2. .env file (.env.dev or .env.prod)")
    print("3. Environment YAML (dev.yaml or prod.yaml)")
    print("4. Base YAML (base.yaml)")
    print("5. Python defaults in settings class")

    print(f"\nCurrent environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")

    # Show example of precedence
    print("\nExample precedence:")
    print(f"- Database host: {settings.database.host}")
    print(f"  (from {settings.environment}.yaml)")
    print(f"- Database password: {settings.database.password}")
    print(f"  (from .env.{settings.environment})")

    # Show how to override
    print("\nTo override any value, use environment variables:")
    print("  export APP_DATABASE__HOST=custom-host.com")
    print("  export APP_REDIS__PORT=6380")


if __name__ == "__main__":
    print("🎯 Production Configuration Demo")
    print("================================\n")

    # Show basic configuration
    demonstrate_configuration()

    # Show configuration layers
    show_configuration_layers()

    print("\n💡 Tips:")
    print("- Run with ENVIRONMENT=prod to see production config")
    print("- Check .env.example for required environment variables")
    print("- Sensitive values are automatically masked in output")
    print("- All objects are instantiated and ready to use!")
