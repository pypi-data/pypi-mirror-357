import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from evo.main import app
from evo.settings import CLITool, Settings

runner = CliRunner()


@pytest.fixture
def mock_settings(tmp_path, monkeypatch):
    """Create a mock settings instance with temporary config."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return Settings()


def test_dev_local_not_in_git_repo(mock_settings):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.side_effect = subprocess.CalledProcessError(128, "git")

        result = runner.invoke(app, ["dev", "test-branch", "--runtime", "local"])

        assert result.exit_code == 1
        assert "Error: Not in a Git repository" in result.stderr


def test_dev_local_worktree_already_exists(mock_settings):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("subprocess.Popen") as mock_popen,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.side_effect = [
            "/Users/test/repo",  # git rev-parse
            "/Users/test/repo-test-branch /Users/test/repo-test-branch",  # git worktree list
        ]
        # Mock Popen for claude command
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = runner.invoke(app, ["dev", "test-branch", "--runtime", "local"])

        assert "Worktree already exists at: /Users/test/repo-test-branch" in result.stdout
        assert mock_popen.called


def test_dev_local_create_new_worktree(mock_settings):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("subprocess.run") as mock_run,
        patch("subprocess.Popen") as mock_popen,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.side_effect = [
            "/Users/test/repo",  # git rev-parse
            "/Users/test/repo /Users/test/repo",  # git worktree list (no matching worktree)
        ]
        # Mock Popen for claude command
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = runner.invoke(app, ["dev", "test-branch"])

        assert "Creating worktree at: /Users/test/repo-test-branch" in result.stdout
        assert "Successfully created worktree for branch 'test-branch'" in result.stdout
        assert mock_run.call_count == 1  # git worktree add
        assert mock_popen.call_count == 1  # claude


def test_dev_local_with_prompt(mock_settings):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("subprocess.run"),
        patch("subprocess.Popen") as mock_popen,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.side_effect = [
            "/Users/test/repo",  # git rev-parse
            "/Users/test/repo /Users/test/repo",  # git worktree list
        ]
        # Mock Popen for claude command
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        runner.invoke(app, ["dev", "test-branch", "--prompt", "fix bugs"])

        # Check that claude was called with prompt
        assert mock_popen.called
        claude_call = mock_popen.call_args
        assert claude_call[0][0] == ["claude", "fix bugs"]


def test_dev_with_prompt_file(mock_settings, tmp_path):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("subprocess.run"),
        patch("subprocess.Popen") as mock_popen,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        # Create a temporary markdown file with prompt
        prompt_file = tmp_path / "refactor-plan.md"
        prompt_content = "Refactor the authentication system"
        prompt_file.write_text(prompt_content)

        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.side_effect = [
            "/Users/test/repo",  # git rev-parse
            "/Users/test/repo /Users/test/repo",  # git worktree list
        ]
        # Mock Popen for claude command
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        runner.invoke(app, ["dev", "test-branch", "--prompt-file", str(prompt_file)])

        # Check that claude was called with prompt file content
        assert mock_popen.called
        claude_call = mock_popen.call_args
        assert claude_call[0][0] == ["claude", prompt_content]


def test_dev_prompt_file_not_found(mock_settings):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.return_value = "/Users/test/repo"  # git rev-parse

        result = runner.invoke(app, ["dev", "test-branch", "--prompt-file", "nonexistent.md"])

        assert result.exit_code == 1
        assert "Error: Prompt file 'nonexistent.md' not found" in result.stderr


def test_dev_prompt_and_prompt_file_mutually_exclusive(mock_settings):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.return_value = "/Users/test/repo"  # git rev-parse

        result = runner.invoke(app, ["dev", "test-branch", "-p", "prompt", "-pf", "file.md"])

        assert result.exit_code == 1
        assert "Error: Cannot use both -p/--prompt and -pf/--prompt-file options" in result.stderr


def test_dev_prompt_file_not_markdown(mock_settings, tmp_path):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        # Create a non-markdown file
        prompt_file = tmp_path / "refactor-plan.txt"
        prompt_file.write_text("Some content")

        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.return_value = "/Users/test/repo"  # git rev-parse

        result = runner.invoke(app, ["dev", "test-branch", "--prompt-file", str(prompt_file)])

        assert result.exit_code == 1
        assert "Error: Prompt file must be a markdown file (.md)" in result.stderr


def test_dev_local_claude_not_found(mock_settings):
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("subprocess.run") as mock_run,
        patch("subprocess.Popen") as mock_popen,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which", return_value="/usr/bin/claude"),
    ):
        mock_settings.set_default_cli(CLITool.claude)
        mock_check_output.side_effect = [
            "/Users/test/repo",  # git rev-parse
            "/Users/test/repo /Users/test/repo",  # git worktree list
        ]

        mock_run.return_value = MagicMock()  # git worktree add succeeds
        mock_popen.side_effect = FileNotFoundError()  # claude command not found

        result = runner.invoke(app, ["dev", "test-branch"])

        assert result.exit_code == 1
        assert "Error: 'claude' command not found" in result.stderr


def test_dev_uses_project_default_cli(mock_settings):
    # Test that dev command uses project settings for CLI tool
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("subprocess.run"),
        patch("subprocess.Popen") as mock_popen,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which") as mock_which,
        patch("evo.main.ProjectSettings") as mock_project_settings,
    ):
        mock_which.return_value = "/usr/bin/claude"

        # Mock project settings
        mock_proj_instance = MagicMock()
        mock_proj_instance.exists.return_value = True
        mock_proj_instance.get_default_cli.return_value = "claude"
        mock_proj_instance.get_disable_firewall.return_value = False
        mock_project_settings.return_value = mock_proj_instance

        mock_check_output.side_effect = [
            "/Users/test/repo",  # git rev-parse
            "/Users/test/repo /Users/test/repo",  # git worktree list
        ]
        # Mock Popen for claude command
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = runner.invoke(app, ["dev", "test-branch"])

        assert "Launching claude" in result.stdout
        # Check that claude was called
        assert mock_popen.called


def test_dev_with_unavailable_claude(mock_settings):
    # Test when claude is not installed
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which") as mock_which,
        patch("evo.main.ProjectSettings") as mock_project_settings,
    ):
        mock_which.return_value = None  # No CLI tools available
        mock_check_output.return_value = "/Users/test/repo"

        # Mock project settings
        mock_proj_instance = MagicMock()
        mock_proj_instance.exists.return_value = True
        mock_proj_instance.get_default_cli.return_value = "claude"
        mock_project_settings.return_value = mock_proj_instance

        result = runner.invoke(app, ["dev", "test-branch"])

        assert result.exit_code == 1
        assert "Error: 'claude' is not installed" in result.stderr


def test_dev_defaults_to_claude_when_no_project_config(mock_settings):
    # Test that dev defaults to claude when no project config exists
    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("subprocess.run"),
        patch("subprocess.Popen") as mock_popen,
        patch("evo.main.settings", mock_settings),
        patch("shutil.which") as mock_which,
        patch("evo.main.ProjectSettings") as mock_project_settings,
    ):
        mock_which.return_value = "/usr/bin/claude"

        # Mock project settings - no config exists
        mock_proj_instance = MagicMock()
        mock_proj_instance.exists.return_value = False
        mock_project_settings.return_value = mock_proj_instance

        mock_check_output.side_effect = [
            "/Users/test/repo",  # git rev-parse
            "/Users/test/repo /Users/test/repo",  # git worktree list
        ]
        # Mock Popen for claude command
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = runner.invoke(app, ["dev", "test-branch"])

        assert result.exit_code == 0
        assert "Launching claude" in result.stdout
        # Check that Popen was called with claude
        assert mock_popen.called
        claude_call = mock_popen.call_args
        assert claude_call[0][0][0] == "claude"


def test_dev_remote_shows_waitlist(mock_settings):
    with patch("evo.main.settings", mock_settings):
        result = runner.invoke(app, ["dev", "test-branch", "--runtime", "remote"])

        assert result.exit_code == 0
        assert "Remote runtime is coming soon!" in result.stdout
        assert "eliseygusev.com" in result.stdout
        assert "Cloud-based development" in result.stdout


def test_init_command(tmp_path):
    # Test the new init command - simplified version
    # Create a mock repo structure
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    # Create git directory to simulate being in a git repo
    git_dir = repo_dir / ".git"
    git_dir.mkdir()

    # Create a temporary evo package directory with templates
    evo_package_dir = tmp_path / "evo_package"
    template_dir = evo_package_dir / ".devcontainer"
    template_dir.mkdir(parents=True)
    (template_dir / "devcontainer.json").write_text("{}")

    with (
        patch("subprocess.check_output") as mock_check_output,
        patch("evo.main.__file__", str(evo_package_dir / "evo" / "main.py")),
    ):
        mock_check_output.return_value = str(repo_dir)

        # Change to repo directory
        import os

        original_cwd = os.getcwd()
        os.chdir(repo_dir)

        try:
            result = runner.invoke(app, ["init"])

            assert result.exit_code == 0
            assert "Devcontainer configuration" in result.stdout
            assert "Project configuration created with defaults" in result.stdout

            # Check that files were created
            assert (repo_dir / ".devcontainer").exists()
            assert (repo_dir / ".evo" / "config.json").exists()

            # Check config content
            config_content = json.loads((repo_dir / ".evo" / "config.json").read_text())
            assert config_content["default_cli"] == "claude"
            assert config_content["worktree_files"] == [".env", ".env.local", ".mcp"]
        finally:
            os.chdir(original_cwd)


def test_usage_no_data(tmp_path, monkeypatch):
    """Test usage command when no Claude data exists."""
    # Mock home directory to temp path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = runner.invoke(app, ["usage"])

    assert result.exit_code == 0
    assert "No Claude usage data found" in result.stdout


def test_usage_with_data(tmp_path, monkeypatch):
    """Test usage command with sample Claude data."""
    # Mock home directory to temp path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # Create Claude directory structure
    claude_dir = tmp_path / ".claude" / "projects" / "test-project"
    claude_dir.mkdir(parents=True)

    # Create sample JSONL data for different days
    now = datetime.now()

    # Day 1: 5 days ago - multiple messages same day
    day1_data_1 = {
        "timestamp": (now - timedelta(days=5)).isoformat() + "Z",
        "message": {
            "model": "claude-3-5-sonnet-20241022",
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 500,
                "cache_creation_input_tokens": 100,
                "cache_read_input_tokens": 50,
            },
        },
    }

    day1_data_2 = {
        "timestamp": (now - timedelta(days=5, hours=1)).isoformat() + "Z",
        "message": {
            "model": "claude-3-5-sonnet-20241022",
            "usage": {
                "input_tokens": 500,
                "output_tokens": 250,
                "cache_creation_input_tokens": 50,
                "cache_read_input_tokens": 25,
            },
        },
    }

    # Day 2: 3 days ago
    day2_data = {
        "timestamp": (now - timedelta(days=3)).isoformat() + "Z",
        "message": {
            "model": "claude-opus-4-20250514",
            "usage": {
                "input_tokens": 2000,
                "output_tokens": 1000,
                "cache_creation_input_tokens": 200,
                "cache_read_input_tokens": 100,
            },
        },
    }

    # Day 3: today
    day3_data = {
        "timestamp": now.isoformat() + "Z",
        "message": {
            "model": "<synthetic>, claude-3-5-haiku-20241022",
            "usage": {
                "input_tokens": 500,
                "output_tokens": 250,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 25,
            },
        },
    }

    # Write JSONL file
    jsonl_file = claude_dir / "test.jsonl"
    with open(jsonl_file, "w") as f:
        f.write(json.dumps(day1_data_1) + "\n")
        f.write(json.dumps(day1_data_2) + "\n")
        f.write(json.dumps(day2_data) + "\n")
        f.write(json.dumps(day3_data) + "\n")
        # Add some invalid lines to test error handling
        f.write('{"invalid": "data"}\n')
        f.write("not json at all\n")

    result = runner.invoke(app, ["usage"])

    assert result.exit_code == 0
    # First check if we got any output
    if "No Claude usage data found" in result.stdout:
        # Debug: print what's happening
        print(f"JSONL file path: {jsonl_file}")
        print(f"JSONL file exists: {jsonl_file.exists()}")
        print(f"Claude dir: {claude_dir}")
        print(f"Files in claude dir: {list(claude_dir.rglob('*'))}")

    assert "Claude Usage Statistics (Last 30 Days)" in result.stdout

    # Check for specific content rather than exact dates
    # The table should contain our test data
    assert "2,475" in result.stdout  # Total tokens for day 1 (two messages)
    assert "3,300" in result.stdout  # Total tokens for day 2
    assert "775" in result.stdout  # Total tokens for day 3

    # Check that model names appear (they might be truncated)
    assert "claude" in result.stdout
    assert "<synthetic>" not in result.stdout

    # Check totals
    assert "TOTAL" in result.stdout
    assert "6,550" in result.stdout  # Total tokens
    # Check the cost is calculated
    assert "$0.13" in result.stdout or "$0.14" in result.stdout  # Total cost (allow for rounding)


def test_usage_old_data_filtered(tmp_path, monkeypatch):
    """Test that usage command filters out data older than 30 days."""
    # Mock home directory to temp path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # Create Claude directory
    claude_dir = tmp_path / ".claude" / "projects" / "test"
    claude_dir.mkdir(parents=True)

    now = datetime.now()

    # Old data (35 days ago) - should be filtered out
    old_data = {
        "timestamp": (now - timedelta(days=35)).isoformat() + "Z",
        "message": {"model": "claude-3-5-sonnet-20241022", "usage": {"input_tokens": 1000, "output_tokens": 500}},
    }

    # Recent data (5 days ago) - should be included
    recent_data = {
        "timestamp": (now - timedelta(days=5)).isoformat() + "Z",
        "message": {"model": "claude-3-5-sonnet-20241022", "usage": {"input_tokens": 2000, "output_tokens": 1000}},
    }

    # Write JSONL file
    jsonl_file = claude_dir / "test.jsonl"
    with open(jsonl_file, "w") as f:
        f.write(json.dumps(old_data) + "\n")
        f.write(json.dumps(recent_data) + "\n")

    result = runner.invoke(app, ["usage"])

    assert result.exit_code == 0
    # Should only show 1 message (recent one)
    assert "TOTAL" in result.stdout
    output_lines = result.stdout.split("\n")
    for line in output_lines:
        if "TOTAL" in line and "1" in line:
            # Found the total line with 1 message
            break
    else:
        raise AssertionError("Expected to find TOTAL with 1 message")


def test_usage_empty_jsonl_files(tmp_path, monkeypatch):
    """Test usage command handles empty JSONL files gracefully."""
    # Mock home directory to temp path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # Create Claude directory with empty files
    claude_dir = tmp_path / ".claude" / "projects" / "test"
    claude_dir.mkdir(parents=True)

    # Create empty JSONL file
    (claude_dir / "empty.jsonl").touch()

    # Create JSONL with only invalid data
    with open(claude_dir / "invalid.jsonl", "w") as f:
        f.write("\n")
        f.write('{"no_message": "field"}\n')
        f.write('{"message": {"no_usage": "field"}}\n')

    result = runner.invoke(app, ["usage"])

    assert result.exit_code == 0
    assert "No Claude usage data found" in result.stdout
