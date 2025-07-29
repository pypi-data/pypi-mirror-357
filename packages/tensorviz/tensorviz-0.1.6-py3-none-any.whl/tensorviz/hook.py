import torch
from .logger import log_layer

def is_sequential_child(name, parent_name):
    return name.startswith(parent_name) and name != parent_name

def register_hooks(model):
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Sequential):
            continue  # skip Sequential containers
        if len(list(module.children())) == 0:
            module.register_forward_hook(
                lambda mod, inp, out, name=name: log_layer(name, inp, out)
            )
