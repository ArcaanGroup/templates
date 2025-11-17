# PDM Setup and Implementation Details

## Overview

This project uses **PDM (Python Dependency Manager)** as the modern dependency management tool. PDM is a fast, reliable Python package manager that uses PEP 517 build backend and PEP 621 project metadata.

## Why PDM?

- ✅ **Fast**: Built with Rust, significantly faster than pip
- ✅ **Modern**: Uses PEP 621 standard for project metadata
- ✅ **Reliable**: Deterministic dependency resolution with lock file
- ✅ **Virtual Environment Management**: Automatic venv creation and management
- ✅ **PEP 517 Compatible**: Works with modern Python packaging standards
- ✅ **No Global Installation**: Dependencies are isolated per project

## Installation

### Prerequisites

- Python 3.12+ installed
- PDM installed globally (if not already):

```bash
pip install pdm
# or
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
```

### Project Setup

1. **Initialize PDM** (already done):
   ```bash
   pdm install
   ```

2. **Verify installation**:
   ```bash
   pdm run python -c "import fastapi; print('FastAPI installed!')"
   ```

## Project Configuration

### pyproject.toml Structure

The `pyproject.toml` file contains all project configuration:

#### 1. Project Metadata (`[project]`)

```toml
[project]
name = "fastapi-enterprise-template"
version = "0.1.0"
description = "Enterprise-ready FastAPI template with Clean Architecture and DDD"
requires-python = ">=3.12"
```

- **name**: Package name
- **version**: Project version
- **requires-python**: Minimum Python version (3.12)

#### 2. Dependencies

**Production Dependencies:**
- `fastapi>=0.116.1` - Web framework
- `uvicorn[standard]>=0.35.0` - ASGI server
- `sqlalchemy>=2.0.43` - ORM
- `asyncpg>=0.30.0` - PostgreSQL async driver
- `aiosqlite>=0.21.0` - SQLite async driver
- `alembic>=1.16.5` - Database migrations
- `pydantic>=2.11.9` - Data validation
- `python-jose[cryptography]>=3.5.0` - JWT handling
- `fastapi-pagination>=0.14.1` - Pagination support
- `prometheus-fastapi-instrumentator>=7.1.0` - Metrics
- `sentry-sdk>=1.4` - Error tracking
- And more...

**Development Dependencies** (`[project.optional-dependencies.dev]`):
- `pytest>=8.4.2` - Testing framework
- `pytest-asyncio>=1.2.0` - Async test support
- `black>=25.1.0` - Code formatter
- `ruff>=0.13.0` - Fast linter
- `mypy>=1.18.1` - Type checker
- `pre-commit>=3.5.0` - Git hooks

#### 3. Tool Configurations

**Black (Code Formatter):**
```toml
[tool.black]
line-length = 100
target-version = ['py312']
```

**Ruff (Linter):**
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "W", "F", "I", "B", "C4", "UP"]
```

**MyPy (Type Checker):**
```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
disallow_untyped_defs = false
```

**Pytest:**
```toml
[tool.pytest.ini_options]
testpaths = ["app/tests"]
asyncio_mode = "auto"
addopts = ["--cov=app", "--cov-report=term-missing"]
```

## PDM Configuration Files

### .pdm-python

Specifies the Python interpreter to use:
```
/home/mohammad/Documents/Projects/Arcaan/Templates/fastapi_template/.venv/bin/python
```

This points to the virtual environment Python interpreter.

### .python-version

For tools like pyenv:
```
3.12
```

### pdm.lock

Auto-generated lock file that pins exact versions of all dependencies and their transitive dependencies. This ensures reproducible builds.

**Important**: Commit `pdm.lock` to version control for reproducible installations.

## Common PDM Commands

### Dependency Management

```bash
# Install all dependencies (production + dev)
pdm install

# Install only production dependencies
pdm install --prod

# Install with specific group
pdm install -G dev

# Add a new dependency
pdm add package-name

# Add a development dependency
pdm add -dG dev package-name

# Add with version constraint
pdm add "fastapi>=0.116.0"

# Remove a dependency
pdm remove package-name

# Update dependencies
pdm update

# Update specific package
pdm update fastapi

# Show installed packages
pdm list

# Show dependency tree
pdm tree
```

### Running Commands

```bash
# Run any command in PDM environment
pdm run <command>

# Examples:
pdm run uvicorn app.main:app --reload
pdm run pytest
pdm run black .
pdm run mypy app
```

### Virtual Environment

```bash
# Show venv location
pdm venv info

# Create venv in project
pdm venv create

# Activate venv (if needed)
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows

# Remove venv
pdm venv remove
```

### Project Information

```bash
# Show project info
pdm info

# Show Python version
pdm python --version

# Show PDM version
pdm --version
```

## Makefile Integration

For convenience, common PDM commands are wrapped in Makefile targets:

```bash
make install       # Install dependencies
make install-dev   # Install with dev dependencies
make run           # Run development server
make test          # Run tests
make lint          # Run linters
make format        # Format code
make type-check    # Type checking
```

## Workflow Examples

### Initial Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd fastapi_template

# 2. Install dependencies
pdm install

# 3. Copy environment file
cp .env.example .env

# 4. Run application
pdm run uvicorn app.main:app --reload
```

### Adding a New Dependency

```bash
# Add production dependency
pdm add redis

# Add development dependency
pdm add -dG dev pytest-xdist

# Update lock file is automatic
git add pdm.lock pyproject.toml
```

### Development Workflow

```bash
# Start development
pdm install

# Run tests
pdm run pytest

# Format code
pdm run black . && pdm run isort .

# Lint code
pdm run ruff check .

# Type check
pdm run mypy app

# Run server
pdm run uvicorn app.main:app --reload
```

## Environment Variables

PDM respects environment variables for configuration:

- `PDM_PYPI_URL`: Custom PyPI index URL
- `PDM_USE_VENV`: Force venv usage (default: auto)
- `PDM_VENV_LOCATION`: Custom venv location

## Integration with IDEs

### VS Code

1. Install Python extension
2. Select interpreter: `.venv/bin/python`
3. PDM commands work automatically

### PyCharm

1. Settings → Project → Python Interpreter
2. Add → Existing Environment
3. Select `.venv/bin/python`

## Best Practices

### 1. Lock File Management

- ✅ **Commit `pdm.lock`** to version control
- ✅ **Update lock file** when adding/removing dependencies
- ✅ **Use exact versions** in production deployments

### 2. Dependency Groups

- Use `dev` group for development-only dependencies
- Use `test` group for testing dependencies (if needed)
- Keep production dependencies minimal

### 3. Version Constraints

```toml
# Good: Allow patch updates
"fastapi>=0.116.0,<0.117.0"

# Good: Allow minor updates
"fastapi>=0.116.0,<0.120.0"

# Avoid: Too loose
"fastapi>=0.116.0"

# Avoid: Too strict (unless necessary)
"fastapi==0.116.1"
```

### 4. Virtual Environment

- Let PDM manage venv automatically
- Don't activate venv manually (use `pdm run`)
- Venv location: `.venv/` in project root

### 5. CI/CD Integration

```yaml
# GitHub Actions example
- name: Install PDM
  run: pip install pdm

- name: Install dependencies
  run: pdm install

- name: Run tests
  run: pdm run pytest
```

## Troubleshooting

### Issue: "PDM not found"

```bash
# Install PDM globally
pip install pdm

# Or use pipx (recommended)
pipx install pdm
```

### Issue: "Python version mismatch"

```bash
# Check Python version
pdm python --version

# Update .pdm-python file
echo "3.12" > .pdm-python

# Or specify in pyproject.toml
requires-python = ">=3.12"
```

### Issue: "Dependencies not installing"

```bash
# Clear cache and reinstall
pdm cache clear
pdm install --force

# Check for conflicts
pdm tree
```

### Issue: "Lock file out of sync"

```bash
# Update lock file
pdm lock

# Reinstall from lock file
pdm sync
```

## Migration from Other Tools

### From pip + requirements.txt

```bash
# Generate pyproject.toml from requirements.txt
pdm import requirements.txt

# Or manually add dependencies
pdm add -r requirements.txt
```

### From Poetry

```bash
# Import from pyproject.toml (Poetry format)
pdm import poetry

# Or convert manually
```

### From pipenv

```bash
# Import from Pipfile
pdm import pipfile
```

## Comparison with Other Tools

| Feature | PDM | pip | Poetry | pipenv |
|---------|-----|-----|--------|--------|
| Speed | ⚡ Very Fast | 🐌 Slow | 🐌 Slow | 🐌 Slow |
| Lock File | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| PEP 621 | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Virtual Env | ✅ Auto | ❌ Manual | ✅ Auto | ✅ Auto |
| Dependency Groups | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| Workspace Support | ✅ Yes | ❌ No | ✅ Yes | ❌ No |

## Additional Resources

- **PDM Documentation**: https://pdm.fming.dev/
- **PEP 621**: https://peps.python.org/pep-0621/
- **PEP 517**: https://peps.python.org/pep-0517/
- **Project Repository**: https://github.com/pdm-project/pdm

## Summary

PDM provides a modern, fast, and reliable way to manage Python dependencies for this FastAPI enterprise template. With proper configuration in `pyproject.toml`, automatic virtual environment management, and comprehensive tooling support, PDM ensures reproducible builds and smooth development workflows.

Key benefits:
- ✅ Fast dependency resolution
- ✅ Automatic virtual environment management
- ✅ PEP 621 compliant
- ✅ Lock file for reproducibility
- ✅ Integrated with development tools
- ✅ Simple and intuitive commands

The project is fully configured and ready to use with PDM!

