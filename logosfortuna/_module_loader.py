"""Helpers for loading legacy hyphenated script modules."""

from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path
from types import ModuleType


ROOT_DIR = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS_DIR = ROOT_DIR / "skills" / "logosFortuna-skill" / "scripts"


@lru_cache(maxsize=None)
def load_legacy_module(module_name: str, file_name: str) -> ModuleType:
    module_path = SKILL_SCRIPTS_DIR / file_name
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
