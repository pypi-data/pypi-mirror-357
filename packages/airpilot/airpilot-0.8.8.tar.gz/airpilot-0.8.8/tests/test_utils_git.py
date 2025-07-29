"""Tests for git utility functions."""

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from airpilot.utils.git import init_git_if_needed


def test_init_git_if_needed_skips_existing_repo(temp_dir: Path) -> None:
    """Test that init_git_if_needed skips directories that already have .git."""
    # Create existing .git directory
    git_dir = temp_dir / ".git"
    git_dir.mkdir()

    # Mock subprocess to ensure it's not called
    with patch('subprocess.run') as mock_run:
        init_git_if_needed(temp_dir)
        mock_run.assert_not_called()


def test_init_git_if_needed_initializes_new_repo(temp_dir: Path, capsys: Any) -> None:
    """Test that init_git_if_needed initializes git in new directory."""
    # Ensure no .git directory exists
    git_dir = temp_dir / ".git"
    assert not git_dir.exists()

    # Mock successful git init
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock()
        init_git_if_needed(temp_dir)

        # Verify git init was called correctly
        mock_run.assert_called_once_with(
            ["git", "init"],
            cwd=temp_dir,
            check=True,
            capture_output=True
        )

    # Verify success message was printed
    captured = capsys.readouterr()
    assert "Git repository initialized successfully" in captured.out


def test_init_git_if_needed_handles_git_not_available(temp_dir: Path, capsys: Any) -> None:
    """Test that init_git_if_needed handles git command not available."""
    # Mock git command not found
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        init_git_if_needed(temp_dir)

    # Verify warning message was printed
    captured = capsys.readouterr()
    assert "Git not found - skipping Git initialization" in captured.out


def test_init_git_if_needed_handles_git_failure(temp_dir: Path, capsys: Any) -> None:
    """Test that init_git_if_needed handles git command failure."""
    # Mock git command failure
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "init"])
        init_git_if_needed(temp_dir)

    # Verify warning message was printed
    captured = capsys.readouterr()
    assert "Could not initialize Git (git not available)" in captured.out
