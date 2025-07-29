"""Tests for UI panel functions."""

from pathlib import Path
from typing import Any

from airpilot.ui.panels import (
    show_backup_panel,
    show_error_panel,
    show_git_panel,
    show_license_help_panel,
    show_license_status_panel,
    show_main_help_panel,
    show_scaffolding_panel,
    show_success_panel,
    show_sync_panel,
    show_version_panel,
)


def test_show_version_panel_displays_version(capsys: Any) -> None:
    """Test show_version_panel displays version information."""
    show_version_panel()

    captured = capsys.readouterr()
    assert "AirPilot CLI" in captured.out
    assert "Version:" in captured.out
    assert "Universal Intelligence Control" in captured.out


def test_show_main_help_panel_displays_help(capsys: Any) -> None:
    """Test show_main_help_panel displays main help information."""
    show_main_help_panel()

    captured = capsys.readouterr()
    assert "AirPilot - Universal Intelligence Control" in captured.out
    assert "air init" in captured.out
    assert "air license" in captured.out
    assert "air sync" in captured.out
    assert "Premium: Real-time vendor sync" in captured.out


def test_show_success_panel_displays_message(capsys: Any) -> None:
    """Test show_success_panel displays success message."""
    test_message = "Operation completed successfully"
    show_success_panel(test_message)

    captured = capsys.readouterr()
    assert test_message in captured.out
    assert "Success" in captured.out


def test_show_error_panel_displays_message(capsys: Any) -> None:
    """Test show_error_panel displays error message."""
    test_message = "Something went wrong"
    show_error_panel(test_message)

    captured = capsys.readouterr()
    assert test_message in captured.out
    assert "Error" in captured.out


def test_show_license_status_panel_for_licensed_user(capsys: Any) -> None:
    """Test show_license_status_panel for licensed user."""
    license_info = {
        'plan': 'poc',
        'licensed': True,
        'features': ['init', 'sync', 'cloud']
    }

    show_license_status_panel(license_info)

    captured = capsys.readouterr()
    assert "Plan: poc" in captured.out
    assert "Status: Active" in captured.out
    assert "init" in captured.out
    assert "sync" in captured.out
    assert "cloud" in captured.out


def test_show_license_status_panel_for_free_user(capsys: Any) -> None:
    """Test show_license_status_panel for free user."""
    license_info = {
        'plan': 'free',
        'licensed': False,
        'features': ['init']
    }

    show_license_status_panel(license_info)

    captured = capsys.readouterr()
    assert "Plan: free" in captured.out
    assert "Status: Free Plan" in captured.out
    assert "init" in captured.out


def test_show_license_status_panel_handles_empty_features(capsys: Any) -> None:
    """Test show_license_status_panel handles empty features list."""
    license_info = {
        'plan': 'free',
        'licensed': False,
        'features': []
    }

    show_license_status_panel(license_info)

    captured = capsys.readouterr()
    assert "Basic initialization and configuration" in captured.out


def test_show_license_help_panel_displays_instructions(capsys: Any) -> None:
    """Test show_license_help_panel displays licensing instructions."""
    show_license_help_panel()

    captured = capsys.readouterr()
    assert "AirPilot Licensing" in captured.out
    assert "shaneholloman@gmail.com" in captured.out
    assert "air license install" in captured.out
    assert "AIRPILOT_POC_LICENSE" in captured.out


def test_show_sync_panel_displays_premium_info(capsys: Any) -> None:
    """Test show_sync_panel displays premium sync information."""
    show_sync_panel()

    captured = capsys.readouterr()
    assert "Premium Sync Feature" in captured.out
    assert "Congratulations!" in captured.out
    assert "Monitors your .air directory" in captured.out
    assert "real-time updates" in captured.out


def test_show_scaffolding_panel_displays_progress(capsys: Any, temp_dir: Path) -> None:
    """Test show_scaffolding_panel displays scaffolding progress."""
    air_dir = temp_dir / ".air"
    show_scaffolding_panel(air_dir)

    captured = capsys.readouterr()
    assert "Creating .air standard structure" in captured.out
    assert str(air_dir) in captured.out
    assert "Universal Intelligence Control" in captured.out


def test_show_git_panel_success_message(capsys: Any) -> None:
    """Test show_git_panel displays success message correctly."""
    show_git_panel("Git repository initialized successfully", "Git Initialized")

    captured = capsys.readouterr()
    assert "Git repository initialized successfully" in captured.out
    assert "Git Initialized" in captured.out


def test_show_git_panel_warning_message(capsys: Any) -> None:
    """Test show_git_panel displays warning message correctly."""
    show_git_panel("Git not found", "Git Warning")

    captured = capsys.readouterr()
    assert "Git not found" in captured.out
    assert "Git Warning" in captured.out


def test_show_backup_panel_displays_message(capsys: Any) -> None:
    """Test show_backup_panel displays backup message."""
    test_message = "Found existing directories"
    show_backup_panel(test_message)

    captured = capsys.readouterr()
    assert test_message in captured.out
    assert "Backup" in captured.out
