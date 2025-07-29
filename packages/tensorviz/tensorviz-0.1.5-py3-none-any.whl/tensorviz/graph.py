from graphviz import Digraph

def render_svg(logs) -> str:
    model = logs["model"]
    input_shape = logs.get("input_shape", (1, 10))

    graph = draw_graph(
        model,
        input_size=input_shape,
        expand_nested=True,
        roll=True,
        graph_dir="LR",
        save_graph=False,
        show_shapes=True,
    )
    return graph.visual_graph  

def generate_graph_svg(logs):
    dot = Digraph()

    for i, layer in enumerate(logs):
        dot.node(str(i), f"{layer['name']}\n{layer['input_shape']} → {layer['output_shape']}")

    for i in range(len(logs) - 1):
        dot.edge(str(i), str(i + 1))

    return dot.pipe(format='svg').decode('utf-8')