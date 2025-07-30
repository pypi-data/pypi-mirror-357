import json
import shutil
import subprocess
import sys
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

from evo.sessions import display_sessions
from evo.settings import CLITool, ProjectSettings, settings
from evo.usage import display_usage_stats


class Runtime(str, Enum):
    local = "local"
    isolated = "isolated"
    remote = "remote"


app = typer.Typer(add_completion=True)
console = Console()


def validate_branch_name(branch_name: str) -> str:
    """Validate git branch name and return sanitized version."""
    # Ensure it's a string
    branch_name = str(branch_name).strip()

    # Check if empty
    if not branch_name:
        typer.echo("Error: Branch name cannot be empty", err=True)
        raise typer.Exit(1)

    # Check for invalid characters
    invalid_chars = [" ", "~", "^", ":", "?", "*", "[", "\\", ".."]
    for char in invalid_chars:
        if char in branch_name:
            typer.echo(f"Error: Branch name cannot contain '{char}'", err=True)
            raise typer.Exit(1)

    # Check start/end conditions
    if branch_name.startswith("."):
        typer.echo("Error: Branch name cannot start with '.'", err=True)
        raise typer.Exit(1)

    if branch_name.endswith("/"):
        typer.echo("Error: Branch name cannot end with '/'", err=True)
        raise typer.Exit(1)

    if branch_name.endswith(".lock"):
        typer.echo("Error: Branch name cannot end with '.lock'", err=True)
        raise typer.Exit(1)

    return branch_name


def _create_worktree(
    branch_name: str,
    repo_root: str,
    copy_worktree_files: bool = True,
) -> Path:
    """Create a git worktree and optionally copy untracked files.

    Args:
        branch_name: Name of the branch to create
        repo_root: Root directory of the git repository
        copy_worktree_files: Whether to copy worktree files from project settings

    Returns:
        Path to the created worktree directory
    """
    # Create worktree directory path
    repo_name = Path(repo_root).name
    worktree_dir = Path(repo_root).parent / f"{repo_name}-{branch_name}"

    # Check if worktree already exists
    worktree_list = subprocess.check_output(["git", "worktree", "list"], text=True)

    if str(worktree_dir) in worktree_list:
        typer.echo(f"Worktree already exists at: {worktree_dir}")
    else:
        # Create the worktree
        typer.echo(f"Creating worktree at: {worktree_dir}")
        try:
            subprocess.run(
                ["git", "worktree", "add", str(worktree_dir), "-b", branch_name],
                check=True,
                capture_output=True,
                text=True,
            )
            typer.echo(f"Successfully created worktree for branch '{branch_name}'")
        except subprocess.CalledProcessError as e:
            # Try without -b flag if branch already exists
            try:
                subprocess.run(
                    ["git", "worktree", "add", str(worktree_dir), branch_name],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                typer.echo(f"Successfully created worktree for existing branch '{branch_name}'")
            except subprocess.CalledProcessError:
                typer.echo(f"Error creating worktree: {e.stderr}", err=True)
                raise typer.Exit(1) from None

        # Copy worktree files (untracked files) from main repository
        if copy_worktree_files:
            project_settings_main = ProjectSettings(Path(repo_root))
            if project_settings_main.exists():
                worktree_files = project_settings_main.get_worktree_files()
                if worktree_files:
                    typer.echo("\nCopying worktree files...")
                    for file_name in worktree_files:
                        source_file = Path(repo_root) / file_name
                        dest_file = worktree_dir / file_name

                        if source_file.exists():
                            typer.echo(f"  Copying {file_name}")
                            try:
                                # Ensure parent directory exists
                                dest_file.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(source_file, dest_file)
                            except (OSError, PermissionError, shutil.Error) as e:
                                typer.echo(f"  Warning: Could not copy {file_name}: {e}", err=True)
                        else:
                            typer.echo(f"  Note: {file_name} not found in main repository", err=True)

    return worktree_dir


def _handle_local_runtime(
    branch_name: str,
    cli_tool: CLITool,
    prompt: str | None,
    repo_root: str,
) -> None:
    """Handle local runtime (former iterate command logic)."""
    # Create worktree with file copying
    worktree_dir = _create_worktree(branch_name, repo_root)

    # Launch CLI tool in the worktree directory
    final_prompt = prompt or ""

    cli_cmd = [cli_tool.value]
    if final_prompt:
        cli_cmd.append(final_prompt)

    typer.echo(f"Launching {cli_tool.value} in: {worktree_dir}")
    try:
        # Use Popen with explicit stdin/stdout/stderr to handle -p parameter properly
        process = subprocess.Popen(
            cli_cmd, cwd=str(worktree_dir), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr
        )
        process.wait()
        if process.returncode != 0:
            typer.echo(f"Error: {cli_tool.value} exited with code {process.returncode}", err=True)
            raise typer.Exit(1) from None
    except FileNotFoundError:
        typer.echo(f"Error: '{cli_tool.value}' command not found. Make sure it's installed.", err=True)
        raise typer.Exit(1) from None


def _handle_isolated_runtime(
    branch_name: str,
    cli_tool: CLITool,
    prompt: str | None,
    repo_root: str,
    disable_firewall: bool,
) -> None:
    """Handle isolated runtime (devcontainer)."""
    # Check if Docker is running
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("Error: Docker is not running or not installed. Please start Docker.", err=True)
        raise typer.Exit(1) from None

    # Check if devcontainer CLI is available
    if not shutil.which("devcontainer"):
        typer.echo("Error: devcontainer CLI not found.", err=True)
        typer.echo("Please install it with: npm install -g @devcontainers/cli", err=True)
        raise typer.Exit(1)

    # Create worktree with file copying
    worktree_dir = _create_worktree(branch_name, repo_root)

    # Copy devcontainer configuration to worktree
    devcontainer_src = Path(repo_root) / ".devcontainer"
    devcontainer_dst = worktree_dir / ".devcontainer"

    if not devcontainer_src.exists():
        typer.echo("Error: .devcontainer directory not found in the repository root.", err=True)
        typer.echo("Please run 'evo init-devcontainer' first to set up the devcontainer configuration.", err=True)
        raise typer.Exit(1)

    if not devcontainer_dst.exists():
        typer.echo("Copying devcontainer configuration...")
        shutil.copytree(devcontainer_src, devcontainer_dst)

    # Prepare the prompt
    final_prompt = prompt or ""

    # Launch with devcontainer CLI
    _launch_with_devcontainer_cli(worktree_dir, devcontainer_dst, cli_tool, final_prompt, disable_firewall, branch_name)


def _handle_remote_runtime() -> None:
    """Handle remote runtime with waitlist message."""
    typer.echo("\n🚀 Remote runtime is coming soon!\n")
    typer.echo("Join the waitlist to be notified when remote development environments are available.")
    typer.echo("\n👉 Register at: https://eliseygusev.com\n")
    typer.echo("Remote environments will offer:")
    typer.echo("  • Cloud-based development with no local setup")
    typer.echo("  • Pre-configured environments with all tools installed")
    typer.echo("  • Scalable resources for large projects")
    typer.echo("  • Team collaboration features")
    raise typer.Exit(0)


@app.command()
def init() -> None:
    """
    Initialize project-specific evo configuration and devcontainer support.

    This command sets up:
    - Project configuration (.evo/config.json)
    - Devcontainer support (.devcontainer/)
    """
    # Get the current repository root
    try:
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.PIPE
        ).strip()
    except subprocess.CalledProcessError:
        typer.echo("Error: Not in a Git repository", err=True)
        raise typer.Exit(1) from None

    project_settings = ProjectSettings(Path(repo_root))

    # Initialize devcontainer files
    devcontainer_dir = Path(repo_root) / ".devcontainer"
    if not devcontainer_dir.exists():
        typer.echo("Setting up devcontainer configuration...")

        # Get the evo package directory
        evo_root = Path(__file__).parent.parent
        template_dir = evo_root / ".devcontainer"

        if not template_dir.exists():
            typer.echo("Error: Devcontainer templates not found. Please ensure EVO is properly installed.", err=True)
            raise typer.Exit(1)

        # Copy devcontainer files
        shutil.copytree(template_dir, devcontainer_dir, dirs_exist_ok=True)
        typer.echo(f"✓ Devcontainer configuration created at: {devcontainer_dir}")
    else:
        typer.echo(f"✓ Devcontainer configuration already exists at: {devcontainer_dir}")

    typer.echo(f"\nInitializing project configuration at: {project_settings.config_file}")

    # Create initial config with defaults
    initial_config = {
        "worktree_files": [".env", ".env.local", ".mcp"],
        "disable_firewall": False,
        "default_cli": "claude",
    }

    # Save the initial config
    project_settings._ensure_config_dir()  # type: ignore[attr-defined]
    project_settings._save_config(initial_config)  # type: ignore[attr-defined]

    typer.echo("\n✓ Project configuration created with defaults:")
    typer.echo("  • Worktree files: .env, .env.local, .mcp")
    typer.echo("  • Disable firewall: false")
    typer.echo("  • Default CLI: claude")

    typer.echo(f"\nEdit {project_settings.config_file} to customize your project settings.")
    typer.echo("\nYou can now use 'evo dev <branch-name>' to create development environments.")


@app.command()
def dev(
    branch_name: str = typer.Argument(..., help="Name of the branch to create worktree for"),
    prompt: str | None = typer.Option(None, "-p", "--prompt", help="Prompt to pass to the CLI tool"),
    runtime: Runtime = typer.Option(  # noqa: B008
        Runtime.local, "-r", "--runtime", help="Development runtime: local, isolated (devcontainer), or remote"
    ),
) -> None:
    """
    Create a Git worktree and launch it with the specified CLI tool.

    Runtime options:
    - local: Run directly on your machine (default)
    - isolated: Run in a devcontainer with network isolation
    - remote: Cloud-based development (coming soon)

    Examples:
        evo dev feature-branch
        evo dev feature-branch --runtime isolated
        evo dev feature-branch -p "Fix the bug in auth"
    """
    # Handle remote runtime first
    if runtime == Runtime.remote:
        _handle_remote_runtime()
        return

    # Validate branch name
    branch_name = validate_branch_name(branch_name)

    # Get the current repository root
    try:
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.PIPE
        ).strip()
    except subprocess.CalledProcessError:
        typer.echo("Error: Not in a Git repository", err=True)
        raise typer.Exit(1) from None

    # Load project settings
    project_settings = ProjectSettings(Path(repo_root))

    # Get CLI tool from project settings
    cli_tool_str = project_settings.get_default_cli() if project_settings.exists() else "claude"
    cli_tool = CLITool(cli_tool_str)

    # Verify the tool is available for local runtime
    if runtime == Runtime.local and cli_tool not in settings.detect_available_clis():
        typer.echo(f"Error: '{cli_tool.value}' is not installed or not found in PATH", err=True)
        raise typer.Exit(1)

    # Get disable_firewall setting from project config
    disable_firewall = project_settings.get_disable_firewall() if project_settings.exists() else False

    # Route to appropriate handler based on runtime
    if runtime == Runtime.local:
        _handle_local_runtime(branch_name, cli_tool, prompt, repo_root)
    elif runtime == Runtime.isolated:
        _handle_isolated_runtime(branch_name, cli_tool, prompt, repo_root, disable_firewall)


def _launch_with_devcontainer_cli(
    worktree_dir: Path,
    devcontainer_dst: Path,
    cli_tool: CLITool,
    final_prompt: str,
    disable_firewall: bool,
    branch_name: str,
) -> None:
    """Launch the devcontainer using the devcontainer CLI."""
    # Read and modify devcontainer.json
    devcontainer_json_path = devcontainer_dst / "devcontainer.json"
    with open(devcontainer_json_path) as f:
        devcontainer_config = json.load(f)

    # Prepare the agent command
    cli_cmd = f"{cli_tool.value}"

    # Add --dangerously-skip-permissions flag for claude in devcontainer
    if cli_tool == CLITool.claude:
        cli_cmd += " --dangerously-skip-permissions"

    if final_prompt:
        escaped_prompt = final_prompt.replace('"', '\\"')
        cli_cmd += f' "{escaped_prompt}"'

    # Modify postCreateCommand to include the agent command
    post_create = devcontainer_config.get("postCreateCommand", "")
    if disable_firewall and "init-firewall.sh" in post_create:
        post_create = ""  # Remove firewall initialization

    # Combine post-create and CLI commands
    final_command = f"{post_create} && {cli_cmd}" if post_create else cli_cmd
    devcontainer_config["postCreateCommand"] = f"/bin/zsh -c '{final_command}'"

    # Remove network capabilities if firewall is disabled
    if disable_firewall and "runArgs" in devcontainer_config:
        devcontainer_config["runArgs"] = [
            arg for arg in devcontainer_config["runArgs"] if arg not in ["--cap-add=NET_ADMIN", "--cap-add=NET_RAW"]
        ]

    # Write the updated config back
    with open(devcontainer_json_path, "w") as f:
        json.dump(devcontainer_config, f, indent=2)

    typer.echo(f"\nLaunching devcontainer for {branch_name}...")
    typer.echo(f"Worktree: {worktree_dir}")
    typer.echo(f"Using CLI tool: {cli_tool.value}")
    if final_prompt:
        typer.echo(f"Prompt: {final_prompt}")

    typer.echo("\nAuthentication is persisted in Docker volumes:")
    typer.echo(f"  - {cli_tool.value} config: evo-{cli_tool.value}-config")

    try:
        # Use devcontainer up to build and start the container
        typer.echo("\nStarting devcontainer...")
        subprocess.run(["devcontainer", "up", "--workspace-folder", str(worktree_dir)], check=True)

        # The postCreateCommand will run the CLI tool automatically
        # We'll attach to see the output
        typer.echo("\nAttaching to devcontainer...")
        subprocess.run(["devcontainer", "exec", "--workspace-folder", str(worktree_dir), "/bin/zsh"], check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error launching devcontainer: {e}", err=True)
        raise typer.Exit(1) from None
    except KeyboardInterrupt:
        typer.echo("\nStopping devcontainer...")
        subprocess.run(["devcontainer", "down", "--workspace-folder", str(worktree_dir)], capture_output=True)
        raise typer.Exit(0) from None


@app.command()
def usage(
    days: int = typer.Option(30, "-d", "--days", help="Number of days to show statistics for"),
    project: str | None = typer.Option(None, "-p", "--project", help="Filter usage by project name"),
) -> None:
    """
    Display Claude usage statistics.

    Shows daily token usage, costs, and models used based on
    data from ~/.claude directory.

    Examples:
        evo usage              # Last 30 days (default)
        evo usage -d 7         # Last 7 days
        evo usage --days 90    # Last 90 days
        evo usage -p myproject # Filter by project
    """
    if days <= 0:
        typer.echo("Error: Days must be a positive number", err=True)
        raise typer.Exit(1)

    display_usage_stats(console, days=days, project_name=project)


@app.command()
def sessions(
    project: str | None = typer.Option(None, "-p", "--project", help="Filter sessions by project name"),
    days: int | None = typer.Option(None, "-d", "--days", help="Number of days to show sessions for"),
    number: int = typer.Option(10, "-n", "--number", help="Maximum number of sessions to display"),
) -> None:
    """
    Display Claude conversation sessions.

    Shows session IDs, project names, and last activity dates.
    By default, tries to get the project name from the current folder
    and shows sessions for that project. If not in a project folder,
    shows the 10 most recent sessions across all projects.

    Examples:
        evo sessions                    # Sessions for current project or 10 most recent
        evo sessions -p myproject       # Sessions for "myproject"
        evo sessions --project app      # Sessions containing "app" in project name
        evo sessions -d 7               # Sessions from last 7 days
        evo sessions --days 30 -n 20    # Last 30 days, up to 20 sessions
    """
    if days is not None and days <= 0:
        typer.echo("Error: Days must be a positive number", err=True)
        raise typer.Exit(1)

    if number <= 0:
        typer.echo("Error: Number must be a positive number", err=True)
        raise typer.Exit(1)

    display_sessions(console, project_name=project, limit=number, days=days)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
