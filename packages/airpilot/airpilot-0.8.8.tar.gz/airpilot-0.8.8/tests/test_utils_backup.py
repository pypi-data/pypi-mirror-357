"""Tests for backup utility functions."""

from pathlib import Path
from typing import Any
from unittest.mock import patch

from airpilot.utils.backup import (
    backup_ai_vendors,
    backup_existing_air,
    detect_air_standard,
)


def test_backup_existing_air_creates_timestamped_backup(temp_dir: Path) -> None:
    """Test that backup_existing_air creates a proper timestamped backup."""
    # Create source .air directory with content
    air_dir = temp_dir / ".air"
    air_dir.mkdir()
    test_file = air_dir / "test.txt"
    test_file.write_text("test content")

    # Mock time.time to get predictable timestamp
    with patch('time.time', return_value=1234567890):
        backup_path = backup_existing_air(air_dir)

    # Verify backup was created correctly
    assert backup_path.name == ".air.backup.1234567890"
    assert backup_path.exists()
    assert backup_path.is_dir()
    assert (backup_path / "test.txt").read_text() == "test content"

    # Verify original was moved (not copied)
    assert not air_dir.exists()


def test_backup_ai_vendors_with_existing_vendors(temp_dir: Path, capsys: Any) -> None:
    """Test backup_ai_vendors detects and reports existing vendor directories."""
    # Create some AI vendor directories
    claude_dir = temp_dir / ".claude"
    claude_dir.mkdir()
    cursor_dir = temp_dir / ".cursor"
    cursor_dir.mkdir()
    copilot_dir = temp_dir / ".github" / "copilot-instructions"
    copilot_dir.mkdir(parents=True)

    # Call function
    backup_ai_vendors(temp_dir)

    # Verify output was printed (checking console output via capsys)
    captured = capsys.readouterr()
    assert "Found existing AI vendor directories" in captured.out
    assert ".claude" in captured.out
    assert ".cursor" in captured.out
    assert ".github/copilot-instructions" in captured.out


def test_backup_ai_vendors_with_no_vendors(temp_dir: Path, capsys: Any) -> None:
    """Test backup_ai_vendors handles empty directory correctly."""
    backup_ai_vendors(temp_dir)

    # Should not print anything if no vendors found
    captured = capsys.readouterr()
    assert captured.out == ""


def test_detect_air_standard_with_standard_structure(temp_dir: Path) -> None:
    """Test detect_air_standard correctly identifies standard .air structure."""
    air_dir = temp_dir / ".air"
    air_dir.mkdir()

    # Create standard structure indicators
    rules_dir = air_dir / "rules"
    rules_dir.mkdir()
    rules_index = rules_dir / "index.md"
    rules_index.write_text("# Rules")

    assert detect_air_standard(air_dir) is True


def test_detect_air_standard_with_non_standard_structure(temp_dir: Path) -> None:
    """Test detect_air_standard correctly identifies non-standard .air structure."""
    air_dir = temp_dir / ".air"
    air_dir.mkdir()

    # Create non-standard structure (missing rules/index.md)
    random_file = air_dir / "random.txt"
    random_file.write_text("random content")

    assert detect_air_standard(air_dir) is False


def test_detect_air_standard_with_nonexistent_directory(temp_dir: Path) -> None:
    """Test detect_air_standard handles non-existent directory."""
    non_existent = temp_dir / "does_not_exist"

    assert detect_air_standard(non_existent) is False
