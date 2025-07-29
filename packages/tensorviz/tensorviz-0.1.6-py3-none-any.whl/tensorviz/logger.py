from rich.console import Console
from rich.table import Table
import torch

logs = []

def log_layer(name, inp, out):
    def shape_str(t):
        return str(t.shape) if isinstance(t, torch.Tensor) else str(type(t))

    def retain_and_get_grad(t):
        if isinstance(t, torch.Tensor) and t.requires_grad:
            t.retain_grad()
            return t.grad
        return None

    group = name.split(".")[0] if "." in name else None

    # Retain grad and get grad stats
    out_grad = None
    grad_info = None

    if isinstance(out, torch.Tensor):
        out.retain_grad()
        out_grad = out.grad
        if out_grad is not None:
            grad_info = {
                "mean": out_grad.mean().item(),
                "std": out_grad.std().item()
            }

        output_shape = shape_str(out)
        dtype = str(out.dtype)
    elif isinstance(out, (tuple, list)) and len(out) > 0:
        # handle multi-output
        output_shape = ", ".join([shape_str(t) for t in out])
        dtype = ", ".join([str(t.dtype) if isinstance(t, torch.Tensor) else "N/A" for t in out])
    else:
        output_shape = "N/A"
        dtype = "N/A"

    logs.append({
        "name": name,
        "input_shape": str(inp[0].shape) if inp and isinstance(inp[0], torch.Tensor) else None,
        "output_shape": output_shape,
        "dtype": dtype,
        "grad": grad_info,
        "group": group
    })

def get_logs():
    return logs

def clear_logs():
    logs.clear()

def print_logs():
    table = Table(title="TensorViz Log")
    table.add_column("Layer", style="cyan")
    table.add_column("Input", style="magenta")
    table.add_column("Output", style="green")
    for log in logs:
        table.add_row(log["name"], log["input_shape"], log["output_shape"])
    Console().print(table)
