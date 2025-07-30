# Evo

A powerful CLI tool for managing Git worktrees with integrated AI coding assistant support. Evo streamlines development workflows by creating isolated Git worktrees and launching them with Claude or other AI assistants.

## Installation

### Install uv (recommended)
First, install uv - a fast Python package manager:
[Installation Guide](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

### Install and Run with uv
```bash
# Install globally
uv tool install evo-tool

# Then use normally
evo usage
evo sessions
evo dev feature-branch
```

### Update to latest version
```bash
# Update with uv
uv tool upgrade evo-tool

# Or reinstall to force latest
uv tool install --force evo-tool
```

### Run without installing
```bash
# Run any command without installation
uvx --from evo-tool evo sessions
uvx --from evo-tool evo usage
```

### Alternative: Install with pip
```bash
pip install evo-tool
```

## Requirements

- Python 3.12+
- Git
- [Claude CLI](https://docs.anthropic.com/en/docs/claude-code/overview#basic-usage): `npm install -g @anthropic-ai/claude-code`
- Docker (for isolated runtime only)

## Quick Start

### 1. Initialize your project
```bash
evo init
```
Creates `.evo/config.json` for project-specific settings.

### 2. Create isolated development branches
```bash
evo dev my-new-feature
```
This creates a new Git worktree at `../{repo-name}-my-new-feature`, allowing you to run multiple Claude instances simultaneously without affecting your main directory.

### 3. Use isolated Docker environment (optional)
```bash
evo dev my-feature --runtime isolated
```

## Commands

### `evo dev <branch-name>`
Create a Git worktree and launch Claude.

**Options:**
- `-p, --prompt` - Initial prompt for Claude
- `-pf, --prompt-file` - Read prompt from a markdown file
- `-r, --runtime` - Development runtime: `local` (default) or `isolated`

**Examples:**
```bash
# With inline prompt
evo dev fix/auth-bug -p "Fix the authentication timeout issue"

# With prompt from markdown file
evo dev refactor/auth -pf refactor-plan.md
```

### `evo usage`
Display Claude usage statistics and costs.

**Options:**
- `-d, --days` - Number of days to show (default: 30)
- `-p, --project` - Filter by project name

**Example:**
```bash
evo usage -d 7  # Last week's usage
```

### `evo sessions`
Display Claude conversation sessions.

**Options:**
- `-d, --days` - Number of days to show (default: 30)
- `-p, --project` - Filter by project name

**Example:**
```bash
evo sessions -d 14  # Last 2 weeks
# Copy a session ID and resume with: claude -r {sessionId}
```

## Configuration

Project settings are stored in `.evo/config.json`:

```json
{
  "worktree_files": [".env", ".env.local", ".mcp"],
  "test_command": "npm test",
  "lint_command": "npm run lint",
  "disable_firewall": false,
  "default_cli": "claude"
}
```

### Key Settings

1. **Environment Files**
   - Git worktrees only copy tracked files
   - Use `worktree_files` to specify untracked files (like `.env`) to copy

2. **Isolated Runtime**
   - `disable_firewall`: Allow network access in Docker containers

## Tips

### Work on multiple features simultaneously
```bash
# Terminal 1
evo dev feature/api-v2

# Terminal 2
evo dev fix/performance

# Terminal 3
evo dev refactor/database
```

### Use complex prompts from files
```bash
# Native markdown file support (recommended)
evo dev refactor/auth -pf refactor-plan.md

# Or using shell substitution
evo dev refactor/auth -p "$(cat refactor-plan.md)"
```

### Track costs across projects
```bash
evo usage -p myproject -d 30
```

## License

MIT License - see LICENSE file for details.
