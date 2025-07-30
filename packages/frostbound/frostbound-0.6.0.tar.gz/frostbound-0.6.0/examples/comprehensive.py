import json
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint

from frostbound.pydanticonf.loader import ConfigLoader
from frostbound.pydanticonf.sources import (
    CompositeConfigSource,
    EnvironmentConfigSource,
    YamlConfigSource,
)

console = Console()


def print_section(title: str, content: Any = None) -> None:
    """Helper to print formatted sections."""
    console.print(Panel(title, style="bold blue"))
    if content is not None:
        pprint(content)
    console.print()


def test_yaml_config_source():
    """Test YamlConfigSource with various YAML structures."""
    print_section("🔧 Testing YamlConfigSource")

    # Create a temporary YAML file with complex nested structure
    yaml_content = {
        "app_name": "Test Application",
        "version": "1.0.0",
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {"username": "admin", "password": "secret123"},
            "pools": [{"name": "read_pool", "size": 10}, {"name": "write_pool", "size": 5}],
        },
        "features": {"logging": True, "metrics": False, "debug_mode": True},
        "api_keys": ["key1", "key2", "key3"],
        "timeout": 30.5,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(yaml_content, f)
        yaml_path = Path(f.name)

    try:
        # Test loading
        yaml_source = YamlConfigSource(yaml_path)
        loaded_data = yaml_source.load()

        console.print("📄 Original YAML content:")
        pprint(yaml_content)

        console.print("📥 Loaded data from YamlConfigSource:")
        pprint(loaded_data)

        # Verify the data matches
        assert loaded_data == yaml_content, "Loaded data should match original YAML content"
        console.print("✅ YamlConfigSource test passed!")

    finally:
        # Clean up
        yaml_path.unlink()

    # Test file not found
    console.print("🚫 Testing file not found scenario:")
    try:
        non_existent_source = YamlConfigSource(Path("non_existent_file.yaml"))
        non_existent_source.load()
        raise AssertionError("Should have raised FileNotFoundError")
    except FileNotFoundError as e:
        console.print(f"✅ Correctly raised FileNotFoundError: {e}")


def test_environment_config_source():
    """Test EnvironmentConfigSource with various environment variable patterns."""
    print_section("🌍 Testing EnvironmentConfigSource")

    # Save original environment
    original_env = dict(os.environ)

    try:
        # Clear test-related environment variables
        for key in list(os.environ.keys()):
            if key.startswith(("TEST_", "MYAPP_")):
                del os.environ[key]

        # Test 1: Basic environment variables with prefix
        console.print("🔹 Test 1: Basic environment variables with prefix")
        os.environ.update(
            {
                "TEST_APP_NAME": "Environment Test App",
                "TEST_VERSION": "2.0.0",
                "TEST_DEBUG": "true",
                "TEST_PORT": "8080",
                "TEST_TIMEOUT": "45.5",
                "OTHER_VAR": "should_be_ignored",  # No TEST_ prefix
            }
        )

        env_source = EnvironmentConfigSource(prefix="TEST")
        loaded_data = env_source.load()

        console.print("Environment variables set:")
        for key, value in os.environ.items():
            if key.startswith("TEST_") or key == "OTHER_VAR":
                console.print(f"  {key}={value}")

        console.print("📥 Loaded data from EnvironmentConfigSource:")
        pprint(loaded_data)

        expected = {
            "app_name": "Environment Test App",
            "version": "2.0.0",
            "debug": True,  # JSON parsed
            "port": 8080,  # JSON parsed
            "timeout": 45.5,  # JSON parsed
        }
        assert loaded_data == expected, f"Expected {expected}, got {loaded_data}"
        console.print("✅ Basic prefix test passed!")

        # Test 2: Nested structures with delimiters
        console.print("\n🔹 Test 2: Nested structures with delimiters")
        os.environ.update(
            {
                "MYAPP_DATABASE__HOST": "db.example.com",
                "MYAPP_DATABASE__PORT": "5432",
                "MYAPP_DATABASE__CREDENTIALS__USERNAME": "dbuser",
                "MYAPP_DATABASE__CREDENTIALS__PASSWORD": "dbpass123",
                "MYAPP_CACHE__REDIS__HOST": "redis.example.com",
                "MYAPP_CACHE__REDIS__PORT": "6379",
                "MYAPP_FEATURES__LOGGING": "true",
                "MYAPP_FEATURES__METRICS": "false",
            }
        )

        nested_source = EnvironmentConfigSource(prefix="MYAPP", delimiter="__")
        nested_data = nested_source.load()

        console.print("📥 Loaded nested data:")
        pprint(nested_data)

        expected_nested = {
            "database": {
                "host": "db.example.com",
                "port": 5432,
                "credentials": {"username": "dbuser", "password": "dbpass123"},
            },
            "cache": {"redis": {"host": "redis.example.com", "port": 6379}},
            "features": {"logging": True, "metrics": False},
        }
        assert nested_data == expected_nested, f"Expected {expected_nested}, got {nested_data}"
        console.print("✅ Nested structure test passed!")

        # Test 3: Array-like structures with numeric keys
        console.print("\n🔹 Test 3: Array-like structures with numeric keys")
        os.environ.update(
            {
                "ARRAY_TEST_SERVERS__0__HOST": "server1.com",
                "ARRAY_TEST_SERVERS__0__PORT": "8001",
                "ARRAY_TEST_SERVERS__1__HOST": "server2.com",
                "ARRAY_TEST_SERVERS__1__PORT": "8002",
                "ARRAY_TEST_SERVERS__2__HOST": "server3.com",
                "ARRAY_TEST_SERVERS__2__PORT": "8003",
            }
        )

        array_source = EnvironmentConfigSource(prefix="ARRAY_TEST")
        array_data = array_source.load()

        console.print("📥 Loaded array-like data:")
        pprint(array_data)

        expected_array = {
            "servers": {
                0: {"host": "server1.com", "port": 8001},
                1: {"host": "server2.com", "port": 8002},
                2: {"host": "server3.com", "port": 8003},
            }
        }
        assert array_data == expected_array, f"Expected {expected_array}, got {array_data}"
        console.print("✅ Array-like structure test passed!")

        # Test 4: Complex JSON values
        console.print("\n🔹 Test 4: Complex JSON values")
        complex_list = ["item1", "item2", "item3"]
        complex_dict = {"nested": {"key": "value"}, "number": 42}

        os.environ.update(
            {
                "JSON_TEST_LIST": json.dumps(complex_list),
                "JSON_TEST_DICT": json.dumps(complex_dict),
                "JSON_TEST_STRING": "plain_string",
                "JSON_TEST_INVALID_JSON": "not{valid}json",
            }
        )

        json_source = EnvironmentConfigSource(prefix="JSON_TEST")
        json_data = json_source.load()

        console.print("📥 Loaded JSON data:")
        pprint(json_data)

        expected_json = {
            "list": complex_list,
            "dict": complex_dict,
            "string": "plain_string",
            "invalid_json": "not{valid}json",  # Falls back to string
        }
        assert json_data == expected_json, f"Expected {expected_json}, got {json_data}"
        console.print("✅ Complex JSON values test passed!")

        # Test 5: No prefix (empty string)
        console.print("\n🔹 Test 5: No prefix (all environment variables)")
        no_prefix_source = EnvironmentConfigSource(prefix="")
        no_prefix_data = no_prefix_source.load()

        console.print("📥 Sample of data with no prefix (showing first 5 keys):")
        sample_keys = list(no_prefix_data.keys())[:5]
        sample_data = {k: no_prefix_data[k] for k in sample_keys}
        pprint(sample_data)
        console.print(f"Total environment variables loaded: {len(no_prefix_data)}")
        console.print("✅ No prefix test passed!")

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def test_composite_config_source():
    """Test CompositeConfigSource with multiple sources and deep merging."""
    print_section("🔄 Testing CompositeConfigSource")

    # Create multiple temporary YAML files
    base_config = {
        "app_name": "Base App",
        "version": "1.0.0",
        "database": {"host": "localhost", "port": 5432, "pool_size": 10},
        "features": {"logging": True, "metrics": False, "debug": False},
    }

    override_config = {
        "app_name": "Override App",  # This will override
        "database": {
            "host": "production.db.com",  # This will override
            "ssl": True,  # This will be added
        },
        "features": {
            "metrics": True,  # This will override
            "caching": True,  # This will be added
        },
        "new_section": {"key": "value"},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
        yaml.dump(base_config, f1)
        base_path = Path(f1.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
        yaml.dump(override_config, f2)
        override_path = Path(f2.name)

    try:
        # Set up environment variables
        original_env = dict(os.environ)
        os.environ.update(
            {
                "COMP_TEST_VERSION": "2.0.0",  # Override version
                "COMP_TEST_DATABASE__PORT": "3306",  # Override database port
                "COMP_TEST_DATABASE__PASSWORD": "env_secret",  # Add password
                "COMP_TEST_FEATURES__DEBUG": "true",  # Override debug
            }
        )

        # Create sources
        base_source = YamlConfigSource(base_path)
        override_source = YamlConfigSource(override_path)
        env_source = EnvironmentConfigSource(prefix="COMP_TEST")

        console.print("🔹 Base configuration:")
        pprint(base_source.load())

        console.print("\n🔹 Override configuration:")
        pprint(override_source.load())

        console.print("\n🔹 Environment configuration:")
        pprint(env_source.load())

        # Test composite source (order matters: base -> override -> env)
        composite_source = CompositeConfigSource(base_source, override_source, env_source)
        final_config = composite_source.load()

        console.print("\n📥 Final merged configuration:")
        pprint(final_config)

        # Verify the merge behavior
        expected_final = {
            "app_name": "Override App",  # From override_config
            "version": "2.0.0",  # From environment (last wins)
            "database": {
                "host": "production.db.com",  # From override_config
                "port": 3306,  # From environment (last wins)
                "pool_size": 10,  # From base_config (preserved)
                "ssl": True,  # From override_config (added)
                "password": "env_secret",  # From environment (added)
            },
            "features": {
                "logging": True,  # From base_config (preserved)
                "metrics": True,  # From override_config (overridden)
                "debug": True,  # From environment (last wins)
                "caching": True,  # From override_config (added)
            },
            "new_section": {
                "key": "value"  # From override_config (added)
            },
        }

        assert final_config == expected_final, f"Expected {expected_final}, got {final_config}"
        console.print("✅ CompositeConfigSource deep merge test passed!")

        # Test with ConfigLoader
        console.print("\n🔹 Testing with ConfigLoader.from_sources:")

        class DatabaseConfig(BaseModel):
            host: str
            port: int
            pool_size: int = 10
            ssl: bool = False
            password: str = "default"

        class FeaturesConfig(BaseModel):
            logging: bool = True
            metrics: bool = False
            debug: bool = False
            caching: bool = False

        class AppSettings(BaseSettings):
            app_name: str
            version: str
            database: DatabaseConfig
            features: FeaturesConfig

            model_config = SettingsConfigDict(case_sensitive=False, extra="allow")

        settings = ConfigLoader.from_sources(AppSettings, base_source, override_source, env_source)
        console.print("📥 Parsed settings object:")
        pprint(settings)

        # Verify settings
        assert settings.app_name == "Override App"
        assert settings.version == "2.0.0"
        assert settings.database.host == "production.db.com"
        assert settings.database.port == 3306
        assert settings.database.password == "env_secret"
        assert settings.features.debug is True
        assert settings.features.metrics is True

        console.print("✅ ConfigLoader integration test passed!")

    finally:
        # Clean up
        base_path.unlink()
        override_path.unlink()
        os.environ.clear()
        os.environ.update(original_env)


def test_edge_cases_and_error_handling():
    """Test edge cases and error handling."""
    print_section("⚠️  Testing Edge Cases and Error Handling")

    # Test 1: Empty YAML file
    console.print("🔹 Test 1: Empty YAML file")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("")  # Empty file
        empty_yaml_path = Path(f.name)

    try:
        empty_source = YamlConfigSource(empty_yaml_path)
        empty_data = empty_source.load()
        console.print(f"📥 Empty YAML loaded as: {empty_data}")
        assert empty_data == {}, "Empty YAML should load as empty dict"
        console.print("✅ Empty YAML test passed!")
    finally:
        empty_yaml_path.unlink()

    # Test 2: Environment source with no matching variables
    console.print("\n🔹 Test 2: Environment source with no matching variables")
    no_match_source = EnvironmentConfigSource(prefix="NONEXISTENT_PREFIX")
    no_match_data = no_match_source.load()
    console.print(f"📥 No matching env vars loaded as: {no_match_data}")
    assert no_match_data == {}, "No matching env vars should load as empty dict"
    console.print("✅ No matching env vars test passed!")

    # Test 3: Composite source with empty sources
    console.print("\n🔹 Test 3: Composite source with empty sources")
    empty_composite = CompositeConfigSource()
    empty_composite_data = empty_composite.load()
    console.print(f"📥 Empty composite loaded as: {empty_composite_data}")
    assert empty_composite_data == {}, "Empty composite should load as empty dict"
    console.print("✅ Empty composite test passed!")

    # Test 4: Prefix normalization
    console.print("\n🔹 Test 4: Prefix normalization")
    original_env = dict(os.environ)
    try:
        os.environ["NORM_TEST_KEY"] = "value"

        # Test different prefix formats
        source1 = EnvironmentConfigSource(prefix="NORM_TEST")  # No underscore
        source2 = EnvironmentConfigSource(prefix="NORM_TEST_")  # With underscore
        EnvironmentConfigSource(prefix=None)  # None prefix
        EnvironmentConfigSource(prefix="")  # Empty prefix

        data1 = source1.load()
        data2 = source2.load()

        console.print(f"📥 Prefix 'NORM_TEST': {data1}")
        console.print(f"📥 Prefix 'NORM_TEST_': {data2}")

        assert data1 == data2 == {"key": "value"}, "Prefix normalization should work"
        console.print("✅ Prefix normalization test passed!")

    finally:
        os.environ.clear()
        os.environ.update(original_env)


def demonstrate_real_world_scenario():
    """Demonstrate a real-world configuration scenario."""
    print_section("🌟 Real-World Scenario Demonstration")

    console.print("This demonstrates a typical application configuration setup:")
    console.print("1. Base config from YAML (defaults)")
    console.print("2. Environment-specific overrides from YAML")
    console.print("3. Runtime overrides from environment variables")
    console.print("4. Secrets from environment variables")

    # Create base configuration
    base_config = {
        "app": {"name": "MyMicroservice", "version": "1.0.0", "environment": "development"},
        "server": {"host": "0.0.0.0", "port": 8000, "workers": 1},
        "database": {"host": "localhost", "port": 5432, "name": "myapp_dev", "pool_size": 5, "ssl_mode": "disable"},
        "redis": {"host": "localhost", "port": 6379, "db": 0},
        "logging": {"level": "DEBUG", "format": "detailed"},
        "features": {"rate_limiting": False, "caching": True, "metrics": False},
    }

    # Create production overrides
    prod_config = {
        "app": {"environment": "production"},
        "server": {"workers": 4},
        "database": {"host": "prod-db.company.com", "name": "myapp_prod", "pool_size": 20, "ssl_mode": "require"},
        "redis": {"host": "prod-redis.company.com"},
        "logging": {"level": "INFO", "format": "json"},
        "features": {"rate_limiting": True, "metrics": True},
    }

    # Create temporary files
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
        yaml.dump(base_config, f1)
        base_path = Path(f1.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
        yaml.dump(prod_config, f2)
        prod_path = Path(f2.name)

    try:
        # Set environment variables (secrets and runtime overrides)
        original_env = dict(os.environ)
        os.environ.update(
            {
                # Secrets
                "MYAPP_DATABASE__PASSWORD": "super_secret_db_password",
                "MYAPP_REDIS__PASSWORD": "redis_secret_password",
                "MYAPP_APP__API_KEY": "api_key_12345",
                # Runtime overrides
                "MYAPP_SERVER__PORT": "9000",
                "MYAPP_LOGGING__LEVEL": "WARNING",
                "MYAPP_FEATURES__DEBUG_MODE": "true",
            }
        )

        # Create sources
        base_source = YamlConfigSource(base_path)
        prod_source = YamlConfigSource(prod_path)
        env_source = EnvironmentConfigSource(prefix="MYAPP")

        console.print("🔹 Base configuration (defaults):")
        pprint(base_source.load())

        console.print("\n🔹 Production overrides:")
        pprint(prod_source.load())

        console.print("\n🔹 Environment variables (secrets + runtime):")
        pprint(env_source.load())

        # Combine all sources
        composite = CompositeConfigSource(base_source, prod_source, env_source)
        final_config = composite.load()

        console.print("\n🎯 Final application configuration:")
        pprint(final_config)

        # Define Pydantic models for validation
        class AppConfig(BaseModel):
            name: str
            version: str
            environment: str
            api_key: str

        class ServerConfig(BaseModel):
            host: str
            port: int
            workers: int

        class DatabaseConfig(BaseModel):
            host: str
            port: int
            name: str
            password: str
            pool_size: int
            ssl_mode: str

        class RedisConfig(BaseModel):
            host: str
            port: int
            db: int
            password: str

        class LoggingConfig(BaseModel):
            level: str
            format: str

        class FeaturesConfig(BaseModel):
            rate_limiting: bool
            caching: bool
            metrics: bool
            debug_mode: bool

        class ApplicationSettings(BaseSettings):
            app: AppConfig
            server: ServerConfig
            database: DatabaseConfig
            redis: RedisConfig
            logging: LoggingConfig
            features: FeaturesConfig

            model_config = SettingsConfigDict(case_sensitive=False)

        # Load and validate
        settings = ConfigLoader.from_sources(ApplicationSettings, base_source, prod_source, env_source)

        console.print("\n✅ Validated application settings:")
        console.print(f"App: {settings.app.name} v{settings.app.version} ({settings.app.environment})")
        console.print(f"Server: {settings.server.host}:{settings.server.port} ({settings.server.workers} workers)")
        console.print(f"Database: {settings.database.host}:{settings.database.port}/{settings.database.name}")
        console.print(f"Redis: {settings.redis.host}:{settings.redis.port}")
        console.print(f"Logging: {settings.logging.level} ({settings.logging.format})")
        console.print(f"Features: rate_limiting={settings.features.rate_limiting}, caching={settings.features.caching}")

        # Verify key behaviors
        assert settings.app.environment == "production"  # From prod override
        assert settings.server.port == 9000  # From environment override
        assert settings.database.password == "super_secret_db_password"  # From environment
        assert settings.features.debug_mode is True  # From environment
        assert settings.database.ssl_mode == "require"  # From prod override
        assert settings.server.workers == 4  # From prod override

        console.print("✅ Real-world scenario test passed!")

    finally:
        # Clean up
        base_path.unlink()
        prod_path.unlink()
        os.environ.clear()
        os.environ.update(original_env)


def main():
    """Run all tests and demonstrations."""
    console.print(
        Panel.fit(
            "🧪 Comprehensive Test Suite for frostbound.pydanticonf.sources\n\n"
            "This test suite demonstrates and validates all functionality of:\n"
            "• YamlConfigSource\n"
            "• EnvironmentConfigSource\n"
            "• CompositeConfigSource\n\n"
            "Each test includes detailed explanations and examples.",
            title="Frostbound Pydanticonf Sources Test Suite",
            style="bold green",
        )
    )

    try:
        test_yaml_config_source()
        test_environment_config_source()
        test_composite_config_source()
        test_edge_cases_and_error_handling()
        demonstrate_real_world_scenario()

        console.print(
            Panel.fit(
                "🎉 All tests passed successfully!\n\n"
                "You now understand how the sources.py module works:\n"
                "• YamlConfigSource loads structured data from YAML files\n"
                "• EnvironmentConfigSource loads from env vars with smart parsing\n"
                "• CompositeConfigSource merges multiple sources with deep merging\n"
                "• ConfigLoader provides convenient factory methods\n\n"
                "The sources are designed to work together to provide flexible,\n"
                "layered configuration management for applications.",
                title="✅ Test Suite Complete",
                style="bold green",
            )
        )

    except Exception as e:
        console.print(Panel.fit(f"❌ Test failed with error:\n{e}", title="Test Failure", style="bold red"))
        raise


if __name__ == "__main__":
    main()
