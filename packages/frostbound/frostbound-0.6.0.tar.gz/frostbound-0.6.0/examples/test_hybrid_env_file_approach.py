"""
Test and Demonstration: Hybrid env_file Approach in ConfigLoader

This script demonstrates and tests the new hybrid approach that intelligently
handles Pydantic's env_file configuration while providing frostbound's enhanced
source composition capabilities.

Run this script to verify the hybrid approach works correctly.
"""

import sys
import tempfile
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel

from frostbound.pydanticonf import ConfigLoader

console = Console()


def test_detection_logic():
    """Test 1: Verify env_file detection works correctly."""
    console.print("🔍 [bold]Test 1: Detection Logic[/bold]")

    # Settings WITH env_file configured
    class SettingsWithEnvFile(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env")
        name: str = "default"

    # Settings WITHOUT env_file
    class SettingsWithoutEnvFile(BaseSettings):
        name: str = "default"

    # Settings with env_file=None (explicitly disabled)
    class SettingsWithNullEnvFile(BaseSettings):
        model_config = SettingsConfigDict(env_file=None)
        name: str = "default"

    # Settings with multiple env files
    class SettingsWithMultipleEnvFiles(BaseSettings):
        model_config = SettingsConfigDict(env_file=(".env", ".env.local"))
        name: str = "default"

    # Test detection
    has_env = ConfigLoader._has_pydantic_env_file_config(SettingsWithEnvFile)
    no_env = ConfigLoader._has_pydantic_env_file_config(SettingsWithoutEnvFile)
    null_env = ConfigLoader._has_pydantic_env_file_config(SettingsWithNullEnvFile)
    multi_env = ConfigLoader._has_pydantic_env_file_config(SettingsWithMultipleEnvFiles)

    console.print(f"   WithEnvFile: [green]{has_env}[/green] ✅")
    console.print(f"   WithoutEnvFile: [red]{no_env}[/red] ✅")
    console.print(f"   WithNullEnvFile: [red]{null_env}[/red] ✅")
    console.print(f"   WithMultipleEnvFiles: [green]{multi_env}[/green] ✅")

    assert has_env, "Should detect env_file configuration"
    assert not no_env, "Should not detect when no env_file"
    assert not null_env, "Should not detect when env_file=None"
    assert multi_env, "Should detect multiple env_file configuration"


def test_pydantic_native_mode():
    """Test 2: Verify Pydantic-native mode works correctly."""
    console.print("\n🐍 [bold]Test 2: Pydantic-Native Mode[/bold]")

    # Create test .env file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("TEST_SECRET=secret_from_env_file\n")
        f.write("TEST_DATABASE_HOST=db.env.server\n")
        f.write("TEST_DATABASE_PORT=5433\n")
        f.write("TEST_DEBUG=true\n")
        env_file = f.name

    # Create test YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("""
database_host: "db.yaml.server"  # This should override .env
api_key: "yaml_api_key"          # This is only in YAML
database_port: 3306              # This should override .env
""")
        yaml_file = f.name

    try:
        # Settings WITH env_file (should trigger Pydantic-native mode)
        class Settings(BaseSettings):
            model_config = SettingsConfigDict(env_file=env_file, env_prefix="TEST_")
            secret: str = "default_secret"
            database_host: str = "default_host"
            database_port: int = 5432
            debug: bool = False
            api_key: str = "default_key"

        # Load using hybrid approach - should use Pydantic-native mode
        settings = ConfigLoader.from_yaml_with_env(Settings, Path(yaml_file))

        console.print("   Results (YAML should override .env):")
        console.print(f"     Secret: [green]{settings.secret}[/green] (from .env)")
        console.print(f"     DB Host: [green]{settings.database_host}[/green] (YAML overrides .env)")
        console.print(f"     DB Port: [green]{settings.database_port}[/green] (YAML overrides .env)")
        console.print(f"     Debug: [green]{settings.debug}[/green] (from .env)")
        console.print(f"     API Key: [green]{settings.api_key}[/green] (from YAML)")

        # Verify Pydantic-native behavior
        assert settings.secret == "secret_from_env_file", "Should load secret from .env"
        assert settings.database_host == "db.yaml.server", "YAML should override .env"
        assert settings.database_port == 3306, "YAML should override .env"
        assert settings.debug, "Should load debug from .env"
        assert settings.api_key == "yaml_api_key", "Should load API key from YAML"

        console.print("   ✅ [green]Pydantic-native mode working correctly![/green]")

    finally:
        import os

        os.unlink(env_file)
        os.unlink(yaml_file)


def test_source_composition_mode():
    """Test 3: Verify source composition mode works correctly."""
    console.print("\n⚡ [bold]Test 3: Source Composition Mode[/bold]")

    # Set environment variables for testing
    import os

    os.environ.update(
        {"COMP_SECRET": "secret_from_env_var", "COMP_DATABASE_HOST": "db.env.server", "COMP_DEBUG": "true"}
    )

    # Create test YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("""
database_host: "db.yaml.server"  # Should be overridden by env var
api_key: "yaml_api_key"          # Only in YAML
database_port: 3306              # Only in YAML
""")
        yaml_file = f.name

    try:
        # Settings WITHOUT env_file (should trigger source composition mode)
        class Settings(BaseSettings):
            # No env_file configured - should use source composition
            secret: str = "default_secret"
            database_host: str = "default_host"
            database_port: int = 5432
            debug: bool = False
            api_key: str = "default_key"

        # Load using hybrid approach - should use source composition mode
        settings = ConfigLoader.from_yaml_with_env(Settings, Path(yaml_file), env_prefix="COMP")

        console.print("   Results (env vars should override YAML):")
        console.print(f"     Secret: [green]{settings.secret}[/green] (from env var)")
        console.print(f"     DB Host: [green]{settings.database_host}[/green] (env var overrides YAML)")
        console.print(f"     DB Port: [green]{settings.database_port}[/green] (from YAML)")
        console.print(f"     Debug: [green]{settings.debug}[/green] (from env var)")
        console.print(f"     API Key: [green]{settings.api_key}[/green] (from YAML)")

        # Verify source composition behavior (env overrides YAML)
        assert settings.secret == "secret_from_env_var", "Should load secret from env var"
        assert settings.database_host == "db.env.server", "Env var should override YAML"
        assert settings.database_port == 3306, "Should load port from YAML"
        assert settings.debug, "Should load debug from env var"
        assert settings.api_key == "yaml_api_key", "Should load API key from YAML"

        console.print("   ✅ [green]Source composition mode working correctly![/green]")

    finally:
        os.unlink(yaml_file)
        # Clean up environment variables
        for key in ["COMP_SECRET", "COMP_DATABASE_HOST", "COMP_DEBUG"]:
            os.environ.pop(key, None)


def test_key_difference():
    """Test 4: Demonstrate the key difference between the two modes."""
    console.print("\n🎯 [bold]Test 4: The Key Difference[/bold]")

    # Create .env file that only Pydantic-native mode should load
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("TEST_SECRET_PASSWORD=only_pydantic_loads_this\n")
        f.write("TEST_SHARED_VALUE=from_env_file\n")
        env_file = f.name

    # Set environment variable that both modes can access
    import os

    os.environ["TEST_SHARED_VALUE"] = "from_env_var"

    # Create YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("shared_value: from_yaml\n")
        yaml_file = f.name

    try:
        # Settings WITH env_file (Pydantic-native mode)
        class SettingsWithEnvFile(BaseSettings):
            model_config = SettingsConfigDict(env_file=env_file, env_prefix="TEST_")
            secret_password: str = "default_password"
            shared_value: str = "default_value"

        # Settings WITHOUT env_file (Source composition mode)
        class SettingsWithoutEnvFile(BaseSettings):
            secret_password: str = "default_password"
            shared_value: str = "default_value"

        # Load both ways
        with_env_file = ConfigLoader.from_yaml_with_env(SettingsWithEnvFile, Path(yaml_file))
        without_env_file = ConfigLoader.from_yaml_with_env(SettingsWithoutEnvFile, Path(yaml_file), env_prefix="TEST")

        console.print("   [bold]WITH env_file (Pydantic-native):[/bold]")
        console.print(f"     Secret Password: [green]{with_env_file.secret_password}[/green]")
        console.print(f"     Shared Value: [green]{with_env_file.shared_value}[/green]")

        console.print("   [bold]WITHOUT env_file (Source composition):[/bold]")
        console.print(f"     Secret Password: [green]{without_env_file.secret_password}[/green]")
        console.print(f"     Shared Value: [green]{without_env_file.shared_value}[/green]")

        # Verify the key difference
        assert with_env_file.secret_password == "only_pydantic_loads_this", "Pydantic should load from .env file"
        assert without_env_file.secret_password == "default_password", "Source composition shouldn't load .env file"

        # Different behavior for shared_value:
        # - Pydantic-native: YAML overrides everything (including env vars)
        # - Source composition: env vars override YAML
        assert with_env_file.shared_value == "from_yaml", "YAML should override in Pydantic-native mode"
        assert without_env_file.shared_value == "from_env_var", "Env var should override YAML in source composition"

        console.print("   ✅ [green]Key difference proven![/green]")
        console.print("     [yellow]Pydantic-native: Loads .env file + YAML overrides everything[/yellow]")
        console.print("     [yellow]Source composition: Only explicit sources + env vars override YAML[/yellow]")

    finally:
        os.unlink(env_file)
        os.unlink(yaml_file)
        os.environ.pop("TEST_SHARED_VALUE", None)


def test_force_override():
    """Test 5: Verify the force override parameter works."""
    console.print("\n🔧 [bold]Test 5: Force Override Parameter[/bold]")

    # Create .env file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("TEST_VALUE=from_env_file\n")
        env_file = f.name

    # Set different environment variable
    import os

    os.environ["FORCE_VALUE"] = "from_force_env_var"

    try:
        # Settings WITH env_file configured
        class Settings(BaseSettings):
            model_config = SettingsConfigDict(env_file=env_file, env_prefix="TEST_")
            value: str = "default_value"

        # Normal behavior (should use Pydantic-native mode)
        normal = ConfigLoader.from_yaml_with_env(Settings)

        # Forced source composition (should ignore env_file)
        forced = ConfigLoader.from_yaml_with_env(
            Settings,
            env_prefix="FORCE",
            respect_pydantic_env_file=False,  # Force source composition
        )

        console.print("   [bold]Normal (Pydantic-native):[/bold]")
        console.print(f"     Value: [green]{normal.value}[/green] (from .env file)")

        console.print("   [bold]Forced (Source composition):[/bold]")
        console.print(f"     Value: [green]{forced.value}[/green] (from FORCE_* env var)")

        # Verify force override works
        assert normal.value == "from_env_file", "Should use .env file normally"
        assert forced.value == "from_force_env_var", "Should ignore .env when forced"

        console.print("   ✅ [green]Force override working correctly![/green]")

    finally:
        os.unlink(env_file)
        os.environ.pop("FORCE_VALUE", None)


def main():
    """Run all tests to verify the hybrid approach works."""
    console.print(
        Panel.fit(
            "🧪 Hybrid env_file Approach Test Suite\n\n"
            "This test suite verifies that the new hybrid approach\n"
            "correctly detects and respects Pydantic's env_file\n"
            "configuration while providing enhanced capabilities.\n\n"
            "Run this to verify the implementation works!",
            title="Test Suite",
            style="bold cyan",
        )
    )

    try:
        test_detection_logic()
        test_pydantic_native_mode()
        test_source_composition_mode()
        test_key_difference()
        test_force_override()

        console.print(
            Panel.fit(
                "🎉 ALL TESTS PASSED!\n\n"
                "The hybrid env_file approach is working correctly:\n\n"
                "✅ Detection logic identifies env_file configuration\n"
                "✅ Pydantic-native mode uses Pydantic's env_file loading\n"
                "✅ Source composition mode uses explicit sources\n"
                "✅ Key behavioral difference is maintained\n"
                "✅ Force override parameter works as expected\n\n"
                "The implementation successfully bridges Pydantic's\n"
                "elegance with frostbound's enhanced capabilities!",
                title="🏆 Success!",
                style="bold green",
            )
        )

        return 0

    except Exception as e:
        console.print(f"\n❌ [bold red]TEST FAILED: {e}[/bold red]")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
