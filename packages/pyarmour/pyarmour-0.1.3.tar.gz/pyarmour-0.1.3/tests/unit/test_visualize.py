import numpy as np
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from pyarmour.visualize import plot_images, plot_accuracy_curve, plot_perturbation_distribution, plot_difference_map, plot_confusion_matrix

def test_plot_images():
    x = np.random.random((5, 1, 28, 28)).astype(np.float32)
    y = np.random.randint(0, 10, 5)
    predictions = np.random.random((5, 10)).astype(np.float32)
    
    # Test with default parameters
    plot_images(x, y, predictions)
    
    # Test with custom parameters
    plot_images(x, y, predictions, 
               n_images=3,
               figsize=(10, 5),
               title="Test Images",
               cmap='gray')

def test_plot_accuracy_curve():
    epsilons = [0.01, 0.02, 0.03, 0.04, 0.05]
    accuracies = [0.95, 0.90, 0.85, 0.80, 0.75]
    
    plot_accuracy_curve(epsilons, accuracies)
    
    # Test with custom parameters
    plot_accuracy_curve(epsilons, accuracies,
                       title="Accuracy vs Epsilon",
                       xlabel="Epsilon",
                       ylabel="Accuracy",
                       figsize=(10, 6))

def test_plot_perturbation_distribution():
    perturbations = np.random.random((100, 1, 28, 28)).astype(np.float32)
    
    plot_perturbation_distribution(perturbations)
    
    # Test with custom parameters
    plot_perturbation_distribution(perturbations,
                                 bins=50,
                                 title="Perturbation Distribution",
                                 figsize=(10, 6))

def test_plot_difference_map():
    original = np.random.random((1, 1, 28, 28)).astype(np.float32)
    adversarial = np.random.random((1, 1, 28, 28)).astype(np.float32)
    
    plot_difference_map(original, adversarial)
    
    # Test with custom parameters
    plot_difference_map(original, adversarial,
                       title="Difference Map",
                       figsize=(8, 8),
                       cmap='seismic')

def test_plot_confusion_matrix():
    predictions = np.random.random((100, 10)).astype(np.float32)
    true_labels = np.random.randint(0, 10, 100)
    
    plot_confusion_matrix(predictions, true_labels)
    
    # Test with custom parameters
    plot_confusion_matrix(predictions, true_labels,
                        title="Confusion Matrix",
                        figsize=(10, 8),
                        cmap='Blues')
