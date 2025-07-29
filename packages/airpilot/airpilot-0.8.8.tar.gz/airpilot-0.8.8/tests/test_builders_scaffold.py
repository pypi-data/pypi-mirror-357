"""Tests for scaffolding builder functions."""

from pathlib import Path
from unittest.mock import patch

from airpilot.builders.scaffold import (
    create_air_readme,
    create_air_standard,
    create_project_context,
)


def test_create_air_standard_creates_complete_structure(temp_dir: Path) -> None:
    """Test that create_air_standard creates complete .air directory structure."""
    air_dir = temp_dir / ".air"

    # Mock the UI panel to avoid console output during testing
    with patch('airpilot.builders.scaffold.show_scaffolding_panel'):
        create_air_standard(air_dir, is_project=True)

    # Verify main directory was created
    assert air_dir.exists()
    assert air_dir.is_dir()

    # Verify core directories exist
    assert (air_dir / "rules").exists()
    assert (air_dir / "prompts").exists()
    assert (air_dir / "workflows").exists()
    assert (air_dir / "frameworks").exists()
    assert (air_dir / "tools").exists()
    assert (air_dir / "domains").exists()

    # Verify project-specific context directory
    assert (air_dir / "context").exists()

    # Verify configuration files
    assert (air_dir / ".airpilot").exists()
    assert (air_dir / "README.md").exists()

    # Verify domain structure
    assert (air_dir / "domains" / "software").exists()
    assert (air_dir / "domains" / "health").exists()
    assert (air_dir / "domains" / "legal").exists()


def test_create_air_standard_global_vs_project(temp_dir: Path) -> None:
    """Test differences between global and project .air standard creation."""
    with patch('airpilot.builders.scaffold.show_scaffolding_panel'):
        # Create global .air
        global_air = temp_dir / "global_air"
        create_air_standard(global_air, is_project=False)

        # Create project .air
        project_air = temp_dir / "project_air"
        create_air_standard(project_air, is_project=True)

    # Global should NOT have context directory
    assert not (global_air / "context").exists()

    # Project should have context directory
    assert (project_air / "context").exists()

    # Both should have core structure
    for air_dir in [global_air, project_air]:
        assert (air_dir / "rules").exists()
        assert (air_dir / "domains").exists()
        assert (air_dir / "README.md").exists()


def test_create_air_readme_content_differences(temp_dir: Path) -> None:
    """Test that create_air_readme generates different content for global vs project."""
    # Test project README
    project_dir = temp_dir / "project"
    project_dir.mkdir()
    create_air_readme(project_dir, is_project=True)

    project_readme = (project_dir / "README.md").read_text()
    assert "Project Intelligence Control" in project_readme
    assert "context/" in project_readme
    assert "Project-level" in project_readme

    # Test global README
    global_dir = temp_dir / "global"
    global_dir.mkdir()
    create_air_readme(global_dir, is_project=False)

    global_readme = (global_dir / "README.md").read_text()
    assert "Global Intelligence Control" in global_readme
    assert "Global" in global_readme
    assert "context/" not in global_readme  # Global doesn't mention context


def test_create_air_readme_skips_existing(temp_dir: Path) -> None:
    """Test that create_air_readme doesn't overwrite existing README."""
    air_dir = temp_dir / ".air"
    air_dir.mkdir()

    # Create existing README
    readme_file = air_dir / "README.md"
    custom_content = "# Custom README Content"
    readme_file.write_text(custom_content)

    create_air_readme(air_dir, is_project=True)

    # Verify existing content was preserved
    assert readme_file.read_text() == custom_content


def test_create_project_context_creates_files(temp_dir: Path) -> None:
    """Test that create_project_context creates proper context files."""
    air_dir = temp_dir / ".air"
    air_dir.mkdir()

    create_project_context(air_dir)

    context_dir = air_dir / "context"
    assert context_dir.exists()
    assert context_dir.is_dir()

    # Verify context files were created
    active_focus = context_dir / "active-focus.md"
    history = context_dir / "history.md"

    assert active_focus.exists()
    assert history.exists()

    # Verify file content structure
    active_content = active_focus.read_text()
    assert "# Active Focus" in active_content
    assert "Current Sprint" in active_content
    assert "Primary Objectives" in active_content

    history_content = history.read_text()
    assert "# Project Timeline and Decisions" in history_content
    assert "Project Overview" in history_content
    assert "Decision Log" in history_content


def test_create_project_context_skips_existing_files(temp_dir: Path) -> None:
    """Test that create_project_context doesn't overwrite existing context files."""
    air_dir = temp_dir / ".air"
    context_dir = air_dir / "context"
    context_dir.mkdir(parents=True)

    # Create existing files with custom content
    active_focus = context_dir / "active-focus.md"
    history = context_dir / "history.md"

    custom_focus = "# Custom Focus Content"
    custom_history = "# Custom History Content"

    active_focus.write_text(custom_focus)
    history.write_text(custom_history)

    create_project_context(air_dir)

    # Verify existing content was preserved
    assert active_focus.read_text() == custom_focus
    assert history.read_text() == custom_history
