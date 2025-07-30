import numpy as np
from typing import Union, Any, Tuple, Optional, List
from .utils import numpy_to_tensor, tensor_to_numpy
from .visualize import plot_images, plot_perturbation_distribution
import matplotlib.pyplot as plt
from scipy.stats import entropy

class FGSM:
    """Fast Gradient Sign Method attack."""
    def __init__(self, model: Any, epsilon: float = 0.01, 
                 max_iterations: int = 100, 
                 early_stopping: bool = True,
                 verbose: bool = True):
        """
        Initialize FGSM attack.
        
        Args:
            model: The neural network model
            epsilon: The magnitude of the perturbation
            max_iterations: Maximum number of iterations for iterative FGSM
            early_stopping: Whether to stop early if no improvement is seen
            verbose: Whether to print progress information
        """
        self.model = model
        self.epsilon = epsilon
        self.max_iterations = max_iterations
        self.early_stopping = early_stopping
        self.verbose = verbose

    def generate(self, x: np.ndarray, y: np.ndarray, 
                visualize: bool = True, 
                num_samples: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate adversarial examples."""
        adv_examples = self._generate_adversarial(x, y)
        original_preds = self.model.forward(x)
        adv_preds = self.model.forward(adv_examples)
        
        if visualize:
            self._visualize_results(x, y, original_preds, adv_examples, adv_preds, num_samples)
            
        return adv_examples, original_preds, adv_preds

class PGD:
    """Projected Gradient Descent attack."""
    def __init__(self, model: Any, epsilon: float = 0.01, 
                 alpha: float = 0.01, 
                 steps: int = 10,
                 random_start: bool = True,
                 verbose: bool = True):
        """
        Initialize PGD attack.
        
        Args:
            model: The neural network model
            epsilon: The maximum perturbation
            alpha: The step size
            steps: Number of iterations
            random_start: Whether to start with random perturbation
            verbose: Whether to print progress information
        """
        self.model = model
        self.epsilon = epsilon
        self.alpha = alpha
        self.steps = steps
        self.random_start = random_start
        self.verbose = verbose

    def generate(self, x: np.ndarray, y: np.ndarray, 
                visualize: bool = True, 
                num_samples: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate adversarial examples."""
        adv_examples = self._generate_adversarial(x, y)
        original_preds = self.model.forward(x)
        adv_preds = self.model.forward(adv_examples)
        
        if visualize:
            self._visualize_results(x, y, original_preds, adv_examples, adv_preds, num_samples)
            
        return adv_examples, original_preds, adv_preds

class DeepFool:
    """DeepFool attack."""
    def __init__(self, model: Any, max_iter: int = 50,
                 overshoot: float = 0.02,
                 verbose: bool = True):
        """
        Initialize DeepFool attack.
        
        Args:
            model: The neural network model
            max_iter: Maximum number of iterations
            overshoot: Overshoot parameter
            verbose: Whether to print progress information
        """
        self.model = model
        self.max_iter = max_iter
        self.overshoot = overshoot
        self.verbose = verbose

    def generate(self, x: np.ndarray, y: np.ndarray, 
                visualize: bool = True, 
                num_samples: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate adversarial examples."""
        adv_examples = self._generate_adversarial(x, y)
        original_preds = self.model.forward(x)
        adv_preds = self.model.forward(adv_examples)
        
        if visualize:
            self._visualize_results(x, y, original_preds, adv_examples, adv_preds, num_samples)
            
        return adv_examples, original_preds, adv_preds

class CW:
    """Carlini-Wagner attack."""
    def __init__(self, model: Any, confidence: float = 0.0,
                 learning_rate: float = 0.01,
                 max_iter: int = 1000,
                 verbose: bool = True):
        """
        Initialize CW attack.
        
        Args:
            model: The neural network model
            confidence: Confidence parameter
            learning_rate: Learning rate
            max_iter: Maximum number of iterations
            verbose: Whether to print progress information
        """
        self.model = model
        self.confidence = confidence
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.verbose = verbose

    def generate(self, x: np.ndarray, y: np.ndarray, 
                visualize: bool = True, 
                num_samples: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate adversarial examples."""
        adv_examples = self._generate_adversarial(x, y)
        original_preds = self.model.forward(x)
        adv_preds = self.model.forward(adv_examples)
        
        if visualize:
            self._visualize_results(x, y, original_preds, adv_examples, adv_preds, num_samples)
            
        return adv_examples, original_preds, adv_preds

class BIM:
    """Basic Iterative Method attack."""
    def __init__(self, model: Any, epsilon: float = 0.01,
                 alpha: float = 0.01,
                 steps: int = 10,
                 verbose: bool = True):
        """
        Initialize BIM attack.
        
        Args:
            model: The neural network model
            epsilon: The maximum perturbation
            alpha: The step size
            steps: Number of iterations
            verbose: Whether to print progress information
        """
        self.model = model
        self.epsilon = epsilon
        self.alpha = alpha
        self.steps = steps
        self.verbose = verbose

class JSMA:
    """Jacobian-based Saliency Map Attack."""
    def __init__(self, model: Any, theta: float = 1.0,
                 gamma: float = 0.1,
                 verbose: bool = True):
        """
        Initialize JSMA attack.
        
        Args:
            model: The neural network model
            theta: The perturbation magnitude
            gamma: The proportion of pixels to modify
            verbose: Whether to print progress information
        """
        self.model = model
        self.theta = theta
        self.gamma = gamma
        self.verbose = verbose

class OnePixel:
    """One pixel attack."""
    def __init__(self, model: Any, max_pixels: int = 10,
                 verbose: bool = True):
        """
        Initialize OnePixel attack.
        
        Args:
            model: The neural network model
            max_pixels: Maximum number of pixels to modify
            verbose: Whether to print progress information
        """
        self.model = model
        self.max_pixels = max_pixels
        self.verbose = verbose

class Spatial:
    """Spatial transformation attack."""
    def __init__(self, model: Any, max_translation: int = 2,
                 max_rotation: float = 10.0,
                 verbose: bool = True):
        """
        Initialize Spatial attack.
        
        Args:
            model: The neural network model
            max_translation: Maximum translation in pixels
            max_rotation: Maximum rotation in degrees
            verbose: Whether to print progress information
        """
        self.model = model
        self.max_translation = max_translation
        self.max_rotation = max_rotation
        self.verbose = verbose

class Noise:
    """Noise attack."""
    def __init__(self, model: Any, noise_type: str = 'gaussian',
                 noise_level: float = 0.1,
                 verbose: bool = True):
        """
        Initialize Noise attack.
        
        Args:
            model: The neural network model
            noise_type: Type of noise ('gaussian', 'salt_pepper', 'speckle')
            noise_level: Level of noise
            verbose: Whether to print progress information
        """
        self.model = model
        self.noise_type = noise_type
        self.noise_level = noise_level
        self.verbose = verbose

class HopSkipJump:
    """HopSkipJump attack."""
    def __init__(self, model: Any, max_iter: int = 100,
                 step_size: float = 0.1,
                 verbose: bool = True):
        """
        Initialize HopSkipJump attack.
        
        Args:
            model: The neural network model
            max_iter: Maximum number of iterations
            step_size: Step size for optimization
            verbose: Whether to print progress information
        """
        self.model = model
        self.max_iter = max_iter
        self.step_size = step_size
        self.verbose = verbose

class Boundary:
    """Boundary attack."""
    def __init__(self, model: Any, max_iter: int = 100,
                 step_size: float = 0.1,
                 verbose: bool = True):
        """
        Initialize Boundary attack.
        
        Args:
            model: The neural network model
            max_iter: Maximum number of iterations
            step_size: Step size for optimization
            verbose: Whether to print progress information
        """
        self.model = model
        self.max_iter = max_iter
        self.step_size = step_size
        self.verbose = verbose

def plot_attack_comparison(original: np.ndarray, attacks: List[Any],
                          attack_names: List[str],
                          num_samples: int = 5) -> None:
    """Plot comparison of different attacks.
    
    Args:
        original: Original images
        attacks: List of attack objects
        attack_names: Names of the attacks
        num_samples: Number of samples to visualize
    """
    num_attacks = len(attacks)
    fig = plt.figure(figsize=(15, 3 * num_attacks))
    
    # Plot original images
    for i in range(num_samples):
        plt.subplot(num_attacks + 1, num_samples, i + 1)
        img = original[i]
        if img.shape[0] == 1:
            img = img[0]
        plt.imshow(img, cmap='gray')
        plt.title(f"Original {i}")
        plt.axis('off')
    
    # Plot adversarial images
    for j, attack in enumerate(attacks):
        adv_examples = attack.generate(original)
        for i in range(num_samples):
            plt.subplot(num_attacks + 1, num_samples, 
                       num_samples * (j + 1) + i + 1)
            img = adv_examples[i]
            if img.shape[0] == 1:
                img = img[0]
            plt.imshow(img, cmap='gray')
            plt.title(f"{attack_names[j]} {i}")
            plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def plot_attack_trajectory(original: np.ndarray, attack: Any,
                          num_steps: int = 10) -> None:
    """Plot the attack trajectory over multiple steps.
    
    Args:
        original: Original image
        attack: Attack object
        num_steps: Number of steps to visualize
    """
    fig = plt.figure(figsize=(15, 5))
    
    # Generate intermediate steps
    adv_examples = [original]
    current = original.copy()
    for _ in range(num_steps):
        current = attack._generate_step(current)
        adv_examples.append(current)
    
    # Plot each step
    for i, img in enumerate(adv_examples):
        plt.subplot(1, num_steps + 1, i + 1)
        if img.shape[0] == 1:
            img = img[0]
        plt.imshow(img, cmap='gray')
        plt.title(f"Step {i}")
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def plot_attack_heatmap(original: np.ndarray, attack: Any,
                       num_samples: int = 5) -> None:
    """Plot heatmap of attack importance.
    
    Args:
        original: Original image
        attack: Attack object
        num_samples: Number of samples to analyze
    """
    fig = plt.figure(figsize=(15, 5))
    
    # Generate heatmap
    heatmap = attack._generate_heatmap(original[:num_samples])
    
    # Plot original and heatmap
    for i in range(num_samples):
        plt.subplot(2, num_samples, i + 1)
        img = original[i]
        if img.shape[0] == 1:
            img = img[0]
        plt.imshow(img, cmap='gray')
        plt.title(f"Original {i}")
        plt.axis('off')
        
        plt.subplot(2, num_samples, num_samples + i + 1)
        plt.imshow(heatmap[i], cmap='hot', alpha=0.5)
        plt.colorbar()
        plt.title(f"Heatmap {i}")
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def analyze_attack_results(original_preds: np.ndarray, adv_preds: np.ndarray,
                          y: np.ndarray, perturbations: np.ndarray) -> dict:
    """Analyze attack results and return statistics.
    
    Args:
        original_preds: Original predictions
        adv_preds: Adversarial predictions
        y: True labels
        perturbations: Perturbation magnitudes
        
    Returns:
        Dictionary containing various statistics
    """
    # Calculate accuracy
    original_acc = np.mean(np.argmax(original_preds, axis=1) == y)
    adv_acc = np.mean(np.argmax(adv_preds, axis=1) == y)
    
    # Calculate success rate
    success_rate = (original_acc - adv_acc) / original_acc
    
    # Calculate perturbation statistics
    perturbation_stats = {
        'mean': np.mean(np.abs(perturbations)),
        'std': np.std(np.abs(perturbations)),
        'max': np.max(np.abs(perturbations)),
        'min': np.min(np.abs(perturbations))
    }
    
    # Calculate prediction confidence
    original_conf = np.max(original_preds, axis=1)
    adv_conf = np.max(adv_preds, axis=1)
    
    # Calculate entropy of predictions
    original_entropy = entropy(original_preds.T)
    adv_entropy = entropy(adv_preds.T)
    
    return {
        'accuracy': {
            'original': original_acc,
            'adversarial': adv_acc,
            'success_rate': success_rate
        },
        'perturbation': perturbation_stats,
        'confidence': {
            'original': np.mean(original_conf),
            'adversarial': np.mean(adv_conf)
        },
        'entropy': {
            'original': np.mean(original_entropy),
            'adversarial': np.mean(adv_entropy)
        }
    }

def plot_attack_statistics(stats: dict, attack_names: List[str]) -> None:
    """Plot attack statistics.
    
    Args:
        stats: Dictionary containing attack statistics
        attack_names: Names of the attacks
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.ravel()
    
    # Accuracy comparison
    original_acc = [stats[name]['accuracy']['original'] for name in attack_names]
    adv_acc = [stats[name]['accuracy']['adversarial'] for name in attack_names]
    axes[0].bar(attack_names, original_acc, label='Original')
    axes[0].bar(attack_names, adv_acc, label='Adversarial')
    axes[0].set_title('Accuracy Comparison')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    
    # Perturbation magnitude
    perturbation_stats = [stats[name]['perturbation']['mean'] for name in attack_names]
    axes[1].bar(attack_names, perturbation_stats)
    axes[1].set_title('Mean Perturbation Magnitude')
    axes[1].set_ylabel('Magnitude')
    
    # Confidence comparison
    original_conf = [stats[name]['confidence']['original'] for name in attack_names]
    adv_conf = [stats[name]['confidence']['adversarial'] for name in attack_names]
    axes[2].bar(attack_names, original_conf, label='Original')
    axes[2].bar(attack_names, adv_conf, label='Adversarial')
    axes[2].set_title('Prediction Confidence')
    axes[2].set_ylabel('Confidence')
    axes[2].legend()
    
    # Entropy comparison
    original_entropy = [stats[name]['entropy']['original'] for name in attack_names]
    adv_entropy = [stats[name]['entropy']['adversarial'] for name in attack_names]
    axes[3].bar(attack_names, original_entropy, label='Original')
    axes[3].bar(attack_names, adv_entropy, label='Adversarial')
    axes[3].set_title('Prediction Entropy')
    axes[3].set_ylabel('Entropy')
    axes[3].legend()
    
    plt.tight_layout()
    plt.show()
