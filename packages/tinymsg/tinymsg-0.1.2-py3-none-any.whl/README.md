# tinymsg

A lightweight serialization library for Python using MessagePack with type-safe Pydantic models. This Python instance of the tinymsg serialization library is directly compatible with [tinymsg-cpp](https://github.com/alangshur/tinymsg-cpp) and tinymsg-rs (coming soon).

## Features

- **Type-safe**: Built on Pydantic for automatic validation and type checking
- **Fast**: Uses MessagePack for efficient binary serialization
- **Simple**: Minimal boilerplate - just inherit from `Message`
- **Nested support**: Handles nested objects, lists, and dicts automatically

## Installation

```bash
uv add tinymsg       # using uv
pip install tinymsg  # using pip
```

## Quick Start

```python
from tinymsg import Message

class Person(Message):
    name: str
    age: int
    email: str

class Team(Message):
    name: str
    members: list[Person]
    active: bool = True

# Create objects
alice = Person(name="Alice", age=30, email="alice@example.com")
bob = Person(name="Bob", age=25, email="bob@example.com")
team = Team(
    name="Engineering", 
    members=[alice, bob]
)

# Serialize to bytes
data = team.pack()

# Deserialize from bytes
restored_team = Team.unpack(data)

print(restored_team.members[0].name)  # "Alice"
```

## Development

This project uses [uv](https://github.com/astral-sh/uv), a fast Python package and project manager. Install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup Development Environment

Automatically create the virtual environment and sync all the dependencies (including dev dependencies): 

```bash
uv sync --group dev
```

Install the pre-commit hooks to auto-run linting, formatting, and static type checks:

```bash
uv run pre-commit install
```

### Development Commands

```bash
# Run tests
uv run pytest
uv run pytest --cov=tinymsg --cov-report=html

# Lint and format code with ruff (runs automatically with pre-commit)
uv run ruff check .
uv run ruff check --fix .
uv run ruff format .

# Type checking (runs automatically with pre-commit)
uv run mypy .

# Run all pre-commit hooks manually (includes ruff, mypy, and uv-lock)
uv run pre-commit run --all-files
```

### Other Useful Commands

```bash
# Add a new dependency
uv add requests

# Add a new dev dependency
uv add --dev mypy

# Sync dependencies
uv sync

# Sync and upgrade dependencies
uv sync --upgrade

# Show dependencies
uv tree
```
