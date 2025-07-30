# ConfigLoader Examples

This directory contains comprehensive examples demonstrating the various features and use cases of frostbound's `ConfigLoader`.

## 📁 Environment Files

The examples use the following pre-created environment files:

- `.env` - Default environment file with basic settings
- `.env.dev` - Development environment configuration
- `.env.prod` - Production environment configuration
- `config.yaml` - YAML configuration for override scenarios

## 📚 Examples Overview

### 01. Basic .env File Loading
**File:** `01_basic_env_loading.py`

Demonstrates the simplest case of loading configuration from a `.env` file using Pydantic's native env_file support.

```bash
python 01_basic_env_loading.py
```

**Key concepts:**
- Basic Pydantic env_file configuration
- How ConfigLoader detects and respects env_file settings

### 02. Different Environment File Names
**File:** `02_different_env_files.py`

Shows how to load from different environment files like `.env.dev`, `.env.prod`.

```bash
python 02_different_env_files.py
```

**Key concepts:**
- Using different env file names
- Environment-specific configurations
- Dynamic environment selection

### 03. Multiple Environment Files
**File:** `03_multiple_env_files.py`

Demonstrates loading from multiple `.env` files with precedence handling.

```bash
python 03_multiple_env_files.py
```

**Key concepts:**
- Loading multiple env files in order
- File precedence (later files override earlier)
- Layered configuration approach

### 04. YAML Override Scenarios
**File:** `04_yaml_override.py`

Shows how YAML configuration overrides `.env` files in hybrid mode.

```bash
python 04_yaml_override.py
```

**Key concepts:**
- YAML as override layer
- Deep merge behavior with `_merge_config_data`
- Nested configuration handling

### 05. No Override Scenarios
**File:** `05_no_override.py`

Demonstrates loading from single sources without overrides.

```bash
python 05_no_override.py
```

**Key concepts:**
- Loading from individual sources
- Graceful handling of missing files
- Default value behavior

### 06. Precedence Demonstration
**File:** `06_precedence_demo.py`

Shows the order of precedence for different configuration sources.

```bash
python 06_precedence_demo.py
```

**Key concepts:**
- Precedence in Pydantic-native mode
- Precedence in source composition mode
- Environment variable priority

### 07. Source Composition vs Pydantic-native Mode
**File:** `07_composition_vs_native.py`

Demonstrates the differences between frostbound's source composition and Pydantic's native env_file handling.

```bash
python 07_composition_vs_native.py
```

**Key concepts:**
- When to use each mode
- Feature comparison
- Forcing composition mode

## 🚀 Running the Examples

1. Install dependencies:
```bash
pip install frostbound pydantic-settings rich
```

2. Navigate to the examples directory:
```bash
cd examples/configloader_scenarios
```

3. Run any example:
```bash
python 01_basic_env_loading.py
```

**Important:** Always run the examples from the `examples/configloader_scenarios` directory to ensure the env files are found correctly. The examples use absolute paths based on the script location to handle different working directories.

## 📋 Quick Reference

### Pydantic-native Mode (Automatic)
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    name: str = "default"

# ConfigLoader detects env_file and uses Pydantic's loading
settings = ConfigLoader.from_yaml_with_env(Settings, Path("config.yaml"))
```

### Source Composition Mode (Explicit)
```python
class Settings(BaseSettings):
    name: str = "default"

# No env_file configured, uses frostbound sources
settings = ConfigLoader.from_yaml_with_env(
    Settings,
    Path("config.yaml"),
    env_prefix="APP_"
)
```

### Force Composition Mode
```python
# Override automatic detection
settings = ConfigLoader.from_yaml_with_env(
    Settings,
    Path("config.yaml"),
    env_prefix="APP_",
    respect_pydantic_env_file=False
)
```

## 🔄 Precedence Rules

### Pydantic-native Mode
1. Class defaults (lowest)
2. .env file(s)
3. YAML override (highest)

### Source Composition Mode
1. Class defaults (lowest)
2. YAML file
3. Environment variables (highest)

## 💡 Tips

- Use Pydantic-native mode when you want to leverage Pydantic's env_file features
- Use source composition mode for explicit control over configuration sources
- The `_merge_config_data` function ensures nested configurations are properly merged
- Always test your configuration precedence to ensure expected behavior