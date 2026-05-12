---
description: UDIV telemetri ozeti - son N gun icinde hangi fazlar/agentlar nasil performans gosterdi
argument-hint: "[gun-sayisi (default 7)]"
allowed-tools: Bash, Read
---

# LogosFortuna Telemetri Raporu

Son `${1:-7}` gunun UDIV dongusu telemetri verilerini ozetler.

## Adimlar

1. Telemetry-writer.py'yi summarize modunda calistir:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/telemetry-writer.py" summarize --days ${1:-7}
```

2. Ciktiyi yorumla:
   - **events_by_type**: hangi event en sik tetikleniyor (faz tamamlama vs geri donus orani)
   - **phase_avg_duration_ms**: hangi faz en uzun suruyor (botlenec analizi)
   - **install_proposal vs install_executed orani**: oneri kabul orani
   - **mcp_need_detected sikligi**: hangi MCP'ler en cok eksik

3. Kullaniciya rapor sun (Markdown table formatinda):

```
## UDIV Telemetri Ozeti (Son 7 Gun)

### Faz Dagilimi
| Faz | Ortalama Sure | Tamamlanma | Geri Donus |
|-----|---------------|------------|------------|
| FAZ_1 | 12.3s | 45 | 2 |
| FAZ_2 | 8.1s | 43 | 5 |
| FAZ_3 | 34.5s | 41 | 8 |
| FAZ_4 | 15.2s | 40 | 1 |

### Auto-Install Performansi
- Toplam oneri: 12
- Kabul edilen: 9 (%75)
- Reddedilen: 3
- Basarisiz kurulum: 0

### En Sik Eksik MCP'ler
1. mcp__slack__* (5 kez)
2. mcp__postgres__* (3 kez)
3. mcp__brave-search__* (2 kez)

### Oneriler
- FAZ_3 ortalama 34.5s → en yavas faz, artim boyutu fazla olabilir
- Auto-install kabul orani %75 → onerilerin cogu degerli
- Slack en sik istenen MCP → kalici kurulum dusunulebilir
```

4. Eger telemetri verisi yoksa:

```
## Telemetri Verisi Yok

Henuz UDIV dongusu kosmamis veya `telemetry_enabled = false`.

Telemetriyi acmak icin:
1. plugin.json'da `telemetry_enabled: true` (default)
2. /lf komutu ile en az 1 UDIV dongusu calistir
3. .specify/telemetry/ dizini olusur
```

## Notlar

- Tum veri lokal kalir (`.specify/telemetry/udiv-runs-*.jsonl`)
- Hicbir veri Anthropic'e veya disariya gonderilmez
- Sessiz mod: `--quiet` ile sadece JSON ciktisi alinabilir
