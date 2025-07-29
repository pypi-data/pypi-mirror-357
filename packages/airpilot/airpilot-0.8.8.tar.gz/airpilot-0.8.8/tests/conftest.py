"""Shared test fixtures and configuration."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Provide a temporary project directory with realistic structure."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_dir = Path(tmp_dir) / "test_project"
        project_dir.mkdir()
        yield project_dir


@pytest.fixture
def mock_home_dir(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Mock user home directory for testing global operations."""
    home_dir = temp_dir / "mock_home"
    home_dir.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home_dir)
    return home_dir
