import subprocess
import tempfile
import json
import os

def test_cli_end_to_end():
    # Create a temporary JSON log file
    logs = [
        {
            "name": "Linear1",
            "input_shape": "(1, 10)",
            "output_shape": "(1, 5)",
            "dtype": "float32",
            "grad": {"mean": 0.01, "std": 0.002},
            "group": "Sequential"
        },
        {
            "name": "ReLU",
            "input_shape": "(1, 5)",
            "output_shape": "(1, 5)",
            "dtype": "float32"
        },
        {
            "name": "Linear2",
            "input_shape": "(1, 5)",
            "output_shape": "(1, 2)",
            "dtype": "float32"
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "log.json")
        output_path = os.path.join(tmpdir, "output.html")

        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(logs, f)

        # Run CLI using subprocess
        result = subprocess.run(
            ["python", "-m", "tensorviz.cli", input_path, "-o", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # CLI should exit with 0 status
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Output HTML file should exist
        assert os.path.exists(output_path), "Output HTML file was not created."

        # Check if output contains expected HTML structure
        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            assert "<html>" in html_content
            assert "<h2>Model Graph</h2>" in html_content
            assert "Linear1" in html_content
