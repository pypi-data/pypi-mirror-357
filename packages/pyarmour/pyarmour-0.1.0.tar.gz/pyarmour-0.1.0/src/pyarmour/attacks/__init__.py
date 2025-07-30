"""Adversarial attack implementations."""

from .fgsm import FGSM
from .pgd import PGD
from .deepfool import DeepFool

__all__ = [
    'FGSM', 'PGD', 'DeepFool'
]
