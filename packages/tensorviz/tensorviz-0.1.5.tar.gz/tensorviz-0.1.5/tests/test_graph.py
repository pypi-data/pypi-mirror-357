import os
from tensorviz.graph import generate_graph_svg
from tensorviz.logger import logs


def test_generate_svg(tmp_path):
    # Mock logs
    test_logs = [
        {"name": "Linear1", "input_shape": "(1, 10)", "output_shape": "(1, 5)", "dtype": "float32"},
        {"name": "ReLU", "input_shape": "(1, 5)", "output_shape": "(1, 5)", "dtype": "float32"},
        {"name": "Linear2", "input_shape": "(1, 5)", "output_shape": "(1, 2)", "dtype": "float32"},
    ]
    svg = generate_graph_svg(test_logs)
    assert svg.lstrip().startswith("<?xml")
    assert "<svg" in svg
