import pytest
import torch

from ..callbacks import EarlyStopping
from ..hyperparameters import EarlyStoppingConfig
from torch import nn
from pydantic import ValidationError


@pytest.fixture
def simple_model() -> nn.Module:
    """Provides a simple PyTorch model for testing."""
    return torch.nn.Linear(10, 2)


def test_early_stopping_min_mode_stops(simple_model: nn.Module) -> None:
    """Tests if early stopping triggers correctly in 'min' mode."""
    config = EarlyStoppingConfig(
        monitor="val_loss", patience=2, mode="min", restore_best_weights=False
    )
    early_stopping = EarlyStopping(config=config)

    # No improvement
    early_stopping(1.0, simple_model, 0)
    assert not early_stopping.should_stop
    early_stopping(1.1, simple_model, 1)
    assert not early_stopping.should_stop
    early_stopping(1.2, simple_model, 2)
    assert early_stopping.should_stop


def test_early_stopping_max_mode_stops(simple_model: nn.Module) -> None:
    """Tests if early stopping triggers correctly in 'max' mode."""
    config = EarlyStoppingConfig(
        monitor="val_acc", patience=2, mode="max", restore_best_weights=False
    )
    early_stopping = EarlyStopping(config=config)

    # No improvement
    early_stopping(0.8, simple_model, 0)
    assert not early_stopping.should_stop
    early_stopping(0.7, simple_model, 1)
    assert not early_stopping.should_stop
    early_stopping(0.6, simple_model, 2)
    assert early_stopping.should_stop


def test_early_stopping_does_not_stop_if_improving(simple_model: nn.Module) -> None:
    """Tests that early stopping does not trigger if the metric is improving."""
    config = EarlyStoppingConfig(monitor="val_loss", patience=3, mode="min")
    early_stopping = EarlyStopping(config=config)

    early_stopping(1.0, simple_model, 0)
    early_stopping(0.9, simple_model, 1)  # Improvement
    early_stopping(0.9, simple_model, 2)
    early_stopping(0.8, simple_model, 3)  # Improvement
    assert not early_stopping.should_stop


def test_restore_best_weights(simple_model: nn.Module) -> None:
    """Tests if the best model weights are restored correctly."""
    config = EarlyStoppingConfig(
        monitor="val_loss", patience=2, mode="min", restore_best_weights=True
    )
    early_stopping = EarlyStopping(config=config)

    # First score, should be best
    simple_model.weight.data.fill_(1.0)  # type: ignore[operator]
    early_stopping(1.0, simple_model, 0)

    # Worse score
    simple_model.weight.data.fill_(2.0)  # type: ignore[operator]
    early_stopping(1.1, simple_model, 1)

    # Even worse score, should stop
    simple_model.weight.data.fill_(3.0)  # type: ignore[operator]
    early_stopping(1.2, simple_model, 2)
    assert early_stopping.should_stop

    # Restore weights and check
    early_stopping.restore_weights(simple_model)
    assert torch.all(simple_model.weight.data == 1.0)  # type: ignore[arg-type]


def test_invalid_mode_raises_pydantic_error() -> None:
    """Tests that an invalid mode raises a Pydantic ValidationError."""
    with pytest.raises(ValidationError, match="Input should be 'min' or 'max'"):
        EarlyStoppingConfig(monitor="val_loss", mode="invalid_mode")  # type: ignore[arg-type]
