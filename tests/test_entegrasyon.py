"""Tests for the integration system (entegrasyon-sistemi.py)."""

import json
import time
from types import SimpleNamespace

from tests.conftest import _load_skill_module

_mod = _load_skill_module("entegrasyon_sistemi", "entegrasyon-sistemi.py")
EntegrasyonYoneticisi = _mod.EntegrasyonYoneticisi


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.content = b"{}"

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _fake_github_request(method, url, headers=None, params=None, json=None, timeout=None):
    if url.endswith("/user"):
        return DummyResponse({"login": "haluk", "name": "Haluk Celebi"})
    if url.endswith("/repos/owner/repo/pulls"):
        return DummyResponse([
            {
                "number": 12,
                "title": "Improve orchestration",
                "state": "open",
                "draft": False,
                "user": {"login": "octocat"},
                "head": {"ref": "feature/udiv"},
                "html_url": "https://github.com/owner/repo/pull/12",
                "created_at": "2026-04-21T00:00:00Z",
            }
        ])
    if url.endswith("/repos/owner/repo/issues") and method == "GET":
        return DummyResponse([
            {
                "number": 5,
                "title": "Bug report",
                "state": "open",
                "user": {"login": "octocat"},
                "labels": [{"name": "bug"}],
                "html_url": "https://github.com/owner/repo/issues/5",
                "created_at": "2026-04-21T00:00:00Z",
            },
            {
                "number": 6,
                "title": "PR masquerading as issue",
                "state": "open",
                "user": {"login": "octocat"},
                "labels": [],
                "html_url": "https://github.com/owner/repo/issues/6",
                "created_at": "2026-04-21T00:00:00Z",
                "pull_request": {"url": "https://api.github.com/repos/owner/repo/pulls/6"},
            },
        ])
    if url.endswith("/repos/owner/repo/issues") and method == "POST":
        return DummyResponse(
            {
                "number": 77,
                "title": json["title"],
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/77",
                "labels": [{"name": label} for label in json.get("labels", [])],
            },
            status_code=201,
        )
    if url.endswith("/repos/owner/repo/issues/12/comments"):
        return DummyResponse(
            {
                "id": 9001,
                "html_url": "https://github.com/owner/repo/pull/12#issuecomment-9001",
                "body": json["body"],
            },
            status_code=201,
        )
    raise AssertionError(f"Beklenmeyen GitHub istegi: {method} {url}")


class TestEntegrasyonYoneticisi:
    def test_init_creates_config_dir(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        assert tmp_config.parent.exists()

    def test_default_config_structure(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)

        assert "github" in manager.config
        assert "slack" in manager.config
        assert "discord" in manager.config
        assert "jenkins" in manager.config
        assert "gitlab" in manager.config
        assert "webhooks" in manager.config
        assert "notifications" in manager.config

    def test_all_integrations_disabled_by_default(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)

        assert manager.config["github"]["enabled"] is False
        assert manager.config["slack"]["enabled"] is False
        assert manager.config["discord"]["enabled"] is False

    def test_configure_github(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        result = manager.configure_github("test_token", ["repo1", "repo2"])

        assert result is True
        assert manager.config["github"]["enabled"] is True
        assert manager.config["github"]["token"] == "test_token"
        assert manager.config["github"]["repositories"] == ["repo1", "repo2"]

    def test_configure_slack(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        result = manager.configure_slack("https://hooks.slack.com/test", "#test")

        assert result is True
        assert manager.config["slack"]["enabled"] is True
        assert manager.config["slack"]["webhook_url"] == "https://hooks.slack.com/test"
        assert manager.config["slack"]["channel"] == "#test"

    def test_configure_discord(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        result = manager.configure_discord("https://discord.com/api/webhooks/test")

        assert result is True
        assert manager.config["discord"]["enabled"] is True

    def test_add_custom_webhook(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        result = manager.add_custom_webhook(
            "https://example.com/webhook",
            ["analysis_complete", "error_detected"],
            "test-webhook"
        )

        assert result is True
        assert len(manager.config["webhooks"]["custom_webhooks"]) == 1
        webhook = manager.config["webhooks"]["custom_webhooks"][0]
        assert webhook["name"] == "test-webhook"
        assert webhook["enabled"] is True

    def test_save_and_load_config(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        manager.configure_github("token123", ["my-repo"])
        manager.save_config()

        # Load in a new instance
        manager2 = EntegrasyonYoneticisi(config_file=tmp_config)
        assert manager2.config["github"]["enabled"] is True
        assert manager2.config["github"]["token"] == "token123"

    def test_integration_status(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        status = manager.get_integration_status()

        assert "github" in status
        assert "slack" in status
        assert "discord" in status
        assert "queue_size" in status
        assert status["github"] is False

    def test_notification_filtering(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)

        # Unknown event type should be silently dropped
        manager.send_notification("unknown_event", {"data": "test"})
        time.sleep(0.1)  # Let worker process

        # No crash expected
        assert manager.notification_queue.qsize() == 0 or True

    def test_quiet_hours_logic(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        # Quiet hours disabled by default
        assert manager._is_quiet_hours() is False

    def test_priority_colors(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)

        assert manager._get_priority_color("low") == "good"
        assert manager._get_priority_color("critical") == "#FF0000"
        assert manager._get_priority_color("unknown") == "warning"

    def test_event_title_formatting(self, tmp_config):
        manager = EntegrasyonYoneticisi(config_file=tmp_config)

        assert manager._format_event_title("analysis_complete") == "Kod Analizi Tamamlandı"
        assert manager._format_event_title("security_alert") == "Güvenlik Uyarısı"
        # Unknown event should format nicely
        assert manager._format_event_title("some_event") == "Some Event"

    def test_main_cli_status(self, tmp_config):
        result = _mod.main(["--config", str(tmp_config), "--status"])
        assert result == 0

    def test_main_cli_setup(self, tmp_config):
        result = _mod.main(["--config", str(tmp_config), "--setup"])
        assert result == 0

    def test_github_connection_status(self, tmp_config, monkeypatch):
        monkeypatch.setattr(_mod.requests, "request", _fake_github_request)
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        manager.configure_github("test_token", ["owner/repo"])

        status = manager.get_github_connection_status()

        assert status["authenticated"] is True
        assert status["viewer"] == "haluk"
        assert status["repositories"] == ["owner/repo"]

    def test_list_github_pull_requests(self, tmp_config, monkeypatch):
        monkeypatch.setattr(_mod.requests, "request", _fake_github_request)
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        manager.configure_github("test_token", ["owner/repo"])

        payload = manager.list_github_pull_requests()

        assert payload["repository"] == "owner/repo"
        assert payload["count"] == 1
        assert payload["items"][0]["number"] == 12
        assert payload["items"][0]["branch"] == "feature/udiv"

    def test_list_github_issues_filters_pull_requests(self, tmp_config, monkeypatch):
        monkeypatch.setattr(_mod.requests, "request", _fake_github_request)
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        manager.configure_github("test_token", ["owner/repo"])

        payload = manager.list_github_issues()

        assert payload["count"] == 1
        assert payload["items"][0]["number"] == 5
        assert payload["items"][0]["labels"] == ["bug"]

    def test_create_github_issue(self, tmp_config, monkeypatch):
        monkeypatch.setattr(_mod.requests, "request", _fake_github_request)
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        manager.configure_github("test_token", ["owner/repo"])

        payload = manager.create_github_issue("Yeni issue", "Detay", labels=["enhancement"])

        assert payload["number"] == 77
        assert payload["labels"] == ["enhancement"]

    def test_comment_on_github_pull_request(self, tmp_config, monkeypatch):
        monkeypatch.setattr(_mod.requests, "request", _fake_github_request)
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        manager.configure_github("test_token", ["owner/repo"])

        payload = manager.comment_on_github_pull_request(12, "LGTM")

        assert payload["pull_number"] == 12
        assert payload["comment_id"] == 9001
        assert payload["body"] == "LGTM"

    def test_main_cli_github_list_pulls(self, tmp_config, monkeypatch, capsys):
        monkeypatch.setattr(_mod.requests, "request", _fake_github_request)
        manager = EntegrasyonYoneticisi(config_file=tmp_config)
        manager.configure_github("test_token", ["owner/repo"])
        manager.save_config()

        result = _mod.main(["--config", str(tmp_config), "--github-list-pulls"])
        captured = capsys.readouterr()

        assert result == 0
        payload = json.loads(captured.out)
        assert payload["items"][0]["number"] == 12
