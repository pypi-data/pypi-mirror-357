from __future__ import annotations

from frostbound.pydanticonf import DynamicConfig, instantiate, register_dependency


# Example classes to instantiate
class Database:
    def __init__(self, host: str, port: int = 5432) -> None:
        self.host = host
        self.port = port
        print(f"Database connected to {host}:{port}")

    def query(self, sql: str) -> str:
        return f"Executing: {sql}"


class Logger:
    def __init__(self, name: str, level: str = "INFO") -> None:
        self.name = name
        self.level = level
        print(f"Logger '{name}' initialized at {level} level")

    def log(self, message: str) -> None:
        print(f"[{self.level}] {self.name}: {message}")


class Service:
    def __init__(self, name: str, database: Database, logger: Logger | None = None) -> None:
        self.name = name
        self.database = database
        self.logger = logger or Logger(f"{name}_logger")
        print(f"Service '{name}' initialized")

    def process(self) -> None:
        result = self.database.query("SELECT * FROM users")
        self.logger.log(f"Processed: {result}")


# Configuration models
class DatabaseConfig(DynamicConfig[Database]):
    host: str
    port: int = 5432


class LoggerConfig(DynamicConfig[Logger]):
    name: str
    level: str = "INFO"


class ServiceConfig(DynamicConfig[Service]):
    name: str
    database: DatabaseConfig  # Nested config - will be instantiated recursively


# Additional test class for _args_ demo
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        print(f"Point created at ({x}, {y})")


def demo_basic_instantiation() -> None:
    print("=== Basic Instantiation ===\n")

    # 1. Instantiate from DynamicConfig
    db_config = DatabaseConfig(
        _target_="examples.instantiate_demo.Database",
        host="localhost",
        port=5433,
    )
    db = instantiate(db_config)
    print(f"Database type: {type(db).__name__}\n")

    # 2. Instantiate from dict
    logger_dict = {
        "_target_": "examples.instantiate_demo.Logger",
        "name": "app_logger",
        "level": "DEBUG",
    }
    logger = instantiate(logger_dict)
    logger.log("Test message")
    print()

    # 3. Override parameters
    instantiate(db_config, port=3306)
    print()


def demo_recursive_instantiation() -> None:
    print("=== Recursive Instantiation ===\n")

    service_config = ServiceConfig(
        _target_="examples.instantiate_demo.Service",
        name="UserService",
        database=DatabaseConfig(
            _target_="examples.instantiate_demo.Database",
            host="prod.db.server",
        ),
    )

    service = instantiate(service_config)
    service.process()
    print()


def demo_dependency_injection() -> None:
    print("=== Dependency Injection ===\n")

    # Register a shared database instance
    shared_db = Database("shared.db.server", 5432)

    # Register by parameter name (more reliable than by type due to import paths)
    register_dependency("database", shared_db)

    # Now services will automatically get the shared database
    service_config = {
        "_target_": "examples.instantiate_demo.Service",
        "name": "OrderService",
        # No need to specify database - it will be injected!
    }

    service = instantiate(service_config)
    service.process()
    print("Note: Dependency was injected by parameter name 'database'")
    print()


def demo_partial_instantiation() -> None:
    print("=== Partial Instantiation ===\n")

    # Create a partial function for creating loggers with a specific level
    error_logger_factory = instantiate(
        {
            "_target_": "examples.instantiate_demo.Logger",
            "_partial_": True,
            "level": "ERROR",
        }
    )

    # Now we can create multiple error loggers
    app_logger = error_logger_factory(name="app")
    db_logger = error_logger_factory(name="database")

    app_logger.log("This is an error")
    db_logger.log("Database connection failed")
    print()


def demo_args_support() -> None:
    print("=== Positional Arguments Support ===\n")

    # Classes using positional arguments can use _args_
    point = instantiate(
        {
            "_target_": "examples.instantiate_demo.Point",
            "_args_": [3.14, 2.71],
        }
    )
    print(f"Point location: ({point.x}, {point.y})")
    print()


def main() -> None:
    print("==== Frostbound Pydanticonf Instantiation Demo ====\n")

    demo_basic_instantiation()
    demo_recursive_instantiation()
    demo_dependency_injection()
    demo_partial_instantiation()
    demo_args_support()

    print("✅ All instantiation patterns demonstrated!")


if __name__ == "__main__":
    main()
