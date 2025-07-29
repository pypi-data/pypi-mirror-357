"""Tests for UI prompt functions."""

from unittest.mock import patch

from airpilot.ui.prompts import confirm_action, confirm_merge, confirm_overwrite


def test_confirm_action_returns_user_response() -> None:
    """Test confirm_action returns user response."""
    with patch('airpilot.ui.prompts.Confirm.ask', return_value=True) as mock_ask:
        result = confirm_action("Do you want to continue?")

        assert result is True
        mock_ask.assert_called_once_with("Do you want to continue?")


def test_confirm_action_handles_negative_response() -> None:
    """Test confirm_action handles negative user response."""
    with patch('airpilot.ui.prompts.Confirm.ask', return_value=False) as mock_ask:
        result = confirm_action("Do you want to continue?")

        assert result is False
        mock_ask.assert_called_once_with("Do you want to continue?")


def test_confirm_overwrite_formats_message_correctly() -> None:
    """Test confirm_overwrite formats message with path."""
    with patch('airpilot.ui.prompts.Confirm.ask', return_value=True) as mock_ask:
        result = confirm_overwrite("/path/to/file")

        assert result is True
        mock_ask.assert_called_once_with("Overwrite existing /path/to/file?")


def test_confirm_merge_formats_message_correctly() -> None:
    """Test confirm_merge formats message with directory name."""
    with patch('airpilot.ui.prompts.Confirm.ask', return_value=False) as mock_ask:
        result = confirm_merge("project_dir")

        assert result is False
        mock_ask.assert_called_once_with("Merge with existing project_dir directory?")
