# PPVC (Python Package Version Checker)

PPVC is a simple and efficient command-line utility that queries PyPI (Python Package Index) for available versions of Python packages. It's designed to be fast, reliable, and easy to use.

## Features

- List all available versions of a Python package
- Get only the latest version of a package
- Limit the number of versions displayed
- Simple and intuitive command-line interface
- Fast response times
- Error handling for network issues and non-existent packages
- Beautiful colorized output with formatted tables
- Version type classification (Final, Pre-release, Post-release)

## Installation

You can install PPVC using pip:

```bash
pip install ppvc
```

## Usage

### Basic Usage

List all available versions of a package:

```bash
ppvc requests
```

### Get Latest Version

Show only the latest version of a package:

```bash
ppvc requests --latest
```

### Limit Versions

Show only the first N versions:

```bash
ppvc django --limit 5
```

### Examples

```bash
# List all versions of the requests package
ppvc requests

# Get the latest version of numpy
ppvc numpy --latest

# Check versions of a specific package
ppvc django

# Show only the 10 most recent versions
ppvc flask --limit 10
```

## Command Line Options

- `--help`: Show help message
- `--version`: Show version information
- `--latest`: Show only the latest version
- `--limit N`: Limit the number of versions shown to N

## Error Handling

PPVC provides clear error messages for common issues:

- Package not found on PyPI
- Network connection problems
- Invalid package names

## Requirements

- Python 3.8 or higher
- Internet connection to access PyPI
- packaging>=23.0 (for version parsing)
- rich>=13.0.0 (for terminal formatting)

## Development

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/rapidrabbitsoft/ppvc.git
cd ppvc

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Test the package
python test_ppvc.py
```

### Building the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Install locally
pip install dist/*.whl
```

## Publishing to PyPI

This package is configured for automated publishing to PyPI using GitHub Actions. See [PUBLISHING.md](PUBLISHING.md) for detailed instructions.

### Quick Publishing Steps

1. Update version in `pyproject.toml` and `ppvc/ppvc.py`
2. Create a new GitHub release with the version tag
3. The GitHub Action will automatically build and publish to PyPI

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Run tests: `python test_ppvc.py`
5. Submit a pull request

For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the BSD 2-Clause License - see the [LICENSE](LICENSE) file for details.

## Author

Chris McMichael (python@apprabb.it)