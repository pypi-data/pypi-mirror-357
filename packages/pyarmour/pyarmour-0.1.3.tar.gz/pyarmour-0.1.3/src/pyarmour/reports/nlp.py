"""NLP-specific report generation."""

from typing import List, Tuple
import difflib
from pathlib import Path


def diff_text(
    orig: str,
    adv: str,
    output_path: Path,
    title: str = "",
) -> None:
    """Generate side-by-side text diff.

    Args:
        orig: Original text
        adv: Adversarial text
        output_path: Path to save the diff
        title: Title for the diff
    """
    # Create HTML diff
    diff = difflib.HtmlDiff().make_file(
        orig.splitlines(),
        adv.splitlines(),
        fromdesc="Original",
        todesc="Adversarial",
    )
    
    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(diff)


def generate_nlp_report(results: list, output_path: str) -> None:
    """Generate HTML report for NLP models.

    Args:
        results: List of test results
        output_path: Path to save the report
    """
    html = ["""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PyArmour NLP Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .result { border: 1px solid #ddd; padding: 20px; margin: 20px 0; }
            .diff { margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PyArmour NLP Report</h1>
    """]

    for result in results:
        html.append(f"<div class='result'>")
        html.append(f"<h2>Attack: {result['attack']} (ε={result['epsilon']})</h2>")
        html.append(f"<p>Accuracy: {result['accuracy']:.2%}</p>")
        
        # Generate example diffs
        examples_dir = Path(output_path).parent / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        for i, (x, adv_x, pred, y) in enumerate(result["examples"][:5]):
            diff_path = examples_dir / f"example_{i}.html"
            diff_text(x, adv_x, diff_path)
            html.append(f"<div class='diff'>")
            html.append(f"<iframe src='{diff_path.relative_to(Path(output_path).parent)}' "
                        f"width='100%' height='300px' frameborder='0'></iframe>")
            html.append("</div>")
        
        html.append("</div>")

    html.append("</div></body></html>")

    # Write HTML to file
    with open(output_path, "w") as f:
        f.write("\n".join(html))
