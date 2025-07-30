# Claude Instructions for EVO Project

## Project Overview
EVO is a Python CLI tool that provides an interface for the Claude Code AI coding assistant. It manages both global user settings and project-specific settings, with support for isolated development environments, usage analytics, and session tracking.

## Key Commands

### `evo init`
Initialize project configuration and devcontainer support. This creates a `.evo` directory with default configuration.

### `evo dev [branch-name]`
Create a Git worktree and launch Claude Code. Supports multiple runtime options:
- `--runtime local` (default): Run directly on your machine
- `--runtime isolated`: Run in a devcontainer with network isolation
- `--runtime remote`: Cloud-based development (waitlist)

### `evo usage`
Display Claude usage statistics and costs:
- Reads from `~/.claude` directory JSONL files
- Calculates token costs for different Claude models
- Supports custom time ranges with `--days` flag (default: 30)
- Shows usage by model with cost breakdowns

### `evo sessions`
Display Claude conversation sessions:
- Lists all sessions from `~/.claude` directory
- Automatically detects and filters by current project
- Shows session dates and project associations

## Settings Architecture

### Global Settings (`Settings` class)
- Located at `~/.config/evo/config.json`
- Stores:
  - `default_cli`: User's default CLI tool preference
  - `completion_installed`: Tracks if shell completion is set up
- Handles CLI tool detection and selection

### Project Settings (`ProjectSettings` class)
- Located at `<project_root>/.evo/config.json`
- Stores:
  - `worktree_files`: Untracked files to copy to new worktrees
  - `disable_firewall`: Disable network isolation in devcontainers
  - `default_cli`: Project-specific CLI tool override

### Local Settings Folder (.evo)
The `.evo` directory is created in the project root and contains:
- `config.json`: Stores all project-specific configuration
- This allows each project to have its own specific commands without affecting global settings

## Features

### Worktree Files
Git worktrees don't include untracked files by default. The "worktree files" feature allows you to specify which untracked files should be automatically copied to new worktrees when using `evo dev`. Common examples:
- `.env` - Environment variables
- `.env.local` - Local environment overrides
- `.mcp` - MCP configuration
- Any other untracked configuration files

Default worktree files: `.env`, `.env.local`, `.mcp`

### Devcontainer Support
EVO supports running Claude in isolated devcontainers:
- Network isolation by default (can be disabled with `disable_firewall`)
- Automatic volume mounting for authentication persistence
- Special handling for Claude with `--dangerously-skip-permissions` flag
- Requires Docker to be installed and running

### Usage Analytics
The `evo usage` command provides detailed analytics:
- Token usage tracking for all Claude models
- Cost calculation based on current pricing
- Support for cache tokens (creation and read)
- Deduplication of entries
- Models supported: Claude 3 Opus, Claude 3.5 Sonnet, Opus 4, Sonnet 4

### Auto-completion
Shell completion is automatically installed on first run. Supports bash, zsh, and fish shells.

## Installation

```bash
# Install from PyPI
pip install evo-cli

# Or install with uv
uv pip install evo-cli
```

## Testing Instructions

### Running Tests
Always use `uv` to run tests:
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_settings.py

# Run specific test class
uv run pytest tests/test_settings.py::TestProjectSettings

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=evo
```

### Test Structure
- Tests are organized by functionality:
  - `test_settings.py`: Global and project settings
  - `test_worktree.py`: Worktree management
  - `test_init.py`: Initialization logic
  - `test_dev.py`: Dev command functionality
  - `test_usage.py`: Usage analytics
  - `test_sessions.py`: Session management
- Uses pytest fixtures for temporary directories and mock objects
- All file operations use temporary paths to avoid side effects

## Code Formatting

### Using Ruff
Always use `uv` to run ruff for formatting and linting:
```bash
# Format code
uv run ruff format .

# Check code style
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Type Checking
Use ty for type checking:
```bash
uv run ty check
```

## Development Workflow

1. **Before making changes**: Run tests to ensure starting from a clean state
2. **After writing code**: 
   - Run `uv run ruff format .` to format
   - Run `uv run ruff check .` to check for style issues
   - Run `uv run ty check` to check types
   - Run `uv run pytest` to ensure all tests pass
3. **When adding new features**: Write tests first (TDD approach recommended)

## Important Patterns

### File Path Handling
- Always use `pathlib.Path` for file operations
- Project settings use absolute paths internally
- Config directories are created with `parents=True, exist_ok=True`

### JSON Configuration
- All configs use 2-space indentation for readability
- Empty configs return `{}` rather than raising errors
- Settings methods handle missing keys gracefully (return None or empty list/dict)

### Subprocess Handling
- Uses `subprocess.Popen` for proper stdin/stdout/stderr handling
- Handles both synchronous execution and streaming output
- Special handling for Claude CLI permissions

### Testing Best Practices
- Use fixtures for temporary directories
- Mock external dependencies (like `shutil.which` for CLI detection)
- Test both positive and negative cases
- Verify file persistence across instance creation
- Mock subprocess calls for external tools

## Common Commands Summary
```bash
# User commands
evo init                        # Initialize project
evo dev feature-branch          # Create worktree and launch Claude
evo dev --runtime isolated      # Launch in devcontainer
evo usage                       # Show usage stats
evo usage --days 7              # Show last week's usage
evo sessions                    # Show conversation sessions

# Development cycle
uv run pytest                   # Run tests
uv run ruff format .            # Format code
uv run ruff check .             # Check style
uv run ty check                 # Check types
uv run pytest --cov=evo         # Check test coverage
```

## Configuration Examples

### Project Configuration (`.evo/config.json`)
```json
{
  "worktree_files": [".env", ".env.local", ".mcp", "config/secrets.json"],
  "disable_firewall": false,
  "default_cli": "claude"
}
```

### Global Configuration (`~/.config/evo/config.json`)
```json
{
  "default_cli": "claude",
  "completion_installed": true
}
```

## Model Pricing (as of last update)
- Claude 3 Opus: $15/$75 per million tokens (input/output)
- Claude 3.5 Sonnet: $3/$15 per million tokens
- Opus 4: $15/$75 per million tokens
- Sonnet 4: $3/$15 per million tokens
- Cache creation: 25% of input cost
- Cache read: 10% of input cost

## Notes for Future Development
- The `agents` directory exists but is currently empty (planned feature)
- Runtime options are extensible - new environments can be added
- All settings are stored in JSON for simplicity and portability
- The `.evo` directory follows conventions of other dev tools (`.git`, `.vscode`)
- Settings persistence is automatic - no explicit save() method needed
- Branch name validation prevents invalid Git branch names
- Worktrees are created as siblings to the main repository