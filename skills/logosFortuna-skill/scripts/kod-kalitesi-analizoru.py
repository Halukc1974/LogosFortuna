#!/usr/bin/env python3
"""
LogosFortuna Kod Kalitesi Analizörü
Kod kalitesini çok boyutlu olarak analiz eder ve 0-100 arası skor verir.
"""

import argparse
import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

class KodKalitesiAnalizoru:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analiz_sonucu = {
            "teknik_kalite": 0,
            "bakim_kolayligi": 0,
            "test_kalitesi": 0,
            "dokumentasyon": 0,
            "toplam_skor": 0,
            "detaylar": {}
        }

    def analiz_et(self) -> Dict[str, Any]:
        """Tam kod kalitesi analizi"""
        python_files = self._python_dosyalarini_bul()
        test_files = self._test_dosyalarini_bul()

        # Teknik kalite analizi
        self.analiz_sonucu["teknik_kalite"] = self._teknik_kalite_analizi(python_files)

        # Bakım kolaylığı analizi
        self.analiz_sonucu["bakim_kolayligi"] = self._bakim_kolayligi_analizi(python_files)

        # Test kalitesi analizi
        self.analiz_sonucu["test_kalitesi"] = self._test_kalitesi_analizi(python_files, test_files)

        # Dokümantasyon analizi
        self.analiz_sonucu["dokumentasyon"] = self._dokumentasyon_analizi(python_files)

        # Toplam skor hesaplama
        self.analiz_sonucu["toplam_skor"] = self._toplam_skor_hesapla()

        # Ensure detaylar keys exist with sensible defaults even if analysis functions returned early
        detaylar = self.analiz_sonucu.setdefault("detaylar", {})
        detaylar.setdefault("teknik", {
            "avg_complexity": 0,
            "duplication_ratio": 0,
            "code_smells": 0,
            "complexity_score": 0,
            "duplication_score": 0,
            "smell_score": 0
        })
        detaylar.setdefault("bakim", {
            "total_functions": 0,
            "long_functions": 0,
            "function_score": 0,
            "naming_score": 0,
            "avg_dependencies": 0,
            "dependency_score": 0
        })
        detaylar.setdefault("dokumentasyon", {
            "total_functions": 0,
            "documented_functions": 0,
            "docstring_coverage": 0,
            "docstring_score": 0,
            "readme_exists": False,
            "readme_quality": 0,
            "readme_score": 0
        })

        return self.analiz_sonucu

    def _python_dosyalarini_bul(self) -> List[Path]:
        """Python dosyalarını bul"""
        python_files = []
        try:
            it = list(self.project_root.rglob("*.py"))
        except Exception as e:
            it = []
        for file_path in it:
            # Skip virtualenvs, caches and VCS dirs by exact path part matching
            parts = [p.lower() for p in file_path.parts]
            if any(skip in parts for skip in ["venv", "__pycache__", ".git"]):
                continue
            # Skip actual test files but not directories with 'test' in their tmp name
            if file_path.name.startswith("test_") or file_path.name.endswith("_test.py"):
                continue
            python_files.append(file_path)
        try:
            if os.getenv('LOGOSFORTUNA_DEBUG'):
                print(f"[kod-kalitesi] project_root exists: {self.project_root.exists()}")
                try:
                    print(f"[kod-kalitesi] project_root iterdir: {[str(p) for p in self.project_root.iterdir()]}")
                except Exception as e:
                    print(f"[kod-kalitesi] iterdir error: {e}")
        except Exception:
            pass
        try:
            if os.getenv('LOGOSFORTUNA_DEBUG'):
                print(f"[kod-kalitesi] found python_files: {[str(p) for p in python_files]}")
        except Exception:
            pass
        return python_files

    def _test_dosyalarini_bul(self) -> List[Path]:
        """Test dosyalarını bul"""
        test_files = []
        for file_path in self.project_root.rglob("test*.py"):
            test_files.append(file_path)
        for file_path in self.project_root.rglob("*_test.py"):
            test_files.append(file_path)
        return test_files

    def _teknik_kalite_analizi(self, python_files: List[Path]) -> int:
        """Teknik kalite skoru (0-100)"""
        if not python_files:
            return 0

        toplam_complexity = 0
        toplam_duplication = 0
        code_smells = 0
        total_lines = 0

        # Kod parçalarını topla (duplication tespiti için)
        code_snippets = []

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    total_lines += len(lines)

                # AST ile complexity analizi
                tree = ast.parse(content)
                complexity = self._calculate_complexity(tree)
                toplam_complexity += complexity

                # Code duplication için snippet'ları topla
                code_snippets.extend(self._extract_snippets(content))

                # Code smells
                code_smells += self._detect_code_smells(content)

            except (SyntaxError, UnicodeDecodeError):
                continue

        # Ortalama complexity (ideal: <10)
        avg_complexity = toplam_complexity / len(python_files) if python_files else 0
        complexity_score = max(0, 100 - (avg_complexity - 5) * 10)  # 5-15 arası ideal
        complexity_score = min(100, complexity_score)

        # Duplication analizi
        duplication_ratio = self._calculate_duplication(code_snippets)
        duplication_score = max(0, 100 - duplication_ratio * 20)  # %5 altında ideal
        duplication_score = min(100, duplication_score)

        # Code smell skoru
        smell_score = max(0, 100 - code_smells * 2)  # Her smell 2 puan düşür
        smell_score = min(100, smell_score)

        # Ağırlıklı ortalama
        teknik_skor = (complexity_score * 0.4 + duplication_score * 0.3 + smell_score * 0.3)

        self.analiz_sonucu["detaylar"]["teknik"] = {
            "avg_complexity": round(avg_complexity, 2),
            "duplication_ratio": round(duplication_ratio, 2),
            "code_smells": code_smells,
            "complexity_score": round(complexity_score, 1),
            "duplication_score": round(duplication_score, 1),
            "smell_score": round(smell_score, 1)
        }

        return round(teknik_skor)

    def _bakim_kolayligi_analizi(self, python_files: List[Path]) -> int:
        """Bakım kolaylığı skoru (0-100)"""
        if not python_files:
            return 0

        total_functions = 0
        long_functions = 0
        naming_score = 0
        dependency_complexity = 0

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                # Function length analizi
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                total_functions += len(functions)

                for func in functions:
                    func_length = len(func.body)
                    if func_length > 50:  # Uzun fonksiyon
                        long_functions += 1

                # Naming quality
                naming_score += self._analyze_naming_quality(tree)

                # Dependency complexity (import sayısı)
                imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
                dependency_complexity += len(imports)

            except (SyntaxError, UnicodeDecodeError):
                continue

        # Function length skoru
        if total_functions > 0:
            long_function_ratio = long_functions / total_functions
            function_score = max(0, 100 - long_function_ratio * 200)  # %10 altında ideal
        else:
            function_score = 100

        # Naming skoru (0-100 arası zaten)
        final_naming_score = naming_score / len(python_files) if python_files else 0

        # Dependency skoru
        avg_dependencies = dependency_complexity / len(python_files) if python_files else 0
        dependency_score = max(0, 100 - (avg_dependencies - 5) * 5)  # 5-15 arası ideal
        dependency_score = min(100, dependency_score)

        # Ağırlıklı ortalama
        bakim_skor = (function_score * 0.4 + final_naming_score * 0.3 + dependency_score * 0.3)

        self.analiz_sonucu["detaylar"]["bakim"] = {
            "total_functions": total_functions,
            "long_functions": long_functions,
            "function_score": round(function_score, 1),
            "naming_score": round(final_naming_score, 1),
            "avg_dependencies": round(avg_dependencies, 2),
            "dependency_score": round(dependency_score, 1)
        }

        return round(bakim_skor)

    def _test_kalitesi_analizi(self, python_files: List[Path], test_files: List[Path]) -> int:
        """Test kalitesi skoru (0-100)"""
        if not python_files:
            return 0

        # Test coverage tahmini (test dosyası/code dosyası oranı)
        test_ratio = len(test_files) / len(python_files) if python_files else 0
        coverage_score = min(100, test_ratio * 100)  # 1:1 oranında max skor

        # Test quality (assert sayısı, mock kullanımı vb.)
        test_quality_score = self._analyze_test_quality(test_files)

        # Integration test varlığı
        integration_tests = len([f for f in test_files if 'integration' in str(f).lower()])
        integration_score = min(100, integration_tests * 25)  # Her integration test 25 puan

        # Ağırlıklı ortalama
        test_skor = (coverage_score * 0.5 + test_quality_score * 0.3 + integration_score * 0.2)

        self.analiz_sonucu["detaylar"]["test"] = {
            "test_files": len(test_files),
            "code_files": len(python_files),
            "test_ratio": round(test_ratio, 2),
            "coverage_score": round(coverage_score, 1),
            "test_quality_score": round(test_quality_score, 1),
            "integration_tests": integration_tests,
            "integration_score": round(integration_score, 1)
        }

        return round(test_skor)

    def _dokumentasyon_analizi(self, python_files: List[Path]) -> int:
        """Dokümantasyon skoru (0-100)"""
        if not python_files:
            return 0

        total_functions = 0
        documented_functions = 0
        readme_exists = False
        readme_quality = 0

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                # Function docstring analizi
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                total_functions += len(functions)

                for func in functions:
                    if ast.get_docstring(func):
                        documented_functions += 1

            except (SyntaxError, UnicodeDecodeError):
                continue

        # README kontrolü
        readme_files = ['README.md', 'README.txt', 'README.rst']
        # Debug info when requested
        try:
            if os.getenv('LOGOSFORTUNA_DEBUG'):
                print(f"[kod-kalitesi] project_root={self.project_root}")
                print("[kod-kalitesi] listing:", list(self.project_root.iterdir()) if self.project_root.exists() else [])
        except Exception:
            pass

        for readme in readme_files:
            if (self.project_root / readme).exists():
                readme_exists = True
                readme_content = (self.project_root / readme).read_text()
                readme_quality = self._analyze_readme_quality(readme_content)
                break

        # Docstring coverage
        if total_functions > 0:
            docstring_coverage = documented_functions / total_functions
            docstring_score = docstring_coverage * 100
        else:
            docstring_score = 100

        # README skoru
        readme_score = readme_quality if readme_exists else 20  # README yoksa düşük skor

        # Ağırlıklı ortalama
        dokumantasyon_skor = (docstring_score * 0.6 + readme_score * 0.4)

        self.analiz_sonucu["detaylar"]["dokumentasyon"] = {
            "total_functions": total_functions,
            "documented_functions": documented_functions,
            "docstring_coverage": round(docstring_coverage * 100, 1) if total_functions > 0 else 0,
            "docstring_score": round(docstring_score, 1),
            "readme_exists": readme_exists,
            "readme_quality": round(readme_quality, 1),
            "readme_score": round(readme_score, 1)
        }

        return round(dokumantasyon_skor)

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Cyclomatic complexity hesaplama"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                complexity += len(node.values) - 1

        return complexity

    def _extract_snippets(self, content: str) -> List[str]:
        """Kod snippet'ları çıkar (duplication tespiti için)"""
        lines = content.split('\n')
        snippets = []

        for i in range(len(lines) - 5):  # 5 satırlık snippet'lar
            snippet = '\n'.join(lines[i:i+5]).strip()
            if len(snippet) > 20:  # Çok kısa snippet'ları atla
                snippets.append(snippet)

        return snippets

    def _calculate_duplication(self, snippets: List[str]) -> float:
        """Kod duplication oranı"""
        if not snippets:
            return 0

        seen = set()
        duplicates = 0

        for snippet in snippets:
            if snippet in seen:
                duplicates += 1
            seen.add(snippet)

        return (duplicates / len(snippets)) * 100

    def _detect_code_smells(self, content: str) -> int:
        """Code smell tespiti"""
        smells = 0

        # Magic numbers
        magic_numbers = re.findall(r'\b\d{2,}\b', content)  # 2+ digit numbers
        smells += len([n for n in magic_numbers if n not in ['100', '0', '1', '10', '60', '24']])

        # Magic strings
        magic_strings = re.findall(r'[\'"]([^\'"]{10,})[\'"]', content)  # 10+ char strings
        smells += len(magic_strings) // 2  # Her 2 magic string için 1 smell

        # Long lines
        lines = content.split('\n')
        long_lines = [line for line in lines if len(line) > 120]
        smells += len(long_lines)

        return smells

    def _analyze_naming_quality(self, tree: ast.AST) -> float:
        """Naming quality analizi (0-100)"""
        score = 0
        total_names = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Name)):
                if hasattr(node, 'name'):
                    name = node.name
                    total_names += 1

                    # Snake_case kontrolü (functions/variables)
                    if isinstance(node, ast.FunctionDef):
                        if re.match(r'^[a-z][a-z0-9_]*$', name):
                            score += 1

                    # CamelCase kontrolü (classes)
                    elif isinstance(node, ast.ClassDef):
                        if re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                            score += 1

                    # Variable naming
                    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                        if re.match(r'^[a-z][a-z0-9_]*$', name) or name.isupper():
                            score += 1

        return (score / total_names * 100) if total_names > 0 else 100

    def _analyze_test_quality(self, test_files: List[Path]) -> float:
        """Test quality analizi (0-100)"""
        if not test_files:
            return 0

        total_score = 0

        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Assert sayısı
                assert_count = len(re.findall(r'\bassert\b', content))
                assert_score = min(100, assert_count * 5)  # Her assert 5 puan

                # Mock/stub kullanımı
                mock_usage = len(re.findall(r'\bmock\b|\bpatch\b|\bMagicMock\b', content))
                mock_score = min(100, mock_usage * 10)  # Her mock 10 puan

                # Test function sayısı
                test_functions = len(re.findall(r'\bdef test_', content))
                function_score = min(100, test_functions * 10)  # Her test function 10 puan

                file_score = (assert_score * 0.4 + mock_score * 0.3 + function_score * 0.3)
                total_score += file_score

            except (UnicodeDecodeError, OSError):
                continue

        return total_score / len(test_files) if test_files else 0

    def _analyze_readme_quality(self, content: str) -> float:
        """README quality analizi (0-100)"""
        score = 0

        # Temel bölümler kontrolü
        sections = ['installation', 'usage', 'contributing', 'license']
        content_lower = content.lower()

        for section in sections:
            if section in content_lower:
                score += 20  # Her bölüm 20 puan

        # Kod örnekleri
        if '```' in content:
            score += 10

        # Bağlantılar
        if '[' in content and '](http' in content:
            score += 10

        # Uzunluk kontrolü
        if len(content) > 500:
            score += 10

        return min(100, score)

    def _toplam_skor_hesapla(self) -> int:
        """Ağırlıklı toplam skor"""
        teknik = self.analiz_sonucu["teknik_kalite"]
        bakim = self.analiz_sonucu["bakim_kolayligi"]
        test = self.analiz_sonucu["test_kalitesi"]
        dokumantasyon = self.analiz_sonucu["dokumentasyon"]

        toplam = (teknik * 0.4 + bakim * 0.3 + test * 0.2 + dokumantasyon * 0.1)
        return round(toplam)

    def rapor_olustur(self) -> str:
        """Detaylı rapor oluştur"""
        sonuc = self.analiz_sonucu
        rapor = ["# Kod Kalitesi Analiz Raporu\n"]

        # Genel skor
        toplam = sonuc["toplam_skor"]
        grade = self._get_grade(toplam)
        rapor.append(f"### Genel Skor: {toplam}/100 ({grade})\n")

        # Detay tablosu
        rapor.append("| Boyut | Skor | Ağırlık | Ağırlıklı Skor |")
        rapor.append("|-------|------|---------|----------------|")

        agirliklar = {"teknik_kalite": 0.4, "bakim_kolayligi": 0.3, "test_kalitesi": 0.2, "dokumentasyon": 0.1}
        isimler = {
            "teknik_kalite": "Teknik Kalite",
            "bakim_kolayligi": "Bakım Kolaylığı",
            "test_kalitesi": "Test Kalitesi",
            "dokumentasyon": "Dokümantasyon"
        }

        for key, agirlik in agirliklar.items():
            skor = sonuc[key]
            agirlikli = skor * agirlik
            rapor.append(f"| {isimler[key]} | {skor} | {agirlik*100:.0f}% | {agirlikli:.1f} |")

        rapor.append(f"| **TOPLAM** | **{toplam}** | **100%** | **{toplam:.1f}** |")
        rapor.append("")

        # Detaylı analiz
        rapor.append("### Detaylı Analiz\n")

        # Teknik kalite detayları
        if "teknik" in sonuc["detaylar"]:
            t = sonuc["detaylar"]["teknik"]
            rapor.append("#### Teknik Kalite")
            rapor.append(f"- **Cyclomatic Complexity**: Ortalama {t['avg_complexity']} {'✅' if t['avg_complexity'] < 10 else '⚠️'}")
            rapor.append(f"- **Code Duplication**: %{t['duplication_ratio']} {'✅' if t['duplication_ratio'] < 5 else '⚠️'}")
            rapor.append(f"- **Code Smells**: {t['code_smells']} adet {'✅' if t['code_smells'] < 10 else '⚠️'}")

        # Diğer boyutların detayları...
        rapor.append("\n### İyileştirme Önerileri\n")
        rapor.append("1. **Teknik Kalite**: Complexity reduction ve duplication elimination")
        rapor.append("2. **Bakım Kolaylığı**: Function decomposition ve naming improvements")
        rapor.append("3. **Test Kalitesi**: Coverage increase ve quality improvements")
        rapor.append("4. **Dokümantasyon**: Docstring coverage and README updates")

        return "\n".join(rapor)

    def _get_grade(self, skor: int) -> str:
        """Skora göre grade belirle"""
        if skor >= 90: return "A - Üstün Kalite"
        elif skor >= 80: return "B - İyi Kalite"
        elif skor >= 70: return "C - Orta Kalite"
        elif skor >= 60: return "D - Düşük Kalite"
        else: return "F - Kötü Kalite"

def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LogosFortuna kod kalitesi analizoru"
    )
    parser.add_argument("project_dir", nargs="?", help="Analiz edilecek proje dizini")
    parser.add_argument("--project", dest="project_dir_flag", help="Analiz edilecek proje dizini")
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Analiz sonucunun cikti formati",
    )
    parser.add_argument("--output", help="Raporu dosyaya yaz")
    return parser


def main(argv=None):
    parser = _build_argument_parser()
    args = parser.parse_args(argv)

    proje_dizini = args.project_dir_flag or args.project_dir
    if not proje_dizini:
        parser.error("Bir proje dizini gerekli. Konumsal arguman veya --project kullanin.")

    if not os.path.isdir(proje_dizini):
        print(f"Hata: {proje_dizini} dizini bulunamadı", file=os.sys.stderr)
        return 1

    analizor = KodKalitesiAnalizoru(proje_dizini)
    sonuc = analizor.analiz_et()
    if args.output_format == "json":
        cikti = json.dumps(sonuc, indent=2, ensure_ascii=False)
    else:
        cikti = analizor.rapor_olustur()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as output_file:
            output_file.write(cikti)
    else:
        print(cikti)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())