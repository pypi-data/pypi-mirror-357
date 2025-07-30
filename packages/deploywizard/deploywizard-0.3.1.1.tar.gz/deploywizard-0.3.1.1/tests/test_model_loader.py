import pytest
import joblib
import torch
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from deploywizard.scaffolder.model_loader import ModelLoader

# Test models
class DummyTorchModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = torch.nn.Linear(10, 2)
    
    def forward(self, x):
        return self.layer(x)

class DummyTFModel:
    def predict(self, x):
        return np.array([[0.5, 0.5]])

@pytest.fixture
def sklearn_model(tmp_path):
    """Create a dummy scikit-learn model."""
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression()
    X = np.random.rand(100, 5)
    y = np.random.randint(0, 2, 100)
    model.fit(X, y)
    
    model_path = tmp_path / "model.pkl"
    joblib.dump(model, model_path)
    return model_path

@pytest.fixture
def pytorch_model(tmp_path):
    """Create a dummy PyTorch model."""
    model = DummyTorchModel()
    model_path = tmp_path / "model.pt"
    torch.save(model.state_dict(), model_path)
    return model_path

@pytest.fixture
def tensorflow_model(tmp_path):
    """Create a dummy TensorFlow model."""
    model = DummyTFModel()
    model_path = tmp_path / "saved_model"
    # In a real test, we'd save a TensorFlow model here
    # For testing, we'll just create a directory structure
    model_path.mkdir()
    return model_path

def test_load_sklearn(sklearn_model):
    """Test loading a scikit-learn model."""
    loader = ModelLoader()
    model = loader.load(sklearn_model, 'sklearn')
    assert hasattr(model, 'predict')
    assert hasattr(model, 'predict_proba')

def test_load_pytorch(pytorch_model):
    """Test loading a PyTorch model."""
    loader = ModelLoader()
    model = loader.load(pytorch_model, 'pytorch')
    assert isinstance(model, dict)  # Should be a state dict
    assert 'layer.weight' in model
    assert 'layer.bias' in model

def test_load_tensorflow(tensorflow_model):
    """Test loading a TensorFlow model."""
    loader = ModelLoader()
    
    # Mock the tensorflow.keras.models.load_model function
    with patch('tensorflow.keras.models.load_model') as mock_load_model:
        # Mock the model to be returned
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Call the method
        model = loader.load(str(tensorflow_model), 'tensorflow')
        
        # Verify the model was loaded with the correct path
        mock_load_model.assert_called_once_with(str(tensorflow_model))
        assert model == mock_model

def test_unsupported_framework(tmp_path):
    """Test loading with an unsupported framework."""
    loader = ModelLoader()
    # Create a dummy model file
    model_path = tmp_path / "dummy.pt"
    model_path.write_text("dummy data")
    
    with pytest.raises(ValueError) as excinfo:
        loader.load(str(model_path), 'unsupported')
    assert "Unsupported framework" in str(excinfo.value)

def test_sklearn_load_error(tmp_path):
    """Test error handling when loading sklearn model fails."""
    loader = ModelLoader()
    dummy_path = tmp_path / "dummy.pkl"
    # Don't create the file to trigger FileNotFoundError
    
    with pytest.raises(FileNotFoundError) as excinfo:
        loader.load(str(dummy_path), 'sklearn')
    assert str(dummy_path) in str(excinfo.value)

def test_pytorch_load_error(tmp_path):
    """Test error handling when loading PyTorch model fails."""
    loader = ModelLoader()
    dummy_path = tmp_path / "dummy.pt"
    # Don't create the file to trigger FileNotFoundError
    
    with pytest.raises(FileNotFoundError) as excinfo:
        loader.load(str(dummy_path), 'pytorch')
    assert str(dummy_path) in str(excinfo.value)

def test_invalid_model_file(tmp_path):
    """Test loading an invalid model file."""
    loader = ModelLoader()
    invalid_file = tmp_path / "invalid.pkl"
    invalid_file.write_text("This is not a valid model")
    
    with pytest.raises(Exception) as excinfo:
        loader.load(str(invalid_file), 'sklearn')
    # Check for any error message about failing to load the model
    assert any(msg in str(excinfo.value).lower() for msg in ["failed", "error", "invalid"])

def test_missing_framework():
    """Test loading a model without specifying the framework."""
    loader = ModelLoader()
    
    with pytest.raises(ValueError) as excinfo:
        loader.load("dummy.pt", "")
    assert "Framework must be specified" in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        loader.load("dummy.pt", None)  # type: ignore
    assert "Framework must be specified" in str(excinfo.value)
