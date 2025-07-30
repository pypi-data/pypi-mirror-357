"""Enterprise-grade dependency injection container module.

This module provides a clean, flexible and powerful dependency injection
container for Python applications, with support for:

- Singleton, transient, and scoped dependencies
- Automatic dependency resolution via constructor injection
- Factory functions with auto-injected dependencies
- Declarative dependency definitions using descriptors
- Thread-safe dependency resolution
- Circular dependency detection
- OpenTelemetry tracing integration
- Scoped lifecycle management

Example:
    ```python
    from frostbound.di import (
        Container,
        Dependency,
        Scope,
        ContainerBuilder,
        inject
    )

    # Define interfaces
    class IDatabase(Protocol):
        def execute(self, query: str) -> None: ...

    class ILogger(Protocol):
        def log(self, message: str) -> None: ...

    # Implement concrete types
    class Database(IDatabase):
        def execute(self, query: str) -> None:
            print(f"Executing: {query}")

    class Logger(ILogger):
        def log(self, message: str) -> None:
            print(f"LOG: {message}")

    # Configure services using Container directly
    container = Container()
    container.register(IDatabase, Database)
    container.register(ILogger, Logger)

    # Or use the builder pattern
    builder = ContainerBuilder()
    builder.register(IDatabase, Database)
    builder.register(ILogger, Logger)
    container = builder.build()

    # Resolve dependencies
    db = container.resolve(IDatabase)
    logger = container.resolve(ILogger)

    # Use in functions with automatic injection
    @inject
    def process_data(db: IDatabase, logger: ILogger) -> None:
        db.execute("SELECT * FROM users")
        logger.log("Data processed")

    # Use declarative injection in classes
    class UserService:
        db = Dependency[IDatabase]
        logger = Dependency[ILogger]

        def process(self) -> None:
            self.db.execute("SELECT * FROM users")
            self.logger.log("Users processed")
    ```
"""

from frostbound.di.container import (
    Container,
    ContainerBuilder,
    Dependency,
    get_container,
    inject,
    set_container,
)
from frostbound.di.providers import (
    AsyncScopeContext,
    FactoryProvider,
    InstanceProvider,
    LazyProvider,
    ScopedProvider,
    SingletonProvider,
    ThreadScopeContext,
    TransientProvider,
)
from frostbound.di.types_ import (
    CircularDependencyError,
    DependencyRegistrationError,
    DependencyResolutionError,
    DIException,
    Factory,
    FactoryWithDeps,
    Provider,
    ResolveOptions,
    Scope,
    ScopeContext,
    ScopeError,
)

__all__ = [
    # Container and utilities
    "Container",
    "ContainerBuilder",
    "Dependency",
    "get_container",
    "set_container",
    "inject",
    # Types
    "CircularDependencyError",
    "DependencyRegistrationError",
    "DependencyResolutionError",
    "DIException",
    "Factory",
    "FactoryWithDeps",
    "Provider",
    "ResolveOptions",
    "Scope",
    "ScopeContext",
    "ScopeError",
    # Providers
    "AsyncScopeContext",
    "FactoryProvider",
    "InstanceProvider",
    "LazyProvider",
    "ScopedProvider",
    "SingletonProvider",
    "ThreadScopeContext",
    "TransientProvider",
]
