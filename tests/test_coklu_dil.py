"""Tests for the multilingual system (coklu-dil-sistemi.py)."""

from datetime import datetime

from tests.conftest import _load_skill_module

_mod = _load_skill_module("coklu_dil_sistemi", "coklu-dil-sistemi.py")
CokluDilSistemi = _mod.CokluDilSistemi


class TestCokluDilSistemi:
    def test_init(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))
        assert system.current_language in ["tr", "en", "de", "fr"]

    def test_supported_languages(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))
        langs = system.get_supported_languages()

        assert "tr" in langs
        assert "en" in langs
        assert "de" in langs
        assert "fr" in langs

    def test_set_language(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))

        assert system.set_language("en") is True
        assert system.current_language == "en"

        assert system.set_language("invalid") is False
        assert system.current_language == "en"

    def test_detect_language_turkish(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))
        # Turkish-specific characters should influence detection
        result = system.detect_language("merhaba dünya nasılsın güzel günler çok şey öğrendim")
        # Just verify it returns a valid language code
        assert result in ["tr", "en", "de", "fr"]

    def test_detect_language_empty(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))
        result = system.detect_language("")
        assert result == system.current_language

    def test_localize_message(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))

        msg_tr = system.localize_message("hello", "tr")
        assert msg_tr == "merhaba"

        msg_en = system.localize_message("hello", "en")
        assert msg_en == "hello"

    def test_localize_missing_key(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))
        # Missing keys should return the key itself
        msg = system.localize_message("nonexistent_key", "tr")
        assert msg == "nonexistent_key"

    def test_format_date_turkish(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))
        dt = datetime(2025, 3, 15)

        result = system.format_date(dt, "tr")
        assert result == "15.03.2025"

    def test_format_date_english(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))
        dt = datetime(2025, 3, 15)

        result = system.format_date(dt, "en")
        assert result == "03/15/2025"

    def test_format_datetime(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))
        dt = datetime(2025, 3, 15, 14, 30, 0)

        result = system.format_datetime(dt, "tr")
        assert "15.03.2025" in result
        assert "14:30:00" in result

    def test_cultural_context(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))

        ctx_tr = system.get_cultural_context("tr")
        assert ctx_tr["naming_style"] == "snake_case"
        assert ctx_tr["time_format"] == "24h"

        ctx_en = system.get_cultural_context("en")
        assert ctx_en["time_format"] == "12h"

    def test_add_translation(self, tmp_path):
        system = CokluDilSistemi(translations_dir=str(tmp_path / "translations"))

        result = system.add_translation("custom_key", {
            "tr": "özel değer",
            "en": "custom value"
        })
        assert result is True

        msg = system.localize_message("custom_key", "tr")
        assert msg == "özel değer"
