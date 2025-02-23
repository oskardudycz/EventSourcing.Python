# Event Sourcing Workshop

This repository contains a workshop project demonstrating event sourcing patterns using Python.

## Prerequisites

- Python 3.13 or higher
- `uv` package manager

## Installation

1. Install `uv` using one of the following methods:

   ```bash
   # Using curl (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Using pip
   pip install uv
   ```

2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd es-workshop
   ```

3. Create and activate a virtual environment using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix-like systems
   # or
   .venv\Scripts\activate     # On Windows
   ```

4. Install dependencies:
   ```bash
   uv pip install --editable ".[dev]"
   ```

   This will install:
   - Main dependencies (pydantic, sqlalchemy)
   - Development dependencies (pytest, postgres drivers, testcontainers)
   - All workspace members in editable mode

## Project Structure

This is a workspace project containing multiple subprojects:
- events_definition
- getting_state_from_events
- appending_events_db
- getting_state_from_events_db

## Running Tests

### Using Make

The project provides Make commands for running tests:

```bash
# Run all tests
make test

# Run tests for specific packages
make test-01  # events_definition
make test-02  # appending_events_db
make test-03  # getting_state_from_events
make test-04  # getting_state_from_events_db

# List all available make commands
make help
```

### Using pytest directly

You can also run tests using pytest directly:

```bash
# Run all tests
pytest

# Run tests for specific packages
pytest events_definition/tests/
pytest appending_events_db/tests/
pytest getting_state_from_events/tests/
pytest getting_state_from_events_db/tests/
```

## Development

The project uses `uv` for dependency management and workspace handling. Key commands:

- Update dependencies: `uv pip install --editable ".[dev]"`
- Add new dependency: Add to pyproject.toml and run the update command
- Clean environment: `uv pip uninstall --all`
