"""Mock services for testing the configuration system."""

from typing import Optional


class Database:
    """Mock database connection."""

    def __init__(self, host: str, port: int = 5432, username: str = "admin",
                 password: Optional[str] = None, pool_size: int = 10):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pool_size = pool_size

    def __repr__(self):
        return f"Database(host={self.host!r}, port={self.port}, username={self.username!r}, pool_size={self.pool_size})"


class RedisCache:
    """Mock Redis cache."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
                 ttl: int = 3600, max_connections: int = 50):
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl
        self.max_connections = max_connections

    def __repr__(self):
        return f"RedisCache(host={self.host!r}, port={self.port}, db={self.db}, ttl={self.ttl})"


class EmailService:
    """Mock email service."""

    def __init__(self, smtp_host: str, smtp_port: int = 587,
                 username: Optional[str] = None, password: Optional[str] = None,
                 use_tls: bool = True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def __repr__(self):
        return f"EmailService(host={self.smtp_host!r}, port={self.smtp_port}, tls={self.use_tls})"


class APIClient:
    """Mock API client with positional args."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def __repr__(self):
        key_preview = f"{self.api_key[:8]}..." if len(self.api_key) > 8 else self.api_key
        return f"APIClient(url={self.base_url!r}, key={key_preview!r}, timeout={self.timeout})"


class Logger:
    """Mock logger for factory pattern testing."""

    def __init__(self, name: str, level: str = "INFO", format: str = "json"):
        self.name = name
        self.level = level
        self.format = format

    def __repr__(self):
        return f"Logger(name={self.name!r}, level={self.level}, format={self.format})"


class Service:
    """Mock service that depends on other services."""

    def __init__(self, name: str, database: Database, cache: RedisCache,
                 logger: Optional[Logger] = None):
        self.name = name
        self.database = database
        self.cache = cache
        self.logger = logger or Logger(name=f"{name}_logger")

    def __repr__(self):
        return f"Service(name={self.name!r}, db={self.database}, cache={self.cache})"
