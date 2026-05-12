# LogosFortuna Self-Update Protokolu

## Amac

LogosFortuna kendi surumunu izleyebilir, yeni surum cikinca kullaniciya bildirir ve onayli update yapar.

## Surum Yonetimi Modeli

`plugin.json`'daki `version` alani semantik versiyonlama kullanir:

- **MAJOR**: UDIV faz yapisi degisirse, geriye uyumsuz API
- **MINOR**: Yeni agent/komut/reference eklemesi, geriye uyumlu
- **PATCH**: Hata duzeltmeleri, dokumantasyon iyilestirmeleri

Mevcut: `1.1.0` (auto-install + skill classifier + telemetry eklenmis hali)

## Update Akisi

```
/lf-update komutu calistirildi
│
├── [1] Mevcut surumu plugin.json'dan oku
├── [2] GitHub Releases API'den en son tag al
├── [3] Karsilastir
│   ├── EQUAL → "Zaten guncel" + cik
│   ├── LOCAL > REMOTE → "Geliştirme surumu kullaniyorsun" + cik
│   └── REMOTE > LOCAL → adim 4'e gec
│
├── [4] Release notes (changelog) cek
│   gh api repos/Halukc1974/LogosFortuna/releases/latest --jq '.body'
│
├── [5] AskUserQuestion ile kullaniciya sor
│   Secenekler:
│   - "Guncelle (onerilen)" → adim 6
│   - "Sadece changelog'u goster, sonra karar ver" → ciktiyi sun + bekle
│   - "Bu surumu atla" → memory'e "skipped-version" kaydet
│
├── [6] Backup
│   git stash veya git tag "pre-update-$(date +%s)"
│
├── [7] Marketplace + plugin update
│   claude plugin marketplace update logosFortuna
│   claude plugin install logosFortuna-skill@logosFortuna
│
├── [8] /reload-plugins (kullaniciya bildirim)
│
└── [9] Telemetri kaydi + Memory MCP'e "updated to X" notu
```

## Otomatik Update Politikasi

`userConfig.auto_update_check` (default: `true`):

- Her SessionStart hook'unda son update kontrolunden 24 saat gectiyse:
  - Quietly check GitHub
  - Yeni surum varsa stderr'e bilgi mesaji bas:
    `"💡 LogosFortuna v1.2.0 mevcut (sen v1.1.0 kullaniyorsun). /lf-update ile guncelle."`
- Otomatik **kurma yok** — sadece bildirim
- Update tetigi kullanicidan gelir (`/lf-update`)

## Surum Karsilastirma

```python
# Pseudo-kod
from packaging import version

current = version.parse("1.1.0")
remote = version.parse("1.2.0")

if remote > current:
    # update suggest
elif current > remote:
    # dev/local versiyonu, atla
else:
    # esit, ge gec
```

Bash icin (packaging yok):

```bash
version_lt() {
  [ "$1" = "$2" ] && return 1
  printf '%s\n%s' "$1" "$2" | sort -V | head -n1 | grep -qx "$1"
}

if version_lt "$CURRENT" "$REMOTE"; then
  echo "Update available"
fi
```

## Update Sirasinda Veri Kaybi Onleme

Kullanici yereldeki dosyalari degistirmis olabilir:

```bash
cd ~/.claude/plugins/local/logosFortuna-skill
if [ -n "$(git status --porcelain)" ]; then
  echo "UYARI: Yerel degisikliklerin var. Update yapmadan once nasil davranayim?"
  # AskUserQuestion:
  #  - Yerel degisiklikleri stash et, update yap, sonra geri al
  #  - Yerel degisiklikleri commit et (kullanici bir branch'a)
  #  - Update'i iptal et
fi
```

## Hata ve Geri Alma

| Senaryo | Aksiyon |
|---------|---------|
| GitHub API rate limit | "Birkaç dakika sonra tekrar deneyin" |
| Network olmadi | "Internet baglantisini kontrol et" |
| `gh` CLI eksik | `curl -s https://api.github.com/...` fallback |
| Update sonrasi plugin yuklenemiyor | git ile onceki tag'e geri don, kullaniciya bildir |
| MCP server'lar update sonrasi calismiyor | `/reload-plugins` + tekrar dene, hata varsa downgrade |

## Constitution Uyumu

| Madde | Uyum |
|-------|------|
| 1. Understand before changing | Changelog gosterilir, onay alinir |
| 2. Small, verifiable increments | Tek bir update, atomic |
| 5. Ogrenme | "Hangi surum surumlerini geçti" memory'e kaydedilir |
| 7. Preserve operator control | Asla otomatik update yok |

## Iliskili Belgeler

- [Auto-Install Protokol](./auto-install-protokol.md) — plugin/MCP install patterns
- [Skill Kesif Tablosu](./skill-kesif-tablosu.md) — yeni surumlerde tablo guncellemesi
