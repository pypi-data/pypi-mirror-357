"""Pytest decorators for adversarial robustness testing."""

from typing import Callable, List, Union, Type, Any
import pytest
from functools import wraps
from pathlib import Path

from .attacks.fgsm import FGSM
from .attacks.pgd import PGD
from .attacks.deepfool import DeepFool
from .utils import tensor_to_numpy, numpy_to_tensor


def adversarial_test(model, attacks=None, epsilons=None, steps=None, alpha=None, max_iter=None):
    """
    Decorator for adversarial robustness testing.

    Args:
        model: The model to test
        attacks: List of attack names (default: ['fgsm', 'pgd', 'deepfool'])
        epsilons: List of epsilon values (default: [0.01, 0.03, 0.1])
        steps: Number of steps for iterative attacks (default: 10)
        alpha: Step size for iterative attacks (default: 0.01)
        max_iter: Maximum iterations for DeepFool (default: 50)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Default values
            attacks = attacks or ['fgsm', 'pgd', 'deepfool']
            epsilons = epsilons or [0.01, 0.03, 0.1]
            steps = steps or 10
            alpha = alpha or 0.01
            max_iter = max_iter or 50
            
            # Create attacks
            attack_instances = []
            for attack_name in attacks:
                if attack_name == 'fgsm':
                    attack_instances.append(FGSM(model, epsilon=epsilons[0]))
                elif attack_name == 'pgd':
                    attack_instances.append(PGD(model, epsilon=epsilons[0], alpha=alpha, steps=steps))
                elif attack_name == 'deepfool':
                    attack_instances.append(DeepFool(model, max_iter=max_iter))
                else:
                    raise ValueError(f"Unsupported attack: {attack_name}")
            
            # Run tests
            for attack in attack_instances:
                for epsilon in epsilons:
                    if hasattr(attack, 'epsilon'):
                        attack.epsilon = epsilon
                    
                    # Generate adversarial examples
                    x = kwargs.get('x')
                    y = kwargs.get('y')
                    
                    if x is None or y is None:
                        raise ValueError("Test function must provide 'x' and 'y' arguments")
                    
                    adv_x = attack.generate(x, y)
                    
                    # Run test with adversarial example
                    func(*args, x=adv_x, y=y, **kwargs)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
