"""Tests for the LogosFortuna CLI entry point."""

import subprocess
import sys


class TestCLI:
    def test_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "logosfortuna", "--help"],
            capture_output=True,
            text=True,
            cwd="/workspaces/LogosFortuna",
        )
        assert result.returncode == 0
        assert "LogosFortuna" in result.stdout or "command" in result.stdout.lower()

    def test_security_subcommand(self, tmp_project):
        result = subprocess.run(
            [sys.executable, "-m", "logosfortuna", "security", "--", str(tmp_project)],
            capture_output=True,
            text=True,
            cwd="/workspaces/LogosFortuna",
        )
        assert result.returncode == 0

    def test_quality_subcommand(self, tmp_project):
        result = subprocess.run(
            [sys.executable, "-m", "logosfortuna", "quality", "--", str(tmp_project)],
            capture_output=True,
            text=True,
            cwd="/workspaces/LogosFortuna",
        )
        assert result.returncode == 0

    def test_integrations_status(self, tmp_config):
        result = subprocess.run(
            [sys.executable, "-m", "logosfortuna", "integrations", "--",
             "--config", str(tmp_config), "--status"],
            capture_output=True,
            text=True,
            cwd="/workspaces/LogosFortuna",
        )
        assert result.returncode == 0

    def test_udiv_subcommand(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "logosfortuna",
                "udiv",
                "--",
                "--task",
                "Yeni bir kalite stratejisi planla",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd="/workspaces/LogosFortuna",
        )
        assert result.returncode == 0
        assert '"current_phase": "anla"' in result.stdout

    def test_no_command_shows_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "logosfortuna"],
            capture_output=True,
            text=True,
            cwd="/workspaces/LogosFortuna",
        )
        assert result.returncode == 0
