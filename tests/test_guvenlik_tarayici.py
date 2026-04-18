"""Tests for the security scanner (guvenlik-tarayici.py)."""

from conftest import _load_skill_module

_mod = _load_skill_module("guvenlik_tarayici", "guvenlik-tarayici.py")
GuvenlikTarayici = _mod.GuvenlikTarayici


class TestGuvenlikTarayici:
    def test_init(self, tmp_project):
        scanner = GuvenlikTarayici(str(tmp_project))
        assert scanner.project_root == tmp_project
        assert "owasp" in scanner.patterns
        assert "sans" in scanner.patterns

    def test_detects_hardcoded_password(self, tmp_project):
        scanner = GuvenlikTarayici(str(tmp_project))
        findings = scanner.tara_dosyalar()

        all_patterns = [f["pattern"] for f in findings["owasp"] + findings["sans"]]
        assert "Hardcoded Password" in all_patterns

    def test_detects_command_injection(self, tmp_project):
        scanner = GuvenlikTarayici(str(tmp_project))
        findings = scanner.tara_dosyalar()

        all_patterns = [f["pattern"] for f in findings["owasp"] + findings["sans"]]
        assert "Command Injection" in all_patterns

    def test_detects_sql_injection(self, tmp_project):
        scanner = GuvenlikTarayici(str(tmp_project))
        findings = scanner.tara_dosyalar()

        owasp_patterns = [f["pattern"] for f in findings["owasp"]]
        sans_patterns = [f["pattern"] for f in findings["sans"]]

        has_sql = any("SQL" in p for p in owasp_patterns + sans_patterns)
        assert has_sql

    def test_clean_project_no_critical(self, tmp_path):
        clean_py = tmp_path / "clean.py"
        clean_py.write_text(
            'def hello():\n'
            '    """Just a greeting."""\n'
            '    return "hello"\n'
        )

        scanner = GuvenlikTarayici(str(tmp_path))
        findings = scanner.tara_dosyalar()

        critical = [f for f in findings["owasp"] + findings["sans"] if f["risk"] >= 9]
        assert len(critical) == 0

    def test_report_generation(self, tmp_project):
        scanner = GuvenlikTarayici(str(tmp_project))
        findings = scanner.tara_dosyalar()
        report = scanner.rapor_olustur(findings)

        assert isinstance(report, str)
        assert "Güvenlik Tarama Raporu" in report
        assert "Özet" in report

    def test_finding_has_required_fields(self, tmp_project):
        scanner = GuvenlikTarayici(str(tmp_project))
        findings = scanner.tara_dosyalar()

        all_findings = findings["owasp"] + findings["sans"]
        assert len(all_findings) > 0

        for finding in all_findings:
            assert "dosya" in finding
            assert "satir" in finding
            assert "pattern" in finding
            assert "aciklama" in finding
            assert "risk" in finding
            assert isinstance(finding["risk"], int)

    def test_skips_test_files(self, tmp_path):
        test_file = tmp_path / "test_example.py"
        test_file.write_text('password = "secret"\n')

        scanner = GuvenlikTarayici(str(tmp_path))
        findings = scanner.tara_dosyalar()

        all_findings = findings["owasp"] + findings["sans"]
        assert len(all_findings) == 0

    def test_empty_project(self, tmp_path):
        scanner = GuvenlikTarayici(str(tmp_path))
        findings = scanner.tara_dosyalar()

        assert findings["owasp"] == []
        assert findings["sans"] == []

    def test_main_cli(self, tmp_project):
        result = _mod.main([str(tmp_project)])
        assert result == 0

    def test_main_cli_json(self, tmp_project):
        result = _mod.main([str(tmp_project), "--report-format", "json"])
        assert result == 0

    def test_main_cli_missing_dir(self):
        result = _mod.main(["--target", "/nonexistent/path"])
        assert result == 1
