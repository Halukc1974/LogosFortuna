---
description: LogosFortuna-Skill surum kontrolu ve guncelleme
allowed-tools: Bash, Read, WebFetch
---

# LogosFortuna Self-Update

Mevcut surum ile GitHub'daki en son surum karsilastirilir, kullanici onayiyla update yapilir.

## Adimlar

1. Mevcut surumu plugin.json'dan oku:

```bash
PLUGIN_JSON="${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"
CURRENT_VERSION=$(grep '"version"' "$PLUGIN_JSON" | head -1 | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
echo "Mevcut surum: $CURRENT_VERSION"
```

2. GitHub'da en son release'i sorgula:

```bash
LATEST=$(gh api repos/Halukc1974/LogosFortuna/releases/latest --jq '.tag_name' 2>/dev/null || echo "")
if [ -z "$LATEST" ]; then
  echo "GitHub'dan surum bilgisi alinamadi (network veya gh CLI eksik olabilir)"
  exit 1
fi
echo "En son surum: $LATEST"
```

3. Surum karsilastir:
   - Esit → "Zaten guncel" mesaji ve cik
   - Farkli → kullaniciya AskUserQuestion ile sor:
     - Changelog'u WebFetch ile oku ve goster
     - "Guncelleyelim mi?" sor

4. Onaylanirsa:

```bash
# Marketplace update
claude plugin marketplace update logosFortuna
# Plugin update
claude plugin install logosFortuna-skill@logosFortuna
# Reload
echo "Calistir: /reload-plugins"
```

5. Reload sonrasi version kontrolu:

```bash
NEW_VERSION=$(grep '"version"' "$PLUGIN_JSON" | head -1 | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
echo "Yeni surum: $NEW_VERSION"
```

## Hata Senaryolari

| Hata | Aksiyon |
|------|---------|
| `gh` CLI yok | Kullaniciya curl ile manuel kontrol komutu sun |
| Network hatasi | "Internet baglantisini kontrol et" |
| Plugin marketplace bulunamadi | `claude plugin marketplace add Halukc1974/LogosFortuna` ile ekle |
| Update sirasinda hata | git checkout ile rollback, kullaniciya hata ilet |

## Telemetri Kaydi

Her update girisimi loglanir:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/telemetry-writer.py" write session_summary \
  --data "{\"event_subtype\":\"self_update\",\"from\":\"$CURRENT_VERSION\",\"to\":\"$LATEST\",\"result\":\"success|failed\"}"
```

## Manuel Geri Alma

Yeni surum sorun cikarirsa:

```bash
# Onceki surume don
cd ~/.claude/plugins/local/logosFortuna-skill
git log --oneline | head -10  # son commit'leri gor
git checkout <onceki-tag-veya-sha>
# veya yeniden installation
claude plugin uninstall logosFortuna-skill
claude plugin install logosFortuna-skill@logosFortuna --version <eski-surum>
```
