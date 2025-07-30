import subprocess
from unittest.mock import patch

from typer.testing import CliRunner

from evo.main import app

runner = CliRunner()


def test_branch_name_with_space():
    """Test that branch names with spaces are rejected."""
    result = runner.invoke(app, ["dev", "feature branch"])
    assert result.exit_code == 1
    assert "Branch name cannot contain ' '" in result.output


def test_branch_name_with_invalid_chars():
    """Test that branch names with invalid characters are rejected."""
    invalid_names = [
        "feature~branch",
        "feature^branch",
        "feature:branch",
        "feature?branch",
        "feature*branch",
        "feature[branch",
        "feature\\branch",
        "feature..branch",
    ]

    for name in invalid_names:
        result = runner.invoke(app, ["dev", name])
        assert result.exit_code == 1
        assert "Branch name cannot contain" in result.output


def test_branch_name_starting_with_dot():
    """Test that branch names starting with dot are rejected."""
    result = runner.invoke(app, ["dev", ".feature"])
    assert result.exit_code == 1
    assert "Branch name cannot start with '.'" in result.output


def test_branch_name_ending_with_slash():
    """Test that branch names ending with slash are rejected."""
    result = runner.invoke(app, ["dev", "feature/"])
    assert result.exit_code == 1
    assert "Branch name cannot end with '/'" in result.output


def test_branch_name_ending_with_lock():
    """Test that branch names ending with .lock are rejected."""
    result = runner.invoke(app, ["dev", "feature.lock"])
    assert result.exit_code == 1
    assert "Branch name cannot end with '.lock'" in result.output


def test_empty_branch_name():
    """Test that empty branch names are rejected."""
    result = runner.invoke(app, ["dev", ""])
    assert result.exit_code == 1
    assert "Branch name cannot be empty" in result.output


def test_valid_branch_names():
    """Test that valid branch names are accepted (up to git check)."""
    valid_names = ["feature/new-feature", "bugfix/issue-123", "release-1.0.0", "hotfix_urgent", "user@feature"]

    # Mock git command to simulate not being in a repository
    with patch("subprocess.check_output") as mock_check_output:
        mock_check_output.side_effect = subprocess.CalledProcessError(128, "git")

        for name in valid_names:
            result = runner.invoke(app, ["dev", name])
            # Should fail at git repository check, not at validation
            assert "Branch name cannot" not in result.output
            assert "Not in a Git repository" in result.output
