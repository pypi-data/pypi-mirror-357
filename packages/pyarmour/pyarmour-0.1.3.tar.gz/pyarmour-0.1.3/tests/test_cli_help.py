"""Test PyArmour CLI help output."""

import pytest
import click
from click.testing import CliRunner

from pyarmour.cli import cli


def test_cli_help() -> None:
    """Test CLI help output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    
    assert result.exit_code == 0
    assert "PyArmour - Zero-configuration adversarial robustness testing" in result.output
    assert "run" in result.output
    assert "--model-path" in result.output
    assert "--data-path" in result.output
    assert "--output" in result.output
    assert "--attacks" in result.output
    assert "--epsilons" in result.output
