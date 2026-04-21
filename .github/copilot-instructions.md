# Project Guidelines

## Architecture
- `logosfortuna/` is the stable Python package surface. It wraps the legacy implementations that live under `skills/logosFortuna-skill/scripts/`.
- `logosfortuna.udiv` is the concrete UDIV runtime scaffold. Extend it when turning documented workflow rules into executable behavior.
- The Claude-facing workflow assets live under `commands/`, `agents/`, and `skills/`. The Copilot-facing discovery assets live under `.github/`.

## Conventions
- Keep claims aligned with implementation. If a feature is not end-to-end, label it as partial in docs and reports.
- Prefer expanding the package wrappers or `logosfortuna.udiv` when adding stable runtime behavior; keep backward-compatible script wrappers working.
- When changing workflow behavior, update both the Claude-facing markdown files and the Copilot-facing `.github` files in the same change.

## Build And Test
- Run `pytest -q` for the full suite.
- Run `pytest -q tests/test_udiv.py tests/test_cli.py tests/test_customizations.py` for workflow/discovery changes.
- Use `python -m logosfortuna udiv -- --task "..."` to inspect the runtime phase plan.

## Key Limits
- Approval gates, backtrack limits, and validation loops are part of the product surface. Do not silently bypass them in docs or runtime code.
- MCP-backed memory, auto-rollback, chaos engineering, and Big-O profiling remain partial until the repository contains a working end-to-end implementation.