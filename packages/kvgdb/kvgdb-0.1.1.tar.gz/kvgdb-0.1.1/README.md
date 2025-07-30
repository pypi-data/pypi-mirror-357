# KVGDB

A Python library for key-value graph database.

## Installation

From PyPI:
```bash
pip install kvgdb
```

From custom repository:
```bash
pip install --index-url https://your.custom.repo/simple/ kvgdb
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kvgdb.git
cd kvgdb
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
# Install the package in editable mode with development dependencies
pip install -e ".[dev]"
```

4. Run tests:
```bash
pytest
```

## Building the Package

To build the package, run:
```bash
./scripts/build_and_publish.sh
```

This will clean the build directories, run tests, and create both wheel and source distribution in the `dist` directory.

## Publishing the Package

### Configuration

1. Create a `.pypirc` file in your home directory with your repository configurations:
```ini
[distutils]
index-servers =
    custom
    pypi

[custom]
repository = https://your.custom.repo/simple/
username = your_username
password = your_password
```

2. For PyPI, create an API token:
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Give it a name (e.g., "kvgdb-upload")
   - Select "Entire account (all projects)" or scope it to this project
   - Copy the token value (you won't see it again!)

### Publishing Options

1. Show help message:
```bash
./scripts/build_and_publish.sh --help
```

2. Publish to PyPI only:
```bash
export PYPI_API_TOKEN="your-pypi-api-token"
./scripts/build_and_publish.sh --publish
```

3. Publish to custom repository only:
```bash
export TWINE_USERNAME="your_username"
export TWINE_PASSWORD="your_password"
./scripts/build_and_publish.sh --publish --repositories custom
```

4. Publish to multiple repositories:
```bash
export PYPI_API_TOKEN="your-pypi-api-token"
export TWINE_USERNAME="your_username"
export TWINE_PASSWORD="your_password"
./scripts/build_and_publish.sh --publish --repositories "pypi custom"
```

5. Publish to multiple repositories and continue on error:
```bash
./scripts/build_and_publish.sh --publish --repositories "pypi custom" --continue-on-error
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 