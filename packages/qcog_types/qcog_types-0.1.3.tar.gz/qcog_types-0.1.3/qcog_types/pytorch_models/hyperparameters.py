from typing import Any, Literal

import torch  # type: ignore
from pydantic import BaseModel, ConfigDict, Field, model_validator
import logging

logger = logging.getLogger(__name__)


class PerGroupOptimizerParams(BaseModel):
    """Parameters for each group of parameters in the optimizer.

    This class defines the configuration for a specific group of model parameters
    that should receive distinct optimizer settings during training.

    Attributes
    ----------
    param_name_contains : list[str]
        List of substrings to identify parameters belonging to this group.
        Parameters whose names contain any of these substrings will be assigned to this group.
    params : dict[str, Any]
        Optimizer parameters specific to this group, e.g., {"lr": 0.0001, "weight_decay": 0.01}.
        These override the default optimizer parameters for this parameter group.
    """

    param_name_contains: list[str]
    params: dict[str, Any]


class OptimizerConfig(BaseModel):
    """Configuration for the optimiz er.

    This class provides a comprehensive configuration for PyTorch optimizers,
    including support for parameter groups with different learning rates or
    other optimizer-specific settings.

    Attributes
    ----------
    type : str
        Type of optimizer, e.g., 'Adam', 'SGD', 'AdamW', 'RMSprop'.
        Must match a class name in torch.optim
    default_params : dict[str, Any]
        Default parameters for the optimizer, e.g., {"lr": 0.001, "weight_decay": 0}.
        These are applied to all parameters unless overridden by group_params.
    group_params : list[PerGroupOptimizerParams] | None
        Optional list of parameter groups with specific optimizer settings.
        Allows different learning rates or other settings for different parts of the model.

    Examples
    --------
    >>> config = OptimizerConfig(
    ...     type="Adam",
    ...     default_params={"lr": 1e-3, "betas": (0.9, 0.999)},
    ...     group_params=[
    ...         PerGroupOptimizerParams(
    ...             param_name_contains=["bias"],
    ...             params={"lr": 1e-4, "weight_decay": 0}
    ...         )
    ...     ]
    ... )
    """

    type: str
    default_params: dict[str, Any] = Field(default_factory=dict)
    group_params: list[PerGroupOptimizerParams] | None = None


class LossFunctionConfig(BaseModel):
    """Configuration for the loss function.

    This class defines the loss function to be used during training,
    supporting built-in PyTorch losses.

    Attributes
    ----------
    type : str
        Name of the loss function class (e.g., 'MSELoss', 'CrossEntropyLoss' from torch.nn)
        or a fully qualified path to a custom loss function (e.g., 'mymodule.CustomLoss').
    params : dict[str, Any]
        Parameters for the loss function constructor.
        Examples: {"reduction": "mean"} for MSELoss, {"weight": [1.0, 2.0]} for weighted losses.

    Examples
    --------
    >>> # Using built-in loss
    >>> config = LossFunctionConfig(type="MSELoss", params={"reduction": "sum"})
    """

    type: str
    params: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SchedulerConfig(BaseModel):
    """Configuration for the learning rate scheduler.

    This class defines the learning rate scheduling strategy to be used during training,
    supporting various scheduling policies from PyTorch.

    Attributes
    ----------
    type : str
        Name of the scheduler class e.g., 'StepLR', 'CosineAnnealingLR', 'ReduceLROnPlateau'
        from torch.optim.lr_scheduler
    params : dict[str, Any]
        Parameters for the learning rate scheduler constructor.
        Examples: {"step_size": 30, "gamma": 0.1} for StepLR,
        {"T_max": 100} for CosineAnnealingLR.
    interval : Literal["epoch", "step"]
        Interval at which the scheduler step should be called.
        'epoch': scheduler.step() called after each epoch.
        'step': scheduler.step() called after each batch/optimization step.

    Notes
    -----
    For ReduceLROnPlateau, ensure params includes 'monitor' key specifying
    which metric to track (e.g., 'val_loss').
    """

    type: str
    params: dict[str, Any]
    interval: Literal["epoch", "step"] = "epoch"


class EarlyStoppingConfig(BaseModel):
    """Configuration for early stopping.

    This class defines the early stopping criteria to prevent overfitting
    by monitoring a metric and stopping training when it stops improving.

    Attributes
    ----------
    monitor : str
        Metric to monitor for early stopping, e.g., 'val_loss', 'val_accuracy'.
        Must match a metric logged during training.
    min_delta : float
        Minimum change in the monitored quantity to qualify as an improvement.
        Changes smaller than min_delta are considered no improvement.
    patience : int
        Number of epochs with no improvement after which training will be stopped.
        Provides tolerance for temporary performance plateaus.
    mode : Literal["min", "max"]
        Whether to minimize or maximize the monitored metric.
        'min': stop when metric stops decreasing (e.g., for loss).
        'max': stop when metric stops increasing (e.g., for accuracy).
    verbose : bool
        If True, prints messages when early stopping conditions are checked or triggered.
    restore_best_weights : bool
        Whether to restore model weights from the epoch with the best value
        of the monitored quantity when training is stopped.

    Examples
    --------
    >>> # Stop if validation loss doesn't improve for 5 epochs
    >>> config = EarlyStoppingConfig(
    ...     monitor="val_loss",
    ...     patience=5,
    ...     mode="min",
    ...     restore_best_weights=True
    ... )
    """

    monitor: str
    min_delta: float = 0.0001
    patience: int = 10
    mode: Literal["min", "max"] = "min"
    verbose: bool = False
    restore_best_weights: bool = True


class GradientClippingConfig(BaseModel):
    """Configuration for gradient clipping.

    This class defines gradient clipping parameters to prevent gradient explosion
    during training by limiting the magnitude of gradients.

    Attributes
    ----------
    max_norm : float
        Maximum allowed norm of the gradients. Gradients are scaled down
        if their norm exceeds this value.
    norm_type : float
        Type of the p-norm to use for computing gradient norm.
        Common values: 2.0 for L2 norm, float('inf') for infinity norm.

    Notes
    -----
    Gradient clipping is applied after gradients are computed but before
    the optimizer step. It helps stabilize training, especially for RNNs
    or when using large learning rates.

    Examples
    --------
    >>> # Clip gradients to max L2 norm of 1.0
    >>> config = GradientClippingConfig(max_norm=1.0, norm_type=2.0)
    """

    max_norm: float
    norm_type: float = 2.0


class ModelHyperparameters(BaseModel):
    """Base hyperparameters for configuring and training any PyTorch model.

    This class provides a comprehensive set of parameters for configuring and training
    PyTorch models. It serves as the base class for model-specific hyperparameter classes
    and includes all common training configuration options.

    Attributes
    ----------
    hsm_model : Literal["general", "pauli", "general_fullenergy"]
        Type of Hilbert Space Model to use.
    weighted_layer: bool
        Whether to use a weighted layer in the model. This adds learnable weights
        to the inputs to the HSM layer.
    epochs : int
        Total number of training epochs.
    batch_size : int
        Number of samples per training batch.
    split : float
        Fraction of the dataset to use for the test set (e.g., 0.2 for 20% test set).
    seed : int | None
        Random seed for reproducibility. If None, no seed is set.
    optimizer_config : OptimizerConfig
        Configuration for the optimizer, including type and parameters.
    loss_fn_config : LossFunctionConfig
        Configuration for the loss function.
    scheduler_config : SchedulerConfig | None
        Optional configuration for the learning rate scheduler.
    early_stopping_config : EarlyStoppingConfig | None
        Optional configuration for early stopping to prevent overfitting.
    gradient_clipping_config : GradientClippingConfig | None
        Optional configuration for gradient clipping to prevent gradient explosion.
    num_workers : int
        Number of worker processes for data loading.
        0 means data will be loaded in the main process.
    pin_memory : bool
        If True, the data loader will copy Tensors into CUDA pinned memory
        before returning them. Useful when transferring data to GPU.
    target : str
        Name of the target column in the dataset.
    device : str
        Device to use for training ('auto', 'cpu', 'cuda', 'mps').
        'auto' will attempt to use CUDA or MPS if available, otherwise CPU.

    Notes
    -----
    The device field supports automatic selection via 'auto', which will
    choose the best available device in order: CUDA > MPS > CPU.

    The model validator performs several consistency checks including device
    validation and learning rate presence verification.
    """

    hsm_model: Literal["general", "pauli", "general_fullenergy"]
    weighted_layer: bool = False
    epochs: int
    batch_size: int
    split: float = 0.2
    seed: int | None = 42

    optimizer_config: OptimizerConfig
    loss_fn_config: LossFunctionConfig
    scheduler_config: SchedulerConfig | None = None

    early_stopping_config: EarlyStoppingConfig | None = None
    gradient_clipping_config: GradientClippingConfig | None = None

    num_workers: int = 0
    pin_memory: bool = False

    target: str

    device: str = "auto"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def _validate_training_setup(self) -> "ModelHyperparameters":
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        elif self.device not in ["cpu", "cuda", "mps"]:
            raise ValueError(
                f"Unsupported device: {self.device}. Must be 'auto', 'cpu', 'cuda', or 'mps'."
            )

        if self.scheduler_config and self.scheduler_config.type == "ReduceLROnPlateau":
            sch_monitor = self.scheduler_config.params.get("monitor", "val_loss")
            if (
                self.early_stopping_config
                and self.early_stopping_config.monitor != sch_monitor
            ):
                logger.warning(
                    f"Scheduler 'ReduceLROnPlateau' monitors '{sch_monitor}'"
                    f" while EarlyStopping monitors '{self.early_stopping_config.monitor}'."
                    f" Ensure these are compatible or intentional."
                )
            if not sch_monitor.startswith(("val_", "train_")):
                logger.warning(
                    f"Scheduler 'ReduceLROnPlateau' monitor '{sch_monitor}' might not be standard."
                    f" Ensure your training loop logs this metric."
                )

        if self.early_stopping_config:
            es_monitor = self.early_stopping_config.monitor
            if not es_monitor.startswith(("val_", "train_")):
                logger.warning(
                    f"EarlyStopping monitor '{es_monitor}' might not be standard."
                    f" Ensure your training loop logs this metric."
                )

        # Validate presence of learning rate in optimizer_config
        if not self.optimizer_config.default_params.get(
            "lr"
        ) and not self.optimizer_config.default_params.get("learning_rate"):
            has_lr_in_groups = False
            if self.optimizer_config.group_params:
                for group in self.optimizer_config.group_params:
                    if group.params.get("lr") or group.params.get("learning_rate"):
                        has_lr_in_groups = True
                        break
            if not has_lr_in_groups:
                logger.warning(
                    "Learning rate ('lr' or 'learning_rate') not found in "
                    "optimizer_config.default_params or any group_params. "
                    "The optimizer's default LR will be used if available. "
                    "Ensure this is intentional or set LR explicitly if your optimizer requires it."
                )

        return self


class GeneralHSModelHyperparameters(ModelHyperparameters):
    """Hyperparameters for the General Hilbert Space Model and its training.

    This class extends ModelHyperparameters with specific parameters required
    for the General HSM, which uses arbitrary Hermitian operators in a
    Hilbert space.

    Attributes
    ----------
    input_operator_count : int
        Number of input operators. Corresponds to the number of input features.
    output_operator_count : int
        Number of output operators. Corresponds to the number of outputs/targets.
    hilbert_space_dims : int
        Dimension of the Hilbert space for each operator. Determines the size
        of the quantum state space.
    beta : float | None
        Mixing parameter for finding the new ground state. If None, the ground state is found
        by taking the eigenvector with the lowest eigenvalue.
    complex : bool
        Whether the operators are complex-valued (True) or real-valued (False).
        Complex is recommended.
    eigh_eps : float | None
        Small epsilon value added to the diagonal of matrices before eigenvalue
        decomposition to ensure numerical stability.

    Notes
    -----
    The model validator ensures consistency between tensor shapes, operator counts,
    and Hilbert space dimensions. It also verifies device consistency and complex
    type matching when pre-defined operators are provided.

    Additional checks are performed in the model code itself.
    """

    hsm_model: Literal["general", "general_fullenergy"]
    input_operator_count: int
    output_operator_count: int
    hilbert_space_dims: int
    beta: float | None = None
    complex: bool = True
    eigh_eps: float | None = 1e-8

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def _validate_general_hsm_specifics(self) -> "GeneralHSModelHyperparameters":
        if self.input_operator_count <= 0:
            raise ValueError("Input operator count must be greater than 0.")
        if self.output_operator_count <= 0:
            raise ValueError("Output operator count must be greater than 0.")
        if self.hilbert_space_dims <= 0:
            raise ValueError("Hilbert space dimension must be greater than 0.")
        return self


class PauliHSModelHyperparameters(ModelHyperparameters):
    """Hyperparameters for the Pauli Hilbert Space Model.

    This class extends ModelHyperparameters with specific parameters required
    for the Pauli HSM, which uses Pauli operators on a system of qubits.

    Attributes
    ----------
    input_operator_count : int
        Number of input Pauli operators. Corresponds to the number of input features.
    output_operator_count : int
        Number of output Pauli operators. Corresponds to the number of dimensions of the target.
    qubits_count : int
        Number of qubits in the Pauli model.
        The Hilbert space dimension will be 2**qubits_count.
    input_operator_pauli_weight : int | None
        The weight of the pauli strings that are used to compose the input operators.
        It is expected to be greater than zero and less than or equal to qubits_count.
        By default this is equal to the number of qubits to completely span the space.
    output_operator_pauli_weight : int | None
        The weight of the pauli strings that are used to compose the output operators.
        It is expected to be greater than zero and less than or equal to qubits_count.
        By default this is equal to the number of qubits to completely span the space.
    eigh_eps : float | None
        A small epsilon value used for numerical stability in eigenvalue solvers.

    Notes
    -----
    The Pauli model represents operators as linear combinations of Pauli strings
    (tensor products of Pauli matrices). The Pauli weight restricts the number of
    non-identity Pauli matrices in the operators.

    Examples
    --------
    >>> # 5-qubits, 10 features, 1-dim output, constrained pauli weight of 2 for input operators.
    >>> config = PauliHSModelHyperparameters(
    ...     hsm_model="pauli",
    ...     input_operator_count=10,
    ...     output_operator_count=1,
    ...     qubits_count=5,
    ...     input_operator_pauli_weight=2,
    ...     # ... other required fields
    ... )
    """

    hsm_model: Literal["pauli"]

    # Model Architecture Specific Params
    input_operator_count: int
    output_operator_count: int
    qubits_count: int

    input_operator_pauli_weight: int | None = None
    output_operator_pauli_weight: int | None = None
    eigh_eps: float | None = 1e-8

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def _validate_pauli_hsm_specifics(self) -> "PauliHSModelHyperparameters":
        if self.input_operator_count <= 0:
            raise ValueError("Input operator count must be greater than 0.")
        if self.output_operator_count <= 0:
            raise ValueError("Output operator count must be greater than 0.")
        if self.qubits_count <= 0:
            raise ValueError("Quibts count must be greater than 0.")
        if self.input_operator_pauli_weight is not None and (
            self.input_operator_pauli_weight > self.qubits_count
            or self.input_operator_pauli_weight < 1
        ):
            raise ValueError(
                "Input Pauli weight cannot be greater than qubits count or less than 1."
            )

        if self.output_operator_pauli_weight is not None and (
            self.output_operator_pauli_weight > self.qubits_count
            or self.output_operator_pauli_weight < 1
        ):
            raise ValueError(
                "Output Pauli weight cannot be greater than qubits count or less than 1."
            )
        return self
