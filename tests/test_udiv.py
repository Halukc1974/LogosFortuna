"""Tests for the UDIV runtime scaffold."""

import json
from pathlib import Path

import pytest

from logosfortuna.udiv import UdivOrchestrator, UdivRuntimeError, main


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def _write_agent(workspace_root: Path, name: str, description: str) -> None:
    agents_dir = workspace_root / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / f"{name}.agent.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"description: \"{description}\"\n"
        "tools: [\"read\"]\n"
        "---\n",
        encoding="utf-8",
    )


def _make_temp_workspace(tmp_path: Path) -> Path:
    _write_agent(tmp_path, "anlama-ajansi", "understanding")
    _write_agent(tmp_path, "uygulama-ajansi", "implementation")
    _write_agent(tmp_path, "dogrulama-ajansi", "validation")
    return tmp_path


class TestUdivOrchestrator:
    def test_load_agent_specs(self):
        orchestrator = UdivOrchestrator(WORKSPACE_ROOT)
        specs = orchestrator.load_agent_specs()

        assert "anlama-ajansi" in specs
        assert "uygulama-ajansi" in specs
        assert specs["anlama-ajansi"].file_path.endswith("anlama-ajansi.agent.md")

    def test_build_full_session(self):
        orchestrator = UdivOrchestrator(WORKSPACE_ROOT)
        session = orchestrator.build_session("Yeni bir orkestrasyon akisi tasarla", mode="full")

        assert session["mode"] == "full"
        assert session["current_phase"] == "anla"
        assert [phase["key"] for phase in session["phases"]] == [
            "anla",
            "tasarla",
            "uygula",
            "dogrula",
        ]
        assert session["phases"][0]["agent"]["name"] == "anlama-ajansi"

    def test_understand_mode_only_contains_anla(self):
        orchestrator = UdivOrchestrator(WORKSPACE_ROOT)
        session = orchestrator.build_session("Hatayi anla", mode="understand")

        assert [phase["key"] for phase in session["phases"]] == ["anla"]

    def test_cli_json_output(self, capsys):
        result = main([
            "--workspace-root",
            str(WORKSPACE_ROOT),
            "--task",
            "Kalite akisini planla",
            "--format",
            "json",
        ])
        captured = capsys.readouterr()

        assert result == 0
        payload = json.loads(captured.out)
        assert payload["task"] == "Kalite akisini planla"
        assert payload["guardrails"]["phase_backtracks"] == 2

    def test_start_session_persists_state(self, tmp_path):
        workspace_root = _make_temp_workspace(tmp_path)
        orchestrator = UdivOrchestrator(workspace_root)

        session = orchestrator.start_session("Yeni UDIV oturumu", mode="full")
        state_file = workspace_root / ".logosfortuna" / "udiv" / f"{session['session_id']}.json"

        assert state_file.exists()
        loaded = orchestrator.load_session(session["session_id"])
        assert loaded["status"] == "active"
        assert loaded["current_phase"] == "anla"
        assert loaded["phases"][0]["status"] == "in_progress"

    def test_advance_requires_approval(self, tmp_path):
        workspace_root = _make_temp_workspace(tmp_path)
        orchestrator = UdivOrchestrator(workspace_root)
        session = orchestrator.start_session("Gorev", mode="full")

        with pytest.raises(UdivRuntimeError):
            orchestrator.advance_session(session["session_id"])

    def test_approve_and_advance_updates_state(self, tmp_path):
        workspace_root = _make_temp_workspace(tmp_path)
        orchestrator = UdivOrchestrator(workspace_root)
        session = orchestrator.start_session("Gorev", mode="full")

        orchestrator.approve_current_phase(session["session_id"])
        updated = orchestrator.advance_session(session["session_id"])

        assert updated["current_phase"] == "tasarla"
        assert updated["approval_counts"]["anla"] == 1
        assert updated["phases"][0]["status"] == "completed"
        assert updated["phases"][1]["status"] == "in_progress"

    def test_backtrack_increments_counter(self, tmp_path):
        workspace_root = _make_temp_workspace(tmp_path)
        orchestrator = UdivOrchestrator(workspace_root)
        session = orchestrator.start_session("Gorev", mode="full")

        orchestrator.approve_current_phase(session["session_id"])
        orchestrator.advance_session(session["session_id"])
        updated = orchestrator.backtrack_session(session["session_id"], reason="tasarim revizyonu")

        assert updated["current_phase"] == "anla"
        assert updated["backtrack_counts"]["tasarla->anla"] == 1
        assert updated["phases"][0]["status"] == "in_progress"

    def test_backtrack_limit_blocks_session(self, tmp_path):
        workspace_root = _make_temp_workspace(tmp_path)
        orchestrator = UdivOrchestrator(workspace_root)
        session = orchestrator.start_session("Gorev", mode="full")
        session_id = session["session_id"]

        for _ in range(2):
            orchestrator.approve_current_phase(session_id)
            orchestrator.advance_session(session_id)
            orchestrator.backtrack_session(session_id)

        orchestrator.approve_current_phase(session_id)
        orchestrator.advance_session(session_id)

        with pytest.raises(UdivRuntimeError):
            orchestrator.backtrack_session(session_id)

        blocked = orchestrator.load_session(session_id)
        assert blocked["status"] == "blocked"
        assert blocked["blocker"]["pair"] == "tasarla->anla"

    def test_cli_session_lifecycle(self, tmp_path, capsys):
        workspace_root = _make_temp_workspace(tmp_path)

        result = main([
            "--workspace-root",
            str(workspace_root),
            "--task",
            "Yeni akisi planla",
            "--start",
            "--format",
            "json",
        ])
        payload = json.loads(capsys.readouterr().out)

        assert result == 0
        session_id = payload["session_id"]

        result = main([
            "--workspace-root",
            str(workspace_root),
            "--session-id",
            session_id,
            "--approve",
            "--format",
            "json",
        ])
        approved_payload = json.loads(capsys.readouterr().out)

        assert result == 0
        assert approved_payload["approval_counts"]["anla"] == 1