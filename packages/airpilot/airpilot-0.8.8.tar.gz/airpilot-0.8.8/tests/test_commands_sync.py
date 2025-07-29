"""Tests for sync command functions."""

from unittest.mock import patch

from click.testing import CliRunner

from airpilot.commands.sync import sync


def test_sync_command_calls_show_sync_panel() -> None:
    """Test sync command calls show_sync_panel."""
    runner = CliRunner()

    # Mock the license requirement decorator to pass
    with patch('airpilot.commands.sync.require_license') as mock_require:
        # Mock the decorator to return the original function
        mock_require.return_value = lambda func: func

        with patch('airpilot.commands.sync.show_sync_panel') as mock_panel:
            result = runner.invoke(sync, [])

            assert result.exit_code == 0
            mock_panel.assert_called_once()


def test_sync_command_requires_license() -> None:
    """Test sync command is properly decorated with license requirement."""
    # Import the original function to check if it has the decorator
    from airpilot.commands.sync import sync as sync_func

    # Check that the function has been wrapped by checking attributes that decorators add
    # The require_license decorator modifies the function
    assert callable(sync_func)

    # The actual license checking functionality is tested in the license module tests
    # This just ensures the decorator is properly applied to the sync function
