from flax import linen as nn
from flax.training.train_state import TrainState
from flax.training import common_utils
from flax import jax_utils
import optax
import jax.numpy as jnp
import jax
import math
from typing import Callable

from mynx import Logs, DataLoader
from mynx.callbacks import Callback
from mynx.callbacks.metrics import EpochCounter, StepCounter, Loading, TimeTracing, Loss


class Model:
    def __init__(self, nn: nn.Module, loss: Callable, data_loader: DataLoader) -> None:
        self.nn = nn
        self.loss = loss
        self.data_loader = data_loader
        self.params = None

    def _step_fn(self, params, state, x, y_true):
        y_pred = state.apply_fn({"params": params}, x)
        loss = self.loss(y_pred, y_true)
        return loss, y_pred

    def _tran_step(self, state, x, y_true):
        grad_fn = jax.value_and_grad(self._step_fn, has_aux=True, allow_int=True)
        (loss, y_pred), grads = grad_fn(state.params, state, x, y_true)
        grads = jax.lax.pmean(grads, axis_name="devices")
        state = state.apply_gradients(grads=grads)
        return loss, y_pred, state

    def tabulate(self, depth: int = 1):
        print(
            nn.tabulate(self.nn, jax.random.PRNGKey(0), depth=depth)(
                self.data_loader.get_batch(0)[0]
            )
        )

    def get_params(self):
        if not self.params:
            self.params = self.nn.init(
                jax.random.PRNGKey(0), self.data_loader.get_batch(0)[0]
            )["params"]
        return self.params

    def _fit_on_train_start(
        self, tx, epochs, total_steps, callbecks, default_callbecks
    ):
        epoch_steps = len(self.data_loader)
        if total_steps:
            epochs = math.ceil(total_steps / epoch_steps)
        elif not epochs:
            raise ValueError("Missing argument epochs or total_steps")
        total_steps = epochs * epoch_steps

        self.callbecks: list[Callback] = [self.data_loader]
        if default_callbecks:
            self.callbecks += [
                EpochCounter(epochs),
                StepCounter(epoch_steps),
                Loading(epoch_steps),
                TimeTracing(epoch_steps),
                Loss(),
            ]
        self.callbecks += callbecks

        self.state = TrainState.create(
            apply_fn=self.nn.apply, params=self.get_params(), tx=tx
        )

        self._tran_step = jax.pmap(self._tran_step, axis_name="devices")

        logs = Logs(state=self.state)

        for callbeck in self.callbecks:
            if callbeck_msg := callbeck.on_train_start(logs):
                print(callbeck_msg)

        total_start_step = logs.state.step
        start_epoch = total_start_step // epoch_steps
        start_step = total_start_step % epoch_steps
        self.data_loader.get_batch_idx.idx = start_step
        self.data_loader.start()

        self.device_state = jax_utils.replicate(logs.state)

        return epochs, logs, start_epoch, start_step

    def _fit_on_epoch_start(self, epoch, logs):
        self.msg = []
        for callbeck in self.callbecks:
            if callbeck_msg := callbeck.on_epoch_start(epoch, logs):
                self.msg.append(callbeck_msg)
        if self.msg != []:
            self.msg = " - ".join(self.msg)
            print(self.msg)

    def _fit_on_step_start(self, step, logs):
        for callbeck in self.callbecks:
            callbeck.on_step_start(step, logs)
        return logs.batch

    def _fit_step(self, batch, logs):
        shard_batch = jax.tree_util.tree_map(common_utils.shard, batch)
        loss, y_pred, self.device_state = self._tran_step(
            self.device_state, *shard_batch
        )
        loss = jnp.mean(loss)
        logs.loss = loss
        logs.y_pred = y_pred
        logs.state = jax_utils.unreplicate(self.device_state)

    def _fit_on_step_end(self, step, logs):
        last_msg_len = len(self.msg)
        self.msg = []
        for callbeck in self.callbecks:
            if callbeck_msg := callbeck.on_step_end(step, logs):
                self.msg.append(callbeck_msg)
        if self.msg != []:
            self.msg = " - ".join(self.msg)
            if len(self.msg) < last_msg_len:
                self.msg += " " * (last_msg_len - len(self.msg))
            print("\r" + self.msg, end="")

    def _fit_on_epoch_end(self, epoch, logs):
        print()
        self.msg = []
        for callbeck in self.callbecks:
            if callbeck_msg := callbeck.on_epoch_end(epoch, logs):
                self.msg.append(callbeck_msg)
        if self.msg != []:
            self.msg = " - ".join(self.msg)
            print(self.msg)

    def _fit_on_train_end(self, logs):
        for callbeck in self.callbecks:
            if callbeck_msg := callbeck.on_train_end(logs):
                print(callbeck_msg)

    def fit(
        self,
        tx: optax.GradientTransformation,
        epochs: int = None,
        total_steps: int = None,
        callbecks: list[Callback] = [],
        default_callbecks: bool = True,
    ):
        epochs, logs, start_epoch, start_step = self._fit_on_train_start(
            tx, epochs, total_steps, callbecks, default_callbecks
        )

        for epoch in range(start_epoch, epochs):
            self._fit_on_epoch_start(epoch, logs)

            for step in range(start_step, len(self.data_loader)):
                batch = self._fit_on_step_start(step, logs)

                self._fit_step(batch, logs)

                self._fit_on_step_end(step, logs)

            self._fit_on_epoch_end(epoch, logs)

            start_step = 0

        self._fit_on_train_end(logs)

        self.state = logs.state
