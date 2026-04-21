"""Top-level LogosFortuna CLI."""

from __future__ import annotations

import argparse

from logosfortuna.integration import main as integration_main
from logosfortuna.quality import main as quality_main
from logosfortuna.security import main as security_main
from logosfortuna.udiv import main as udiv_main


def main() -> int:
    parser = argparse.ArgumentParser(description="LogosFortuna command runner")
    subparsers = parser.add_subparsers(dest="command")

    integrations = subparsers.add_parser(
        "integrations",
        help="Run integration setup and notification helpers",
    )
    integrations.add_argument("args", nargs=argparse.REMAINDER)

    security = subparsers.add_parser(
        "security",
        help="Run security scanning helpers",
    )
    security.add_argument("args", nargs=argparse.REMAINDER)

    quality = subparsers.add_parser(
        "quality",
        help="Run quality analysis helpers",
    )
    quality.add_argument("args", nargs=argparse.REMAINDER)

    udiv = subparsers.add_parser(
        "udiv",
        help="Build a concrete UDIV runtime plan from the repository specs",
    )
    udiv.add_argument("args", nargs=argparse.REMAINDER)

    parsed = parser.parse_args()

    if parsed.command == "integrations":
        forwarded_args = parsed.args
        if forwarded_args and forwarded_args[0] == "--":
            forwarded_args = forwarded_args[1:]
        return integration_main(forwarded_args)

    if parsed.command == "security":
        forwarded_args = parsed.args
        if forwarded_args and forwarded_args[0] == "--":
            forwarded_args = forwarded_args[1:]
        return security_main(forwarded_args)

    if parsed.command == "quality":
        forwarded_args = parsed.args
        if forwarded_args and forwarded_args[0] == "--":
            forwarded_args = forwarded_args[1:]
        return quality_main(forwarded_args)

    if parsed.command == "udiv":
        forwarded_args = parsed.args
        if forwarded_args and forwarded_args[0] == "--":
            forwarded_args = forwarded_args[1:]
        return udiv_main(forwarded_args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
