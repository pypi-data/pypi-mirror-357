# DeployWizard

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DeployWizard is a powerful CLI tool that automates the deployment of machine learning models as production-ready REST APIs with Docker support. It generates all the necessary code and configuration files to containerize your ML models with FastAPI, making deployment a breeze.

## Features

- **Multi-Framework Support**: Works with scikit-learn, PyTorch, and TensorFlow models
- **Production-Ready**: Generates Dockerfiles and optimized FastAPI applications
- **Environment-Aware**: Handles both development and production environments
- **Secure by Default**: Uses non-root users in containers and secure defaults
- **Easy to Use**: Simple CLI interface for generating deployment code
- **Customizable**: Flexible template system for advanced customization

## Installation

Install DeployWizard using pip:

```bash
pip install deploywizard
```

## Quick Start

1. **Generate a new project** (replace `model.pkl` with your model file):
   ```bash
   python -m deploywizard init --model model.pkl --framework sklearn --output my_ml_api
   ```

2. **Navigate to the project directory**:
   ```bash
   cd my_ml_api
   ```

3. **Build the Docker image**:
   ```bash
   docker build -t my-ml-api .
   ```

4. **Run the container**:
   ```bash
   docker run -p 8000:8000 my-ml-api
   ```

5. **Test the API**:
   ```bash
   curl http://localhost:8000/health
   ```

## Usage

### Initialize a New Project

```bash
python -m deploywizard init --model path/to/your/model.pkl --framework [sklearn|pytorch|tensorflow] --output output_directory
```

#### Options:

- `--model`: Path to your trained model file (required)
- `--framework`: ML framework used to train the model (required)
- `--output`: Output directory for the generated project (default: current directory)
- `--api`: API framework to use (currently only FastAPI is supported)

### Project Structure

Generated projects follow this structure:

```
my_ml_api/
├── app/
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── model.pkl        # Your trained model (copied from source)
├── Dockerfile           # Docker configuration
└── README.md            # Project-specific documentation
```

## Configuration

### Environment Variables

The following environment variables can be used to configure the application:

- `MODEL_PATH`: Path to the model file (default: `/app/model.pkl` in Docker)
- `ENV`: Environment mode (`development` or `production`, defaults to `production` in Docker)

### Customizing the API

You can modify the generated `app/main.py` file to customize the API endpoints, add authentication, or modify the request/response schemas.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ using FastAPI and Docker
- Inspired by the need for simple ML model deployment solutions
- Thanks to all contributors who have helped improve this project!
