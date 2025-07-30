import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from deploywizard.scaffolder.docker_generator import DockerGenerator

def test_generate_dockerfile_defaults(tmp_path):
    """Test generating a Dockerfile with default parameters."""
    generator = DockerGenerator()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create a dummy requirements.txt
    (output_dir / "requirements.txt").write_text("fastapi\nuvicorn\n")
    
    # Mock the open function to capture the written content
    with patch('builtins.open', mock_open()) as mock_file:
        generator.generate(
            output_dir=str(output_dir),
            template_vars={
                'model_name': 'model.pkl',
                'python_version': '3.10',
                'additional_deps': {}
            }
        )
    
    # Verify the Dockerfile was created
    mock_file.assert_called_once_with(output_dir / 'Dockerfile', 'w')
    
    # Get the written content
    written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
    
    # Verify content
    assert 'FROM python:3.10' in written_content
    assert 'COPY requirements.txt .' in written_content
    assert 'RUN pip install --no-cache-dir -r requirements.txt' in written_content
    assert 'COPY app/ ./app' in written_content
    assert 'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]' in written_content

@pytest.mark.parametrize("use_gpu,expected_base_image", [
    (False, 'python:3.10'),
    (True, 'nvidia/cuda:11.8.0-base-ubuntu22.04')
])
def test_dockerfile_variations(tmp_path, use_gpu, expected_base_image):
    """Test different Dockerfile variations."""
    generator = DockerGenerator()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create a requirements.txt file
    (output_dir / 'requirements.txt').write_text('fastapi\nuvicorn\n')
    
    with patch('builtins.open', mock_open()) as mock_file:
        generator.generate(
            output_dir=str(output_dir),
            template_vars={
                'model_name': 'model.pkl',
                'python_version': '3.10',
                'use_gpu': use_gpu,
                'additional_deps': {}
            }
        )
    
    # Get the written content
    written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
    
    # Verify base image
    assert f'FROM {expected_base_image}' in written_content
    
    # Verify GPU-specific setup if needed
    if use_gpu:
        assert 'ENV NVIDIA_VISIBLE_DEVICES=all' in written_content
        assert 'ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility' in written_content

def test_custom_requirements(tmp_path):
    """Test with custom requirements."""
    generator = DockerGenerator()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create a custom requirements file
    requirements = output_dir / 'custom_requirements.txt'
    requirements.write_text('fastapi\nuvicorn\nnumpy\npandas\n')
    
    with patch('builtins.open', mock_open()) as mock_file:
        generator.generate(
            output_dir=str(output_dir),
            template_vars={
                'model_name': 'model.pkl',
                'python_version': '3.10',
                'requirements_file': 'custom_requirements.txt',
                'additional_deps': {}
            }
        )
    
    # Get the written content
    written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
    
    # Verify custom requirements are used
    assert 'COPY custom_requirements.txt requirements.txt' in written_content

def test_file_write_errors(tmp_path):
    """Test error handling during file writing."""
    generator = DockerGenerator()
    output_dir = tmp_path / "output"
    
    # Make the directory read-only to cause a permission error
    output_dir.mkdir(mode=0o444)
    
    # Test that the appropriate exception is raised
    with pytest.raises(PermissionError):
        generator.generate(
            output_dir=str(output_dir),
            template_vars={
                'model_name': 'model.pkl',
                'python_version': '3.10',
                'additional_deps': {}
            }
        )

def test_docker_generator_with_extra_args(tmp_path):
    """Test DockerGenerator with extra arguments."""
    generator = DockerGenerator()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create a requirements.txt file
    (output_dir / 'requirements.txt').write_text('fastapi\nuvicorn\n')
    
    with patch('builtins.open', mock_open()) as mock_file:
        generator.generate(
            output_dir=str(output_dir),
            template_vars={
                'model_name': 'model.pkl',
                'python_version': '3.10',
                'additional_deps': {
                    'system': ['git', 'curl']
                },
                'service_name': 'custom-service',
                'port': 8080
            }
        )
    
    # Get the written content
    written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
    
    # Verify extra arguments are used
    assert 'RUN apt-get update && apt-get install -y git curl' in written_content
    assert 'EXPOSE 8080' in written_content
