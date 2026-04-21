# LogosFortuna-Skill - UDIV Meta-Orkestrasyon Sistemi

Kisisel iteratif anlama ve uygulama plugin'i. Her gorevi dort fazli UDIV dongusuyle cozer:

**Anla → Tasarla → Uygula → Dogrula**

## Kurulum

```bash
git clone https://github.com/Halukc1974/LogosFortuna.git ~/.claude/plugins/local/logosFortuna-skill
```

Claude Code'u yeniden baslat. Plugin otomatik olarak taninacak.

## Komutlar

| Komut | Aciklama |
|-------|----------|
| `/lf [gorev]` | Tam UDIV dongusu baslat |
| `/lf-anla [alan]` | Sadece derin anlama fazi |
| `/lf-dogrula [alan]` | 5 boyutlu dogrulama |

## Bilesenleri

- **4 Uzman Agent**: anlama, uygulama, ogrenme, dogrulama
- **3 Slash Komutu**: /lf, /lf-anla, /lf-dogrula
- **3 Hook**: SessionStart (baglam), PostToolUse (syntax), Stop (ogrenme)
- **3 Referans**: UDIV protokol, arac orkestrasyon, kalite kapilari
- **Memory Entegrasyonu**: Oturum arasi ogrenme

## Dongu Koruma

Kisir dongu ve sonsuz tekrarlari onlemek icin yerlesik limitler:

| Mekanizma | Limit | Davranis |
|-----------|-------|----------|
| Faz geri donusu | Max 2 / faz cifti | Kullaniciya eskalasyon |
| Artim denemesi | Max 3 / artim | Durdur ve raporla |
| Dogrulama-Uygulama turu | Max 2 tur | Kalan sorunlari kullaniciya sun |
| Faz 1 kesfetme | Max 5 arac cagrisi | Mevcut bilgiyle ilerle |

## Gorev Siniflandirma

UDIV dongusu gorev karmasikligina gore adapte olur:

| Seviye | Akis |
|--------|------|
| **Basit** | Anla (hafif) → Uygula → Dogrula |
| **Orta** | Anla → Tasarla (tek oneri) → Uygula → Dogrula |
| **Karmasik** | Tam UDIV dongusu (2-3 yaklasim) |

## Farkli Makinede Guncelleme

```bash
cd ~/.claude/plugins/local/logosFortuna-skill && git pull
```

## Durum Özeti

Bu repo calisan bir cekirdege sahip, ancak butun ileri ozellikler henuz tam anlamiyla uctan uca degil. Asagidaki tablo mevcut durumu ozetler:

| Alan | Durum | Not |
|------|-------|-----|
| UDIV runtime | Kısmi ama somut | `python -m logosfortuna udiv` faz plani ve guardrail uretir |
| Güvenlik tarama | Hazır | OWASP/SANS regex + heuristic tarama ve rapor uretiliyor |
| Kalite analizi | Hazır | 4 boyutlu skor ve rapor uretiliyor |
| Entegrasyon teslimi | Kısmi | Slack, Discord ve custom webhook gonderimi var; GitHub/Jenkins/GitLab tarafı config agirlikli |
| Çoklu dil | Kısmi | Dil algılama ve localization var; top-level CLI wrapper yok |
| UX / kişiselleştirme | Deneysel | Profil, öneri ve gamification var; editor UI entegrasyonu yok |
| Auto-rollback / chaos / Big-O profiler | Planlanan | Dokumanda var, repoda tam runtime karsiligi henuz yok |

## Çalışan Yüzeyler

### Python runtime
- `python -m logosfortuna udiv -- --task "..."` ile somut UDIV faz plani olusturur
- `python -m logosfortuna integrations -- --status` ile entegrasyon durumunu gosterir
- `python -m logosfortuna security -- --target . --report-format json` ile guvenlik taramasi yapar
- `python -m logosfortuna quality -- --project . --output-format json` ile kalite analizi yapar

### Claude tarafı
- `.claude-plugin/` altinda plugin metadata bulunur
- `commands/` ve `agents/` altinda Claude odakli prompt ve agent tanimlari bulunur

### Copilot / VS Code tarafı
- `.github/copilot-instructions.md` proje genel davranisini tanimlar
- `.github/prompts/lf*.prompt.md` ile `/lf`, `/lf-anla`, `/lf-dogrula` karsiliklari bulunur
- `.github/agents/` ve `.github/skills/logosfortuna-skill/` altinda Copilot kesif dosyalari bulunur

## Uygulanan Moduller

### Güvenlik Tarama
- OWASP ve SANS siniflarina gore regex tabanli tarama
- Risk puanli bulgu modeli ve markdown/json raporlama

### Kalite Analizi
- 0-100 arasi cok boyutlu skor
- Teknik kalite, bakim, test ve dokumantasyon analizi

### Çoklu Dil Desteği
- Turkce, Ingilizce, Almanca ve Fransizca icin localization verisi
- Basit n-gram/frekans tabanli dil algilama

### Entegrasyonlar
- Slack ve Discord webhook gonderimi
- Custom webhook retry/backoff desteği
- GitHub/Jenkins/GitLab icin config ve durum modeli

## Kısmi / Planlanan Alanlar

- Memory graph entegrasyonu ve otomatik MCP kayitlari host ortama bagli
- Git rollback ve temp branch akisi belgelenmis durumda, fakat repoda tam otomatiklestirilmis degil
- Chaos engineering, mutation testing ve Big-O profiler dokumanda tanimli; uygulama tarafi henuz parcali
- Coklu dil ve UX modulleri Python API olarak mevcut, fakat packaging tarafinda birinci sinif CLI yuzeyi degil

## Yapılandırma

### Temel Kurulum
```bash
# UDIV faz planini olustur
python -m logosfortuna udiv -- --task "Yeni kullanıcı API'si ekle"

# Entegrasyonları yapılandır
python scripts/entegrasyon-sistemi.py --setup

# Güvenlik tarayıcıyı çalıştır
python scripts/guvenlik-tarayici.py --target /path/to/project --report-format json

# Kalite analizörü
python scripts/kod-kalitesi-analizoru.py --project /path/to/project --output-format json
```

Not: `coklu-dil-sistemi.py` su an top-level CLI wrapper olarak paketlenmis degil; Python API veya skill icinden kullanilir.

### Gelişmiş Yapılandırma
```json
{
  "integrations": {
    "github": {
      "enabled": true,
      "token": "your_github_token",
      "repositories": ["repo1", "repo2"]
    },
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/...",
      "channel": "#dev-notifications"
    },
    "quality_gates": {
      "min_score": 80,
      "block_on_failure": true
    }
  }
}
```

## Kullanım Örnekleri

### Tam UDIV Dongusu
```bash
/lf Yeni kullanıcı API'si ekle
```
→ Derin anlama → Tasarım önerileri → Artımlı uygulama → 5 boyutlu doğrulama

CLI tarafinda ayni akisin plan iskeleti:

```bash
python -m logosfortuna udiv -- --task "Yeni kullanıcı API'si ekle" --format json
```

### Sadece Güvenlik Tarama
```bash
python scripts/guvenlik-tarayici.py --target /src --report-format json
```

### Kalite Analizi
```bash
python scripts/kod-kalitesi-analizoru.py --project . --output-format text --output quality-report.md
```

### Entegrasyon Testi
```bash
python scripts/entegrasyon-sistemi.py --test-notifications
```

### GitHub PR ve Issue Akislari
```bash
# GitHub baglanti durumunu dogrula
python -m logosfortuna integrations -- --github-connection

# Configure edilen veya verilen repo icin PR listesini al
python -m logosfortuna integrations -- --github-list-pulls --github-repo owner/repo --state open

# Issue listesini al
python -m logosfortuna integrations -- --github-list-issues --github-repo owner/repo --state open

# Yeni issue olustur
python -m logosfortuna integrations -- --github-create-issue --github-repo owner/repo --title "Bug raporu" --body "Detaylar"

# Bir pull request'e yorum ekle
python -m logosfortuna integrations -- --github-comment-pr --github-repo owner/repo --pull-number 12 --body "LGTM"
```

### Modül Üzerinden Çalıştırma
```bash
python -m logosfortuna integrations -- --status
python -m logosfortuna security -- --target . --report-format json
python -m logosfortuna quality -- --project . --output-format json
python -m logosfortuna udiv -- --task "Kalite stratejisi planla"
```

## API Referansı

### Entegrasyon API
```python
from logosfortuna.integration import get_integration_manager

manager = get_integration_manager()

# Bildirim gönder
manager.send_notification("analysis_complete", {"score": 85})

# GitHub yapılandır
manager.configure_github("token", ["repo1", "repo2"])

# GitHub baglantisini dogrula
print(manager.get_github_connection_status())

# PR ve issue akisini kullan
print(manager.list_github_pull_requests("owner/repo"))
print(manager.list_github_issues("owner/repo"))
print(manager.create_github_issue("Yeni issue", "Detay", repository="owner/repo"))
print(manager.comment_on_github_pull_request(12, "LGTM", repository="owner/repo"))

# Slack yapılandır
manager.configure_slack("webhook_url", "#channel")
```

### Güvenlik API
```python
from logosfortuna.security import SecurityScanner

scanner = SecurityScanner("/path/to/project")
results = scanner.tara_dosyalar()
print(scanner.rapor_olustur(results))
```

### Kalite API
```python
from logosfortuna.quality import QualityAnalyzer

analyzer = QualityAnalyzer("/path/to/project")
result = analyzer.analiz_et()
print(f"Kalite Skoru: {result['toplam_skor']}/100")
```

### UDIV Runtime API
```python
from logosfortuna.udiv import UdivOrchestrator

orchestrator = UdivOrchestrator("/path/to/workspace")
session = orchestrator.build_session("Yeni entegrasyon akisini planla")
print(session["current_phase"])
```

## Desteklenen Ortamlar

- ✅ **Claude Code**: `.claude-plugin/`, `commands/`, `agents/`, `skills/`
- ✅ **VS Code / GitHub Copilot**: `.github/copilot-instructions.md`, `.github/prompts/`, `.github/agents/`, `.github/skills/`
- ⚠️ **Diger editorler**: Markdown tabanli tanimlar yeniden kullanilabilir, ancak kesif davranisi host uygulamaya baglidir

## Lisans

MIT License - Ticari ve kişisel kullanım için ücretsiz.

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## İletişim

- **GitHub Issues**: Hata raporları ve özellik istekleri
- **Discussions**: Genel tartışmalar ve yardım
- **Wiki**: Detaylı dokümantasyon ve kılavuzlar
