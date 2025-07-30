# PyPI Publishing and Installation Instructions

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Generate an API token at https://pypi.org/manage/account/token/
3. Install build tools: `pip install build twine`

## Publishing to PyPI

### First-time setup

1. Create `~/.pypirc` file:
```ini
[pypi]
username = __token__
password = <your-token-here>
```

### Building and uploading

1. Clean previous builds:
```bash
rm -rf dist/ build/ *.egg-info/
```

2. Build the package:
```bash
python -m build
```

3. Upload to PyPI:
```bash
python -m twine upload dist/*
```

### Automated publishing (using uv)

```bash
# Build with uv
uv build

# Upload with twine
uv run twine upload dist/*
```

## Installation Instructions

### Install using uv (recommended)

```bash
# Install globally
uv tool install evo-cli

# Or install in a project
uv add evo-cli
```

### Install using pip

```bash
# Install globally
pip install evo-cli

# Or install in a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install evo-cli
```

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/evo.git
cd evo

# Install with uv
uv pip install -e .

# Or install with pip
pip install -e .
```

## Updating the Package

### Update using uv

```bash
# Update global tool
uv tool upgrade evo-cli

# Or update in a project
uv add --upgrade evo-cli
```

### Update using pip

```bash
# Update to latest version
pip install --upgrade evo-cli

# Update to specific version
pip install evo-cli==0.2.0
```

## Version Management

Before publishing a new version:

1. Update version in `pyproject.toml`
2. Commit changes: `git commit -am "Bump version to X.Y.Z"`
3. Tag the release: `git tag vX.Y.Z`
4. Push changes: `git push && git push --tags`

## Testing Before Publishing

### Test on TestPyPI first

1. Register at https://test.pypi.org/
2. Upload to TestPyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

3. Install from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ evo-cli
```

## Common Issues

### Name conflicts
If `evo-cli` is taken, consider alternatives like:
- `evo-worktree`
- `evo-git-cli`
- `evo-dev-cli`

### Token authentication
Always use API tokens instead of passwords. Create project-specific tokens for better security.

### Build errors
Ensure you have the latest versions:
```bash
pip install --upgrade build twine
```