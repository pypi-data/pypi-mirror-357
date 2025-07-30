"""DeepFool attack implementation."""

from typing import Union, Optional
import numpy as np
from pathlib import Path
from pyarmour.visualize import plot_images, plot_perturbation_distribution


class DeepFool:
    """DeepFool attack."""

    def __init__(self, model: "SimpleCNN", max_iter: int = 50):
        """Initialize DeepFool attack.

        Args:
            model: The neural network model
            max_iter: Maximum number of iterations
        """
        self.model = model
        self.max_iter = max_iter

    def generate(self, x: np.ndarray, y: np.ndarray, 
                 visualize: bool = True, 
                 num_samples: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate adversarial examples using DeepFool.

        Args:
            x: Input data (batch_size, channels, height, width)
            y: True labels (batch_size,)
            visualize: Whether to show visualization of results
            num_samples: Number of samples to visualize

        Returns:
            Tuple of (adversarial examples, original predictions, adversarial predictions)
        """
        # Convert inputs to float32
        x = x.astype(np.float32)
        y = y.astype(np.int32)
        
        # Get original predictions
        original_predictions = self.model.forward(x)
        
        # Initialize adversarial examples
        adv_examples = x.copy()
        
        # Generate adversarial examples
        adv_examples = self._generate_adversarial(adv_examples, y)
        
        # Get adversarial predictions
        adv_predictions = self.model.forward(adv_examples)
        
        # Calculate success rate
        original_correct = np.mean(np.argmax(original_predictions, axis=1) == y)
        adv_correct = np.mean(np.argmax(adv_predictions, axis=1) == y)
        
        print(f"\nOriginal accuracy: {original_correct:.2%}")
        print(f"Adversarial accuracy: {adv_correct:.2%}")
        print(f"Success rate: {(original_correct - adv_correct) / original_correct:.2%}")
        
        # Visualize results
        if visualize:
            print("\n=== Original Images ===")
            plot_images(x[:num_samples], y[:num_samples], original_predictions[:num_samples])
            
            print("\n=== Adversarial Images ===")
            plot_images(adv_examples[:num_samples], y[:num_samples], 
                       adv_predictions[:num_samples], adversarial=True)
            
            # Plot perturbation distribution
            perturbation = adv_examples - x
            plot_perturbation_distribution(perturbation)
        
        return adv_examples, original_predictions, adv_predictions

    def _generate_adversarial(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Generate adversarial examples using numerical differentiation."""
        # Initialize adversarial examples
        adv_examples = x.copy()
        
        # Calculate gradients using numerical differentiation
        gradients = np.zeros_like(x)
        
        # Use parallel computation for gradients
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                for k in range(x.shape[2]):
                    for l in range(x.shape[3]):
                        # Perturb the input slightly
                        x_plus = x.copy()
                        x_plus[i, j, k, l] += 1e-4
                        x_minus = x.copy()
                        x_minus[i, j, k, l] -= 1e-4
                        
                        # Calculate predictions with perturbed inputs
                        pred_plus = self.model.forward(x_plus)
                        pred_minus = self.model.forward(x_minus)
                        
                        # Calculate gradient using central difference
                        gradients[i, j, k, l] = (
                            (pred_plus[i, y[i]] - pred_minus[i, y[i]]) / (2 * 1e-4)
                        )
        
        # Generate perturbation
        perturbation = np.sign(gradients)
        
        # Create adversarial examples
        adv_examples = x + perturbation
        
        # Clip values to [0, 1]
        adv_examples = np.clip(adv_examples, 0, 1)
        
        return adv_examples
