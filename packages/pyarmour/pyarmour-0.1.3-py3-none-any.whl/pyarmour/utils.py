"""Utility functions for PyArmour."""

from typing import Union, Any, Tuple
import numpy as np
from pathlib import Path

class SimpleCNN:
    def __init__(self):
        # Initialize weights with random values
        self.conv1_weights = np.random.randn(32, 1, 3, 3) * 0.01
        self.conv1_bias = np.zeros(32)
        
        self.conv2_weights = np.random.randn(64, 32, 3, 3) * 0.01
        self.conv2_bias = np.zeros(64)
        
        self.fc1_weights = np.random.randn(9216, 128) * 0.01
        self.fc1_bias = np.zeros(128)
        
        self.fc2_weights = np.random.randn(128, 10) * 0.01
        self.fc2_bias = np.zeros(10)

    def conv2d(self, x, weights, bias, stride=1):
        """2D Convolution using NumPy"""
        batch_size, in_channels, height, width = x.shape
        out_channels, in_channels, kernel_h, kernel_w = weights.shape
        
        out_height = (height - kernel_h) // stride + 1
        out_width = (width - kernel_w) // stride + 1
        
        output = np.zeros((batch_size, out_channels, out_height, out_width))
        
        for b in range(batch_size):
            for c in range(out_channels):
                for i in range(out_height):
                    for j in range(out_width):
                        patch = x[b, :, i*stride:i*stride+kernel_h, j*stride:j*stride+kernel_w]
                        output[b, c, i, j] = np.sum(patch * weights[c]) + bias[c]
        
        return output

    def max_pool2d(self, x, pool_size=2):
        """2D Max Pooling using NumPy"""
        batch_size, channels, height, width = x.shape
        out_height = height // pool_size
        out_width = width // pool_size
        
        output = np.zeros((batch_size, channels, out_height, out_width))
        
        for b in range(batch_size):
            for c in range(channels):
                for i in range(out_height):
                    for j in range(out_width):
                        patch = x[b, c, i*pool_size:(i+1)*pool_size, j*pool_size:(j+1)*pool_size]
                        output[b, c, i, j] = np.max(patch)
        
        return output

    def forward(self, x):
        """Forward pass using NumPy operations"""
        # Conv1
        x = self.conv2d(x, self.conv1_weights, self.conv1_bias)
        x = np.maximum(0, x)  # ReLU activation
        
        # Conv2
        x = self.conv2d(x, self.conv2_weights, self.conv2_bias)
        x = np.maximum(0, x)  # ReLU activation
        
        # Max Pool
        x = self.max_pool2d(x)
        
        # Flatten
        x = x.reshape(x.shape[0], -1)
        
        # FC1
        x = np.dot(x, self.fc1_weights) + self.fc1_bias
        x = np.maximum(0, x)  # ReLU activation
        
        # FC2
        x = np.dot(x, self.fc2_weights) + self.fc2_bias
        
        return x


def get_framework(model: Any) -> str:
    """Determine the framework of the model."""
    return "numpy"  # Since we're using NumPy implementation


def tensor_to_numpy(x: np.ndarray) -> np.ndarray:
    """Convert tensor to numpy array."""
    return x


def numpy_to_tensor(x: np.ndarray) -> np.ndarray:
    """Convert numpy array to tensor."""
    return x.astype(np.float32)


def load_model(path: Union[str, Path]) -> "SimpleCNN":
    """Load a saved model weights.
    
    Args:
        path: Path to the model weights file
        
    Returns:
        SimpleCNN model with loaded weights
    """
    path = Path(path)
    if path.suffix != ".npz":
        raise ValueError(f"Unsupported model file extension: {path.suffix}")
    
    model = SimpleCNN()
    try:
        weights = np.load(path)
        model.conv1_weights = weights['conv1_weights']
        model.conv1_bias = weights['conv1_bias']
        model.conv2_weights = weights['conv2_weights']
        model.conv2_bias = weights['conv2_bias']
        model.fc1_weights = weights['fc1_weights']
        model.fc1_bias = weights['fc1_bias']
        model.fc2_weights = weights['fc2_weights']
        model.fc2_bias = weights['fc2_bias']
        return model
    except Exception as e:
        raise ValueError(f"Failed to load model from {path}: {str(e)}")


def load_data(path: Union[str, Path]) -> Tuple[Any, Any]:
    """Load test data."""
    path = Path(path)
    if path.is_dir():
        # Handle directory of images
        raise NotImplementedError("Directory data loading not implemented")
    elif path.suffix == ".npz":
        data = np.load(path)
        return data["x_test"], data["y_test"]
    else:
        raise ValueError(f"Unsupported data format: {path.suffix}")
