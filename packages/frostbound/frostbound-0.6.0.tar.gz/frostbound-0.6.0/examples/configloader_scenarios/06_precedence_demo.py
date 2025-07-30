"""
Example 06: Precedence Demonstration
Shows the order of precedence for different configuration sources
"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from frostbound.pydanticonf import ConfigLoader

console = Console()


def demo_precedence():
    """Demonstrate configuration precedence in different modes."""
    console.print(Panel("Example 06: Precedence Demonstration", style="bold blue"))

    # Set up test value in all sources
    test_key = "priority_test"

    # Create test files with different values
    with open(".env.base", "w") as f:
        f.write(f"{test_key}=from_env_base\n")
        f.write("port=1000\n")

    with open(".env.override", "w") as f:
        f.write(f"{test_key}=from_env_override\n")
        f.write("port=2000\n")

    with open("test_config.yaml", "w") as f:
        f.write(f"{test_key}: from_yaml\n")
        f.write("port: 3000\n")

    # Set environment variable
    os.environ[f"TEST_{test_key.upper()}"] = "from_env_var"
    os.environ["TEST_PORT"] = "4000"

    try:
        # Base settings class
        class Settings(BaseSettings):
            priority_test: str = "from_defaults"
            port: int = 5000

        console.print("\n[bold]Pydantic-native mode precedence:[/bold]")
        console.print("[dim](When env_file is configured)[/dim]\n")

        # 1. Multiple env files
        class MultiEnvSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=[".env.base", ".env.override"],
                env_prefix="",
            )

        settings1 = MultiEnvSettings()
        console.print("1. Multiple .env files:")
        console.print(f"   priority_test = [yellow]{settings1.priority_test}[/yellow]")
        console.print(f"   port = [yellow]{settings1.port}[/yellow]")
        console.print("   [dim]→ Later files override earlier ones[/dim]")

        # 2. With YAML override
        settings2 = ConfigLoader.from_yaml_with_env(MultiEnvSettings, yaml_path=Path("test_config.yaml"))
        console.print("\n2. .env files + YAML override:")
        console.print(f"   priority_test = [green]{settings2.priority_test}[/green]")
        console.print(f"   port = [green]{settings2.port}[/green]")
        console.print("   [dim]→ YAML overrides .env files[/dim]")

        console.print("\n[bold]Source composition mode precedence:[/bold]")
        console.print("[dim](When env_file is NOT configured)[/dim]\n")

        # 3. YAML + Environment variables
        settings3 = ConfigLoader.from_yaml_with_env(Settings, yaml_path=Path("test_config.yaml"), env_prefix="TEST_")
        console.print("3. YAML + Environment variables:")
        console.print(f"   priority_test = [blue]{settings3.priority_test}[/blue]")
        console.print(f"   port = [blue]{settings3.port}[/blue]")
        console.print("   [dim]→ Environment variables override YAML[/dim]")

        # Create comprehensive precedence table
        console.print("\n[bold]Complete Precedence Order:[/bold]")

        table = Table(title="Configuration Source Precedence")
        table.add_column("Mode", style="cyan")
        table.add_column("Precedence Order (Low → High)", style="green")
        table.add_column("Example", style="yellow")

        table.add_row(
            "Pydantic-native\n(with env_file)",
            "1. Class defaults\n2. .env files (in order)\n3. YAML override",
            "defaults → .env → .env.prod → config.yaml",
        )

        table.add_row(
            "Source composition\n(no env_file)",
            "1. Class defaults\n2. YAML file\n3. Environment variables",
            "defaults → config.yaml → APP_* env vars",
        )

        table.add_row(
            "Forced composition\n(respect_pydantic_env_file=False)",
            "1. Class defaults\n2. YAML file\n3. Environment variables",
            "Ignores env_file config",
        )

        console.print("\n")
        console.print(table)

        # Demonstrate with actual environment variable override
        console.print("\n[bold]Live demonstration with environment variable:[/bold]")

        # Pydantic with env vars
        class EnvVarSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=".env.base",
                env_prefix="TEST_",
                case_sensitive=False,
            )

        settings4 = EnvVarSettings()
        console.print("\nWith Pydantic env_prefix='TEST_':")
        console.print(f"   priority_test = [magenta]{settings4.priority_test}[/magenta]")
        console.print(f"   port = [magenta]{settings4.port}[/magenta]")
        console.print("   [dim]→ Environment variables have highest precedence![/dim]")

    finally:
        # Clean up
        for f in [".env.base", ".env.override", "test_config.yaml"]:
            if os.path.exists(f):
                os.unlink(f)
        os.environ.pop(f"TEST_{test_key.upper()}", None)
        os.environ.pop("TEST_PORT", None)


if __name__ == "__main__":
    demo_precedence()
