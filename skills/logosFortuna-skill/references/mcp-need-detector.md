# MCP Need-Detector — Faz 1 Eklentisi

## Amac

Faz 1'in baslangicinda kullanicinin gorevini analiz ederek **hangi MCP server'larin** veya **plugin'lerin** gerekli oldugunu tespit eder. Bulunan eksiklikler `auto-install-protokol`'a aktarilir.

## Tetik

Faz 1 ANLA basinda, "Baglam Yukle" adimindan once calisir:

```
Faz 1 ANLA
├── [a] Prompt Enrichment Pipeline
├── [b] MCP Need-Detector  ◄── BU BELGE
├── [c] Baglam Yukle (memory, CLAUDE.md, constitution)
├── [d] Derin Kesfetme
└── ...
```

## Algoritma

```
1. Kullanici prompt'undan ANAHTAR EYLEMLER cikar
   ornek: "Postgres'ten users tablosunu oku" 
          → eylemler: ["db_query", "sql"]

2. Eylem → MCP haritasini uygula (asagidaki tablo)

3. Her gerekli MCP icin:
   ├── system-reminder araclar listesinde var mi?
   │   ├── Evet → OK, devam
   │   └── Hayir → eksik listeye ekle
   
4. Eksik listesi varsa Faz 1 enrichment raporuna:
   "ℹ️ Bu gorev icin gerekli MCP'ler eksik: [liste]"
   "Onayli-Otomatik politika ile kurulum onerebilir miyim?"

5. Kullanici onaylarsa → auto-install-protokol.md akisini calistir
```

## Eylem → MCP Haritasi

### Veri ve Bilgi

| Anahtar Eylem | Gerekli MCP | Marketplace |
|---------------|-------------|-------------|
| db_query, sql, postgres | `mcp__postgres__query` | `postgres@claude-plugins-official` |
| veri tablosu, csv, excel | `xlsx` skill | builtin |
| web fetch, scraping | `mcp__fetch__fetch` veya `WebFetch` | builtin |
| web search, guncel bilgi | `mcp__brave-search__brave_web_search` | `brave-search@claude-plugins-official` |
| dokuman oku PDF | `pdf` skill | builtin |

### Iletisim ve Bildirim

| Anahtar Eylem | Gerekli MCP | Marketplace |
|---------------|-------------|-------------|
| slack mesaj | `mcp__slack__*` | `slack@claude-plugins-official` |
| discord | yok (custom MCP gerekli) | manuel |
| email gonder | yok (SMTP MCP gerekli) | manuel |
| github issue/PR | `mcp__github__*` veya `gh` CLI | `github@claude-plugins-official` |

### Geliştirme ve Yapi

| Anahtar Eylem | Gerekli MCP | Marketplace |
|---------------|-------------|-------------|
| jira/atlassian | `mcp__atlassian__*` | `atlassian@claude-plugins-official` |
| linear ticket | `mcp__linear__*` | `linear@claude-plugins-official` |
| notion sayfa | `mcp__notion__*` | `notion@claude-plugins-official` |
| figma tasarim | `mcp__figma__*` | `figma@claude-plugins-official` |
| sentry hata | `mcp__sentry__*` | `sentry@claude-plugins-official` |

### Altyapi ve Dağitim

| Anahtar Eylem | Gerekli MCP | Marketplace |
|---------------|-------------|-------------|
| vercel deploy | `mcp__vercel__*` | `vercel@claude-plugins-official` |
| firebase | `mcp__firebase__*` | `firebase@claude-plugins-official` |
| supabase | `mcp__supabase__*` | `supabase@claude-plugins-official` |
| aws | `mcp__aws-*__*` | `aws-core@claude-plugins-official` |

### Akil Yurutme ve Hafiza

| Anahtar Eylem | Gerekli MCP | Marketplace |
|---------------|-------------|-------------|
| onceki kararlari hatirla | `mcp__memory__*` | memory (npm/claude mcp add) |
| coklu adim karmasik | `mcp__sequential-thinking__sequentialthinking` | sequential-thinking |

### Tasarim ve UI

| Anahtar Eylem | Gerekli MCP | Skill |
|---------------|-------------|-------|
| react/vue komponent | yok | `frontend-design` skill |
| stitch tasarim | `mcp__stitch__*` | stitch (custom marketplace) |
| shadcn-ui | yok | `shadcn-ui` skill |

## Anahtar Eylem Ayiklama Heuristikleri

```
Kullanici prompt'u: "Postgres'ten son 10 kullaniciyi cek, Slack'e ozet gonder"

Adim 1: NLP analizi (kelime cikarma)
  → kelimeler: [postgres, kullanici, cek, slack, ozet, gonder]

Adim 2: Eylem isaretleyici sozluk
  postgres → db_query
  cek + db → sql query
  slack + gonder → slack_message
  ozet → text_generation (yerel, MCP gerekmez)

Adim 3: Gerekli MCP'ler
  ├── mcp__postgres__query ← EKSIK (varsayim)
  └── mcp__slack__* ← EKSIK (varsayim)

Adim 4: Rapor
  "Bu gorev 2 MCP gerektiriyor: postgres, slack"
```

## Kalipsiz Talepler

Kullanici acik bir MCP gerektirici eylem dile getirmiyorsa Need-Detector **HICBIR** oneri yapmaz. Ornekler:

| Prompt | MCP Onerisi |
|--------|-------------|
| "Bu fonksiyonu refactor et" | YOK (sadece dosya islemi) |
| "Tests yaz" | YOK |
| "README guncelle" | YOK |
| "Belirsiz, ne yapsam?" | YOK (anlama gerektirir, MCP degil) |

## False Positive Onleme

Detector kati olmali, **gereksiz oneri yapmamali**:

| Sahte Tetik | Niye Yanlis |
|-------------|-------------|
| "user" kelimesi → veri tabani | Kod icindeki "user variable" olabilir |
| "post" kelimesi → blog | HTTP POST request olabilir |
| "send" → email/slack | Verikodu icin "send signal" olabilir |

**Kural**: 2+ destekleyici keyword olmadan MCP onerme.

## Telemetri

Her detection sonucu loglanir:

```jsonl
{
  "ts": "...",
  "event": "mcp_need_detected",
  "prompt": "<truncated>",
  "needs": ["postgres", "slack"],
  "user_decision": "install_postgres,skip_slack",
  "outcome": "task_completed_with_partial_mcps"
}
```

## Hibrit Otomasyon Karari

| Politika | Davranis |
|----------|----------|
| `approved-auto` | Her eksik MCP icin AskUserQuestion |
| `autonomous` | Eksikleri otomatik kur (uyari + onay 1 kez bastan alinir) |
| `whitelist` | Sadece beyaz liste otomatik, digerleri AskUserQuestion |
| `suggest-only` | Asla kurma, sadece "manuel komut" goster |

## Iliskili Belgeler

- [Auto-Install Protokol](./auto-install-protokol.md)
- [Skill Kesif Tablosu](./skill-kesif-tablosu.md)
- [Arac Orkestrasyon Fallback](./arac-orkestrasyon.md)
