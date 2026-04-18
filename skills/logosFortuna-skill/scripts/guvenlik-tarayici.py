#!/usr/bin/env python3
"""
LogosFortuna Güvenlik Tarayıcı
OWASP Top 10 ve SANS Top 25'e göre kod güvenliği taraması yapar.
"""

import re
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

class GuvenlikTarayici:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.bulgular = []
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, List[Tuple[str, str, str, int]]]:
        """Güvenlik açıkları için regex pattern'leri"""
        return {
            "owasp": [
                # A01: Injection
                ("SQL Injection", r"(SELECT|INSERT|UPDATE|DELETE).*(\+|concat|format).*\%.*", "SQL enjeksiyon riski", 9),
                ("Command Injection", r"(os\.system|subprocess\.call|exec).*\(.*\+.*\)", "Komut enjeksiyonu", 9),
                ("NoSQL Injection", r"\$where.*\+|\$or.*\+", "NoSQL enjeksiyonu", 8),

                # A02: Broken Authentication
                ("Hardcoded Password", r"password.*=.*['\"][^'\"]*['\"]", "Sabit kodlanmış şifre", 8),
                ("Weak Session Timeout", r"SESSION_COOKIE_AGE.*=.*[0-9]{1,3}", "Zayıf session timeout", 6),

                # A03: Sensitive Data Exposure
                ("No HTTPS", r"http://.*(api|auth|login)", "HTTPS kullanılmıyor", 7),
                ("Log Sensitive Data", r"log.*(password|token|key)", "Hassas veri loglanıyor", 6),

                # A07: Cross-Site Scripting
                ("XSS Risk", r"innerHTML.*\+|document\.write.*\+", "XSS güvenlik açığı", 8),
                ("No Input Sanitization", r"\.value|\.text.*\+.*innerHTML", "Girdi sanitizasyonu yok", 7),
            ],
            "sans": [
                # SQL Injection variations
                ("SQL Injection - String Concat", r"cursor\.execute.*\+|query.*\+", "SQL string concatenation", 9),
                ("SQL Injection - Format", r"cursor\.execute.*\%|\.format.*query", "SQL format riski", 8),

                # Buffer Overflow
                ("Buffer Overflow Risk", r"memcpy|strcpy|strcat.*[^,)]*,", "Buffer overflow potansiyeli", 7),

                # Path Traversal
                ("Path Traversal", r"open.*\.\..*\/|path.*\.\.", "Path traversal açığı", 8),
                ("Directory Traversal", r"\.\.\/|\.\.\\", "Directory traversal", 7),

                # Authentication Bypass
                ("Weak Password Check", r"len\(password\).*[<>=].*[0-5]", "Zayıf şifre kontrolü", 6),

                # Race Conditions
                ("File Race Condition", r"if.*os\.path\.exists.*open", "Race condition riski", 6),

                # Error Information Leak
                ("Error Info Leak", r"except.*print.*error|traceback\.print", "Hata bilgisi sızıntısı", 5),
            ]
        }

    def tara_dosyalar(self) -> Dict[str, List[Dict]]:
        """Projedeki Python dosyalarını tara"""
        python_files = list(self.project_root.rglob("*.py"))

        owasp_bulgular = []
        sans_bulgular = []

        for dosya in python_files:
            if "test" in str(dosya).lower() or "venv" in str(dosya):
                continue

            try:
                with open(dosya, 'r', encoding='utf-8') as f:
                    icerik = f.read()
                    satirlar = icerik.split('\n')

                # OWASP taraması
                for pattern_adi, regex, aciklama, risk in self.patterns["owasp"]:
                    matches = re.finditer(regex, icerik, re.IGNORECASE)
                    for match in matches:
                        satir_no = icerik[:match.start()].count('\n') + 1
                        owasp_bulgular.append({
                            "dosya": str(dosya.relative_to(self.project_root)),
                            "satir": satir_no,
                            "pattern": pattern_adi,
                            "aciklama": aciklama,
                            "risk": risk,
                            "kod": satirlar[satir_no-1].strip() if satir_no <= len(satirlar) else ""
                        })

                # SANS taraması
                for pattern_adi, regex, aciklama, risk in self.patterns["sans"]:
                    matches = re.finditer(regex, icerik, re.IGNORECASE)
                    for match in matches:
                        satir_no = icerik[:match.start()].count('\n') + 1
                        sans_bulgular.append({
                            "dosya": str(dosya.relative_to(self.project_root)),
                            "satir": satir_no,
                            "pattern": pattern_adi,
                            "aciklama": aciklama,
                            "risk": risk,
                            "kod": satirlar[satir_no-1].strip() if satir_no <= len(satirlar) else ""
                        })

            except Exception as e:
                print(f"Hata: {dosya} okunamadı - {e}", file=sys.stderr)

        return {
            "owasp": owasp_bulgular,
            "sans": sans_bulgular
        }

    def rapor_olustur(self, bulgular: Dict[str, List[Dict]]) -> str:
        """Güvenlik tarama raporunu oluştur"""
        rapor = ["# Güvenlik Tarama Raporu\n"]

        # Özet tablosu
        owasp_sayisi = len(bulgular["owasp"])
        sans_sayisi = len(bulgular["sans"])

        rapor.append("## Özet\n")
        rapor.append("| Kategori | Toplam | Kritik | Yüksek | Orta | Düşük |")
        rapor.append("|----------|--------|--------|--------|------|-------|")

        # OWASP istatistikleri
        owasp_kritik = len([b for b in bulgular["owasp"] if b["risk"] >= 9])
        owasp_yuksek = len([b for b in bulgular["owasp"] if 7 <= b["risk"] < 9])
        owasp_orta = len([b for b in bulgular["owasp"] if 4 <= b["risk"] < 7])
        owasp_dusuk = len([b for b in bulgular["owasp"] if b["risk"] < 4])

        rapor.append(f"| OWASP Top 10 | {owasp_sayisi} | {owasp_kritik} | {owasp_yuksek} | {owasp_orta} | {owasp_dusuk} |")

        # SANS istatistikleri
        sans_kritik = len([b for b in bulgular["sans"] if b["risk"] >= 9])
        sans_yuksek = len([b for b in bulgular["sans"] if 7 <= b["risk"] < 9])
        sans_orta = len([b for b in bulgular["sans"] if 4 <= b["risk"] < 7])
        sans_dusuk = len([b for b in bulgular["sans"] if b["risk"] < 4])

        rapor.append(f"| SANS Top 25 | {sans_sayisi} | {sans_kritik} | {sans_yuksek} | {sans_orta} | {sans_dusuk} |")

        toplam = owasp_sayisi + sans_sayisi
        toplam_kritik = owasp_kritik + sans_kritik
        toplam_yuksek = owasp_yuksek + sans_yuksek
        toplam_orta = owasp_orta + sans_orta
        toplam_dusuk = owasp_dusuk + sans_dusuk

        rapor.append(f"| **TOPLAM** | **{toplam}** | **{toplam_kritik}** | **{toplam_yuksek}** | **{toplam_orta}** | **{toplam_dusuk}** |")
        rapor.append("")

        # Kritik bulgular
        if toplam_kritik > 0:
            rapor.append("## Kritik Bulgular\n")
            for bulgu in bulgular["owasp"] + bulgular["sans"]:
                if bulgu["risk"] >= 9:
                    rapor.append(f"1. **[{bulgu['pattern']}]** - `{bulgu['dosya']}:{bulgu['satir']}`")
                    rapor.append(f"   - **Risk**: Kritik ({bulgu['risk']}/10)")
                    rapor.append(f"   - **Açıklama**: {bulgu['aciklama']}")
                    if bulgu['kod']:
                        rapor.append(f"   - **Kod**: `{bulgu['kod']}`")
                    rapor.append("")

        # Yüksek risk bulguları
        yuksek_bulgular = [b for b in bulgular["owasp"] + bulgular["sans"] if 7 <= b["risk"] < 9]
        if yuksek_bulgular:
            rapor.append("## Yüksek Risk Bulguları\n")
            for i, bulgu in enumerate(yuksek_bulgular, 1):
                rapor.append(f"{i}. **[{bulgu['pattern']}]** - `{bulgu['dosya']}:{bulgu['satir']}`")
                rapor.append(f"   - **Risk**: Yüksek ({bulgu['risk']}/10)")
                rapor.append(f"   - **Açıklama**: {bulgu['aciklama']}")
                if bulgu['kod']:
                    rapor.append(f"   - **Kod**: `{bulgu['kod']}`")
                rapor.append("")

        # Yapılandırma önerileri
        rapor.append("## Yapılandırma Önerileri\n")
        rapor.append("1. **HTTPS Zorunlu**: Tüm bağlantılar HTTPS üzerinden")
        rapor.append("2. **CSP Header**: Content Security Policy ekleyin")
        rapor.append("3. **HSTS**: HTTP Strict Transport Security etkinleştirin")
        rapor.append("4. **Input Validation**: Tüm kullanıcı girdilerini validate edin")
        rapor.append("5. **Prepared Statements**: SQL sorguları için prepared statements kullanın")
        rapor.append("")

        # Sonraki adımlar
        rapor.append("## Sonraki Adımlar\n")
        if toplam_kritik > 0:
            rapor.append("1. **KRITIK**: Kritik açıkları hemen düzeltin")
        rapor.append("2. Güvenlik test araçları entegre edin (OWASP ZAP, Burp Suite)")
        rapor.append("3. Düzenli güvenlik taramaları planlayın")
        rapor.append("4. Güvenlik eğitimleri düzenleyin")
        rapor.append("")

        return "\n".join(rapor)

def main():
    if len(sys.argv) != 2:
        print("Kullanım: python guvenlik-tarayici.py <proje_dizini>", file=sys.stderr)
        sys.exit(1)

    proje_dizini = sys.argv[1]

    if not os.path.isdir(proje_dizini):
        print(f"Hata: {proje_dizini} dizini bulunamadı", file=sys.stderr)
        sys.exit(1)

    tarayici = GuvenlikTarayici(proje_dizini)
    bulgular = tarayici.tara_dosyalar()
    rapor = tarayici.rapor_olustur(bulgular)

    print(rapor)

if __name__ == "__main__":
    main()