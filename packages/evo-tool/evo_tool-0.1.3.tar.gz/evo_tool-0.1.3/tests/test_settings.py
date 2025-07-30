import json
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from evo.settings import CLITool, ProjectSettings, Settings


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory for testing."""
    config_dir = tmp_path / ".config" / "evo"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def settings_instance(temp_config_dir, monkeypatch):
    """Create a Settings instance with a temporary config directory."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent.parent)
    return Settings()


class TestSettings:
    def test_init_creates_config_dir(self, temp_config_dir, monkeypatch):
        """Test that Settings initialization creates the config directory."""
        monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent.parent)
        settings = Settings()
        assert settings.config_dir.exists()
        assert settings.config_dir == temp_config_dir

    def test_get_default_cli_none(self, settings_instance):
        """Test getting default CLI when none is set."""
        assert settings_instance.get_default_cli() is None

    def test_set_and_get_default_cli(self, settings_instance):
        """Test setting and getting default CLI."""
        from evo.settings import CLITool

        settings_instance.set_default_cli(CLITool.claude)
        assert settings_instance.get_default_cli() == CLITool.claude

        # Verify it's persisted to file
        with open(settings_instance.config_file) as f:
            config = json.load(f)
            assert config["default_cli"] == "claude"

    @patch("shutil.which")
    def test_detect_available_clis(self, mock_which, settings_instance):
        """Test detecting available CLI tools."""

        # Mock which to return path for claude
        def which_side_effect(cmd):
            if cmd == "claude":
                return f"/usr/bin/{cmd}"
            return None

        mock_which.side_effect = which_side_effect

        available = settings_instance.detect_available_clis()
        assert CLITool.claude in available
        assert len(available) == 1

    @patch("shutil.which")
    @patch("typer.prompt")
    @patch("typer.echo")
    def test_prompt_for_default_cli_success(self, mock_echo, mock_prompt, mock_which, settings_instance):
        """Test prompting for default CLI selection."""
        # Mock available CLIs
        mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}" if cmd == "claude" else None

        # Mock user selecting option 1 (claude)
        mock_prompt.return_value = "1"

        result = settings_instance.prompt_for_default_cli()

        assert result == CLITool.claude
        assert settings_instance.get_default_cli() == CLITool.claude

        # Verify the prompt shows correct available options
        echo_calls = [call[0][0] for call in mock_echo.call_args_list]
        assert any("claude ✓" in call for call in echo_calls)
        # Only claude should be shown

    @patch("shutil.which")
    @patch("typer.echo")
    def test_prompt_for_default_cli_no_tools(self, mock_echo, mock_which, settings_instance):
        """Test prompting when no CLI tools are available."""
        # Mock no CLIs available
        mock_which.return_value = None

        with pytest.raises(typer.Exit) as exc_info:
            settings_instance.prompt_for_default_cli()

        assert exc_info.value.exit_code == 1  # type: ignore[attr-defined]
        mock_echo.assert_called_with("Error: No supported CLI tool found (claude)", err=True)

    @patch("shutil.which")
    @patch("typer.prompt")
    @patch("typer.echo")
    def test_prompt_for_default_cli_invalid_selection(self, mock_echo, mock_prompt, mock_which, settings_instance):
        """Test prompting with invalid selections."""
        # Mock available CLIs
        mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}" if cmd == "claude" else None

        # Mock user selecting invalid options then valid one
        mock_prompt.side_effect = ["5", "0", "1"]  # 5=out of range, 0=invalid, 1=claude

        result = settings_instance.prompt_for_default_cli()

        assert result == CLITool.claude
        # Verify error messages for invalid selections
        error_calls = [call for call in mock_echo.call_args_list if call[1].get("err")]
        assert len(error_calls) >= 2

    @patch("shutil.which")
    @patch("typer.prompt")
    @patch("typer.echo")
    def test_prompt_for_default_cli_cancelled(self, mock_echo, mock_prompt, mock_which, settings_instance):
        """Test cancelling the prompt."""
        # Mock available CLIs
        mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}" if cmd == "claude" else None

        # Mock user pressing Ctrl+C
        mock_prompt.side_effect = KeyboardInterrupt()

        with pytest.raises(typer.Exit) as exc_info:
            settings_instance.prompt_for_default_cli()

        assert exc_info.value.exit_code == 1  # type: ignore[attr-defined]

    def test_config_persistence(self, settings_instance):
        """Test that configuration persists across Settings instances."""
        settings_instance.set_default_cli(CLITool.claude)

        # Create new instance
        new_settings = Settings()
        assert new_settings.get_default_cli() == CLITool.claude


class TestProjectSettings:
    @pytest.fixture
    def temp_project_dir(self, tmp_path):
        """Create a temporary project directory."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        return project_dir

    @pytest.fixture
    def project_settings(self, temp_project_dir):
        """Create a ProjectSettings instance with a temporary directory."""
        return ProjectSettings(temp_project_dir)

    def test_init_with_project_root(self, temp_project_dir):
        """Test initialization with explicit project root."""
        settings = ProjectSettings(temp_project_dir)
        assert settings.project_root == temp_project_dir
        assert settings.config_dir == temp_project_dir / ".evo"
        assert settings.config_file == temp_project_dir / ".evo" / "config.json"

    def test_init_without_project_root(self, monkeypatch, temp_project_dir):
        """Test initialization without project root uses current directory."""
        monkeypatch.chdir(temp_project_dir)
        settings = ProjectSettings()
        assert settings.project_root == temp_project_dir
        assert settings.config_dir == temp_project_dir / ".evo"

    def test_exists_false_initially(self, project_settings):
        """Test that exists() returns False when config doesn't exist."""
        assert not project_settings.exists()

    def test_exists_true_after_save(self, project_settings):
        """Test that exists() returns True after saving config."""
        project_settings.set_worktree_files([".env", ".custom"])
        assert project_settings.exists()

    def test_ensure_config_dir_creates_directory(self, project_settings):
        """Test that _ensure_config_dir creates the .evo directory."""
        assert not project_settings.config_dir.exists()
        project_settings._ensure_config_dir()
        assert project_settings.config_dir.exists()
        assert project_settings.config_dir.is_dir()

    def test_multiple_settings_updates(self, project_settings):
        """Test updating multiple settings preserves all values."""
        # Set different settings
        project_settings.set_worktree_files([".env", ".secrets"])
        project_settings.set_disable_firewall(True)
        project_settings.set_default_cli("claude")

        # Verify all are preserved
        assert project_settings.get_worktree_files() == [".env", ".secrets"]
        assert project_settings.get_disable_firewall() is True
        assert project_settings.get_default_cli() == "claude"

    def test_config_file_format(self, project_settings):
        """Test that config file is properly formatted JSON."""
        project_settings.set_worktree_files(["file1", "file2"])
        project_settings.set_disable_firewall(False)
        project_settings.set_default_cli("claude")

        # Read and verify JSON structure
        with open(project_settings.config_file) as f:
            content = f.read()
            config = json.loads(content)  # Should not raise
            assert "worktree_files" in config
            assert "disable_firewall" in config
            assert "default_cli" in config

        # Verify indentation (should be 2 spaces)
        assert "  " in content  # Check for indentation

    def test_load_config_handles_missing_file(self, project_settings):
        """Test that _load_config returns empty dict for missing file."""
        config = project_settings._load_config()
        assert config == {}

    def test_load_config_handles_existing_file(self, project_settings):
        """Test that _load_config loads existing configuration."""
        # Create config manually
        project_settings._ensure_config_dir()
        test_config = {"worktree_files": [".env"], "other_key": "value"}
        with open(project_settings.config_file, "w") as f:
            json.dump(test_config, f)

        # Load and verify
        loaded = project_settings._load_config()
        assert loaded == test_config

    def test_persistence_across_instances(self, temp_project_dir):
        """Test that settings persist across ProjectSettings instances."""
        # First instance
        settings1 = ProjectSettings(temp_project_dir)
        settings1.set_worktree_files(["file1", "file2"])
        settings1.set_disable_firewall(True)
        settings1.set_default_cli("claude")

        # Second instance
        settings2 = ProjectSettings(temp_project_dir)
        assert settings2.get_worktree_files() == ["file1", "file2"]
        assert settings2.get_disable_firewall() is True
        assert settings2.get_default_cli() == "claude"

    def test_nested_project_directories(self, tmp_path):
        """Test ProjectSettings in nested directory structure."""
        # Create nested structure
        parent_dir = tmp_path / "parent"
        child_dir = parent_dir / "child"
        child_dir.mkdir(parents=True)

        # Create settings for both
        parent_settings = ProjectSettings(parent_dir)
        child_settings = ProjectSettings(child_dir)

        # Set different values
        parent_settings.set_default_cli("claude")
        child_settings.set_disable_firewall(True)

        # Verify they're independent
        assert parent_settings.get_default_cli() == "claude"
        assert child_settings.get_disable_firewall() is True
        assert parent_settings.config_file != child_settings.config_file

    def test_get_worktree_files_default(self, project_settings):
        """Test getting worktree files returns default when none are set."""
        assert project_settings.get_worktree_files() == [".env", ".env.local", ".mcp"]

    def test_set_and_get_worktree_files(self, project_settings):
        """Test setting and getting worktree files."""
        files = [".env", ".secrets", "config.local"]
        project_settings.set_worktree_files(files)
        assert project_settings.get_worktree_files() == files

        # Verify persistence
        with open(project_settings.config_file) as f:
            config = json.load(f)
            assert config["worktree_files"] == files

    def test_worktree_files_persistence(self, temp_project_dir):
        """Test that worktree files persist across instances."""
        # First instance
        settings1 = ProjectSettings(temp_project_dir)
        files = [".env.local", ".mcp", "custom.config"]
        settings1.set_worktree_files(files)

        # Second instance
        settings2 = ProjectSettings(temp_project_dir)
        assert settings2.get_worktree_files() == files

    def test_empty_worktree_files(self, project_settings):
        """Test setting empty list of worktree files."""
        project_settings.set_worktree_files([])
        assert project_settings.get_worktree_files() == []

        # Verify it's stored as empty list, not using defaults
        with open(project_settings.config_file) as f:
            config = json.load(f)
            assert config["worktree_files"] == []
