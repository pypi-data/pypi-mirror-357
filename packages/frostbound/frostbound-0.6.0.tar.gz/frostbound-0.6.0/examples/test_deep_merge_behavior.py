"""
Demonstrate the improved deep merge behavior in from_pydantic_native().
This shows how secrets from .env are preserved when YAML provides partial overrides.
"""

import os
import tempfile
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel

from frostbound.pydanticonf import ConfigLoader

console = Console()


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "admin"
    password: str = "default_password"
    ssl_mode: str = "require"
    pool_size: int = 10


class OpenAIConfig(BaseModel):
    api_key: str
    api_version: str = "v1"
    azure_endpoint: str | None = None
    model: str = "gpt-4"


class AppSettings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database: DatabaseConfig = DatabaseConfig()
    openai: OpenAIConfig

    model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__")


def test_deep_merge():
    """Test that deep merge preserves secrets from environment."""

    console.print(
        Panel.fit(
            "🔒 Deep Merge Behavior Test\n\n"
            "This demonstrates how from_pydantic_native() uses deep merge\n"
            "to preserve secrets from environment variables when YAML\n"
            "provides partial configuration overrides.",
            title="Deep Merge Demo",
            style="bold cyan",
        )
    )

    # Set up environment variables (simulating .env file)
    os.environ.update(
        {
            "APP_DATABASE__PASSWORD": "super-secret-password-from-env",
            "APP_DATABASE__USER": "prod_user",
            "APP_OPENAI__API_KEY": "sk-real-api-key-do-not-commit",
            "APP_DEBUG": "true",
        }
    )

    # Create YAML with partial overrides
    yaml_content = """
app_name: "Production App"
database:
  host: "prod.db.company.com"
  port: 5433
  # Note: password NOT specified - should come from env

openai:
  api_version: "v2"
  model: "gpt-4-turbo"
  # Note: api_key NOT specified - should come from env
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = Path(f.name)

    try:
        # Load configuration
        settings = ConfigLoader.from_pydantic_native(AppSettings, yaml_path=yaml_path)

        console.print("\n📊 Configuration Results:")
        console.print(f"  App Name: [green]{settings.app_name}[/green] (from YAML)")
        console.print(f"  Debug: [green]{settings.debug}[/green] (from env)")

        console.print("\n🗄️  Database Configuration:")
        console.print(f"  Host: [green]{settings.database.host}[/green] (from YAML)")
        console.print(f"  Port: [green]{settings.database.port}[/green] (from YAML)")
        console.print(f"  User: [green]{settings.database.user}[/green] (from env)")
        console.print(f"  Password: [green]{'*' * 10}[/green] (from env - preserved!)")
        console.print(f"  SSL Mode: [green]{settings.database.ssl_mode}[/green] (default - not overridden)")
        console.print(f"  Pool Size: [green]{settings.database.pool_size}[/green] (default - not overridden)")

        console.print("\n🤖 OpenAI Configuration:")
        console.print("  API Key: [green]sk-****[/green] (from env - preserved!)")
        console.print(f"  API Version: [green]{settings.openai.api_version}[/green] (from YAML)")
        console.print(f"  Model: [green]{settings.openai.model}[/green] (from YAML)")

        # Verify the critical behavior
        assert settings.database.password == "super-secret-password-from-env", "Password should be from env!"
        assert settings.openai.api_key == "sk-real-api-key-do-not-commit", "API key should be from env!"
        assert settings.database.host == "prod.db.company.com", "Host should be from YAML"
        assert settings.database.ssl_mode == "require", "Unspecified fields should keep defaults"

        console.print("\n✅ [bold green]Success![/bold green] Deep merge correctly:")
        console.print("  • Preserved secrets from environment variables")
        console.print("  • Applied overrides from YAML")
        console.print("  • Kept default values for unspecified fields")

    finally:
        os.unlink(yaml_path)
        # Clean up env vars
        for key in ["APP_DATABASE__PASSWORD", "APP_DATABASE__USER", "APP_OPENAI__API_KEY", "APP_DEBUG"]:
            os.environ.pop(key, None)


def compare_with_explicit_sources():
    """Show how to achieve the same with explicit sources."""

    console.print("\n" + "=" * 60 + "\n")
    console.print(
        Panel.fit(
            "🔄 Alternative: Using from_explicit_sources()\n\n"
            "For complete control, you can use explicit sources\n"
            "with environment variables last to ensure they win.",
            title="Explicit Sources",
            style="bold yellow",
        )
    )

    # Set up environment
    os.environ["APP_OPENAI__API_KEY"] = "sk-real-api-key"

    yaml_content = """
openai:
  api_key: "PLACEHOLDER_DO_NOT_COMMIT"
  api_version: "v2"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = Path(f.name)

    try:
        from frostbound.pydanticonf.sources import EnvironmentConfigSource, YamlConfigSource

        # Environment source LAST = highest precedence
        settings = ConfigLoader.from_explicit_sources(
            AppSettings,
            [
                YamlConfigSource(yaml_path),  # Lower precedence
                EnvironmentConfigSource("APP_", "__"),  # Higher precedence
            ],
        )

        console.print("  With explicit sources (env last):")
        console.print("  API Key: [green]sk-****[/green] (env overrides YAML placeholder ✅)")

        assert settings.openai.api_key == "sk-real-api-key"

    finally:
        os.unlink(yaml_path)
        os.environ.pop("APP_OPENAI__API_KEY", None)


if __name__ == "__main__":
    test_deep_merge()
    compare_with_explicit_sources()

    console.print("\n" + "=" * 60 + "\n")
    console.print(
        Panel.fit(
            "🎯 Key Takeaways\n\n"
            "1. from_pydantic_native() now ALWAYS uses deep merge\n"
            "2. Secrets from .env/environment are preserved\n"
            "3. YAML provides partial overrides, not replacements\n"
            "4. No more dangerous 'override' mode that loses data\n"
            "5. For full control, use from_explicit_sources()",
            title="Summary",
            style="bold green",
        )
    )
