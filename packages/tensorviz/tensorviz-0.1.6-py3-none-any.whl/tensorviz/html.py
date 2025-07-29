# tensorviz/html.py

def render_html(logs, svg):
    log_html = "".join(
        f"<div><b>{log['name']}</b>: {log['input_shape']} → {log['output_shape']} ({log['dtype']})</div>"
        for log in logs
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>TensorViz</title></head>
    <body>
        <h1>Model Layers</h1>
        {log_html}
        <h2>Graph</h2>
        {svg}
    </body>
    </html>
    """
