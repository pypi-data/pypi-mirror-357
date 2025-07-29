from tensorviz.html import render_html

def test_html_render():
    mock_logs = [
        {
            "name": "Linear1",
            "input_shape": "(1, 10)",
            "output_shape": "(1, 5)",
            "dtype": "float32",
            "grad": {"mean": 0.001, "std": 0.002},
            "group": "Sequential"
        }
    ]
    mock_svg = "<svg>dummy</svg>"
    html = render_html(mock_logs, mock_svg)
    assert "Linear1" in html and "(1, 10) → (1, 5)" in html
