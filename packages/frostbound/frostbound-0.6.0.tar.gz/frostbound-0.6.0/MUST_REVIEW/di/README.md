# Enterprise-Grade Dependency Injection Container

A powerful, flexible, and type-safe dependency injection container for Python applications.

## Features

- **Multiple Lifetime Scopes**: Support for singleton, transient, and scoped dependencies
- **Automatic Dependency Resolution**: Constructor injection with automatic type resolution
- **Flexible Registration Options**: Register types, instances, and factory functions
- **Declarative Dependency Definition**: Define dependencies as class attributes
- **Thread-Safe and Async-Compatible**: Safe for use in multi-threaded and async applications
- **Circular Dependency Detection**: Detects and reports circular dependencies
- **Strong Type Safety**: Leverages Python's type hints for strong type checking
- **OpenTelemetry Integration**: Built-in tracing support for better observability
- **Extensible Provider Model**: Easily add custom provider implementations
- **Service Decorators**: Apply decorators to services without modifying their implementation
- **Function Parameter Injection**: Automatically inject dependencies into function parameters
- **Container Builder Pattern**: Fluent API for configuring containers
- **Customizable Scope Contexts**: Support for custom scoping strategies

## Installation

```bash
pip install frostbound-di
```

## Basic Usage

```python
from frostbound.di import Container, inject

# Define a service interface and implementation
class Database:
    def query(self, sql: str) -> list:
        print(f"Executing: {sql}")
        return []

class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_users(self) -> list:
        return self.db.query("SELECT * FROM users")

# Create and configure the container
container = Container()
container.register(Database)
container.register(UserRepository)

# Resolve and use services
repo = container.resolve(UserRepository)
users = repo.get_users()

# Function parameter injection
@inject
def process_users(repo: UserRepository) -> None:
    users = repo.get_users()
    # Process users...

process_users()  # UserRepository is automatically injected
```

## Advanced Usage

### Declarative Dependencies

```python
from frostbound.di import Dependency

class UserService:
    # Dependencies are defined as class attributes
    db = Dependency[Database]

    def get_users(self) -> list:
        return self.db.query("SELECT * FROM users")

# Only need to register Database in the container
container.register(Database)

# Create a service instance and use it
service = UserService()
users = service.get_users()  # Database is automatically injected
```

### Container Builder Pattern

```python
from frostbound.di import ContainerBuilder, Scope

builder = ContainerBuilder()
builder.register(IDatabase, Database, scope=Scope.SINGLETON)
builder.register(ILogger, Logger)
builder.register_factory(
    AppConfig,
    lambda: AppConfig.from_env_vars()
)
builder.register_decorator(ILogger, add_timestamp_decorator)

container = builder.build()
```

### Scoped Dependencies

```python
from frostbound.di import Container, Scope

# Create a container with a request scope context
container = Container(scope_context=request_scope)

# Register services with appropriate scopes
container.register(ILogger, Logger, scope=Scope.SINGLETON)  # One per application
container.register(IDatabase, Database, scope=Scope.SCOPED)  # One per request
container.register(UserService, scope=Scope.TRANSIENT)  # New instance each time

# Use scopes in a web application
with request_scope.scope() as req_id:
    # All scoped dependencies created in this context
    # will be associated with this request scope
    service = container.resolve(UserService)
    # When the scope ends, scoped dependencies are eligible for cleanup
```

## API Reference

### Container

The main container class that manages dependency registrations and resolutions.

```python
# Create a container
container = Container()

# Register services
container.register(IService, ServiceImpl, scope=Scope.SINGLETON)
container.register_instance(Config, config_instance)
container.register_factory(Database, create_database)

# Register a decorator
container.register_decorator(IService, logging_decorator)

# Resolve services
service = container.resolve(IService)

# Create a scoped context
with container.scope() as scope_id:
    # Resolve scoped dependencies
    db = container.resolve(Database)
```

### Dependency

A descriptor for declarative dependency injection.

```python
class UserService:
    db = Dependency[Database]
    logger = Dependency[Logger]

    def process(self):
        self.logger.info("Processing users")
        users = self.db.query("SELECT * FROM users")
        # Process users...
```

### ContainerBuilder

A builder for creating and configuring containers.

```python
builder = ContainerBuilder()
builder.register(IService, ServiceImpl)
builder.register_instance(Config, config_instance)
builder.use_scope_context(request_scope)
container = builder.build()
```

### Scope

An enum that defines the lifetime of registered dependencies.

- `Scope.SINGLETON`: One instance for the entire application
- `Scope.TRANSIENT`: New instance created each time
- `Scope.SCOPED`: One instance per scope (e.g., per request)

### ScopeContext

An interface for managing scope lifecycles.

- `ThreadScopeContext`: Scope based on thread identity
- `AsyncScopeContext`: Scope that works with async code
- Custom implementations for specific needs (e.g., per HTTP request)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
