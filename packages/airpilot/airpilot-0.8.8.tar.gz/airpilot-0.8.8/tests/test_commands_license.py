"""Tests for license command functions."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from airpilot.commands.license import help as license_help
from airpilot.commands.license import install, license, remove, status


def test_license_command_without_subcommand_shows_status() -> None:
    """Test license command without subcommand shows license status."""
    runner = CliRunner()

    mock_license_info = {
        'plan': 'poc',
        'licensed': True,
        'features': ['init', 'sync']
    }

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = MagicMock()
        mock_instance.get_license_info.return_value = mock_license_info
        mock_manager.return_value = mock_instance

        with patch('airpilot.commands.license.show_license_status_panel') as mock_panel:
            result = runner.invoke(license, [])

            assert result.exit_code == 0
            mock_panel.assert_called_once_with(mock_license_info)


def test_license_command_shows_premium_info_for_unlicensed() -> None:
    """Test license command shows premium feature info for unlicensed users."""
    runner = CliRunner()

    mock_license_info = {
        'plan': 'free',
        'licensed': False,
        'features': ['init']
    }

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = MagicMock()
        mock_instance.get_license_info.return_value = mock_license_info
        mock_manager.return_value = mock_instance

        with patch('airpilot.commands.license.show_license_status_panel'):
            result = runner.invoke(license, [])

            assert result.exit_code == 0
            # Should show premium features info
            assert "Premium Features Available" in result.output


def test_install_command_with_valid_key() -> None:
    """Test install command with valid license key."""
    runner = CliRunner()

    mock_license_info = {
        'plan': 'poc',
        'licensed': True,
        'features': ['init', 'sync']
    }

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = MagicMock()
        mock_instance.install_license.return_value = True
        mock_instance.get_license_info.return_value = mock_license_info
        mock_manager.return_value = mock_instance

        result = runner.invoke(install, ['airpilot-poc-test123-test456'])

        assert result.exit_code == 0
        mock_instance.install_license.assert_called_once_with('airpilot-poc-test123-test456')
        assert "SUCCESS: License installed!" in result.output


def test_install_command_with_invalid_key() -> None:
    """Test install command with invalid license key."""
    runner = CliRunner()

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = MagicMock()
        mock_instance.install_license.return_value = False
        mock_manager.return_value = mock_instance

        result = runner.invoke(install, ['invalid-key'])

        assert result.exit_code == 0
        mock_instance.install_license.assert_called_once_with('invalid-key')
        assert "Invalid license key" in result.output


def test_remove_command_with_confirmation() -> None:
    """Test remove command when user confirms removal."""
    runner = CliRunner()

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = MagicMock()
        mock_instance.remove_license.return_value = True
        mock_manager.return_value = mock_instance

        with patch('airpilot.commands.license.confirm_action', return_value=True):
            result = runner.invoke(remove, [])

            assert result.exit_code == 0
            mock_instance.remove_license.assert_called_once()
            assert "License removed successfully" in result.output


def test_remove_command_without_confirmation() -> None:
    """Test remove command when user cancels removal."""
    runner = CliRunner()

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance

        with patch('airpilot.commands.license.confirm_action', return_value=False):
            result = runner.invoke(remove, [])

            assert result.exit_code == 0
            # Should not call remove_license if user cancels
            mock_instance.remove_license.assert_not_called()


def test_remove_command_handles_removal_failure() -> None:
    """Test remove command handles license removal failure."""
    runner = CliRunner()

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = MagicMock()
        mock_instance.remove_license.return_value = False
        mock_manager.return_value = mock_instance

        with patch('airpilot.commands.license.confirm_action', return_value=True):
            result = runner.invoke(remove, [])

            assert result.exit_code == 0
            assert "Failed to remove license" in result.output


def test_status_command_shows_detailed_info() -> None:
    """Test status command shows detailed license information."""
    runner = CliRunner()

    mock_license_info = {
        'plan': 'poc',
        'licensed': True,
        'features': ['init', 'sync']
    }

    with patch('airpilot.commands.license.LicenseManager') as mock_manager:
        mock_instance = MagicMock()
        mock_instance.get_license_info.return_value = mock_license_info
        mock_manager.return_value = mock_instance

        result = runner.invoke(status, [])

        assert result.exit_code == 0
        # Should show both free and premium features
        assert "Free Features" in result.output
        assert "Premium Features" in result.output
        assert "air init" in result.output
        assert "air sync" in result.output


def test_help_command_calls_help_panel() -> None:
    """Test help command calls show_license_help_panel."""
    runner = CliRunner()

    with patch('airpilot.commands.license.show_license_help_panel') as mock_help:
        result = runner.invoke(license_help, [])

        assert result.exit_code == 0
        mock_help.assert_called_once()
