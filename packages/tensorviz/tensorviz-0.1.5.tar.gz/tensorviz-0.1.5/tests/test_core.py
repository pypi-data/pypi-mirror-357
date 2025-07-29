import torch
import torch.nn as nn
from tensorviz.hook import register_hooks
from tensorviz.logger import logs, clear_logs

class DummyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.seq = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 2)
        )

    def forward(self, x):
        return self.seq(x)

def test_hook_model_and_logging():
    model = DummyModel()
    x = torch.randn(1, 10, requires_grad=True)
    
    clear_logs()
    register_hooks(model)

    # Forward and backward pass
    output = model(x)
    loss = output.sum()
    loss.backward()

    # Assertions
    assert isinstance(logs, list)
    assert len(logs) > 0

    for entry in logs:
        assert "name" in entry
        assert "input_shape" in entry
        assert "output_shape" in entry
        assert "dtype" in entry
        # grad may be None if it's not a parameter or has no backward connection
        if "grad" in entry and entry["grad"] is not None:
            assert "mean" in entry["grad"]
            assert "std" in entry["grad"]
