# Xify

Xify is a Python tool for interacting with the X API.

## Features

*   **X API Interaction:** Provides functionalities to connect to and use the X API (formerly Twitter API).

## Installation

You can install Xify directly from GitHub or by cloning the repository.

### From PyPI (Recommended)

```bash
pip install xify
```

### From GitHub Releases

1.  Go to the [Releases page](https://github.com/filming/xify/releases)
2.  Download the latest `xify-X.Y.Z-py3-none-any.whl` file.
3.  Install it using pip:
    ```bash
    pip install /path/to/downloaded/xify-X.Y.Z-py3-none-any.whl
    ```
    Replace `X.Y.Z` with the actual version number and `/path/to/downloaded/` with the correct path to the file.

### From Source (after cloning)

1.  Clone the repository:
    ```bash
    git clone https://github.com/filming/xify.git
    cd xify
    ```
2.  Install using pip (this will also install dependencies listed in [`pyproject.toml`](pyproject.toml)):
    ```bash
    pip install .
    ```
    If you are developing the project, you might prefer an editable install:
    ```bash
    pip install -e .[dev]
    ```
    *(The `[dev]` extra will install development dependencies like `mypy` and `ruff`.)*

## Usage


*(Detailed usage instructions and examples will be added as the library develops.)*

## Configuration

*(Details on configuration, such as API key management or other settings, will be added here.)*

## Dependencies

Core dependencies are managed via [`pyproject.toml`](pyproject.toml) and will be listed here as they are added. The project requires Python >=3.10.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
