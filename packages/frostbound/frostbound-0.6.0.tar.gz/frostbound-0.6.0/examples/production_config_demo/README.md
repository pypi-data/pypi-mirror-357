# Production Configuration Demo

This example demonstrates a production-ready configuration system using `BaseSettingsWithInstantiation` from pydanticonf.

## Features Demonstrated

- ✅ **Type-safe configuration** with `DynamicConfig[T]`
- ✅ **Multi-environment support** (dev, prod, staging, etc.)
- ✅ **Secure secrets management** via environment variables
- ✅ **Configuration layering** with proper precedence
- ✅ **Automatic object instantiation** from configuration
- ✅ **YAML + .env file support**
- ✅ **Nested configuration** with environment variable overrides

## File Structure

```
production_config_demo/
├── config/
│   ├── base.yaml          # Base configuration (all environments)
│   ├── dev.yaml           # Development overrides
│   └── prod.yaml          # Production overrides
├── .env.dev               # Development secrets
├── .env.prod              # Production secrets (example values)
├── .env.example           # Template for developers
├── models.py              # Component classes (Database, Redis, etc.)
├── config_models.py       # Type-safe DynamicConfig models
├── settings.py            # Main settings with BaseSettingsWithInstantiation
└── main.py                # Demo application
```

## Quick Start

1. **Run in development mode** (default):
   ```bash
   python main.py
   ```

2. **Run in production mode**:
   ```bash
   ENVIRONMENT=prod python main.py
   ```

3. **Create your own environment**:
   ```bash
   # Copy the template
   cp .env.example .env.staging
   
   # Create environment-specific config
   cp config/dev.yaml config/staging.yaml
   
   # Run with your environment
   ENVIRONMENT=staging python main.py
   ```

## Configuration Precedence

Settings are loaded in this order (highest to lowest priority):

1. **Environment variables** (e.g., `APP_DATABASE__PASSWORD`)
2. **.env file** (e.g., `.env.prod`)
3. **Environment YAML** (e.g., `prod.yaml`)
4. **Base YAML** (`base.yaml`)
5. **Python defaults** (in settings.py)

## Environment Variables

Nested configuration uses double underscores (`__`):

- `APP_DATABASE__PASSWORD` → `database.password`
- `APP_REDIS__HOST` → `redis.host`
- `APP_STORAGE__ACCESS_KEY_ID` → `storage.access_key_id`

## Security Best Practices

1. **Never commit .env files** with real secrets
2. **Use .env.example** as a template
3. **Store production secrets** in a secure system:
   - AWS Secrets Manager
   - Kubernetes Secrets
   - HashiCorp Vault
   - CI/CD secret management

4. **Validate required secrets** in production (see `validate_production_config`)

## Type Safety

All configurations are type-safe with full IDE support:

```python
# Define type-safe config
class DatabaseConfig(DynamicConfig[Database]):
    host: str = "localhost"
    port: int = 5432
    password: Optional[str] = None  # From environment

# Use in settings
class AppSettings(BaseSettingsWithInstantiation):
    database: DatabaseConfig = DatabaseConfig(
        _target_="path.to.Database"
    )

# Get instantiated object with proper types
settings = AppSettings()
settings.database.connect()  # Full IDE autocomplete!
```

## Adding New Services

1. Create the service class in `models.py`
2. Create a `DynamicConfig` class in `config_models.py`
3. Add to `settings.py` with proper type
4. Add configuration to YAML files
5. Add secrets to `.env.example`

## Production Deployment

1. Set environment variables from your secret management system
2. Mount environment-specific YAML if needed
3. Set `ENVIRONMENT` variable
4. Validate configuration on startup

Example Kubernetes deployment:

```yaml
env:
  - name: ENVIRONMENT
    value: "prod"
  - name: APP_DATABASE__PASSWORD
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: db-password
```

## Testing

Create test-specific configuration:

```python
# tests/conftest.py
os.environ["ENVIRONMENT"] = "test"
os.environ["APP_DATABASE__PASSWORD"] = "test_password"

# Your tests get properly configured instances
def test_database_connection(settings):
    assert settings.database.connect() is not None
```