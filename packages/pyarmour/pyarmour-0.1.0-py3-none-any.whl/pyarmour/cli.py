"""Command-line interface for PyArmour."""

import click
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple

from .attacks.fgsm import FGSM
from .attacks.pgd import PGD
from .attacks.deepfool import DeepFool
from .visualize import plot_confusion_matrix, plot_difference_map, plot_distribution
from .utils import load_model, SimpleCNN


@click.group()
def cli() -> None:
    """PyArmour - Zero-configuration adversarial robustness testing."""
    pass


@cli.command()
@click.option(
    "--model-path",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to saved model file",
)
@click.option(
    "--data-path",
    required=True,
    type=click.Path(exists=True),
    help="Path to test data",
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False),
    default="report.html",
    help="Output report file path",
)
@click.option(
    "--attacks",
    multiple=True,
    type=click.Choice(["fgsm", "pgd", "deepfool"]),
    default=["fgsm", "pgd", "deepfool"],
    help="Attacks to run",
)
@click.option(
    "--epsilons",
    multiple=True,
    type=float,
    default=[0.03, 0.1],
    help="Epsilon values for attacks",
)
def load_data(data_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load data from numpy files.
    
    Args:
        data_path: Path to directory containing x_test.npy and y_test.npy
        
    Returns:
        Tuple of (x_test, y_test) numpy arrays
    """
    x_test = np.load(Path(data_path) / 'x_test.npy')
    y_test = np.load(Path(data_path) / 'y_test.npy')
    return x_test, y_test

def run(
    model_path: str,
    data_path: str,
    output: str,
    attacks: List[str],
    epsilons: List[float],
) -> None:
    """Run adversarial testing and generate a report."""
    print("\n=== Starting Adversarial Testing ===")
    print(f"\nLoading model from {model_path}")
    try:
        model = load_model(model_path)
        print(f"\nModel loaded successfully!")
        print(f"Model type: {type(model)}")
        print("\nModel architecture:")
        print("- Conv1 weights:", model.conv1_weights.shape)
        print("- Conv1 bias:", model.conv1_bias.shape)
        print("- Conv2 weights:", model.conv2_weights.shape)
        print("- Conv2 bias:", model.conv2_bias.shape)
        print("- FC1 weights:", model.fc1_weights.shape)
        print("- FC1 bias:", model.fc1_bias.shape)
        print("- FC2 weights:", model.fc2_weights.shape)
        print("- FC2 bias:", model.fc2_bias.shape)
    except Exception as e:
        print(f"\nError loading model: {str(e)}")
        raise
    
    print(f"\nLoading data from {data_path}")
    try:
        x_test, y_test = load_data(data_path)
        print(f"\nData loaded successfully!")
        print(f"Input data shape: {x_test.shape}")
        print(f"Label data shape: {y_test.shape}")
        print(f"Input data dtype: {x_test.dtype}")
        print(f"Label data dtype: {y_test.dtype}")
        print(f"Input data range: min={x_test.min()}, max={x_test.max()}")
        print(f"First 5 labels: {y_test[:5]}")
    except Exception as e:
        print(f"\nError loading data: {str(e)}")
        raise
    
    print(f"\nFramework: NumPy")

    # Initialize attacks
    attack_instances = []
    for attack_type in attacks:
        if attack_type == "fgsm":
            attack_instances.append(FGSM(model))
        elif attack_type == "pgd":
            attack_instances.append(PGD(model))
        elif attack_type == "deepfool":
            attack_instances.append(DeepFool(model))

    # Run tests and collect results
    results = []
    for attack in attack_instances:
        for epsilon in epsilons:
            adv_examples = attack.generate(x_test, y_test)  # Pass y_test since we need labels
            predictions = model.forward(adv_examples)  # Use forward method for NumPy
            
            # Calculate metrics using NumPy
            accuracy = np.mean(np.argmax(predictions, axis=1) == y_test)
            
            results.append({
                "attack": attack.__class__.__name__,
                "epsilon": epsilon,
                "accuracy": float(accuracy),  # Convert to float for JSON serialization
                "examples": list(zip(x_test, adv_examples, predictions, y_test))
            })

    # Generate visualization
    print("\nGenerating visualization...")
    
    # Plot confusion matrix
    plot_confusion_matrix(results, output.replace('.html', '_confusion.png'))
    
    # Plot difference map
    plot_difference_map(results, output.replace('.html', '_difference.png'))
    
    # Plot distribution
    plot_distribution(results, output.replace('.html', '_distribution.png'))
    
    print(f"\nVisualization saved to {output.replace('.html', '*.png')}")


if __name__ == "__main__":
    cli()
