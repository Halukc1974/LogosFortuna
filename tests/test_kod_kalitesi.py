"""Tests for the code quality analyzer (kod-kalitesi-analizoru.py)."""

from conftest import _load_skill_module

_mod = _load_skill_module("kod_kalitesi_analizoru", "kod-kalitesi-analizoru.py")
KodKalitesiAnalizoru = _mod.KodKalitesiAnalizoru


class TestKodKalitesiAnalizoru:
    def test_init(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        assert analyzer.project_root == tmp_project

    def test_full_analysis(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        result = analyzer.analiz_et()

        assert "teknik_kalite" in result
        assert "bakim_kolayligi" in result
        assert "test_kalitesi" in result
        assert "dokumentasyon" in result
        assert "toplam_skor" in result
        assert "detaylar" in result

    def test_scores_are_in_range(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        result = analyzer.analiz_et()

        for key in ["teknik_kalite", "bakim_kolayligi", "test_kalitesi", "dokumentasyon", "toplam_skor"]:
            assert 0 <= result[key] <= 100, f"{key} score {result[key]} out of range"

    def test_empty_project(self, tmp_path):
        analyzer = KodKalitesiAnalizoru(str(tmp_path))
        result = analyzer.analiz_et()

        assert result["teknik_kalite"] == 0
        assert result["toplam_skor"] == 0

    def test_technical_details(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        result = analyzer.analiz_et()

        assert "teknik" in result["detaylar"]
        teknik = result["detaylar"]["teknik"]
        assert "avg_complexity" in teknik
        assert "duplication_ratio" in teknik
        assert "code_smells" in teknik

    def test_maintenance_details(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        result = analyzer.analiz_et()

        assert "bakim" in result["detaylar"]
        bakim = result["detaylar"]["bakim"]
        assert "total_functions" in bakim
        assert "naming_score" in bakim

    def test_documentation_details(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        result = analyzer.analiz_et()

        assert "dokumentasyon" in result["detaylar"]
        doc = result["detaylar"]["dokumentasyon"]
        assert doc["readme_exists"] is True
        assert doc["readme_quality"] > 0

    def test_weighted_total(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        result = analyzer.analiz_et()

        expected = round(
            result["teknik_kalite"] * 0.4
            + result["bakim_kolayligi"] * 0.3
            + result["test_kalitesi"] * 0.2
            + result["dokumentasyon"] * 0.1
        )
        assert abs(result["toplam_skor"] - expected) <= 1

    def test_report_generation(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        analyzer.analiz_et()
        report = analyzer.rapor_olustur()

        assert isinstance(report, str)
        assert "Kod Kalitesi Analiz Raporu" in report
        assert "Genel Skor" in report

    def test_grade_levels(self, tmp_project):
        analyzer = KodKalitesiAnalizoru(str(tmp_project))
        assert "A" in analyzer._get_grade(95)
        assert "B" in analyzer._get_grade(85)
        assert "C" in analyzer._get_grade(75)
        assert "D" in analyzer._get_grade(65)
        assert "F" in analyzer._get_grade(50)

    def test_main_cli(self, tmp_project):
        result = _mod.main([str(tmp_project)])
        assert result == 0

    def test_main_cli_json(self, tmp_project):
        result = _mod.main([str(tmp_project), "--output-format", "json"])
        assert result == 0
