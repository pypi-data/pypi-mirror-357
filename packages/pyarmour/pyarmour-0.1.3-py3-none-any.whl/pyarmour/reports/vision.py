"""Vision-specific report generation."""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def plot_heatmap(
    orig: np.ndarray,
    adv: np.ndarray,
    output_path: Path,
    title: str = "",
) -> None:
    """Plot heatmap showing differences between original and adversarial images.

    Args:
        orig: Original image
        adv: Adversarial image
        output_path: Path to save the plot
        title: Plot title
    """
    # Calculate difference
    diff = np.abs(adv - orig)
    
    # Create figure
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Original image
    ax1.imshow(orig)
    ax1.set_title("Original")
    ax1.axis("off")
    
    # Adversarial image
    ax2.imshow(adv)
    ax2.set_title("Adversarial")
    ax2.axis("off")
    
    # Difference heatmap
    heatmap = ax3.imshow(diff, cmap="hot", interpolation="nearest")
    ax3.set_title("Difference Heatmap")
    ax3.axis("off")
    
    # Add colorbar
    plt.colorbar(heatmap, ax=ax3)
    
    # Save figure
    plt.savefig(output_path)
    plt.close()


def generate_vision_report(results: list, output_path: str) -> None:
    """Generate HTML report for vision models.

    Args:
        results: List of test results
        output_path: Path to save the report
    """
    html = ["""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PyArmour Vision Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .result { border: 1px solid #ddd; padding: 20px; margin: 20px 0; }
            .image-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
            img { max-width: 100%; height: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PyArmour Vision Report</h1>
    """]

    for result in results:
        html.append(f"<div class='result'>")
        html.append(f"<h2>Attack: {result['attack']} (ε={result['epsilon']})</h2>")
        html.append(f"<p>Accuracy: {result['accuracy']:.2%}</p>")
        
        # Generate example images
        examples_dir = Path(output_path).parent / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        for i, (x, adv_x, pred, y) in enumerate(result["examples"][:5]):
            img_path = examples_dir / f"example_{i}.png"
            plot_heatmap(x, adv_x, img_path)
            html.append(f"<div class='image-grid'>")
            html.append(f"<img src='{img_path.relative_to(Path(output_path).parent)}' alt='Example {i}'>")
            html.append("</div>")
        
        html.append("</div>")

    html.append("</div></body></html>")

    # Write HTML to file
    with open(output_path, "w") as f:
        f.write("\n".join(html))
