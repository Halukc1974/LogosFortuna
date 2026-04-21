"""Minimal UDIV runtime scaffold for LogosFortuna.

This module turns the repository's documented UDIV process into a concrete,
testable runtime surface. It does not execute model agents directly; instead it
loads the available agent specifications, builds a guarded phase plan and emits
that plan as text or JSON for higher-level tooling.
"""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
from datetime import UTC, datetime
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4


AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    tools: List[str]
    file_path: str


@dataclass(frozen=True)
class PhaseSpec:
    key: str
    title: str
    description: str
    agent: str
    requires_approval: bool


PHASES: Dict[str, PhaseSpec] = {
    "anla": PhaseSpec(
        key="anla",
        title="Faz 1: ANLA",
        description="Niyeti, etki alanını ve riskleri haritalandır.",
        agent="anlama-ajansi",
        requires_approval=True,
    ),
    "tasarla": PhaseSpec(
        key="tasarla",
        title="Faz 2: TASARLA",
        description="Alternatif yaklaşımları üret ve seçimi netleştir.",
        agent="anlama-ajansi",
        requires_approval=True,
    ),
    "uygula": PhaseSpec(
        key="uygula",
        title="Faz 3: UYGULA",
        description="Onaylı yaklaşımı küçük, doğrulanabilir artımlarla uygula.",
        agent="uygulama-ajansi",
        requires_approval=True,
    ),
    "dogrula": PhaseSpec(
        key="dogrula",
        title="Faz 4: DOGRULA ve OGREN",
        description="Fonksiyonel, yapısal ve anayasal doğrulamayı tamamla.",
        agent="dogrulama-ajansi",
        requires_approval=False,
    ),
}


MODE_PHASES = {
    "full": ["anla", "tasarla", "uygula", "dogrula"],
    "understand": ["anla"],
    "validate": ["dogrula"],
}


DEFAULT_GUARDRAILS = {
    "phase_backtracks": 2,
    "increment_attempts": 3,
    "validation_cycles": 2,
    "phase1_discovery_calls": 5,
    "full_restarts": 1,
}


class UdivRuntimeError(RuntimeError):
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_frontmatter(content: str) -> Dict[str, Any]:
    if not content.startswith("---\n"):
        return {}

    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        return {}

    raw_frontmatter = parts[0].splitlines()[1:]
    data: Dict[str, Any] = {}
    index = 0

    while index < len(raw_frontmatter):
        line = raw_frontmatter[index]
        stripped = line.strip()
        index += 1

        if not stripped or ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value in {">", "|"}:
            block_lines: List[str] = []
            while index < len(raw_frontmatter):
                candidate = raw_frontmatter[index]
                if candidate.startswith("  ") or candidate.startswith("\t"):
                    block_lines.append(candidate.strip())
                    index += 1
                    continue
                if not candidate.strip():
                    block_lines.append("")
                    index += 1
                    continue
                break
            data[key] = " ".join(part for part in block_lines if part).strip()
            continue

        if value.startswith("[") and value.endswith("]"):
            try:
                data[key] = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                data[key] = value
            continue

        if value.lower() in {"true", "false"}:
            data[key] = value.lower() == "true"
            continue

        data[key] = value.strip('"\'')

    return data


class UdivOrchestrator:
    def __init__(self, workspace_root: str | Path):
        self.workspace_root = Path(workspace_root)
        self.agents_dir = self.workspace_root / "agents"
        self.state_dir = self.workspace_root / ".logosfortuna" / "udiv"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _build_phases(self, mode: str, agent_specs: Dict[str, AgentSpec]) -> List[Dict[str, Any]]:
        phases = []
        for phase_key in MODE_PHASES[mode]:
            phase = PHASES[phase_key]
            phases.append(
                {
                    "key": phase.key,
                    "title": phase.title,
                    "description": phase.description,
                    "requires_approval": phase.requires_approval,
                    "approved": False,
                    "status": "pending",
                    "agent": asdict(agent_specs[phase.agent]) if phase.agent in agent_specs else {"name": phase.agent},
                }
            )
        if phases:
            phases[0]["status"] = "in_progress"
        return phases

    def _session_file(self, session_id: str) -> Path:
        return self.state_dir / f"{session_id}.json"

    def _save_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        session["updated_at"] = _now_iso()
        state_file = self._session_file(session["session_id"])
        state_file.write_text(json.dumps(session, indent=2, ensure_ascii=False), encoding="utf-8")
        session["state_file"] = str(state_file)
        return session

    def _load_session(self, session_id: str) -> Dict[str, Any]:
        state_file = self._session_file(session_id)
        if not state_file.exists():
            raise UdivRuntimeError(f"UDIV oturumu bulunamadi: {session_id}")
        return json.loads(state_file.read_text(encoding="utf-8"))

    def _phase_index(self, session: Dict[str, Any], phase_key: str | None = None) -> int:
        target_phase = phase_key or session.get("current_phase")
        if target_phase is None:
            raise UdivRuntimeError("Aktif faz yok.")
        for index, phase in enumerate(session["phases"]):
            if phase["key"] == target_phase:
                return index
        raise UdivRuntimeError(f"Bilinmeyen faz: {target_phase}")

    def _append_history(self, session: Dict[str, Any], action: str, details: Dict[str, Any] | None = None) -> None:
        session.setdefault("history", []).append(
            {
                "timestamp": _now_iso(),
                "action": action,
                "details": details or {},
            }
        )

    def load_agent_specs(self) -> Dict[str, AgentSpec]:
        specs: Dict[str, AgentSpec] = {}
        if not self.agents_dir.exists():
            return specs

        for file_path in sorted(self.agents_dir.glob("*.agent.md")):
            content = file_path.read_text(encoding="utf-8")
            frontmatter = _parse_frontmatter(content)
            name = str(frontmatter.get("name") or file_path.stem.replace(".agent", ""))
            specs[name] = AgentSpec(
                name=name,
                description=str(frontmatter.get("description", "")).strip(),
                tools=list(frontmatter.get("tools", [])) if isinstance(frontmatter.get("tools", []), list) else [],
                file_path=str(file_path.relative_to(self.workspace_root)),
            )
        return specs

    def classify_task(self, task: str) -> str:
        normalized = task.strip().lower()
        if not normalized:
            return "orta"

        word_count = len(re.findall(r"\w+", normalized))
        architecture_words = {
            "mimari",
            "refactor",
            "orkestrasyon",
            "monolit",
            "mikroservis",
            "workflow",
            "agent",
            "çok aşamalı",
            "cok asamali",
        }
        if word_count >= 14 or any(word in normalized for word in architecture_words):
            return "karmasik"
        if word_count <= 5:
            return "basit"
        return "orta"

    def build_session(self, task: str, mode: str = "full") -> Dict[str, Any]:
        agent_specs = self.load_agent_specs()
        phases = self._build_phases(mode, agent_specs)

        return {
            "task": task.strip(),
            "mode": mode,
            "complexity": self.classify_task(task),
            "workspace_root": str(self.workspace_root),
            "guardrails": dict(DEFAULT_GUARDRAILS),
            "status": "planned",
            "current_phase": phases[0]["key"] if phases else None,
            "available_agents": sorted(agent_specs.keys()),
            "approval_counts": {},
            "backtrack_counts": {},
            "validation_cycles_used": 0,
            "phases": phases,
        }

    def start_session(self, task: str, mode: str = "full") -> Dict[str, Any]:
        session = deepcopy(self.build_session(task=task, mode=mode))
        session["session_id"] = uuid4().hex[:12]
        session["status"] = "active"
        session["created_at"] = _now_iso()
        self._append_history(session, "start", {"mode": mode})
        return self._save_session(session)

    def load_session(self, session_id: str) -> Dict[str, Any]:
        return self._load_session(session_id)

    def approve_current_phase(self, session_id: str) -> Dict[str, Any]:
        session = self._load_session(session_id)
        if session.get("status") in {"completed", "blocked"}:
            raise UdivRuntimeError("Tamamlanmis veya bloklanmis oturum onaylanamaz.")

        phase_index = self._phase_index(session)
        current_phase = session["phases"][phase_index]
        current_phase["approved"] = True
        approval_counts = session.setdefault("approval_counts", {})
        approval_counts[current_phase["key"]] = approval_counts.get(current_phase["key"], 0) + 1
        self._append_history(session, "approve", {"phase": current_phase["key"]})
        return self._save_session(session)

    def advance_session(self, session_id: str) -> Dict[str, Any]:
        session = self._load_session(session_id)
        if session.get("status") in {"completed", "blocked"}:
            raise UdivRuntimeError("Tamamlanmis veya bloklanmis oturum ilerletilemez.")

        phase_index = self._phase_index(session)
        current_phase = session["phases"][phase_index]

        if current_phase["requires_approval"] and not current_phase.get("approved"):
            raise UdivRuntimeError(
                f"Faz gecisi icin onay gerekli: {current_phase['key']}"
            )

        current_phase["status"] = "completed"
        self._append_history(session, "advance", {"from": current_phase["key"]})

        if phase_index == len(session["phases"]) - 1:
            session["current_phase"] = None
            session["status"] = "completed"
            session["completed_at"] = _now_iso()
            return self._save_session(session)

        next_phase = session["phases"][phase_index + 1]
        next_phase["status"] = "in_progress"
        next_phase["approved"] = False
        session["current_phase"] = next_phase["key"]
        session["status"] = "active"
        return self._save_session(session)

    def backtrack_session(self, session_id: str, reason: str | None = None) -> Dict[str, Any]:
        session = self._load_session(session_id)
        if session.get("status") == "completed":
            raise UdivRuntimeError("Tamamlanmis oturum geri dondurulemez.")

        current_index = self._phase_index(session)
        if current_index == 0:
            raise UdivRuntimeError("Ilk fazdan daha geriye donulemez.")

        current_phase = session["phases"][current_index]["key"]
        previous_phase = session["phases"][current_index - 1]["key"]
        pair_key = f"{current_phase}->{previous_phase}"
        backtrack_counts = session.setdefault("backtrack_counts", {})
        next_count = backtrack_counts.get(pair_key, 0) + 1

        validation_cycles_used = session.get("validation_cycles_used", 0)
        if pair_key == "dogrula->uygula":
            validation_cycles_used += 1

        if next_count > session["guardrails"]["phase_backtracks"] or validation_cycles_used > session["guardrails"]["validation_cycles"]:
            session["status"] = "blocked"
            session["blocker"] = {
                "type": "backtrack_limit",
                "pair": pair_key,
                "message": f"Geri donus limiti asildi: {pair_key}",
            }
            self._append_history(session, "block", {"pair": pair_key, "reason": reason or "limit"})
            self._save_session(session)
            raise UdivRuntimeError(f"Geri donus limiti asildi: {pair_key}", exit_code=2)

        backtrack_counts[pair_key] = next_count
        session["validation_cycles_used"] = validation_cycles_used
        session["status"] = "active"
        session.pop("blocker", None)

        for index, phase in enumerate(session["phases"]):
            if index < current_index - 1:
                phase["status"] = "completed"
            elif index == current_index - 1:
                phase["status"] = "in_progress"
                phase["approved"] = False
            else:
                phase["status"] = "pending"
                phase["approved"] = False

        session["current_phase"] = previous_phase
        self._append_history(
            session,
            "backtrack",
            {"from": current_phase, "to": previous_phase, "count": next_count, "reason": reason or ""},
        )
        return self._save_session(session)

    def render_text(self, session: Dict[str, Any]) -> str:
        lines = [
            "# UDIV Runtime Plan",
            "",
            f"- Oturum: {session.get('session_id', 'plan-only')}",
            f"- Gorev: {session['task']}",
            f"- Mod: {session['mode']}",
            f"- Karmaşıklık: {session['complexity']}",
            f"- Durum: {session.get('status', 'planned')}",
            f"- Aktif Faz: {session['current_phase']}",
            "",
            "## Guardrails",
        ]

        for key, value in session["guardrails"].items():
            lines.append(f"- {key}: {value}")

        lines.extend(["", "## Fazlar"])
        for index, phase in enumerate(session["phases"], start=1):
            lines.append(f"{index}. {phase['title']}")
            lines.append(f"   - Agent: {phase['agent']['name']}")
            lines.append(f"   - Onay gerekli: {'evet' if phase['requires_approval'] else 'hayir'}")
            lines.append(f"   - Onaylandi: {'evet' if phase.get('approved') else 'hayir'}")
            lines.append(f"   - Durum: {phase.get('status', 'pending')}")
            lines.append(f"   - Aciklama: {phase['description']}")

        if session.get("approval_counts"):
            lines.extend(["", "## Onay Sayaçları"])
            for key, value in sorted(session["approval_counts"].items()):
                lines.append(f"- {key}: {value}")

        if session.get("backtrack_counts"):
            lines.extend(["", "## Geri Dönüş Sayaçları"])
            for key, value in sorted(session["backtrack_counts"].items()):
                lines.append(f"- {key}: {value}")

        if session.get("blocker"):
            lines.extend(["", "## Blokaj", f"- {session['blocker']['message']}"])

        return "\n".join(lines)


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LogosFortuna UDIV runtime scaffolding")
    parser.add_argument("task", nargs="?", help="UDIV ile planlanacak gorev")
    parser.add_argument("--task", dest="task_flag", help="UDIV ile planlanacak gorev")
    parser.add_argument(
        "--mode",
        choices=sorted(MODE_PHASES.keys()),
        default="full",
        help="Hangi UDIV diliminin planlanacagi",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Cikti formati",
    )
    parser.add_argument(
        "--workspace-root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Agent tanimlarinin okunacagi workspace kok dizini",
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--start", action="store_true", help="Kalici bir UDIV oturumu baslat")
    action_group.add_argument("--status", action="store_true", help="Kayitli oturum durumunu goster")
    action_group.add_argument("--approve", action="store_true", help="Aktif fazi onayla")
    action_group.add_argument("--advance", action="store_true", help="Aktif fazdan sonraki faza gec")
    action_group.add_argument("--backtrack", action="store_true", help="Bir onceki faza geri don")
    parser.add_argument("--session-id", help="Kalici oturum kimligi")
    parser.add_argument("--reason", help="Geri donus veya blokaj nedeni")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_argument_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    task = args.task_flag or args.task
    orchestrator = UdivOrchestrator(args.workspace_root)

    try:
        if args.start:
            if not task:
                parser.error("--start icin bir gorev gerekli. Konumsal arguman veya --task kullanin.")
            session = orchestrator.start_session(task=task, mode=args.mode)
        elif args.status:
            if not args.session_id:
                parser.error("--status icin --session-id gerekli")
            session = orchestrator.load_session(args.session_id)
        elif args.approve:
            if not args.session_id:
                parser.error("--approve icin --session-id gerekli")
            session = orchestrator.approve_current_phase(args.session_id)
        elif args.advance:
            if not args.session_id:
                parser.error("--advance icin --session-id gerekli")
            session = orchestrator.advance_session(args.session_id)
        elif args.backtrack:
            if not args.session_id:
                parser.error("--backtrack icin --session-id gerekli")
            session = orchestrator.backtrack_session(args.session_id, reason=args.reason)
        else:
            if not task:
                parser.error("Bir gorev gerekli. Konumsal arguman veya --task kullanin.")
            session = orchestrator.build_session(task=task, mode=args.mode)
    except UdivRuntimeError as exc:
        print(str(exc), file=__import__("sys").stderr)
        return exc.exit_code

    if args.format == "json":
        print(json.dumps(session, indent=2, ensure_ascii=False))
    else:
        print(orchestrator.render_text(session))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())