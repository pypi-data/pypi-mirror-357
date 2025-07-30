"""Component models representing actual services and connections.

These are the real objects that will be instantiated from configuration.
They represent databases, caches, storage services, etc.
"""

import time
from typing import Any, Optional


class Database:
    """PostgreSQL database connection."""

    def __init__(
        self,
        host: str,
        port: int = 5432,
        database: str = "app",
        username: str = "postgres",
        password: Optional[str] = None,
        pool_size: int = 10,
        timeout: int = 30,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.pool_size = pool_size
        self.timeout = timeout
        self._connected = False

    def connect(self) -> None:
        """Simulate database connection."""
        print(f"🗄️  Connecting to PostgreSQL at {self.host}:{self.port}/{self.database}")
        print(f"   Username: {self.username}")
        print(f"   Password: {'***' if self.password else 'None'}")
        print(f"   Pool size: {self.pool_size}")
        time.sleep(0.1)  # Simulate connection time
        self._connected = True
        print("✅ Database connected!")

    def query(self, sql: str) -> list[dict[str, str]]:
        """Simulate database query."""
        if not self._connected:
            self.connect()
        print(f"🔍 Executing SQL: {sql}")
        return [{"id": 1, "name": "Sample"}]


class RedisCache:
    """Redis cache for fast data access."""

    def __init__(
        self,
        host: str,
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ssl: bool = False,
        cluster_mode: bool = False,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.ssl = ssl
        self.cluster_mode = cluster_mode
        self._connected = False

    def connect(self) -> None:
        """Connect to Redis."""
        print(f"🔴 Connecting to Redis at {self.host}:{self.port} (db={self.db})")
        print(f"   SSL: {self.ssl}")
        print(f"   Cluster mode: {self.cluster_mode}")
        print(f"   Auth: {'Enabled' if self.password else 'Disabled'}")
        self._connected = True
        print("✅ Redis connected!")

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self._connected:
            self.connect()
        print(f"📖 Redis GET {key}")
        return f"cached_value_for_{key}"

    def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set value in cache."""
        if not self._connected:
            self.connect()
        print(f"📝 Redis SET {key} = {value} (TTL: {ttl}s)")


class S3Storage:
    """AWS S3 storage service."""

    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,  # For S3-compatible services
        use_ssl: bool = True,
    ):
        self.bucket = bucket
        self.region = region
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.endpoint_url = endpoint_url
        self.use_ssl = use_ssl

    def upload(self, key: str, data: bytes) -> str:
        """Upload data to S3."""
        print(f"☁️  Uploading to S3 bucket '{self.bucket}'")
        print(f"   Region: {self.region}")
        print(f"   Key: {key}")
        print(f"   Size: {len(data)} bytes")
        print(f"   Endpoint: {self.endpoint_url or 'AWS'}")
        return f"s3://{self.bucket}/{key}"

    def download(self, key: str) -> bytes:
        """Download data from S3."""
        print(f"⬇️  Downloading from S3: {key}")
        return b"sample data"


class APIClient:
    """External API client with authentication."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        timeout: int = 30,
        retry_count: int = 3,
        rate_limit: int = 100,  # requests per minute
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.retry_count = retry_count
        self.rate_limit = rate_limit

    def request(self, endpoint: str, method: str = "GET", data: Optional[dict[str, str]] = None) -> dict[str, str]:
        """Make API request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        print(f"🌐 API {method} {url}")
        print(f"   Timeout: {self.timeout}s")
        print(f"   Retries: {self.retry_count}")
        print(f"   Rate limit: {self.rate_limit}/min")
        print(f"   Auth: {'API Key' if self.api_key else 'None'}")
        return {"status": "success", "data": data or {}}  # type: ignore


class Logger:
    """Application logger with different levels."""

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        format: str = "json",
        output: str = "stdout",
        buffer_size: int = 1000,
    ):
        self.name = name
        self.level = level
        self.format = format
        self.output = output
        self.buffer_size = buffer_size
        self._setup()

    def _setup(self):
        """Setup logger configuration."""
        print(f"📝 Setting up logger '{self.name}'")
        print(f"   Level: {self.level}")
        print(f"   Format: {self.format}")
        print(f"   Output: {self.output}")

    def log(self, level: str, message: str, **kwargs: Any):
        """Log a message."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.format == "json":
            print(f'{{"time": "{timestamp}", "level": "{level}", "logger": "{self.name}", "msg": "{message}"}}')
        else:
            print(f"[{timestamp}] {level} [{self.name}] {message}")

    def info(self, message: str, **kwargs: Any):
        self.log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs: Any):
        self.log("ERROR", message, **kwargs)


class SentryMonitoring:
    """Sentry error monitoring service."""

    def __init__(
        self,
        dsn: Optional[str] = None,
        environment: str = "development",
        release: Optional[str] = None,
        sample_rate: float = 1.0,
        traces_sample_rate: float = 0.1,
        debug: bool = False,
    ):
        self.dsn = dsn
        self.environment = environment
        self.release = release
        self.sample_rate = sample_rate
        self.traces_sample_rate = traces_sample_rate
        self.debug = debug
        self._initialized = False

    def initialize(self):
        """Initialize Sentry SDK."""
        if self.dsn:
            print("🚨 Initializing Sentry monitoring")
            print(f"   Environment: {self.environment}")
            print(f"   Release: {self.release or 'latest'}")
            print(f"   Sample rate: {self.sample_rate * 100}%")
            print(f"   Traces: {self.traces_sample_rate * 100}%")
            self._initialized = True
            print("✅ Sentry initialized!")
        else:
            print("⚠️  Sentry DSN not provided, monitoring disabled")

    def capture_exception(self, error: Exception):
        """Capture an exception."""
        if self._initialized:
            print(f"🚨 Sentry: Captured {type(error).__name__}: {error}")
