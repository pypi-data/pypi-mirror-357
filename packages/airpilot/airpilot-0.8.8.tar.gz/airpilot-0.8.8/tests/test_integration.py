"""Integration tests for the complete AirPilot CLI."""

import os
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from airpilot.cli import cli


def test_cli_version_flag() -> None:
    """Test CLI --version flag displays version information."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])

    assert result.exit_code == 0
    assert "AirPilot CLI" in result.output
    assert "Version:" in result.output
    assert "Universal Intelligence Control" in result.output


def test_cli_no_command_shows_help() -> None:
    """Test CLI without command shows main help panel."""
    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert result.exit_code == 0
    assert "AirPilot - Universal Intelligence Control" in result.output
    assert "air init" in result.output
    assert "air license" in result.output
    assert "air sync" in result.output


def test_cli_init_command_integration() -> None:
    """Test CLI init command integration."""
    runner = CliRunner()

    with patch('airpilot.commands.init.init_current_directory') as mock_init:
        result = runner.invoke(cli, ['init'])

        assert result.exit_code == 0
        mock_init.assert_called_once_with(False)


def test_cli_init_global_integration() -> None:
    """Test CLI init --global command integration."""
    runner = CliRunner()

    with patch('airpilot.commands.init.init_global_intelligence') as mock_global:
        result = runner.invoke(cli, ['init', '--global'])

        assert result.exit_code == 0
        mock_global.assert_called_once()


def test_cli_init_project_integration() -> None:
    """Test CLI init <project> command integration."""
    runner = CliRunner()

    with patch('airpilot.commands.init.init_new_project') as mock_project:
        result = runner.invoke(cli, ['init', 'test_project'])

        assert result.exit_code == 0
        mock_project.assert_called_once_with('test_project', False)


def test_cli_license_command_integration() -> None:
    """Test CLI license command integration."""
    runner = CliRunner()

    mock_license_info = {
        'plan': 'free',
        'licensed': False,
        'features': ['init']
    }

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = mock_manager.return_value
        mock_instance.get_license_info.return_value = mock_license_info

        result = runner.invoke(cli, ['license'])

        assert result.exit_code == 0
        assert "Plan:" in result.output


def test_cli_license_install_integration() -> None:
    """Test CLI license install command integration."""
    runner = CliRunner()

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = mock_manager.return_value
        mock_instance.install_license.return_value = True
        mock_instance.get_license_info.return_value = {
            'plan': 'poc',
            'licensed': True,
            'features': ['init', 'sync']
        }

        result = runner.invoke(cli, ['license', 'install', 'test-key'])

        assert result.exit_code == 0
        mock_instance.install_license.assert_called_once_with('test-key')


def test_cli_sync_command_integration() -> None:
    """Test CLI sync command integration."""
    runner = CliRunner()

    # Mock the license requirement to pass
    with patch('airpilot.commands.sync.require_license') as mock_require:
        mock_require.return_value = lambda func: func

        with patch('airpilot.commands.sync.show_sync_panel') as mock_panel:
            result = runner.invoke(cli, ['sync'])

            assert result.exit_code == 0
            mock_panel.assert_called_once()


def test_cli_error_handling() -> None:
    """Test CLI error handling for invalid commands."""
    runner = CliRunner()
    result = runner.invoke(cli, ['invalid-command'])

    # Should exit with error and show Panel UI
    assert result.exit_code != 0
    # Must use Panel UI
    assert "╭" in result.output and "╰" in result.output
    assert "Command Not Found" in result.output
    assert "Unknown command 'invalid-command'" in result.output


def test_full_init_workflow_integration(tmp_path: Path) -> None:
    """Test complete init workflow creates proper directory structure."""
    runner = CliRunner()

    # Change to temp directory for test
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Mock all the external dependencies but let the real structure creation happen
        with patch('airpilot.commands.init.init_git_if_needed'):
            with patch('airpilot.commands.init.backup_ai_vendors'):
                with patch('airpilot.commands.init.detect_air_standard', return_value=False):
                    with patch('airpilot.builders.scaffold.show_scaffolding_panel'):
                        result = runner.invoke(cli, ['init'])

                        assert result.exit_code == 0

                        # Verify .air directory was created
                        air_dir = tmp_path / ".air"
                        assert air_dir.exists()

                        # Verify core structure exists
                        assert (air_dir / "rules").exists()
                        assert (air_dir / "domains").exists()
                        assert (air_dir / "README.md").exists()

                        # Verify project config was created
                        assert (tmp_path / ".airpilot").exists()
    finally:
        os.chdir(original_cwd)
