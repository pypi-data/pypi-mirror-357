# PyRSCA

Python bindings for the RSCA (Rust Signature and Certificate Authority) library.

## Development with uv

This project is managed using [uv](https://docs.astral.sh/uv/), a fast Python package manager.

### Prerequisites

1. Install uv:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install Rust (if not already installed):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

### Quick Start

1. **Setup development environment:**
   ```bash
   cd pyrsca
   uv sync --dev
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Build the extension:**
   ```bash
   uv run maturin develop
   ```

4. **Run tests:**
   ```bash
   uv run pytest
   ```

### Development Workflow

1. **Install dependencies:**
   ```bash
   uv add --dev <package-name>
   ```

2. **Build for development:**
   ```bash
   uv run maturin develop --release
   ```

3. **Build wheels:**
   ```bash
   uv run maturin build --release
   ```

4. **Publish (when ready):**
   ```bash
   uv run maturin publish
   ```

### Project Structure

- `src/lib.rs` - Rust source code with Python bindings
- `pyrsca/` - Python package source
- `tests/` - Python tests
- `pyproject.toml` - Project configuration and dependencies
- `Cargo.toml` - Rust dependencies and build configuration

### Available Commands

#### Using uv directly:
- `uv sync` - Install all dependencies
- `uv run pytest` - Run tests
- `uv run maturin develop` - Build and install in development mode
- `uv run maturin build` - Build distribution wheels
- `uv add <package>` - Add a new dependency
- `uv remove <package>` - Remove a dependency

#### Using the development script (recommended):
The `dev.sh` script handles environment conflicts and provides convenient commands:

- `./dev.sh sync` - Install/update dependencies
- `./dev.sh dev` - Build in development mode
- `./dev.sh build` - Build release mode
- `./dev.sh test` - Run tests
- `./dev.sh clean` - Clean build artifacts
- `./dev.sh install` - Install package in editable mode
- `./dev.sh help` - Show help

**Note**: The development script automatically handles conda/uv environment conflicts.

### Python Version Management

This project supports Python 3.7+ and uses Python 3.11 by default. You can change this by:

1. **Update `.python-version`:**
   ```bash
   echo "3.12" > .python-version
   ```

2. **Recreate virtual environment:**
   ```bash
   uv sync --reinstall
   ```

### Features

- **PyTWCA**: Python wrapper for TWCA certificate operations
- **PKCS7 Signature**: Traditional PKCS7 signature operations
- **PKCS1 Signature**: New PKCS1 signature with base64 encoded data and certificate
- **Certificate operations**: Extract certificate information and base64 encoding
- **Certificate validation**: Validate and extract certificate information

### Usage Example

```python
from pyrsca import PyTWCA

# Initialize TWCA instance
twca = PyTWCA("/path/to/cert.pfx", "password", "192.168.1.1")

# Get certificate person ID
person_id = twca.get_cert_person_id()
print(f"Certificate Person ID: {person_id}")

# PKCS7 signature (traditional method)
pkcs7_signature = twca.sign("data to sign")
print(f"PKCS7 Signature: {pkcs7_signature}")

# PKCS1 signature (new method) - returns format: pkcs1.{signature}.{data_base64}.{cert_base64}
pkcs1_result = twca.sign_pkcs1("data to sign")
print(f"PKCS1 Result: {pkcs1_result}")

# Get base64 encoded certificate
cert_base64 = twca.get_cert_base64()
print(f"Certificate Base64: {cert_base64}")


# Check expiration
expire_timestamp = twca.get_expire_timestamp()
print(f"Certificate expires at: {expire_timestamp}")
```
