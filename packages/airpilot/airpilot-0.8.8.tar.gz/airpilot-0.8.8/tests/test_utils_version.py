"""Tests for version utility functions."""

from airpilot.utils.version import get_version


def test_get_version_returns_string() -> None:
    """Test that get_version returns a valid version string."""
    version = get_version()

    assert isinstance(version, str)
    assert len(version) > 0
    assert "." in version  # Should have dot notation like "0.6.5"


def test_get_version_consistent() -> None:
    """Test that get_version returns consistent results."""
    version1 = get_version()
    version2 = get_version()

    assert version1 == version2
