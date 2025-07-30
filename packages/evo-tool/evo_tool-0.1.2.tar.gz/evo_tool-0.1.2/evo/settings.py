import json
import shutil
from enum import Enum
from pathlib import Path
from typing import Any, TypedDict

import typer

CLI_TOOLS = ["claude"]


class CLITool(str, Enum):
    claude = "claude"


class ProjectConfig(TypedDict, total=False):
    """Project-specific configuration stored in .evo/config.json"""

    worktree_files: list[str]  # Untracked files to copy to worktrees
    disable_firewall: bool  # Disable network firewall in devcontainer
    default_cli: str  # Default CLI tool (e.g., "claude")


class ProjectSettings:
    def __init__(self, project_root: Path | None = None):
        if project_root:
            self.project_root = project_root
        else:
            self.project_root = Path.cwd()
        self.config_dir = self.project_root / ".evo"
        self.config_file = self.config_dir / "config.json"

    def exists(self) -> bool:
        return self.config_file.exists()

    def _ensure_config_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict[str, Any]:
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}

    def _save_config(self, config: dict[str, Any]) -> None:
        self._ensure_config_dir()
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def get_worktree_files(self) -> list[str]:
        """Get list of untracked files to copy to worktrees."""
        config = self._load_config()
        return config.get("worktree_files", [".env", ".env.local", ".mcp"])

    def set_worktree_files(self, files: list[str]) -> None:
        """Set list of untracked files to copy to worktrees."""
        config = self._load_config()
        config["worktree_files"] = files
        self._save_config(config)

    def get_disable_firewall(self) -> bool:
        """Get whether to disable firewall in devcontainer."""
        config = self._load_config()
        return config.get("disable_firewall", False)

    def set_disable_firewall(self, disable: bool) -> None:
        """Set whether to disable firewall in devcontainer."""
        config = self._load_config()
        config["disable_firewall"] = disable
        self._save_config(config)

    def get_default_cli(self) -> str:
        """Get the default CLI tool for this project."""
        config = self._load_config()
        return config.get("default_cli", "claude")

    def set_default_cli(self, cli: str) -> None:
        """Set the default CLI tool for this project."""
        config = self._load_config()
        config["default_cli"] = cli
        self._save_config(config)


class Settings:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "evo"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict[str, Any]:
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}

    def _save_config(self, config: dict[str, Any]) -> None:
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def get_default_cli(self) -> CLITool | None:
        config = self._load_config()
        cli_str = config.get("default_cli")
        if cli_str:
            return CLITool(cli_str)
        return None

    def set_default_cli(self, cli: CLITool) -> None:
        config = self._load_config()
        config["default_cli"] = cli.value
        self._save_config(config)

    def detect_available_clis(self) -> list[CLITool]:
        available = []
        for cli in CLITool:
            if shutil.which(cli.value):
                available.append(cli)
        return available

    def prompt_for_default_cli(self) -> CLITool:
        available_clis = self.detect_available_clis()

        if not available_clis:
            typer.echo("Error: No supported CLI tool found (claude)", err=True)
            raise typer.Exit(1)

        typer.echo("No default CLI tool configured. Available options:")
        cli_list = list(CLITool)
        for i, cli in enumerate(cli_list):
            if cli in available_clis:
                typer.echo(f"  [{i + 1}] {cli.value} ✓")
            else:
                typer.echo(f"  [{i + 1}] {cli.value} (not installed)")

        while True:
            try:
                choice = typer.prompt("\nSelect default CLI tool (enter number)")
                idx = int(choice) - 1
                if 0 <= idx < len(cli_list) and cli_list[idx] in available_clis:
                    selected = cli_list[idx]
                    self.set_default_cli(selected)
                    typer.echo(f"Default CLI set to: {selected.value}")
                    return selected
                else:
                    typer.echo("Invalid selection. Please choose an available tool.", err=True)
            except (ValueError, KeyboardInterrupt):
                typer.echo("\nCancelled.", err=True)
                raise typer.Exit(1) from None


settings = Settings()
