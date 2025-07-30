# Evo

A powerful CLI tool for managing Git worktrees with integrated AI coding assistant support. Evo streamlines development workflows by creating isolated Git worktrees and launching them with Claude or other AI assistants.

## Features

- **Smart Git Worktree Management**: Create and manage worktrees with a single command
- **AI Assistant Integration**: Built-in support for Claude and other coding assistants
- **Isolated Development**: Optional devcontainer support for secure, isolated environments
- **Project Configuration**: Define build, test, and lint commands per project
- **Usage Analytics**: Track token usage and costs for AI assistants
- **Session Management**: View and filter coding sessions by project
- **Automatic File Sync**: Copy untracked files (like .env) to new worktrees

## Installation

### From PyPI

```bash
pip install evo
```

### From Source

```bash
git clone https://github.com/yourusername/evo.git
cd evo
pip install -e .
```

### Requirements

- Python 3.12+
- Git
- Claude CLI (or other supported AI assistant)
- For isolated runtime:
  - Docker
  - devcontainer CLI (`npm install -g @devcontainers/cli`)

## Quick Start

1. **Initialize your project**:
```bash
evo init
```

This creates:
- `.evo/config.json` - Project-specific configuration
- `.devcontainer/` - Devcontainer support files

2. **Create a development environment**:
```bash
evo dev feature/new-feature
```

3. **Launch with a specific task**:
```bash
evo dev fix/bug-123 -p "Fix the authentication timeout issue"
```

## Commands

### `evo init`

Initialize project configuration and devcontainer support.

```bash
evo init
```

Creates the `.evo/config.json` file with default settings and sets up devcontainer configuration for isolated development.

### `evo dev`

Create a Git worktree and launch it with an AI assistant.

```bash
evo dev <branch-name> [OPTIONS]
```

**Arguments:**
- `branch_name` - Name of the branch to create worktree for

**Options:**
- `-p, --prompt` - Initial prompt to pass to the AI assistant
- `-r, --runtime` - Development runtime: `local` (default), `isolated`, or `remote`

**Examples:**
```bash
# Basic usage
evo dev feature/new-api

# With specific task
evo dev fix/memory-leak -p "Investigate and fix the memory leak in the worker process"

# Using isolated devcontainer
evo dev feature/secure-feature --runtime isolated
```

**Behavior:**
1. Creates a worktree at `../{repo-name}-{branch-name}`
2. Creates new branch if it doesn't exist
3. Copies configured worktree files (e.g., .env)
4. Runs configured build commands
5. Launches AI assistant with test/lint commands in prompt

### `evo usage`

Display AI assistant usage statistics for the last N days.

```bash
evo usage [OPTIONS]
```

**Options:**
- `-d, --days` - Number of days to show (default: 30)

**Examples:**
```bash
# Last 30 days
evo usage

# Last week
evo usage -d 7

# Last quarter
evo usage --days 90
```

Shows:
- Daily token usage by model
- Estimated costs
- Total tokens and costs for the period

### `evo sessions`

Display recent coding sessions, filtered by project.

```bash
evo sessions [OPTIONS]
```

**Options:**
- `-p, --project` - Filter sessions by project name

**Examples:**
```bash
# Sessions for current project
evo sessions

# Sessions for specific project
evo sessions -p myapp

# Sessions matching pattern
evo sessions --project api
```

## Configuration

### Project Configuration

Located at `.evo/config.json` in your project root:

```json
{
  "build_commands": ["npm install", "npm run build"],
  "test_command": "npm test",
  "lint_command": "npm run lint",
  "worktree_files": [".env", ".env.local", ".mcp"],
  "disable_firewall": false,
  "default_cli": "claude"
}
```

**Options:**
- `build_commands` - Commands to run after creating worktree
- `test_command` - Test command to include in AI prompt
- `lint_command` - Lint command to include in AI prompt  
- `worktree_files` - Untracked files to copy to new worktrees
- `disable_firewall` - Allow network access in devcontainers
- `default_cli` - AI assistant to use (currently only "claude")

### Global Configuration

Located at `~/.config/evo/config.json`:

```json
{
  "default_cli": "claude"
}
```

Currently stores the default CLI tool preference.

## Isolated Development (Devcontainers)

For enhanced security and isolation, use the `--runtime isolated` option:

```bash
evo dev feature/secure --runtime isolated
```

Benefits:
- Network isolation (configurable)
- Consistent development environment
- No local environment pollution
- Automatic cleanup

Requirements:
- Docker Desktop or Docker Engine
- devcontainer CLI

## Tips and Best Practices

1. **Branch Naming**: Use descriptive hierarchical names
   ```bash
   evo dev feature/auth/oauth2
   evo dev bugfix/api/rate-limiting
   ```

2. **Complex Prompts**: Use files for detailed instructions
   ```bash
   evo dev refactor/database -p "$(cat refactor-plan.md)"
   ```

3. **Environment Files**: Configure important untracked files
   ```json
   {
     "worktree_files": [".env", ".env.local", "config/secrets.json"]
   }
   ```

4. **Build Automation**: Set up build commands to prepare the environment
   ```json
   {
     "build_commands": ["npm install", "npm run generate", "npm run db:migrate"]
   }
   ```

## How It Works

1. **Worktree Creation**: Creates a Git worktree in a sibling directory
2. **Branch Management**: Creates new branches or checks out existing ones
3. **File Synchronization**: Copies specified untracked files
4. **Environment Setup**: Runs build commands to prepare the workspace
5. **AI Integration**: Launches AI assistant with context about test/lint commands
6. **Session Tracking**: Records sessions for usage analytics

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/evo.git
cd evo

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (if available)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=evo

# Run specific test file
pytest tests/test_settings.py
```

### Code Quality

```bash
# Format code
ruff format .

# Run linter
ruff check .

# Type checking (if mypy is configured)
mypy evo
```

## Troubleshooting

### Worktree Creation Fails
- Ensure you're in a Git repository
- Check for existing worktree with same name
- Verify branch name is valid

### Claude Not Found
- Install Claude CLI: Follow instructions at [claude.ai](https://claude.ai)
- Verify installation: `which claude`
- Restart terminal after installation

### Devcontainer Issues
- Ensure Docker is running
- Install devcontainer CLI: `npm install -g @devcontainers/cli`
- Check Docker permissions

### Permission Errors
- Check directory permissions
- For devcontainers, ensure Docker socket access
- On macOS/Linux, may need to run Docker commands with proper group

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

Please read our contributing guidelines for more details.

## Roadmap

- [ ] Support for additional AI assistants
- [ ] Remote development environments
- [ ] Team collaboration features
- [ ] Enhanced usage analytics
- [ ] Worktree templates
- [ ] Plugin system

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/evo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/evo/discussions)
- **Documentation**: This README and code comments

---

Built with 🧬 by developers, for developers.