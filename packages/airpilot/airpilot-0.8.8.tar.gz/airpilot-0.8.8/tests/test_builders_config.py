"""Tests for configuration builder functions."""

import json
from pathlib import Path

from airpilot.builders.config import (
    create_airpilot_project_config,
)


def test_create_airpilot_project_config_creates_valid_config(temp_dir: Path) -> None:
    """Test that create_airpilot_project_config creates valid project configuration."""
    create_airpilot_project_config(temp_dir)

    airpilot_file = temp_dir / ".airpilot"
    assert airpilot_file.exists()

    config_data = json.loads(airpilot_file.read_text())

    # Verify essential configuration keys
    assert config_data["enabled"] is True
    assert config_data["source"] == ".air/rules/"
    assert config_data["sourceIsDirectory"] is True
    assert config_data["indexFileName"] == "index.md"
    assert config_data["defaultFormat"] == "markdown"
    assert config_data["autoSync"] is True
    assert config_data["showStatus"] is True

    # Verify vendors configuration
    assert "vendors" in config_data
    vendors = config_data["vendors"]
    assert "claude" in vendors
    assert "copilot" in vendors

    # Verify vendor structure
    claude_config = vendors["claude"]
    assert claude_config["enabled"] is True
    assert claude_config["path"] == ".claude/"
    assert claude_config["format"] == "markdown"
    assert claude_config["isDirectory"] is True


# REMOVED TESTS: create_air_config_file tests
# These tested the architectural violation of putting .airpilot files 
# inside .air directories. CRITICAL: .airpilot files must NEVER
# be placed inside .air directories.
