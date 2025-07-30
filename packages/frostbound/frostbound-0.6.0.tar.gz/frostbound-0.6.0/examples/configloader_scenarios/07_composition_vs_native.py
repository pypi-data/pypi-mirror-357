"""
Example 07: Source Composition vs Pydantic-native Mode
Demonstrates the differences between frostbound's source composition
and Pydantic's native env_file handling
"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from frostbound.pydanticonf import ConfigLoader

console = Console()


def demo_composition_vs_native():
    """Show differences between source composition and Pydantic-native modes."""
    console.print(Panel("Example 07: Source Composition vs Pydantic-native Mode", style="bold blue"))

    # Base settings for comparison
    class Settings(BaseSettings):
        app_name: str = "DefaultApp"
        debug: bool = False
        port: int = 3000
        database_url: str = "sqlite:///default.db"
        cache_enabled: bool = False

    # Set up environment variable
    os.environ["MYAPP_PORT"] = "7000"
    os.environ["MYAPP_CACHE_ENABLED"] = "true"

    try:
        console.print("\n[bold cyan]Mode 1: Pydantic-native (with env_file)[/bold]")
        console.print("[dim]Uses Pydantic's built-in env_file loading[/dim]\n")

        # Pydantic-native approach
        class PydanticNativeSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=".env",
                env_prefix="MYAPP_",  # Pydantic handles env vars too
            )

        # Show the code
        code1 = """class PydanticNativeSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MYAPP_",
    )

settings = PydanticNativeSettings()  # Or ConfigLoader.from_yaml_with_env()"""

        syntax1 = Syntax(code1, "python", theme="monokai", line_numbers=True)
        console.print(syntax1)

        settings1 = PydanticNativeSettings()
        console.print("\nResult:")
        console.print(f"  App Name: [green]{settings1.app_name}[/green] (from .env)")
        console.print(f"  Port: [green]{settings1.port}[/green] (from MYAPP_PORT env var)")
        console.print(f"  Cache: [green]{settings1.cache_enabled}[/green] (from MYAPP_CACHE_ENABLED)")

        console.print("\n[bold]Features:[/bold]")
        console.print("  ✓ Leverages all Pydantic features (encoding, multiple files, etc.)")
        console.print("  ✓ Environment variables work with Pydantic's env_prefix")
        console.print("  ✓ Automatic type conversion and validation")
        console.print("  ✓ Can add YAML override with ConfigLoader.from_yaml_with_env()")

        console.print("\n" + "=" * 60 + "\n")

        console.print("[bold cyan]Mode 2: Source Composition (no env_file)[/bold]")
        console.print("[dim]Uses frostbound's explicit source system[/dim]\n")

        # Source composition approach
        code2 = """# No env_file in model_config
settings = ConfigLoader.from_yaml_with_env(
    Settings,
    yaml_path=Path("config.yaml"),
    env_prefix="MYAPP_",
    env_nested_delimiter="__"
)"""

        syntax2 = Syntax(code2, "python", theme="monokai", line_numbers=True)
        console.print(syntax2)

        settings2 = ConfigLoader.from_yaml_with_env(
            Settings, yaml_path=Path("config.yaml"), env_prefix="MYAPP_", env_nested_delimiter="__"
        )

        console.print("\nResult:")
        console.print(f"  App Name: [blue]{settings2.app_name}[/blue] (from config.yaml)")
        console.print(f"  Port: [blue]{settings2.port}[/blue] (from MYAPP_PORT env var)")
        console.print(f"  Cache: [blue]{settings2.cache_enabled}[/blue] (from MYAPP_CACHE_ENABLED)")

        console.print("\n[bold]Features:[/bold]")
        console.print("  ✓ Full control over source ordering")
        console.print("  ✓ Custom delimiter for nested env vars (e.g., DB__HOST)")
        console.print("  ✓ Can mix and match any ConfigSource implementations")
        console.print("  ✓ Explicit precedence: YAML → Environment variables")

        console.print("\n" + "=" * 60 + "\n")

        console.print("[bold cyan]Mode 3: Force Source Composition[/bold]")
        console.print("[dim]Override Pydantic's env_file detection[/dim]\n")

        # Force composition mode
        code3 = """class SettingsWithEnvFile(Settings):
    model_config = SettingsConfigDict(env_file=".env")

# Force source composition despite env_file config
settings = ConfigLoader.from_yaml_with_env(
    SettingsWithEnvFile,
    yaml_path=Path("config.yaml"),
    env_prefix="MYAPP_",
    respect_pydantic_env_file=False  # Force composition mode
)"""

        syntax3 = Syntax(code3, "python", theme="monokai", line_numbers=True)
        console.print(syntax3)

        class SettingsWithEnvFile(Settings):
            model_config = SettingsConfigDict(env_file=".env")

        settings3 = ConfigLoader.from_yaml_with_env(
            SettingsWithEnvFile, yaml_path=Path("config.yaml"), env_prefix="MYAPP_", respect_pydantic_env_file=False
        )

        console.print("\nResult:")
        console.print("  [yellow]Ignores .env file configuration![/yellow]")
        console.print("  Uses only: config.yaml → MYAPP_* env vars")
        console.print(f"  App Name: [yellow]{settings3.app_name}[/yellow] (from config.yaml)")
        console.print(f"  Port: [yellow]{settings3.port}[/yellow] (from MYAPP_PORT)")
        console.print(f"  Cache: [yellow]{settings3.cache_enabled}[/yellow] (from MYAPP_CACHE_ENABLED)")

        # Comparison table
        console.print("\n[bold]When to use each mode:[/bold]\n")

        console.print("[green]Pydantic-native mode:[/green]")
        console.print("  • You're already using Pydantic's env_file")
        console.print("  • You want to add YAML as an override layer")
        console.print("  • You need Pydantic's env features (encoding, etc.)")

        console.print("\n[blue]Source composition mode:[/blue]")
        console.print("  • You want explicit control over sources")
        console.print("  • You need custom delimiters for nested env vars")
        console.print("  • You're building a custom configuration system")

        console.print("\n[yellow]Forced composition mode:[/yellow]")
        console.print("  • You're migrating from Pydantic env_file")
        console.print("  • You need to temporarily override behavior")
        console.print("  • Testing different configuration strategies")

    finally:
        # Clean up
        os.environ.pop("MYAPP_PORT", None)
        os.environ.pop("MYAPP_CACHE_ENABLED", None)


if __name__ == "__main__":
    demo_composition_vs_native()
