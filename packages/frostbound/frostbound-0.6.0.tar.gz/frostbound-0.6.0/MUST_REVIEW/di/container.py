"""Enterprise-grade dependency injection container.

This module provides a robust dependency injection container with support for:
- Singleton, transient, and scoped dependencies
- Automatic dependency resolution via constructor injection
- Factory functions with auto-injected dependencies
- Declarative dependency definitions
- Thread-safe dependency resolution
- Circular dependency detection
- OpenTelemetry tracing integration
- Scoped lifecycle management
"""

import functools
import inspect
import threading
import uuid
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Callable, Dict, Generic, Iterator, List, Protocol, Set, Type, TypeVar, cast, overload

try:
    # Import OpenTelemetry if available
    from opentelemetry import trace
    from opentelemetry.trace.status import Status, StatusCode

    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False

    # Create dummy classes if OpenTelemetry is not available
    class DummySpan:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def set_status(self, *args):
            pass

        def record_exception(self, *args):
            pass

        def set_attribute(self, *args):
            pass

    class DummyTracer:
        def start_as_current_span(self, name):
            return DummySpan()

    class DummyProvider:
        def get_tracer(self, name):
            return DummyTracer()

    trace = type("DummyTrace", (), {"get_tracer_provider": lambda: DummyProvider()})

# Import dependency injection types and providers
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
    ContainerProtocol,
    DependencyRegistrationError,
    DependencyResolutionError,
    DIException,
    Factory,
    Provider,
    RegistrationInfo,
    ResolveOptions,
    Scope,
    ScopeContext,
    ScopeError,
    T,
    TImpl,
    TService,
    get_constructor_params,
)


# Get a tracer for this module
_tracer = trace.get_tracer_provider().get_tracer("frostbound.di.container")


class Dependency(Generic[T]):
    """Descriptor for declarative dependency injection.

    This class allows for a declarative style of dependency injection where
    dependencies are defined as class attributes and automatically resolved.

    Example:
        ```python
        class MyService:
            db = Dependency[Database]

            def __init__(self):
                # db is automatically injected
                self.db.execute("SELECT 1")
        ```
    """

    def __init__(self, service_type: Type[T]) -> None:
        """Initialize the dependency descriptor.

        Args:
            service_type: The type of the dependency to inject
        """
        self.service_type = service_type
        self.name = None

    def __set_name__(self, owner: Any, name: str) -> None:
        """Set the attribute name when used as a class attribute.

        Args:
            owner: The class that owns this descriptor
            name: The attribute name
        """
        self.name = name

    def __get__(self, instance: Any, owner: Type[Any]) -> T:
        """Get the dependency instance.

        Args:
            instance: The instance that owns this descriptor
            owner: The class that owns this descriptor

        Returns:
            The resolved dependency

        Raises:
            DIException: If the container is not available
        """
        if instance is None:
            # Class access, not instance access
            return self

        # Get the container
        container = get_container()

        # Resolve the dependency
        dependency = container.resolve(self.service_type)

        # Cache the dependency on the instance for performance
        if self.name is not None:
            setattr(instance, self.name, dependency)

        return dependency


class Container:
    """Enterprise-grade dependency injection container.

    This container supports:
    - Registration of services with different lifetimes (singleton, transient, scoped)
    - Automatic dependency resolution via constructor injection
    - Factory functions with auto-injected dependencies
    - Thread-safe dependency resolution
    - Circular dependency detection
    - OpenTelemetry tracing integration
    - Scoped lifecycle management
    """

    def __init__(self, scope_context: ScopeContext | None = None) -> None:
        """Initialize the container.

        Args:
            scope_context: The scope context to use for scoped dependencies
        """
        # Dictionary mapping service types to their registration info
        self._registrations: Dict[Type[Any], RegistrationInfo] = {}
        # Dictionary mapping service types to their providers
        self._providers: Dict[Type[Any], Provider[Any]] = {}
        # Lock for thread safety
        self._lock = threading.RLock()
        # Stack for detecting circular dependencies
        self._resolution_stack: List[Type[Any]] = []
        # Scope context for scoped dependencies
        self._scope_context = scope_context or ThreadScopeContext()
        # Set of registered decorators
        self._decorators: Dict[Type[Any], List[Callable[[Any], Any]]] = {}

    @overload
    def register(
        self,
        service_type: Type[TService],
        *,
        scope: Scope = Scope.SINGLETON,
    ) -> None: ...

    @overload
    def register(
        self,
        service_type: Type[TService],
        implementation_type: Type[TImpl],
        *,
        scope: Scope = Scope.SINGLETON,
    ) -> None: ...

    def register(
        self,
        service_type: Type[TService],
        implementation_type: Type[TImpl] | None = None,
        *,
        scope: Scope = Scope.SINGLETON,
    ) -> None:
        """Register a service with an implementation.

        Args:
            service_type: The service type to register
            implementation_type: The implementation type to use (defaults to service_type)
            scope: The scope of the dependency (singleton, transient, or scoped)

        Raises:
            DependencyRegistrationError: If the registration fails
        """
        with _tracer.start_as_current_span("Container.register") as span:
            span.set_attribute("service_type", service_type.__name__)
            if implementation_type:
                span.set_attribute("implementation_type", implementation_type.__name__)
            span.set_attribute("scope", scope.name)

            with self._lock:
                try:
                    impl_type = implementation_type
                    if impl_type is None:
                        # Explicitly use cast here to deal with the type variance
                        impl_type = cast(Type[TImpl], service_type)

                    if not inspect.isclass(service_type):
                        raise DependencyRegistrationError(f"Service type must be a class, got {type(service_type)}")

                    if not inspect.isclass(impl_type):
                        raise DependencyRegistrationError(f"Implementation type must be a class, got {type(impl_type)}")

                    info = RegistrationInfo(
                        service_type=service_type,
                        implementation_type=impl_type,
                        scope=scope,
                    )

                    self._registrations[service_type] = info
                    # Clear cached provider when re-registering
                    if service_type in self._providers:
                        del self._providers[service_type]

                    span.set_status(Status(StatusCode.OK))
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise DependencyRegistrationError(f"Failed to register {service_type}: {str(e)}") from e

    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Register a pre-created instance.

        Args:
            service_type: The service type to register
            instance: The instance to use

        Raises:
            DependencyRegistrationError: If the registration fails
        """
        with _tracer.start_as_current_span("Container.register_instance") as span:
            span.set_attribute("service_type", service_type.__name__)

            with self._lock:
                try:
                    if not inspect.isclass(service_type):
                        raise DependencyRegistrationError(f"Service type must be a class, got {type(service_type)}")

                    if not isinstance(instance, service_type):
                        raise DependencyRegistrationError(f"Instance {instance} is not an instance of {service_type}")

                    info = RegistrationInfo(
                        service_type=service_type,
                        implementation_type=type(instance),
                        scope=Scope.SINGLETON,
                        instance=instance,
                    )

                    self._registrations[service_type] = info
                    self._providers[service_type] = InstanceProvider(instance)
                    span.set_status(Status(StatusCode.OK))
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise DependencyRegistrationError(
                        f"Failed to register instance {instance} for {service_type}: {str(e)}"
                    ) from e

    def register_factory(
        self,
        service_type: Type[T],
        factory: Factory[T],
        *,
        scope: Scope = Scope.SINGLETON,
    ) -> None:
        """Register a factory function.

        Args:
            service_type: The service type to register
            factory: The factory function to use
            scope: The scope of the dependency (singleton, transient, or scoped)

        Raises:
            DependencyRegistrationError: If the registration fails
        """
        with _tracer.start_as_current_span("Container.register_factory") as span:
            span.set_attribute("service_type", service_type.__name__)
            span.set_attribute("scope", scope.name)

            with self._lock:
                try:
                    if not inspect.isclass(service_type):
                        raise DependencyRegistrationError(f"Service type must be a class, got {type(service_type)}")

                    if not callable(factory):
                        raise DependencyRegistrationError(f"Factory must be callable, got {type(factory)}")

                    info = RegistrationInfo(
                        service_type=service_type,
                        implementation_type=None,
                        scope=scope,
                        factory=factory,
                    )

                    self._registrations[service_type] = info
                    # Clear cached provider when re-registering
                    if service_type in self._providers:
                        del self._providers[service_type]

                    span.set_status(Status(StatusCode.OK))
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise DependencyRegistrationError(
                        f"Failed to register factory {factory} for {service_type}: {str(e)}"
                    ) from e

    def register_decorator(
        self,
        service_type: Type[T],
        decorator: Callable[[T], T],
    ) -> None:
        """Register a decorator for a service.

        Decorators are applied in registration order when a service is resolved.

        Args:
            service_type: The service type to decorate
            decorator: The decorator function to apply

        Raises:
            DependencyRegistrationError: If the registration fails
        """
        with _tracer.start_as_current_span("Container.register_decorator") as span:
            span.set_attribute("service_type", service_type.__name__)

            with self._lock:
                try:
                    if not inspect.isclass(service_type):
                        raise DependencyRegistrationError(f"Service type must be a class, got {type(service_type)}")

                    if not callable(decorator):
                        raise DependencyRegistrationError(f"Decorator must be callable, got {type(decorator)}")

                    if service_type not in self._decorators:
                        self._decorators[service_type] = []

                    self._decorators[service_type].append(decorator)
                    span.set_status(Status(StatusCode.OK))
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise DependencyRegistrationError(
                        f"Failed to register decorator {decorator} for {service_type}: {str(e)}"
                    ) from e

    @overload
    def resolve(self, service_type: Type[T]) -> T: ...

    @overload
    def resolve(self, service_type: Type[T], *, options: ResolveOptions) -> T | None: ...

    def resolve(self, service_type: Type[T], *, options: ResolveOptions | None = None) -> T | None:
        """Resolve a service instance.

        Args:
            service_type: The service type to resolve
            options: Options for dependency resolution

        Returns:
            An instance of the service, or None if optional and not found

        Raises:
            DependencyResolutionError: If the resolution fails
            CircularDependencyError: If a circular dependency is detected
        """
        options = options or ResolveOptions()

        with _tracer.start_as_current_span("Container.resolve") as span:
            span.set_attribute("service_type", service_type.__name__)
            span.set_attribute("optional", options.optional)

            try:
                # Check for circular dependencies
                if service_type in self._resolution_stack:
                    path = " -> ".join(t.__name__ for t in self._resolution_stack + [service_type])
                    span.set_status(Status(StatusCode.ERROR))
                    span.set_attribute("circular_dependency_path", path)
                    raise CircularDependencyError(f"Circular dependency detected: {path}")

                self._resolution_stack.append(service_type)

                try:
                    # Try to get the provider from the cache
                    if service_type in self._providers:
                        result = self._providers[service_type].get()
                        result = self._apply_decorators(service_type, result)
                        span.set_status(Status(StatusCode.OK))
                        return cast(T, result)

                    # If not cached, create a new provider
                    with self._lock:
                        if service_type in self._providers:
                            # Check again inside the lock
                            result = self._providers[service_type].get()
                            result = self._apply_decorators(service_type, result)
                            span.set_status(Status(StatusCode.OK))
                            return cast(T, result)

                        if service_type not in self._registrations:
                            # Try to auto-register the service if it's concrete
                            if (
                                options.allow_auto_registration
                                and inspect.isclass(service_type)
                                and not inspect.isabstract(service_type)
                                and not service_type.__name__.startswith("_")
                            ):
                                span.set_attribute("auto_registered", True)
                                self.register(service_type)
                            else:
                                if options.optional:
                                    span.set_attribute("not_found", True)
                                    span.set_status(Status(StatusCode.OK))
                                    return None
                                span.set_status(Status(StatusCode.ERROR))
                                raise DependencyResolutionError(f"No registration found for {service_type}")

                        # Get the registration info
                        info = self._registrations[service_type]

                        # Create the provider based on the registration info
                        provider = self._create_provider(info)

                        # Cache the provider
                        self._providers[service_type] = provider

                        result = provider.get()
                        result = self._apply_decorators(service_type, result)
                        span.set_status(Status(StatusCode.OK))
                        return cast(T, result)
                finally:
                    # Remove the service from the resolution stack
                    self._resolution_stack.pop()
            except CircularDependencyError:
                # Re-raise circular dependency errors
                raise
            except Exception as e:
                if isinstance(e, DependencyResolutionError):
                    # Re-raise resolution errors
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise

                # Wrap any other exceptions
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise DependencyResolutionError(f"Failed to resolve {service_type}: {str(e)}") from e

    def _apply_decorators(self, service_type: Type[Any], instance: T) -> T:
        """Apply registered decorators to a service instance.

        Args:
            service_type: The service type
            instance: The instance to decorate

        Returns:
            The decorated instance
        """
        if service_type not in self._decorators:
            return instance

        result = instance
        for decorator in self._decorators[service_type]:
            result = decorator(result)

        return cast(T, result)

    def _create_provider(self, info: RegistrationInfo) -> Provider[Any]:
        """Create a provider based on the registration info.

        Args:
            info: The registration info

        Returns:
            A provider

        Raises:
            DependencyResolutionError: If the provider creation fails
        """
        with _tracer.start_as_current_span("Container._create_provider") as span:
            span.set_attribute("service_type", info.service_type.__name__)
            span.set_attribute("scope", info.scope.name)

            if info.instance is not None:
                return InstanceProvider(info.instance)

            if info.factory is not None:
                factory_provider = FactoryProvider(info.factory, self)
            else:
                assert info.implementation_type is not None
                impl_type = info.implementation_type
                factory_provider = FactoryProvider(lambda: self._create_instance(impl_type), self)

            # Create the appropriate provider based on the scope
            if info.scope == Scope.SINGLETON:
                return SingletonProvider(factory_provider)
            elif info.scope == Scope.TRANSIENT:
                return TransientProvider(factory_provider)
            elif info.scope == Scope.SCOPED:
                return ScopedProvider(factory_provider, self._scope_context)
            else:
                span.set_status(Status(StatusCode.ERROR))
                raise DependencyResolutionError(f"Unknown scope: {info.scope}")

    def _create_instance(self, implementation_type: Type[T]) -> T:
        """Create an instance of a type, resolving constructor dependencies.

        Args:
            implementation_type: The type to instantiate

        Returns:
            An instance of the type

        Raises:
            DependencyResolutionError: If the instantiation fails
        """
        with _tracer.start_as_current_span("Container._create_instance") as span:
            span.set_attribute("implementation_type", implementation_type.__name__)

            try:
                # Get constructor parameters with their types from the cache
                params = get_constructor_params(implementation_type)

                # For each parameter, try to resolve it
                kwargs = {}
                for name, param_type in params:
                    try:
                        param_value = self.resolve(param_type)
                        kwargs[name] = param_value
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR))
                        span.record_exception(e)
                        raise DependencyResolutionError(
                            f"Failed to resolve parameter {name} of type {param_type} for {implementation_type}: {str(e)}"
                        ) from e

                # Create the instance
                instance = implementation_type(**kwargs)
                span.set_status(Status(StatusCode.OK))
                return instance
            except Exception as e:
                if isinstance(e, DependencyResolutionError):
                    # Re-raise resolution errors
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise

                # Wrap any other exceptions
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise DependencyResolutionError(f"Failed to create instance of {implementation_type}: {str(e)}") from e

    def clear(self) -> None:
        """Clear all registrations and providers."""
        with _tracer.start_as_current_span("Container.clear") as span:
            with self._lock:
                self._registrations.clear()
                self._providers.clear()
                self._decorators.clear()
                span.set_status(Status(StatusCode.OK))

    @contextmanager
    def scope(self, scope_id: str | None = None) -> Iterator[str]:
        """Context manager for scope handling.

        Args:
            scope_id: Optional scope identifier. If None, a new ID will be generated.

        Yields:
            The scope ID.

        Example:
            ```python
            with container.scope() as scope_id:
                service = container.resolve(MyService)
                # service is scoped to this context
            # service is automatically disposed when the scope exits
            ```
        """
        with self._scope_context.scope(scope_id) as sid:
            yield sid


class ContainerBuilder:
    """Builder for creating and configuring containers.

    This class provides a fluent API for configuring a container,
    similar to the builder pattern in other DI frameworks.

    Example:
        ```python
        builder = ContainerBuilder()
        builder.register(IService, Service)
        builder.register_instance(Config, config)
        container = builder.build()
        ```
    """

    def __init__(self) -> None:
        """Initialize the container builder."""
        self._registrations: List[Callable[[Container], None]] = []
        self._decorators: List[Callable[[Container], None]] = []
        self._scope_context: ScopeContext | None = None

    def register(
        self,
        service_type: Type[TService],
        implementation_type: Type[TImpl] | None = None,
        *,
        scope: Scope = Scope.SINGLETON,
    ) -> "ContainerBuilder":
        """Register a service with an implementation.

        Args:
            service_type: The service type to register
            implementation_type: The implementation type to use (defaults to service_type)
            scope: The scope of the dependency (singleton, transient, or scoped)

        Returns:
            The builder instance for method chaining
        """

        def register_service(container: Container) -> None:
            container.register(service_type, implementation_type, scope=scope)

        self._registrations.append(register_service)
        return self

    def register_instance(
        self,
        service_type: Type[T],
        instance: T,
    ) -> "ContainerBuilder":
        """Register a pre-created instance.

        Args:
            service_type: The service type to register
            instance: The instance to use

        Returns:
            The builder instance for method chaining
        """

        def register_instance_service(container: Container) -> None:
            container.register_instance(service_type, instance)

        self._registrations.append(register_instance_service)
        return self

    def register_factory(
        self,
        service_type: Type[T],
        factory: Factory[T],
        *,
        scope: Scope = Scope.SINGLETON,
    ) -> "ContainerBuilder":
        """Register a factory function.

        Args:
            service_type: The service type to register
            factory: The factory function to use
            scope: The scope of the dependency (singleton, transient, or scoped)

        Returns:
            The builder instance for method chaining
        """

        def register_factory_service(container: Container) -> None:
            container.register_factory(service_type, factory, scope=scope)

        self._registrations.append(register_factory_service)
        return self

    def register_decorator(
        self,
        service_type: Type[T],
        decorator: Callable[[T], T],
    ) -> "ContainerBuilder":
        """Register a decorator for a service.

        Args:
            service_type: The service type to decorate
            decorator: The decorator function to apply

        Returns:
            The builder instance for method chaining
        """

        def register_decorator_service(container: Container) -> None:
            container.register_decorator(service_type, decorator)

        self._decorators.append(register_decorator_service)
        return self

    def use_scope_context(self, scope_context: ScopeContext) -> "ContainerBuilder":
        """Set the scope context to use for scoped dependencies.

        Args:
            scope_context: The scope context to use

        Returns:
            The builder instance for method chaining
        """
        self._scope_context = scope_context
        return self

    def build(self) -> Container:
        """Build and configure a container.

        Returns:
            The configured container
        """
        container = Container(scope_context=self._scope_context)

        # Apply all registrations
        for register in self._registrations:
            register(container)

        # Apply all decorators after registrations
        for register_decorator in self._decorators:
            register_decorator(container)

        return container


# Global container instance
_container: Container | None = None
_container_lock = threading.RLock()


@lru_cache(maxsize=1)
def get_container() -> Container:
    """Get the global container instance.

    Returns:
        The global container instance
    """
    global _container
    with _container_lock:
        if _container is None:
            _container = Container()
    return _container


def set_container(container: Container) -> None:
    """Set the global container instance.

    Args:
        container: The container to set as the global instance
    """
    global _container
    with _container_lock:
        _container = container
        # Clear the lru_cache for get_container
        get_container.cache_clear()


def inject(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to inject dependencies into function arguments.

    This decorator automatically resolves dependencies for function arguments
    based on their type annotations.

    Example:
        ```python
        @inject
        def process_data(db: Database, logger: Logger):
            # db and logger are automatically injected
            db.execute("SELECT 1")
            logger.info("Data processed")
        ```

    Args:
        func: The function to inject dependencies into

    Returns:
        The decorated function
    """
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        container = get_container()

        # Skip parameters that already have values
        bound_args = sig.bind_partial(*args, **kwargs)

        # For each parameter that doesn't have a value, try to resolve it
        for name, param in sig.parameters.items():
            if name in bound_args.arguments:
                continue

            if param.annotation != inspect.Parameter.empty:
                try:
                    # Resolve the dependency
                    kwargs[name] = container.resolve(param.annotation)
                except Exception:
                    # If the parameter has a default value, skip it
                    if param.default != inspect.Parameter.empty:
                        continue
                    # Otherwise re-raise the exception
                    raise

        return func(*args, **kwargs)

    return wrapper
