import numpy as np
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from pyarmour.utils import SimpleCNN, load_model, tensor_to_numpy, numpy_to_tensor

@pytest.mark.usefixtures("sample_model")
@pytest.mark.usefixtures("sample_data")
@pytest.mark.usefixtures("sample_predictions")

def test_simple_cnn_init(sample_model):
    assert hasattr(sample_model, 'conv1')
    assert hasattr(sample_model, 'conv2')
    assert hasattr(sample_model, 'fc1')
    assert hasattr(sample_model, 'fc2')

def test_simple_cnn_forward(sample_model, sample_data):
    x = sample_data[0][:1]
    output = sample_model.forward(x)
    assert output.shape == (1, 10)
    assert isinstance(output, np.ndarray)

def test_load_model():
    # Create a temporary model file
    model = SimpleCNN()
    temp_file = Path("temp_model.npz")
    try:
        # Save model weights
        np.savez(temp_file,
                 conv1_weights=model.conv1_weights,
                 conv1_bias=model.conv1_bias,
                 conv2_weights=model.conv2_weights,
                 conv2_bias=model.conv2_bias,
                 fc1_weights=model.fc1_weights,
                 fc1_bias=model.fc1_bias,
                 fc2_weights=model.fc2_weights,
                 fc2_bias=model.fc2_bias)
        
        # Load and verify
        loaded_model = load_model(temp_file)
        assert isinstance(loaded_model, SimpleCNN)
        
        # Verify weights match
        assert np.allclose(model.conv1_weights, loaded_model.conv1_weights)
        assert np.allclose(model.conv1_bias, loaded_model.conv1_bias)
        assert np.allclose(model.conv2_weights, loaded_model.conv2_weights)
        assert np.allclose(model.conv2_bias, loaded_model.conv2_bias)
        assert np.allclose(model.fc1_weights, loaded_model.fc1_weights)
        assert np.allclose(model.fc1_bias, loaded_model.fc1_bias)
        assert np.allclose(model.fc2_weights, loaded_model.fc2_weights)
        assert np.allclose(model.fc2_bias, loaded_model.fc2_bias)
    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()

def test_model_predictions():
    model = SimpleCNN()
    x = np.random.random((1, 1, 28, 28)).astype(np.float32)
    predictions = model.forward(x)
    
    assert predictions.shape == (1, 10)
    assert isinstance(predictions, np.ndarray)
    assert predictions.dtype == np.float32
