"""Test PyArmour package imports."""

import pytest
import pyarmour


def test_api_export() -> None:
    """Test that all public API functions are exported."""
    assert "adversarial_test" in pyarmour.__all__
    assert "cli" in pyarmour.__all__


def test_version() -> None:
    """Test package version."""
    assert hasattr(pyarmour, "__version__")
    assert isinstance(pyarmour.__version__, str)
