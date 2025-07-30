# Publishing Guide

This project supports both automated publishing via GitHub Actions and manual
publishing via script.

## Setup Requirements

### 1. PyPI Trusted Publisher

Since this project uses trusted publishing (no credentials in GitHub), you need
to:

1. Go to your PyPI project settings
2. Navigate to "Publishing" → "Trusted Publishers"
3. Add a new GitHub publisher with:
    - Owner: Your GitHub username/org
    - Repository: frost
    - Workflow: publish.yml
    - Environment: (leave blank)

### 2. GitHub Repository Settings

Ensure your repository has:

-   Actions enabled
-   Write permissions for workflows (Settings → Actions → General → Workflow
    permissions)

## How It Works

### Automatic Version Bumping

The project uses `python-semantic-release` which automatically bumps versions
based on your commit messages:

-   **PATCH** (0.1.0 → 0.1.1): Bug fixes

    -   Commit format: `fix: description`
    -   Example: `fix: resolve import error in utils module`

-   **MINOR** (0.1.0 → 0.2.0): New features

    -   Commit format: `feat: description`
    -   Example: `feat: add new monad implementations`

-   **MAJOR** (0.1.0 → 1.0.0): Breaking changes
    -   Commit format: `feat!: description` or include `BREAKING CHANGE:` in
        commit body
    -   Example: `feat!: redesign API interface`

### Other Commit Types

-   `docs:` - Documentation changes (no version bump)
-   `style:` - Code style changes (no version bump)
-   `refactor:` - Code refactoring (no version bump)
-   `perf:` - Performance improvements (PATCH)
-   `test:` - Test changes (no version bump)
-   `build:` - Build system changes (no version bump)
-   `ci:` - CI configuration (no version bump)
-   `chore:` - Other changes (no version bump)

## Publishing Process

The workflow automatically:

1. **On push to main branch**:

    - Analyzes commits since last release
    - Determines version bump type
    - Updates version in `pyproject.toml`
    - Creates git tag
    - Creates GitHub release
    - Builds package with `uv build`
    - Publishes to PyPI using trusted publisher

2. **Manual trigger**:
    - Use "Actions" tab → "Publish to PyPI" → "Run workflow"

## Example Workflow

```bash
# Make changes
git add .

# Commit with conventional format
git commit -m "feat: add new error handling utilities"

# Push to main
git push origin main

# GitHub Actions will:
# - Bump version from 0.1.0 → 0.2.0
# - Create tag v0.2.0
# - Build and publish to PyPI
```

## Troubleshooting

1. **No version bump**: Check commit message format
2. **Publishing fails**: Verify trusted publisher is configured on PyPI
3. **Permission errors**: Check GitHub repository settings

## Manual Publishing with Auto-Versioning

### Prerequisites

1. **Install uv** (if not installed):

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. **Set PyPI Token** (if not already set):

    ```bash
    export PYPI_TOKEN="pypi-YOUR_TOKEN_HERE"
    ```

### Publishing Steps

1. **Make commits with conventional format**:

    ```bash
    git commit -m "feat: add new functionality"    # Minor version bump
    git commit -m "fix: resolve bug"               # Patch version bump
    git commit -m "feat!: breaking change"        # Major version bump
    ```

2. **Run Publish Script**:

    ```bash
    ./scripts/publish.sh
    ```

3. **Follow Prompts**:
    - Script analyzes commits and suggests version bump
    - Type `y` to proceed with auto-versioning
    - Script handles version bump, build, and upload

## Testing Locally

```bash
# Check what version would be bumped to
uv run --with python-semantic-release -- semantic-release version --print

# Build package locally
uv build
```

# 🚀 frostbound Package Deployment Guide

This guide covers deploying the `frostbound` package to PyPI using modern
UV-based workflows.

## 📋 Quick Start

### Manual Deployment (Recommended for first-time users)

1. **Set up tokens** (one-time setup):

    ```bash
    # Get tokens from:
    # TestPyPI: https://test.pypi.org/account/api-tokens/
    # PyPI: https://pypi.org/account/api-tokens/

    export TESTPYPI_TOKEN="pypi-your-testpypi-token-here"
    export PYPI_TOKEN="pypi-your-pypi-token-here"
    ```

2. **Deploy to TestPyPI first** (testing):

    ```bash
    make publish-test
    ```

3. **Verify TestPyPI installation**:

    ```bash
    make verify-install
    ```

4. **Deploy to PyPI** (production):
    ```bash
    make publish-prod
    ```

### Automated Deployment Script

Use the comprehensive deployment script for a guided experience:

```bash
# Full deployment (TestPyPI → PyPI)
./scripts/deploy.sh

# TestPyPI only
./scripts/deploy.sh --test-only

# PyPI only (skip TestPyPI)
./scripts/deploy.sh --prod-only

# Skip CI tests
./scripts/deploy.sh --skip-tests
```

## 🏗️ Build System

### Available Make Targets

| Command               | Description                                                    |
| --------------------- | -------------------------------------------------------------- |
| `make build`          | Build package for distribution                                 |
| `make publish-test`   | Publish to TestPyPI (requires `TESTPYPI_TOKEN`)                |
| `make publish-prod`   | Publish to PyPI (requires `PYPI_TOKEN`)                        |
| `make verify-install` | Verify package installation                                    |
| `make ci`             | Run full CI pipeline (format, lint, typecheck, test, coverage) |
| `make clean`          | Clean build artifacts                                          |

### Manual Build Process

```bash
# 1. Clean previous builds
make clean

# 2. Run CI pipeline
make ci

# 3. Build package
make build

# 4. Check artifacts
ls -la dist/
```

## 🔑 Authentication Setup

### PyPI Tokens (Recommended)

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Create TestPyPI account**: https://test.pypi.org/account/register/
3. **Generate tokens**:

    - PyPI: https://pypi.org/account/api-tokens/
    - TestPyPI: https://test.pypi.org/account/api-tokens/

4. **Set environment variables**:

    ```bash
    # In your shell profile (.bashrc, .zshrc, etc.)
    export PYPI_TOKEN="pypi-your-pypi-token-here"
    export TESTPYPI_TOKEN="pypi-your-testpypi-token-here"

    # Or use a .env file (not recommended for production)
    echo "PYPI_TOKEN=pypi-your-pypi-token-here" >> .env
    echo "TESTPYPI_TOKEN=pypi-your-testpypi-token-here" >> .env
    source .env
    ```

### GitHub Actions Secrets

For automated deployment via GitHub Actions:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add repository secrets:
    - `PYPI_TOKEN`: Your PyPI token
    - `TESTPYPI_TOKEN`: Your TestPyPI token

## 🤖 GitHub Actions CI/CD

### Automatic Deployment

The workflow automatically deploys on version tags:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### Manual Deployment

Trigger deployment manually from GitHub Actions:

1. Go to Actions → 📦 Publish Package
2. Click "Run workflow"
3. Choose environment: `testpypi`, `pypi`, or `both`
4. Optionally skip tests

### Trusted Publishing (Recommended)

For enhanced security, set up trusted publishing:

1. **PyPI Setup**:

    - Go to https://pypi.org/project/frostbound/
    - Go to "Publishing" → "Add a new publisher"
    - Add GitHub as publisher with your repo details

2. **TestPyPI Setup** (when supported):
    - Same process at https://test.pypi.org/project/frostbound/

With trusted publishing, no tokens are needed in GitHub Actions.

## 📦 Package Configuration

### pyproject.toml

The project is configured with:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "frostbound"
version = "0.1.0"  # Update this for new releases
# ... other metadata

# UV publishing indexes
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true

[[tool.uv.index]]
name = "pypi"
url = "https://pypi.org/simple/"
publish-url = "https://upload.pypi.org/legacy/"
default = true
```

## 🔄 Version Management

### Updating Version

1. **Update pyproject.toml**:

    ```toml
    version = "0.2.0"  # Increment version
    ```

2. **Commit changes**:

    ```bash
    git add pyproject.toml
    git commit -m "bump: version 0.2.0"
    ```

3. **Create and push tag**:
    ```bash
    git tag v0.2.0
    git push origin main
    git push origin v0.2.0
    ```

### Semantic Versioning

Follow [SemVer](https://semver.org/) guidelines:

-   `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
-   **MAJOR**: Breaking changes
-   **MINOR**: New features (backward compatible)
-   **PATCH**: Bug fixes (backward compatible)

## 🧪 Testing Deployment

### TestPyPI Workflow

Always test on TestPyPI first:

```bash
# 1. Deploy to TestPyPI
make publish-test

# 2. Test installation from TestPyPI
uv run --with frostbound \
  --index-url https://test.pypi.org/simple/ \
  --no-project \
  -- python -c "import frostbound; print('Success!')"

# 3. If everything works, deploy to PyPI
make publish-prod
```

### Local Testing

```bash
# Build and test locally
make build
python -m pip install dist/*.whl
python -c "import frostbound; print('Local installation works!')"
pip uninstall frostbound
```

## 🚨 Troubleshooting

### Common Issues

1. **"Package already exists"**:

    - Version already published
    - Increment version in `pyproject.toml`

2. **"Authentication failed"**:

    - Check token environment variables
    - Verify token hasn't expired
    - Ensure token has correct permissions

3. **"Build failed"**:

    - Run `make ci` to check for issues
    - Fix formatting, linting, or test errors

4. **"UV not found"**:
    - Install UV: https://docs.astral.sh/uv/getting-started/installation/

### Debug Commands

```bash
# Check UV version
uv --version

# Check build artifacts
ls -la dist/

# Check token environment variables (without revealing values)
echo "PYPI_TOKEN set: ${PYPI_TOKEN:+yes}"
echo "TESTPYPI_TOKEN set: ${TESTPYPI_TOKEN:+yes}"

# Dry run build
uv build --help
```

## 📚 Resources

-   **UV Documentation**: https://docs.astral.sh/uv/
-   **PyPI**: https://pypi.org/project/frostbound/
-   **TestPyPI**: https://test.pypi.org/project/frostbound/
-   **Python Packaging Guide**: https://packaging.python.org/
-   **Semantic Versioning**: https://semver.org/

## 🎯 Best Practices

1. **Always test on TestPyPI first**
2. **Run full CI pipeline before publishing**
3. **Use semantic versioning**
4. **Keep tokens secure** (use environment variables)
5. **Set up trusted publishing** for GitHub Actions
6. **Test package installation** after publishing
7. **Document breaking changes** in release notes

## 🤝 Contributing

When contributing to deployment configuration:

1. Test changes on TestPyPI first
2. Update this documentation
3. Test both manual and automated workflows
4. Verify GitHub Actions work correctly

---

**Need help?** Open an issue or check the troubleshooting section above.
