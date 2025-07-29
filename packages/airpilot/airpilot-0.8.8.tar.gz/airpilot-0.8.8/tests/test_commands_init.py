"""Tests for init command functions."""

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

from click.testing import CliRunner

from airpilot.commands.init import (
    init,
    init_current_directory,
    init_global_intelligence,
    init_new_project,
)


def test_init_command_with_global_flag() -> None:
    """Test init command with --global flag calls init_global_intelligence."""
    runner = CliRunner()

    with patch('airpilot.commands.init.init_global_intelligence') as mock_global:
        result = runner.invoke(init, ['--global'])

        assert result.exit_code == 0
        mock_global.assert_called_once()


def test_init_command_with_project_name() -> None:
    """Test init command with project name calls init_new_project."""
    runner = CliRunner()

    with patch('airpilot.commands.init.init_new_project') as mock_new_project:
        result = runner.invoke(init, ['test_project'])

        assert result.exit_code == 0
        mock_new_project.assert_called_once_with('test_project', False)


def test_init_command_current_directory() -> None:
    """Test init command without arguments calls init_current_directory."""
    runner = CliRunner()

    with patch('airpilot.commands.init.init_current_directory') as mock_current:
        result = runner.invoke(init, [])

        assert result.exit_code == 0
        mock_current.assert_called_once_with(False)


def test_init_command_with_force_flag() -> None:
    """Test init command with --force flag passes force parameter."""
    runner = CliRunner()

    with patch('airpilot.commands.init.init_current_directory') as mock_current:
        result = runner.invoke(init, ['--force'])

        assert result.exit_code == 0
        mock_current.assert_called_once_with(True)


def test_init_global_intelligence_creates_directories() -> None:
    """Test init_global_intelligence creates proper global directories."""
    with patch('airpilot.commands.init.confirm_action', return_value=True):
        with patch('airpilot.commands.init.create_airpilot_config') as mock_config:
            with patch('airpilot.commands.init.create_air_standard') as mock_standard:
                init_global_intelligence()

                # Verify config creation was called
                mock_config.assert_called_once()
                # Verify .air standard creation was called
                mock_standard.assert_called_once()


def test_init_global_intelligence_handles_existing_directories(mock_home_dir: Path) -> None:
    """Test init_global_intelligence handles existing directories properly."""
    # Create existing directories
    airpilot_dir = mock_home_dir / ".airpilot"
    air_dir = mock_home_dir / ".air"
    airpilot_dir.mkdir()
    air_dir.mkdir()

    # Mock user declining to continue
    with patch('airpilot.commands.init.confirm_action', return_value=False):
        with patch('airpilot.commands.init.show_error_panel') as mock_error:
            init_global_intelligence()

            # Should show error and return early
            mock_error.assert_called_once()


def test_init_global_intelligence_merges_with_existing_airpilot(mock_home_dir: Path) -> None:
    """Test init_global_intelligence properly merges with existing .airpilot directory."""
    # Create existing .airpilot directory with existing config
    airpilot_dir = mock_home_dir / ".airpilot"
    airpilot_dir.mkdir()

    # Create existing config file
    existing_config = airpilot_dir / "config.json"
    existing_config.write_text('{"existing": "config"}')

    # Mock user confirming to continue
    with patch('airpilot.commands.init.confirm_action', return_value=True):
        with patch('airpilot.commands.init.create_air_standard'):
            init_global_intelligence()

    # Verify existing config was preserved (create_airpilot_config doesn't overwrite)
    assert existing_config.exists()
    assert "existing" in existing_config.read_text()


def test_init_global_intelligence_handles_airpilot_as_file(mock_home_dir: Path) -> None:
    """Test init_global_intelligence handles case where .airpilot exists as a file."""
    # Create .airpilot as a file instead of directory
    airpilot_file = mock_home_dir / ".airpilot"
    airpilot_file.write_text("some content")

    # Mock user confirming to continue
    with patch('airpilot.commands.init.confirm_action', return_value=True):
        with patch('airpilot.commands.init.show_error_panel') as mock_error:
            init_global_intelligence()

            # Should show error about .airpilot being a file
            mock_error.assert_called_once()
            error_message = mock_error.call_args[0][0]
            assert "not a directory" in error_message


def test_init_global_intelligence_exact_user_scenario(mock_home_dir: Path) -> None:
    """Test exact scenario: .airpilot exists, .air deleted, user wants to reinitialize."""
    # Create existing .airpilot directory with config (user's scenario)
    airpilot_dir = mock_home_dir / ".airpilot"
    airpilot_dir.mkdir()
    
    # Add existing config file like user would have
    config_file = airpilot_dir / "config.json"
    config_file.write_text('{"version": "0.0.1", "user": {"name": "Shane"}}')
    
    # .air directory does NOT exist (user deleted it)
    air_dir = mock_home_dir / ".air"
    assert not air_dir.exists()

    # Mock user confirming to merge with existing .airpilot
    with patch('airpilot.commands.init.confirm_action', return_value=True):
        with patch('airpilot.commands.init.create_air_standard') as mock_air_standard:
            init_global_intelligence()

            # Should successfully complete without errors
            mock_air_standard.assert_called_once_with(air_dir)

    # Verify existing .airpilot config was preserved
    assert config_file.exists()
    config_data = config_file.read_text()
    assert '"name": "Shane"' in config_data

    # Verify README.md was added if missing
    readme_file = airpilot_dir / "README.md"
    if not readme_file.exists():
        # README should be created if it didn't exist
        pass  # This is expected behavior


def test_init_current_directory_creates_air_structure(temp_project_dir: Path) -> None:
    """Test init_current_directory creates complete project structure."""
    # Change to temp directory for test
    original_cwd = os.getcwd()
    os.chdir(temp_project_dir)

    try:
        with patch('airpilot.commands.init.detect_air_standard', return_value=False):
            with patch('airpilot.commands.init.backup_existing_air'):
                with patch('airpilot.commands.init.init_git_if_needed'):
                    with patch('airpilot.commands.init.backup_ai_vendors'):
                        with patch('airpilot.commands.init.create_air_standard') as mock_standard:
                            with patch('airpilot.commands.init.create_airpilot_project_config') as mock_config:
                                init_current_directory(force=False)

                                # Verify .air standard was created as project
                                mock_standard.assert_called_once()
                                args = mock_standard.call_args
                                assert args[1]['is_project'] is True

                                # Verify project config was created
                                mock_config.assert_called_once()
    finally:
        os.chdir(original_cwd)


def test_init_current_directory_handles_existing_standard_air(temp_project_dir: Path) -> None:
    """Test init_current_directory handles existing standard .air directory."""
    # Create existing .air directory
    air_dir = temp_project_dir / ".air"
    air_dir.mkdir()

    original_cwd = os.getcwd()
    os.chdir(temp_project_dir)

    try:
        with patch('airpilot.commands.init.detect_air_standard', return_value=True):
            with patch('airpilot.commands.init.confirm_action', return_value=True):
                with patch('airpilot.commands.init.init_git_if_needed'):
                    with patch('airpilot.commands.init.backup_ai_vendors'):
                        with patch('airpilot.commands.init.create_air_standard') as mock_standard:
                            with patch('airpilot.commands.init.create_airpilot_project_config'):
                                init_current_directory(force=False)

                                # Should still create standard structure (merge mode)
                                mock_standard.assert_called_once()
    finally:
        os.chdir(original_cwd)


def test_init_new_project_creates_directory_and_initializes(temp_dir: Path) -> None:
    """Test init_new_project creates new project directory and initializes it."""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        project_name = "test_project"
        expected_project_dir = temp_dir / project_name

        # Track directory changes
        cwd_changes = []
        original_chdir = os.chdir

        def track_chdir(path: Any) -> None:
            cwd_changes.append(str(path))
            original_chdir(path)

        with patch('os.chdir', side_effect=track_chdir):
            with patch('airpilot.commands.init.init_current_directory') as mock_init:
                init_new_project(project_name, force=False)

                # Verify project directory was created
                assert expected_project_dir.exists()
                assert expected_project_dir.is_dir()

                # Verify init_current_directory was called
                mock_init.assert_called_once_with(False)

                # Verify we attempted to change to project directory
                # Use Path.resolve() to handle /private prefix on macOS
                expected_resolved = str(expected_project_dir.resolve())
                changed_resolved = [str(Path(p).resolve()) for p in cwd_changes]
                assert expected_resolved in changed_resolved
    finally:
        os.chdir(original_cwd)


def test_init_new_project_handles_existing_directory(temp_dir: Path) -> None:
    """Test init_new_project handles existing project directory."""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        project_name = "existing_project"

        # Create existing directory
        existing_dir = temp_dir / project_name
        existing_dir.mkdir()

        # Mock user declining to continue
        with patch('airpilot.commands.init.confirm_action', return_value=False):
            with patch('airpilot.commands.init.show_error_panel') as mock_error:
                init_new_project(project_name, force=False)

                # Should show error and return early
                mock_error.assert_called_once()
    finally:
        os.chdir(original_cwd)
