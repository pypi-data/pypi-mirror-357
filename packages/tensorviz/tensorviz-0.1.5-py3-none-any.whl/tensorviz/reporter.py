import os
import json
from jinja2 import Environment, FileSystemLoader
from torchview import draw_graph

def export_json(logs, filename="logs.json"):
    """Export logs to a JSON file."""
    with open(filename, "w") as f:
        json.dump(logs, f, indent=2)

def save_svg(logs, svg_path="graph.svg"):
    """Generate SVG graph using torchview and save to file."""
    model = logs.get("model")
    input_shape = logs.get("input_shape", (1, 10))

    if model is None:
        print("[WARN] Model not found in logs. Skipping SVG rendering.")
        return

    try:
        graph = draw_graph(
            model,
            input_size=input_shape,
            expand_nested=True,
            roll=True,
            graph_dir="LR",
            save_graph=False,
            show_shapes=True,
        )
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(graph.visual_graph)
        print(f"[OK] Model SVG saved to {svg_path}")
    except Exception as e:
        print(f"[ERROR] Failed to draw SVG: {e}")

def render_html(logs, output="tensorviz.html", svg_path="graph.svg"):
    """Render an interactive HTML report from logs and graph."""
    save_svg(logs, svg_path)  # 🔹 Auto-generate the SVG

    env = Environment(
        loader=FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), "templates"))
    )
    template = env.get_template("report.html.j2")

    svg_content = ""
    if os.path.exists(svg_path):
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()

    html_content = template.render(logs=logs, graph_svg=svg_content)

    with open(output, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] TensorViz HTML report saved to {output}")
