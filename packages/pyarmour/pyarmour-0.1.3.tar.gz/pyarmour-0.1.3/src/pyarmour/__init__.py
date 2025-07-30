"""PyArmour - Zero-configuration adversarial robustness testing for ML models."""

from .decorators import adversarial_test
from .cli import cli

__all__ = ["adversarial_test", "cli"]
__version__ = "0.1.0"
