# EVO Devcontainer Documentation

## Overview

The EVO devcontainer provides an isolated development environment with pre-installed Claude Code assistant while maintaining authentication persistence across sessions.

## Authentication Persistence Strategy

### How It Works

Authentication for Claude Code is persisted using Docker named volumes. This ensures that you only need to authenticate once, and your credentials will be available across all devcontainer sessions.

### Volume Mapping

The devcontainer uses dedicated volumes for configuration and authentication:

- **Claude Code**: `evo-claude-config` → `/home/node/.claude`
- **EVO Global**: `evo-global-config` → `/home/node/.evo`

Additional persistent volumes:
- **Bash History**: `evo-bashhistory` → `/commandhistory`
- **UV Cache**: `evo-uv-cache` → `/home/node/.cache/uv`

### First-Time Setup

1. When you first launch a devcontainer with `evo dev <branch>`, Claude Code will prompt for authentication
2. Complete the authentication process (API key)
3. The authentication tokens/credentials are automatically saved to the persistent volume
4. Future devcontainer launches will reuse these credentials

### Managing Authentication

#### View Docker Volumes
```bash
# List all EVO-related volumes
docker volume ls | grep evo-

# Inspect a specific volume
docker volume inspect evo-claude-config
```

#### Reset Authentication
If you need to re-authenticate or switch accounts:

```bash
# Remove Claude Code's config volume
docker volume rm evo-claude-config

# Remove all EVO volumes (full reset)
docker volume rm $(docker volume ls -q | grep evo-)
```

#### Backup Authentication
To backup your authentication data:

```bash
# Create a backup directory
mkdir -p ~/evo-auth-backup

# Backup Claude Code's config
docker run --rm -v evo-claude-config:/source -v ~/evo-auth-backup:/backup alpine tar -czf /backup/claude-config.tar.gz -C /source .

# Restore from backup
docker run --rm -v evo-claude-config:/target -v ~/evo-auth-backup:/backup alpine tar -xzf /backup/claude-config.tar.gz -C /target
```

## Security Considerations

### Network Firewall

The devcontainer includes an optional firewall that restricts network access to only approved domains:
- GitHub APIs and repositories
- Package registries (npm, PyPI)
- Anthropic API for Claude Code

To disable the firewall, use the `--no-firewall` flag:
```bash
evo dev my-feature --no-firewall
```

### Volume Security

- Volumes are only accessible to containers running on your local Docker daemon
- Claude Code's configuration is isolated in its own volume
- Volumes persist on your local machine and are not synced to any remote location

## Troubleshooting

### Authentication Not Persisting

1. Check if the volume exists:
   ```bash
   docker volume ls | grep evo-claude-config
   ```

2. Verify volume is properly mounted:
   ```bash
   docker inspect <container-id> | grep Mounts -A 20
   ```

3. Check permissions inside container:
   ```bash
   ls -la ~/.claude/
   ```

### CLI Tool Not Found

If Claude Code is not available in the container:

1. Rebuild the devcontainer:
   ```bash
   # In VS Code
   Ctrl/Cmd + Shift + P → "Dev Containers: Rebuild Container"
   ```

2. Check if the tool is installed:
   ```bash
   which claude
   npm list -g @anthropic-ai/claude-code
   ```

### Network Issues

If you're experiencing connectivity issues:

1. Check firewall status (if enabled):
   ```bash
   sudo iptables -L
   sudo ipset list allowed-domains
   ```

2. Try disabling the firewall:
   ```bash
   evo dev my-feature --no-firewall
   ```

## Best Practices

1. **Regular Updates**: Periodically rebuild your devcontainer to get the latest Claude Code version
2. **Volume Backup**: Backup your authentication volumes before major changes
3. **Branch Isolation**: Each worktree gets its own devcontainer instance, maintaining complete isolation
4. **Resource Cleanup**: Remove old worktrees and their containers when done:
   ```bash
   git worktree remove <path>
   ```