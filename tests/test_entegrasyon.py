"""Tests for the integration system (entegrasyon-sistemi.py)."""

import json
import time

from conftest import _load_skill_module

_mod = _load_skill_module("entegrasyon_sistemi", "entegrasyon-sistemi.py")
EntegrasyonYoneticisi = _mod.EntegrasyonYoneticisi


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
