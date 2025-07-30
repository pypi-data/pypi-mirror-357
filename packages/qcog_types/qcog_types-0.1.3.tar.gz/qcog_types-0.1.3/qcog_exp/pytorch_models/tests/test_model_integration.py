# type: ignore
from ..model import train, TrainContext  # type: ignore

from pathlib import Path
import sys
from unittest.mock import patch, MagicMock
import pandas as pd  # type: ignore
import numpy as np  # type: ignore

# Attempt to add project directories to sys.path for robust imports
# This is often handled by test runners or PYTHONPATH configuration
try:
    # Assuming this test file is in qcog_exp/intech/pytorch_models/tests
    # project_root (hone-packages) is parents[4]
    project_root = Path(__file__).resolve().parents[4]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

except IndexError:
    print(
        "Warning: Could not robustly add project directories to sys.path. Imports might fail if not run from project root or with PYTHONPATH set."
    )

# Mock boto3 to prevent import errors since we're mocking resolve_dataset anyway
sys.modules["boto3"] = MagicMock()

# Use absolute imports from the project root


class TestModelTrainingRuns:
    def _get_base_context(self) -> TrainContext:
        return {
            "status_id": "test_run",
            "dataset_bucket": "s3",  # Changed back to s3 since we're mocking
            "dataset_format": "csv",
            # NotRequired fields like save_checkpoint, load_last_checkpoint are omitted
        }

    def _create_mock_dataset(self) -> pd.DataFrame:
        """Create a mock dataset with the expected structure for testing."""
        np.random.seed(42)  # For reproducible test data

        # Create mock features (5 input features to match input_operator_count)
        n_samples = 20  # Small dataset for testing
        feature_data = {
            "feature_1": np.random.randn(n_samples),
            "feature_2": np.random.randn(n_samples),
            "feature_3": np.random.randn(n_samples),
            "feature_4": np.random.randn(n_samples),
            "feature_5": np.random.randn(n_samples),
            "scaled_demedian_forward_return_22d": np.random.randn(
                n_samples
            ),  # Target variable
        }

        return pd.DataFrame(feature_data)

    def _run_training_test(self, hyperparameters_dict: dict):
        context = self._get_base_context()
        params = {"hyperparameters": hyperparameters_dict}

        # Create mock dataset
        mock_dataset = self._create_mock_dataset()

        # Mock the resolve_dataset function to return our mock dataset
        with patch("qcog_exp.pytorch_models.model.resolve_dataset") as mock_resolve:
            mock_resolve.return_value = mock_dataset

            results = train(
                context=context,
                dataset_path="mock://test_dataset.csv",  # Mock path since we're mocking the function
                params=params,
            )

            # Verify resolve_dataset was called with correct parameters
            mock_resolve.assert_called_once_with(
                dataset_path="mock://test_dataset.csv",
                bucket_type=context["dataset_bucket"],
                dataset_format=context["dataset_format"],
            )

        assert results is not None, "Train function returned None"
        assert "metrics" in results, "Metrics not found in training results"
        assert "test_loss" in results["metrics"], "test_loss not found in metrics"
        assert isinstance(results["metrics"]["test_loss"], float), (
            "test_loss is not a float"
        )
        print(
            f"Successfully ran training for {hyperparameters_dict['hsm_model']}. Test loss: {results['metrics']['test_loss']:.4f}"
        )

    def test_general_hsm_run(self):
        hyperparameters = {
            "hsm_model": "general",
            "epochs": 1,
            "batch_size": 4,
            "seed": 42,
            "target": "scaled_demedian_forward_return_22d",
            "device": "cpu",
            "num_workers": 0,
            "pin_memory": False,
            "split": 0.5,  # Ensure train/test sets are not empty for small dataset
            "input_operator_count": 5,  # Matches mock dataset features
            "output_operator_count": 1,  # Matches mock dataset target
            "hilbert_space_dims": 2,
            "complex": True,
            "optimizer_config": {"type": "Adam", "default_params": {"lr": 1e-3}},
            "loss_fn_config": {"type": "MSELoss", "params": {}},
        }
        self._run_training_test(hyperparameters)

    def test_pauli_hsm_run(self):
        hyperparameters = {
            "hsm_model": "pauli",
            "epochs": 1,
            "batch_size": 4,
            "seed": 42,
            "target": "scaled_demedian_forward_return_22d",
            "device": "cpu",
            "num_workers": 0,
            "pin_memory": False,
            "split": 0.5,
            "input_operator_count": 5,
            "output_operator_count": 1,
            "qubits_count": 2,  # Results in hilbert_space_dims = 2**2 = 4
            "optimizer_config": {"type": "Adam", "default_params": {"lr": 1e-3}},
            "loss_fn_config": {"type": "MSELoss", "params": {}},
        }
        self._run_training_test(hyperparameters)

    def test_general_fullenergy_hsm_run(self):
        # general_fullenergy uses GeneralHSModelHyperparameters structure for validation
        # and specific parameters for its layer.
        hyperparameters = {
            "hsm_model": "general_fullenergy",
            "epochs": 1,
            "batch_size": 4,
            "seed": 42,
            "target": "scaled_demedian_forward_return_22d",
            "device": "cpu",
            "num_workers": 0,
            "pin_memory": False,
            "split": 0.5,
            "input_operator_count": 5,  # Required by GeneralHSModelHyperparameters & PytorchGeneralHSMFullEnergy
            "output_operator_count": 1,  # Required by GeneralHSModelHyperparameters & PytorchGeneralHSMFullEnergy
            "hilbert_space_dims": 2,  # Required by GeneralHSModelHyperparameters & PytorchGeneralHSMFullEnergy
            # 'complex': True, # Included in GeneralHSModelHyperparameters, defaults to True
            "optimizer_config": {"type": "Adam", "default_params": {"lr": 1e-3}},
            "loss_fn_config": {"type": "MSELoss", "params": {}},
        }
        self._run_training_test(hyperparameters)

    def test_training_with_weighted_layer(self):
        """Tests a training run with the weighted_layer enabled."""
        hyperparameters = {
            "hsm_model": "general",
            "weighted_layer": True,  # Enable the weighted layer
            "epochs": 1,
            "batch_size": 4,
            "seed": 42,
            "target": "scaled_demedian_forward_return_22d",
            "device": "cpu",
            "num_workers": 0,
            "pin_memory": False,
            "split": 0.5,
            "input_operator_count": 5,
            "output_operator_count": 1,
            "hilbert_space_dims": 2,
            "complex": True,
            "optimizer_config": {"type": "Adam", "default_params": {"lr": 1e-3}},
            "loss_fn_config": {"type": "MSELoss", "params": {}},
        }
        self._run_training_test(hyperparameters)

    def test_training_without_weighted_layer(self):
        """Tests a training run with the weighted_layer disabled."""
        hyperparameters = {
            "hsm_model": "general",
            "weighted_layer": False,  # Explicitly disable the weighted layer
            "epochs": 1,
            "batch_size": 4,
            "seed": 42,
            "target": "scaled_demedian_forward_return_22d",
            "device": "cpu",
            "num_workers": 0,
            "pin_memory": False,
            "split": 0.5,
            "input_operator_count": 5,
            "output_operator_count": 1,
            "hilbert_space_dims": 2,
            "complex": True,
            "optimizer_config": {"type": "Adam", "default_params": {"lr": 1e-3}},
            "loss_fn_config": {"type": "MSELoss", "params": {}},
        }
        self._run_training_test(hyperparameters)
