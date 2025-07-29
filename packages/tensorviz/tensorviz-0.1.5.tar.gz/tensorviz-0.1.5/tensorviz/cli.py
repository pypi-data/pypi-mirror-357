import typer
import json
import sys
from tensorviz.reporter import render_html
from tensorviz.graph import render_svg

app = typer.Typer()

@app.command()
def main(
    model_path: str,
    output: str = typer.Option("tensorviz.html", "--output", "-o", help="Output HTML file")
):
    """
    Render a TensorViz report from a JSON model log.

    MODEL_PATH: Path to the input JSON log file.
    """
    try:
        with open(model_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        typer.echo(f"[x] File not found: {model_path}", err=True)
        sys.exit(1)
    except json.JSONDecodeError:
        typer.echo(f"[x] Failed to decode JSON from: {model_path}", err=True)
        sys.exit(1)

    try:
        render_svg(logs)
        render_html(logs, output=output)
    except Exception as e:
        typer.echo(f"[x] Failed to render report: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    app()
