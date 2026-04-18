#!/usr/bin/env python3
"""Compatibility CLI wrapper for the quality analyzer."""

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from logosfortuna.quality import main


if __name__ == "__main__":
    raise SystemExit(main())