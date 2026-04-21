"""Structural tests for Copilot discovery assets."""

from pathlib import Path

from logosfortuna.udiv import _parse_frontmatter


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def test_copilot_instructions_exists():
    instructions = WORKSPACE_ROOT / ".github" / "copilot-instructions.md"
    assert instructions.exists()


def test_copilot_skill_name_matches_folder():
    skill_file = WORKSPACE_ROOT / ".github" / "skills" / "logosfortuna-skill" / "SKILL.md"
    frontmatter = _parse_frontmatter(skill_file.read_text(encoding="utf-8"))

    assert frontmatter["name"] == "logosfortuna-skill"
    assert "UDIV" in frontmatter["description"]


def test_prompts_have_expected_agents():
    prompt_dir = WORKSPACE_ROOT / ".github" / "prompts"
    expected = {
        "lf.prompt.md": "logosfortuna-udiv",
        "lf-anla.prompt.md": "anlama-ajansi",
        "lf-dogrula.prompt.md": "dogrulama-ajansi",
    }

    for file_name, agent_name in expected.items():
        frontmatter = _parse_frontmatter((prompt_dir / file_name).read_text(encoding="utf-8"))
        assert frontmatter["agent"] == agent_name
        assert frontmatter["description"]


def test_orchestrator_agent_references_core_subagents():
    agent_file = WORKSPACE_ROOT / ".github" / "agents" / "logosfortuna-udiv.agent.md"
    frontmatter = _parse_frontmatter(agent_file.read_text(encoding="utf-8"))

    assert frontmatter["name"] == "logosfortuna-udiv"
    assert frontmatter["agents"] == [
        "anlama-ajansi",
        "uygulama-ajansi",
        "dogrulama-ajansi",
        "ogrenme-ajansi",
    ]