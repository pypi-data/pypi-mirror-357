from pathlib import Path
import pickle
from flax.training.train_state import TrainState
from typing import Literal

from mynx.callbacks import Callback
from mynx.logs import Logs


class CheckPoint(Callback):
    def __init__(
        self, path: Path, run_on: Literal["epoch", "step"] = "epoch", freq: int = 1
    ):
        self.path = path
        self.run_on = run_on
        self.freq = freq
        super().__init__()

    def on_epoch_end(self, epoch: int, logs: Logs):
        if self.run_on == "step" or self.run_on == "epoch" and epoch % self.freq == 0:
            self.save(logs)

    def on_step_end(self, step: int, logs: Logs):
        if self.run_on == "step" and step % self.freq == 0:
            self.save(logs)

    def save(self, logs: Logs):
        if not self.path.parent.exists():
            self.path.parent.mkdir()
        with open(self.path, "wb") as f:
            pickle.dump((logs.state.step, logs.state.params, logs.state.opt_state), f)

    def on_train_start(self, logs: Logs):
        if not self.path.exists():
            return
        with open(self.path, "rb") as f:
            step, params, opt_state = pickle.load(f)
        logs.state = TrainState(
            step=step,
            apply_fn=logs.state.apply_fn,
            params=params,
            tx=logs.state.tx,
            opt_state=opt_state,
        )
