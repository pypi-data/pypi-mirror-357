import pytest
import sys
import os
import numpy as np

# Add the source directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Fixtures for common test data
@pytest.fixture
def sample_model():
    from pyarmour.utils import SimpleCNN
    return SimpleCNN()

@pytest.fixture
def sample_data():
    x = np.random.random((10, 1, 28, 28)).astype(np.float32)
    y = np.random.randint(0, 10, 10)
    return x, y

@pytest.fixture
def sample_predictions():
    return np.random.random((10, 10)).astype(np.float32)
