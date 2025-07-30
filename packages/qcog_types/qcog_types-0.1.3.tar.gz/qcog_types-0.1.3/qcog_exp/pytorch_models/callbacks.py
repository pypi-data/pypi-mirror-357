import logging
from typing import Any

import torch  # type: ignore

from hyperparameters import EarlyStoppingConfig

# Initialize logger at module level
logger = logging.getLogger(__name__)

StateDict = dict[str, Any]


class EarlyStopping:
    """Implements early stopping logic.

    Monitors a metric and stops training when it stops improving.

    Attributes
    ----------
    patience : int
        Number of epochs to wait for improvement before stopping.
    mode : str
        "min" or "max". Whether the monitored metric should be minimized or maximized.
    min_delta : float
        Minimum change in the monitored quantity to qualify as an improvement.
    monitor : str
        The metric to monitor (e.g., "val_loss").
    restore_best_weights : bool
        If True, the model weights from the epoch with the best score will be restored.
    verbose : bool
        If True, prints messages for each step.
    """

    def __init__(self, config: EarlyStoppingConfig) -> None:
        self.config = config
        self.best_score = float("inf") if self.config.mode == "min" else float("-inf")
        self.epochs_no_improve = 0
        self.best_model_state_dict: StateDict | None = None
        self._stop_training = False

    def __call__(self, score: float, model: torch.nn.Module, epoch: int) -> None:
        """Call the early stopping logic.

        Parameters
        ----------
        score : float
            The metric score for the current epoch.
        model : torch.nn.Module
            The model being trained.
        epoch : int
            The current epoch number.
        """
        improved = False
        if self.config.mode == "min":
            if score < self.best_score - self.config.min_delta:
                self.best_score = score
                improved = True
        elif self.config.mode == "max":
            if score > self.best_score + self.config.min_delta:
                self.best_score = score
                improved = True
        else:
            raise ValueError(
                f"Invalid mode: {self.config.mode}. Expected 'min' or 'max'."
            )

        if improved:
            self.epochs_no_improve = 0
            if self.config.restore_best_weights:
                self.best_model_state_dict = {
                    k: v.clone() for k, v in model.state_dict().items()
                }
                if self.config.verbose:
                    logger.info(
                        f"EarlyStopping: New best model found at epoch {epoch} with {self.config.monitor}: {self.best_score:.4f}"
                    )
        else:
            self.epochs_no_improve += 1
            if self.config.verbose:
                logger.info(
                    f"EarlyStopping: No improvement for {self.epochs_no_improve} epochs. Patience: {self.config.patience}"
                )

        if self.epochs_no_improve >= self.config.patience:
            self._stop_training = True
            if self.config.verbose:
                logger.info(
                    f"EarlyStopping: Stopping training at epoch {epoch} as {self.config.monitor} did not improve for {self.config.patience} epochs."
                )

    @property
    def should_stop(self) -> bool:
        """Whether the training should be stopped."""
        return self._stop_training

    def restore_weights(self, model: torch.nn.Module) -> None:
        """Restore model weights to the best found so far."""
        if self.config.restore_best_weights and self.best_model_state_dict:
            if self.config.verbose:
                logger.info("EarlyStopping: Restoring best model weights.")
            model.load_state_dict(self.best_model_state_dict)
