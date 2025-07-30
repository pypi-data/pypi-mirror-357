from typing import Any, Callable, Literal, NotRequired, TypedDict, Unpack
import numpy as np  # type: ignore
import torch  # type: ignore
from qcog_torch.layers.general import PytorchGeneralHSM  # type: ignore
from qcog_torch.layers.pauli import PytorchPauliHSM  # type: ignore
from qcog_torch.layers.general_full_energy import PytorchGeneralHSMFullEnergy  # type: ignore
from qcog_torch.layers.weighted import WeightedLayer  # type: ignore
import pandas as pd  # type: ignore
from torch.utils.data import Dataset, DataLoader  # type: ignore
from qcog_torch import nptype  # type: ignore
from resolve_dataset import resolve_dataset
from split_dataset import split_dataset
from callbacks import EarlyStopping
from hyperparameters import (
    ModelHyperparameters,
    GeneralHSModelHyperparameters,
    PauliHSModelHyperparameters,
)
import logging
import time

# Required exports --------------------------------------------------------+
# The following exports are used by the API to determine the version       |
# of the train and predict functions.                                      |
#                                                                          |
# Hyperparameters will eventually be used to generate a package for        |
# the client that will be used to validate and type hint the parameters    |
# -------------------------------------------------------------------------+

TRAIN_VERSION = "v0.0.1"
PREDICT_VERSION = "v0.0.1"

# -------------------------------------------------------------------------+

ColumnName = str
Function = Literal["to_datetime"]
ApplyTransform = dict[ColumnName, Function]

# Create a union type for all supported hyperparameter types
SupportedHyperparameters = (
    GeneralHSModelHyperparameters | PauliHSModelHyperparameters | ModelHyperparameters
)


class DataFrameDataset(Dataset):
    """DataFrame Dataset."""

    def __init__(self, df: pd.DataFrame, target: str, device: str):
        """
        Initialize a dataset from a dataframe

        Parameters
        ----------
        df: pd.DataFrame
            Dataframe with data to use
        target: str
            Target variable name which must be a column in df
        device: str
            Device for torch
        """
        target_data = df[[target]].values.astype(nptype(), copy=True)
        inputs_data = df.drop([target], axis=1).values.astype(nptype(), copy=True)
        self.target = torch.tensor(target_data).to(device=device)
        self.inputs = torch.tensor(inputs_data).to(device=device)

    def __len__(self) -> int:
        """Get the length of the dataset."""
        return len(self.target)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Get an item from the dataset."""
        return self.inputs[idx, :], self.target[idx, :]


StateDict = dict[str, Any]


class Checkpoint(TypedDict):
    model_state_dict: StateDict
    timestamp: str
    current_epoch: int
    other_states: dict[str, Any] | None
    optimizer_state_dict: dict[str, Any] | None
    hyperparameters: dict[str, Any] | None
    metrics: dict[str, Any] | None


class SaveCheckpointKwargs(TypedDict):
    """
    Kwargs for the save_checkpoint method.

    model_state_dict: The model state dictionary when the checkpoint was saved.
    current_epoch: The current epoch when the checkpoint was saved.
    other_states: Other states to save (e.g, loss, optimizers, etc.)
    optimizer_state_dict: The optimizer state dictionary when the checkpoint was saved.
    hyperparameters: The hyperparameters of the experiment.
    metrics: The metrics of the experiment at the time the checkpoint was saved.
    """

    model_state_dict: dict[str, Any]
    current_epoch: int
    other_states: dict[str, Any] | None
    hyperparameters: dict[str, Any] | None
    metrics: dict[str, Any] | None


class TrainContext(TypedDict):
    status_id: str  # The train identifier
    save_checkpoint: NotRequired[Callable[[Unpack[SaveCheckpointKwargs]], None]]
    load_last_checkpoint: NotRequired[Callable[[], Checkpoint | None]]
    dataset_bucket: str
    dataset_format: str


def train(
    context: TrainContext,
    dataset_path: str,
    *,
    params: dict[str, Any],
) -> dict[str, Any]:
    print("=== STARTING TRAINING ===")
    print(f"Status ID: {context.get('status_id', 'unknown')}")

    hyperparameters_dict: dict = params.get("hyperparameters", {})

    if not hyperparameters_dict:
        raise ValueError("Hyperparameters must be provided")

    # Determine the HSM model type to parse the correct hyperparameters
    hsm_model_type = hyperparameters_dict.get("hsm_model")
    print(f"HSM Model Type: {hsm_model_type}")

    hyperparameters: SupportedHyperparameters
    if hsm_model_type == "general":
        hyperparameters = GeneralHSModelHyperparameters.model_validate(
            hyperparameters_dict
        )
    elif hsm_model_type == "pauli":
        hyperparameters = PauliHSModelHyperparameters.model_validate(
            hyperparameters_dict
        )
    elif hsm_model_type == "general_fullenergy":
        # General Full Energy model uses GeneralHSModelHyperparameters for its structure
        hyperparameters = GeneralHSModelHyperparameters.model_validate(
            hyperparameters_dict
        )
    else:
        raise ValueError(
            f"hsm_model type '{hsm_model_type}' is not explicitly handled or is missing. Available types are: general, pauli, general_fullenergy"
        )

    print("Training Configuration:")
    print(f"  - Epochs: {hyperparameters.epochs}")
    print(f"  - Batch Size: {hyperparameters.batch_size}")
    print(f"  - Target: {hyperparameters.target}")
    print(f"  - Test Split: {hyperparameters.split}")
    print(f"  - Seed: {hyperparameters.seed}")

    # Extract hooks to save and extract checkpoints
    save_checkpoint_hook = context.get("save_checkpoint", None)
    load_last_checkpoint_hook = context.get("load_last_checkpoint", None)

    # Extract dataset information from the context
    dataset_bucket = context.get("dataset_bucket", "s3")
    dataset_format = context.get("dataset_format", "csv")

    # Check if there is a checkpoint
    checkpoint: Checkpoint | None = None

    if load_last_checkpoint_hook:
        checkpoint = load_last_checkpoint_hook()

    # Initialize checkpoint-related variables
    epochs_completed: int = 0
    optimizer_state_dict: dict[str, Any] | None = None
    model_state_dict: dict[str, Any] | None = None

    if checkpoint:
        epochs_completed = checkpoint.get("current_epoch", 0)
        model_state_dict = checkpoint.get("model_state_dict")
        other_states = checkpoint.get("other_states")
        if other_states:
            optimizer_state_dict = other_states.get("optimizer_state_dict")
            loss = other_states.get("loss")

        print(f"Resuming from checkpoint - Epochs completed: {epochs_completed}")
    else:
        print("Starting fresh training - no checkpoint found")

    # Use validated hyperparameters
    torch.manual_seed(hyperparameters.seed if hyperparameters.seed is not None else 42)

    # Device setup from hyperparameters - Correctly use the validated device from Pydantic model
    device = hyperparameters.device
    print(f"Using device: {device}")
    print(f"Dataset path: {dataset_path}")

    print("Loading dataset...")
    dataset = resolve_dataset(
        dataset_path=dataset_path,
        bucket_type=dataset_bucket,
        dataset_format=dataset_format,
    )
    print(f"Dataset loaded - Shape: {dataset.shape}")

    # Use split from the typed hyperparameter object
    train_df, test_df = split_dataset(dataset, test_size=hyperparameters.split)
    print(f"Dataset split - Train: {train_df.shape}, Test: {test_df.shape}")

    # Derive operator counts from the data for training
    data_derived_input_operator_count = (
        train_df.shape[1] - 1
    )  # Assuming target is one column
    data_derived_output_operator_count = 1  # Assuming single output

    print(
        f"Data-derived dimensions - Input operators: {data_derived_input_operator_count}, Output operators: {data_derived_output_operator_count}"
    )

    # Check that the operator counts are consistent with the data
    if isinstance(
        hyperparameters, (GeneralHSModelHyperparameters, PauliHSModelHyperparameters)
    ):
        if hyperparameters.input_operator_count != data_derived_input_operator_count:
            raise ValueError(
                f"Input operator count (feature dimension) mismatch: "
                f"Hyperparameters: {hyperparameters.input_operator_count} != "
                f"Data: {data_derived_input_operator_count}"
            )
        if hyperparameters.output_operator_count != data_derived_output_operator_count:
            raise ValueError(
                f"Output operator count (target dimension) mismatch: "
                f"Hyperparameters: {hyperparameters.output_operator_count} != "
                f"Data: {data_derived_output_operator_count}"
            )

    print("Creating data loaders...")
    train_dataset = DataFrameDataset(
        df=train_df, target=hyperparameters.target, device=device
    )
    test_dataset = DataFrameDataset(
        df=test_df, target=hyperparameters.target, device=device
    )
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=hyperparameters.batch_size,
        shuffle=True,
        num_workers=hyperparameters.num_workers,
        pin_memory=hyperparameters.pin_memory,
    )
    test_dataloader = DataLoader(
        test_dataset,
        batch_size=test_df.shape[0],
        shuffle=False,
        num_workers=hyperparameters.num_workers,
        pin_memory=hyperparameters.pin_memory,
    )
    print(
        f"Data loaders created - Train batches: {len(train_dataloader)}, Test batches: {len(test_dataloader)}"
    )

    print("Initializing model...")
    # Model instantiation based on hsm_model type
    hsm_layer: PytorchGeneralHSM | PytorchPauliHSM | PytorchGeneralHSMFullEnergy
    if hyperparameters.hsm_model == "general":
        assert isinstance(hyperparameters, GeneralHSModelHyperparameters)
        hsm_layer = PytorchGeneralHSM(
            input_operator_count=hyperparameters.input_operator_count,
            output_operator_count=hyperparameters.output_operator_count,
            hilbert_space_dims=hyperparameters.hilbert_space_dims,
            beta=hyperparameters.beta,
            complex=hyperparameters.complex,
            eigh_eps=hyperparameters.eigh_eps,
            device=device,
        )
    elif hyperparameters.hsm_model == "pauli":
        assert isinstance(hyperparameters, PauliHSModelHyperparameters)
        hsm_layer = PytorchPauliHSM(
            input_operator_count=hyperparameters.input_operator_count,
            output_operator_count=hyperparameters.output_operator_count,
            qubits_count=hyperparameters.qubits_count,
            input_operator_pauli_weight=hyperparameters.input_operator_pauli_weight,
            output_operator_pauli_weight=hyperparameters.output_operator_pauli_weight,
            eigh_eps=hyperparameters.eigh_eps,
            device=device,
        )
    elif hyperparameters.hsm_model == "general_fullenergy":
        assert isinstance(hyperparameters, GeneralHSModelHyperparameters)
        hsm_layer = PytorchGeneralHSMFullEnergy(
            input_operator_count=hyperparameters.input_operator_count,
            output_operator_count=hyperparameters.output_operator_count,
            hilbert_space_dims=hyperparameters.hilbert_space_dims,
            device=device,
        )
    else:
        # This case should ideally be caught by the initial hyperparameter validation
        raise ValueError(f"Unsupported hsm_model type: {hyperparameters.hsm_model}")

    if hyperparameters.weighted_layer:
        model = WeightedLayer(hsm_layer=hsm_layer, device=device)
        print("Using WeightedLayer wrapper")
    else:
        model = hsm_layer
        print("Using HSM layer directly")

    # Display information about the model
    print(f"Model: {model}")
    print(
        f"Model named parameters: {[(name, param.shape) for name, param in model.named_parameters()]}"
    )

    # Load the checkpoint if it exists
    if model_state_dict:  # Check if model_state_dict was loaded from checkpoint
        print("Loading model from checkpoint...")
        # Add diagnostic logging to debug tensor size mismatch
        print("=== DEBUGGING MODEL LOADING ===")
        print(
            f"Hyperparameters input_operator_count: {hyperparameters.input_operator_count}"
        )
        print("Expected model parameter shapes:")
        for name, param in model.named_parameters():
            print(f"  {name}: {param.shape}")

        print("Checkpoint model parameter shapes:")
        for name, tensor in model_state_dict.items():
            if hasattr(tensor, "shape"):
                print(f"  {name}: {tensor.shape}")
            else:
                print(f"  {name}: {type(tensor)}")
        print("=== END DEBUGGING ===")

        model.load_state_dict(model_state_dict)
        print("Model loaded successfully from checkpoint")

    print("Setting up optimizer...")
    # Optimizer setup
    opt_config = hyperparameters.optimizer_config
    optimizer_cls = getattr(torch.optim, opt_config.type)

    param_groups = []
    if opt_config.group_params:
        # Create a set of all parameter names for easier lookup
        # all_param_names = {name for name, _ in model.named_parameters()} # This variable was unused

        # Assign parameters to groups
        assigned_param_names = set()
        for group_spec in opt_config.group_params:
            group_params_list = []
            for name, param in model.named_parameters():
                if (
                    any(substr in name for substr in group_spec.param_name_contains)
                    and name not in assigned_param_names
                ):
                    group_params_list.append(param)
                    assigned_param_names.add(name)
            if group_params_list:
                param_groups.append({"params": group_params_list, **group_spec.params})
            else:
                print(
                    f"Optimizer group with 'param_name_contains': {group_spec.param_name_contains} did not match any parameters."
                )

        # Add remaining parameters with default settings
        default_params_list = [
            param
            for name, param in model.named_parameters()
            if name not in assigned_param_names
        ]
        if default_params_list:
            param_groups.append(
                {"params": default_params_list, **opt_config.default_params}
            )
        elif not param_groups:
            param_groups.append(
                {"params": model.parameters(), **opt_config.default_params}
            )

    else:
        param_groups = [{"params": model.parameters(), **opt_config.default_params}]

    optimizer = optimizer_cls(param_groups)

    print(f"Optimizer: {optimizer}")
    print(f"Optimizer State Dict (initial): {optimizer.state_dict()}")

    if optimizer_state_dict:  # Check if optimizer_state_dict was loaded from checkpoint
        optimizer.load_state_dict(optimizer_state_dict)
        print("Optimizer state loaded from checkpoint")

    print("Setting up loss function...")
    # Loss function setup
    loss_fn_config = hyperparameters.loss_fn_config
    loss_fn_cls = getattr(torch.nn, loss_fn_config.type)
    loss_fn = loss_fn_cls(**loss_fn_config.params)

    print(f"Loss function: {loss_fn}")

    # Scheduler setup (optional)
    scheduler = None
    if hyperparameters.scheduler_config:
        sch_config = hyperparameters.scheduler_config
        scheduler_cls = getattr(torch.optim.lr_scheduler, sch_config.type)
        scheduler = scheduler_cls(optimizer, **sch_config.params)
        print(f"Scheduler: {scheduler}")

    # Early stopping setup (optional)
    early_stopping: EarlyStopping | None = None
    if hyperparameters.early_stopping_config:
        es_config = hyperparameters.early_stopping_config
        early_stopping = EarlyStopping(config=es_config)
        print(
            f"Early stopping enabled: monitor='{es_config.monitor}', patience={es_config.patience}"
        )

    # Initialize training metrics tracking
    train_loss_history = []
    val_loss_history = []
    epoch_times = []
    best_val_loss = float('inf')

    # Get dataset sizes
    train_dataset_size = len(train_dataset)
    val_dataset_size = len(test_dataset)  # Currently using test set as validation

    # Start training timer
    training_start_time = time.time()

    print("=== STARTING TRAINING LOOP ===")
    # Training loop
    for epoch in range(hyperparameters.epochs - epochs_completed):
        epoch_start_time = time.time()
        actual_epoch = epoch + epochs_completed
        model.train(True)
        epoch_train_loss = 0.0
        num_train_batches = 0

        for batch, (X, y) in enumerate(train_dataloader):
            # Only print batch info every 10 batches to reduce log crowding
            if batch % 10 == 0:
                print(f"Epoch {actual_epoch}/{hyperparameters.epochs} - Batch {batch}/{len(train_dataloader)}")

            pred = model(X)
            loss = loss_fn(pred, y)
            epoch_train_loss += loss.item()
            num_train_batches += 1

            if loss is not None:
                # Only print loss every 100 batches to reduce log crowding
                if batch % 100 == 0:
                    print(f"Loss: {loss.item()}")

                optimizer.zero_grad()
                loss.backward()
                if hyperparameters.gradient_clipping_config:
                    clip_config = hyperparameters.gradient_clipping_config
                    torch.nn.utils.clip_grad_norm_(
                        model.parameters(),
                        max_norm=clip_config.max_norm,
                        norm_type=clip_config.norm_type,
                    )
                optimizer.step()

        avg_epoch_train_loss = (
            epoch_train_loss / num_train_batches if num_train_batches > 0 else 0.0
        )

        # Only print epoch results every 10 epochs to reduce log crowding
        if actual_epoch % 10 == 0 or actual_epoch == epochs_completed:
            print(f"Epoch {actual_epoch} Training Loss: {avg_epoch_train_loss:.4f}")

        # Validation step (conceptual - needs actual validation data and metric calculation)
        model.eval()
        epoch_val_loss = 0.0  # Placeholder for actual validation metric
        num_val_batches = 0
        with torch.no_grad():
            for (
                X_val,
                y_val,
            ) in (
                test_dataloader
            ):  # Using test_dataloader for now, ideally a separate val_dataloader
                pred_val = model(X_val)
                val_loss_item = loss_fn(
                    pred_val, y_val
                ).item()  # Assuming same loss_fn for validation
                epoch_val_loss += val_loss_item
                num_val_batches += 1

        avg_epoch_val_loss = (
            epoch_val_loss / num_val_batches if num_val_batches > 0 else 0.0
        )

        avg_epoch_val_loss = epoch_val_loss / num_val_batches if num_val_batches > 0 else 0.0
        print(f"Epoch {actual_epoch} Validation Loss: {avg_epoch_val_loss:.4f}")

        # Track metrics
        train_loss_history.append(avg_epoch_train_loss)
        val_loss_history.append(avg_epoch_val_loss)

        # Update best validation loss
        if avg_epoch_val_loss < best_val_loss:
            best_val_loss = avg_epoch_val_loss

        # Track epoch time
        epoch_end_time = time.time()
        epoch_time = epoch_end_time - epoch_start_time
        epoch_times.append(epoch_time)

        # Only print validation results every 10 epochs to reduce log crowding
        if actual_epoch % 10 == 0 or actual_epoch == epochs_completed:
            print(f"Epoch {actual_epoch} Validation Loss: {avg_epoch_val_loss:.4f}")

        # Store epoch metrics in a dictionary to avoid hardcoding
        epoch_metrics = {
            "train_loss": avg_epoch_train_loss,
            "val_loss": avg_epoch_val_loss,
        }

        # Scheduler step
        if scheduler:
            if (
                hyperparameters.scheduler_config
                and hyperparameters.scheduler_config.type == "ReduceLROnPlateau"
            ):
                # ReduceLROnPlateau typically uses a validation metric
                metric_to_monitor_scheduler = (
                    hyperparameters.scheduler_config.params.get("monitor", "val_loss")
                )
                if metric_to_monitor_scheduler in epoch_metrics:
                    scheduler.step(epoch_metrics[metric_to_monitor_scheduler])
                else:
                    print(
                        f"Metric '{metric_to_monitor_scheduler}' not found for scheduler. Available metrics: {list(epoch_metrics.keys())}"
                    )
            elif (
                hyperparameters.scheduler_config
                and hyperparameters.scheduler_config.interval == "epoch"
            ):
                scheduler.step()
            # Step-based schedulers would be handled inside the batch loop (not implemented here for simplicity)

        # Early stopping check
        if early_stopping:
            metric_to_monitor_es = early_stopping.config.monitor
            if metric_to_monitor_es in epoch_metrics:
                current_metric_val = epoch_metrics[metric_to_monitor_es]
                early_stopping(current_metric_val, model, actual_epoch)
                if early_stopping.should_stop:
                    print(f"Early stopping triggered at epoch {actual_epoch}")
                    break  # Exit training loop
            else:
                raise ValueError(
                    f"Metric '{metric_to_monitor_es}' for early stopping not found. Available metrics: {list(epoch_metrics.keys())}"
                )

        # Save the checkpoint
        if save_checkpoint_hook:
            save_checkpoint_hook(
                model_state_dict=model.state_dict(),
                current_epoch=actual_epoch + 1,
                other_states={
                    "optimizer_state_dict": optimizer.state_dict(),
                    "loss": avg_epoch_train_loss,
                },
                hyperparameters=hyperparameters.model_dump(),
                metrics={
                    "loss": avg_epoch_train_loss,
                },
            )

    # Restore best weights if early stopping was used and configured to do so
    if early_stopping and early_stopping.config.restore_best_weights:
        early_stopping.restore_weights(model)
        print("Best weights restored from early stopping")

    # End training timer
    training_end_time = time.time()
    total_training_time = training_end_time - training_start_time

    # Calculate average epoch time
    avg_epoch_time = sum(epoch_times) / len(epoch_times) if epoch_times else 0.0

    # Final epoch count
    final_epochs_completed = epochs_completed + len(train_loss_history)

    # Get final losses
    final_train_loss = train_loss_history[-1] if train_loss_history else 0.0
    final_val_loss = val_loss_history[-1] if val_loss_history else 0.0

    print("=== EVALUATING ON TEST SET ===")
    # Test
    model.eval()
    num_batches = len(test_dataloader)
    test_loss = 0.0
    with torch.no_grad():
        for X, y in test_dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()

    test_loss /= num_batches
    print(f"Final Test Loss: {test_loss:.6f}")
    print("=== TRAINING COMPLETED ===")

    return {
        "metrics": {
            "test_loss": test_loss,
            "train_loss_history": train_loss_history,
            "val_loss_history": val_loss_history,
            "final_train_loss": final_train_loss,
            "final_val_loss": final_val_loss,
            "epochs_completed": final_epochs_completed,
            "best_val_loss": best_val_loss,
            "train_dataset_size": train_dataset_size,
            "val_dataset_size": val_dataset_size,
            "total_training_time": total_training_time,
            "avg_epoch_time": avg_epoch_time,
            "checkpoint_metrics": ["loss"]
        }
    }


class PredictContext(TypedDict):
    pass


def predict(
    context: PredictContext,
    checkpoint: Checkpoint,
    *,
    params: dict[str, Any],
) -> dict[str, Any]:
    print("=== STARTING PREDICTION ===")

    # Load hyperparameters from checkpoint
    hyperparameters_dict = checkpoint.get("hyperparameters")
    if not hyperparameters_dict:
        raise ValueError("Hyperparameters must be provided in the checkpoint")

    # Determine the HSM model type to parse the correct hyperparameters object
    hsm_model_type = hyperparameters_dict.get("hsm_model")
    print(f"HSM Model Type from checkpoint: {hsm_model_type}")

    hyperparameters_obj: SupportedHyperparameters
    if hsm_model_type == "general":
        hyperparameters_obj = GeneralHSModelHyperparameters.model_validate(
            hyperparameters_dict
        )
    elif hsm_model_type == "pauli":
        hyperparameters_obj = PauliHSModelHyperparameters.model_validate(
            hyperparameters_dict
        )
    elif hsm_model_type == "general_fullenergy":
        hyperparameters_obj = GeneralHSModelHyperparameters.model_validate(
            hyperparameters_dict
        )
    else:
        # If the hsm_model_type from checkpoint is unknown, we attempt to fall back to base ModelHyperparameters
        # or raise an error if that's not suitable / hsm_model_type is truly unrecognized.
        print(
            f"hsm_model type '{hsm_model_type}' in checkpoint is not explicitly handled or is missing. "
            f"Falling back to ModelHyperparameters for prediction. Model rehydration might be incomplete if model-specific params are needed."
        )
        # It's safer to raise an error if the specific model type can't be determined for rehydration
        # as Pytorch*HSM layers require specific counts.
        # However, the user might have a case where ModelHyperparameters is sufficient.
        # For now, let's try to validate with ModelHyperparameters as a last resort before erroring.
        try:
            hyperparameters_obj = ModelHyperparameters.model_validate(
                hyperparameters_dict
            )
        except Exception as e:
            raise ValueError(
                f"Unsupported or invalid hsm_model type '{hsm_model_type}' in checkpoint for prediction. Error: {e}"
            )

    print("Model Configuration from checkpoint:")
    print(
        f"  - Input operators: {getattr(hyperparameters_obj, 'input_operator_count', None)}"
    )
    print(
        f"  - Output operators: {getattr(hyperparameters_obj, 'output_operator_count', None)}"
    )
    print(f"  - Device: {hyperparameters_obj.device}")
    print(f"  - Weighted layer: {hyperparameters_obj.weighted_layer}")

    dataset_bucket = str(context.get("dataset_bucket", "s3"))
    dataset_format = str(context.get("dataset_format", "csv"))

    device = (
        hyperparameters_obj.device
    )  # Use device from loaded and validated hyperparameters object
    print(f"Using device: {device}")

    print("Rehydrating model from checkpoint...")
    # Rehydrate the model based on hsm_model type stored in the hyperparameter object itself
    hsm_layer: PytorchGeneralHSM | PytorchPauliHSM | PytorchGeneralHSMFullEnergy
    if hyperparameters_obj.hsm_model == "general":
        assert isinstance(hyperparameters_obj, GeneralHSModelHyperparameters)
        input_op_count = hyperparameters_obj.input_operator_count
        output_op_count = hyperparameters_obj.output_operator_count

        hsm_layer = PytorchGeneralHSM(
            input_operator_count=input_op_count,
            output_operator_count=output_op_count,
            hilbert_space_dims=hyperparameters_obj.hilbert_space_dims,
            beta=hyperparameters_obj.beta,
            complex=hyperparameters_obj.complex,
            eigh_eps=hyperparameters_obj.eigh_eps,
            device=device,
        )
        print("Created PytorchGeneralHSM layer")
    elif hyperparameters_obj.hsm_model == "pauli":
        assert isinstance(hyperparameters_obj, PauliHSModelHyperparameters)
        hsm_layer = PytorchPauliHSM(
            input_operator_count=hyperparameters_obj.input_operator_count,
            output_operator_count=hyperparameters_obj.output_operator_count,
            qubits_count=hyperparameters_obj.qubits_count,
            input_operator_pauli_weight=hyperparameters_obj.input_operator_pauli_weight,
            output_operator_pauli_weight=hyperparameters_obj.output_operator_pauli_weight,
            eigh_eps=hyperparameters_obj.eigh_eps,
            device=device,
        )
        print("Created PytorchPauliHSM layer")
    elif hyperparameters_obj.hsm_model == "general_fullenergy":
        assert isinstance(hyperparameters_obj, GeneralHSModelHyperparameters)
        hsm_layer = PytorchGeneralHSMFullEnergy(
            input_operator_count=hyperparameters_obj.input_operator_count,
            output_operator_count=hyperparameters_obj.output_operator_count,
            hilbert_space_dims=hyperparameters_obj.hilbert_space_dims,
            device=device,
        )
        print("Created PytorchGeneralHSMFullEnergy layer")
    else:
        raise ValueError(
            f"Unsupported hsm_model type in checkpoint: {hyperparameters_obj.hsm_model}"
        )

    if hyperparameters_obj.weighted_layer:
        model = WeightedLayer(hsm_layer=hsm_layer, device=device)
        print("Using WeightedLayer wrapper")
    else:
        model = hsm_layer
        print("Using HSM layer directly")

    # Display information about the model
    print(f"Model: {model}")
    print(
        f"Model named parameters: {[(name, param.shape) for name, param in model.named_parameters()]}"
    )

    model_state_dict = checkpoint.get("model_state_dict")
    if not model_state_dict:
        raise ValueError("model_state_dict not found in checkpoint")

    print("Loading model weights from checkpoint...")
    model.load_state_dict(model_state_dict)
    print("Model weights loaded successfully")

    dataset_path = params.get("dataset_path", None)
    dataset_buffer = params.get("dataset_buffer", None)

    if dataset_path is None and dataset_buffer is None:
        raise ValueError("Dataset path or buffer must be provided")

    print("Loading prediction dataset...")
    if dataset_path:
        print(f"Dataset path: {dataset_path}")
    else:
        print("Using dataset buffer")

    dataset = resolve_dataset(
        dataset_path=dataset_path,
        dataset_buffer=dataset_buffer,
        bucket_type=dataset_bucket,
        dataset_format=dataset_format,
    )

    print(f"Prediction dataset loaded - Shape: {dataset.shape}")
    dataset = dataset.values.astype(np.float32)
    X: torch.Tensor = torch.tensor(dataset)
    X = X.to(device)
    print(f"Input tensor shape: {X.shape}")

    print("Running prediction...")
    model.eval()

    with torch.no_grad():
        pred = model(X)

    print(f"Prediction completed - Output shape: {pred.shape}")
    print("=== PREDICTION COMPLETED ===")

    return {"predictions": pred}


if __name__ == "__main__":
    import dotenv  # type: ignore

    dotenv.load_dotenv()

    result = train(
        context={
            "status_id": "test",
            "dataset_bucket": "local",
            "dataset_format": "csv",
        },
        dataset_path="test_dataset.csv",
        params={
            "hyperparameters": {
                "hsm_model": "general",
                "epochs": 1000,  # Increased to test early stopping
                "batch_size": 5,  # Smaller batch size for test dataset
                "seed": 24,
                "target": "scaled_demedian_forward_return_22d",
                "device": "cpu",  # Use CPU for testing
                "num_workers": 0,
                "pin_memory": False,
                "split": 0.2,  # 80/20 train/test split
                # GeneralHSModel specific - these will be updated by data_derived_input/output_operator_count in train
                "input_operator_count": 5,
                "output_operator_count": 1,
                "hilbert_space_dims": 4,
                "complex": True,
                "optimizer_config": {
                    "type": "Adam",
                    "default_params": {"lr": 1e-3},
                    "group_params": [
                        {
                            "param_name_contains": ["input_diag"],
                            "params": {"lr": 1e-4, "weight_decay": 0},
                        }
                    ],
                },
                "loss_fn_config": {"type": "MSELoss", "params": {}},
                "scheduler_config": {
                    "type": "StepLR",
                    "params": {"step_size": 3, "gamma": 0.5},
                    "interval": "epoch",
                },
                "early_stopping_config": {
                    "monitor": "val_loss",
                    "patience": 3,
                    "mode": "min",
                    "min_delta": 0.0001,
                    "verbose": True,
                    "restore_best_weights": True,
                },
                "gradient_clipping_config": {"max_norm": 1.0, "norm_type": 2.0},
            },
        },
    )
    print("\nTraining Results:")
    metrics = result['metrics']
    print(f"Test Loss: {metrics['test_loss']:.6f}")
    print(f"Final Train Loss: {metrics['final_train_loss']:.6f}")
    print(f"Final Val Loss: {metrics['final_val_loss']:.6f}")
    print(f"Best Val Loss: {metrics['best_val_loss']:.6f}")
    print(f"Epochs Completed: {metrics['epochs_completed']}")
    print(f"Train Dataset Size: {metrics['train_dataset_size']}")
    print(f"Val Dataset Size: {metrics['val_dataset_size']}")
    print(f"Total Training Time: {metrics['total_training_time']:.2f} seconds")
    print(f"Average Epoch Time: {metrics['avg_epoch_time']:.2f} seconds")
    print(f"Training History Length: {len(metrics['train_loss_history'])}")
    print(f"Validation History Length: {len(metrics['val_loss_history'])}")
    print(f"Test Loss: {result['metrics']['test_loss']:.6f}")
