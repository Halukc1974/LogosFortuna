"""Shared test fixtures and helpers."""

import sys
import tempfile
from pathlib import Path

import pytest

# Make skill scripts importable
SKILL_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "logosFortuna-skill" / "scripts"


def _load_skill_module(module_name: str, file_name: str):
    """Load a skill script module by file name."""
    import importlib.util

    module_path = SKILL_SCRIPTS_DIR / file_name
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory with sample Python files."""
    # Main module
    main_py = tmp_path / "main.py"
    main_py.write_text(
        'import os\n'
        '\n'
        'def greet(name: str) -> str:\n'
        '    """Return a greeting message."""\n'
        '    return f"Hello, {name}"\n'
        '\n'
        'def add(a: int, b: int) -> int:\n'
        '    """Add two numbers."""\n'
        '    return a + b\n'
    )

    # A file with intentional issues for security scanner
    vuln_py = tmp_path / "vulnerable.py"
    vuln_py.write_text(
        'import os\n'
        'import subprocess\n'
        '\n'
        'password = "hardcoded123"\n'
        '\n'
        'def run_command(cmd):\n'
        '    os.system("ls " + cmd)\n'
        '\n'
        'def query_db(user_input):\n'
        '    query = "SELECT * FROM users WHERE id=" + user_input\n'
        '    return query\n'
    )

    # README
    readme = tmp_path / "README.md"
    readme.write_text(
        "# Test Project\n\n"
        "## Installation\n\nRun `pip install .`\n\n"
        "## Usage\n\n```python\nfrom main import greet\n```\n\n"
        "## Contributing\n\nPRs welcome.\n\n"
        "## License\n\nMIT\n"
    )

    return tmp_path


@pytest.fixture
def tmp_config(tmp_path):
    """Create a temporary config file path for integration manager."""
    return tmp_path / "config" / "integrations.json"
