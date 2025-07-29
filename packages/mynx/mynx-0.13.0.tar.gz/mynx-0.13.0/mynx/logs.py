from dataclasses import dataclass
from flax.training.train_state import TrainState
from flax.typing import Array


@dataclass
class Logs:
    state: TrainState | None = None
    batch: Array = None
    loss: Array = None
    y_pred: Array = None
