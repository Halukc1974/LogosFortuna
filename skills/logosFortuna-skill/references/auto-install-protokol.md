# Otomatik Plugin/MCP Kurulum Protokolu — Onayli-Otomatik

## Amac

LogosFortuna-Skill, gorev sirasinda eksik bir plugin veya MCP server tespit ederse kullaniciya onay sorarak kurulumu otomatik tetikler. Bu belge, kullanicinin sectiği **"Onayli-Otomatik"** politikasinin uygulamasidir.

## Tasarim Prensipleri

1. **Hicbir kurulum kullanici onayi olmadan yapilmaz** — `AskUserQuestion` zorunlu
2. **Her teklif gerekce icerir** — "Niye gerekli?" sorusuna 1-2 cumlede cevap
3. **Resmi marketplace tercih edilir** — `claude-plugins-official` once aranir
4. **Geri alinabilir** — kurulum sonrasi `claude plugin uninstall` ile temizlenir
5. **Sessionda 1 kez sor** — ayni eksik tekrar tespit edilirse oturum sonuna kadar tekrar sorma

## Karar Akisi

```
Faz 1 ANLA: gorev analiz edildi
│
├── [1] Gerekli yetenekler tespit et
│     ornek: "Slack mesaj gonder" → mcp__slack__* gerekli
│            "Postgres sorgu yaz" → mcp__postgres__* gerekli
│            "Figma'dan komponent" → figma plugin gerekli
│
├── [2] Mevcut ortamla karsilastir
│     Bash: claude plugin list 2>/dev/null
│     Bash: ls ~/.claude/plugins/installed_plugins.json (eger var)
│     System-reminder: yuklu skill listesi
│
├── [3] Eksik tespit edildi
│     ├── Kullaniciya AskUserQuestion ile sor:
│     │     "Bu gorev icin '<plugin>' gerekli. Kuralim mi?"
│     │     Secenekler: Evet (kur) | Hayir (manuel devam) | Atla (kullanma)
│     │
│     ├── EVET → Bash:
│     │     claude plugin install <name>@claude-plugins-official --scope user
│     │     (Eger MCP ise: claude mcp add ... daha uygundur)
│     │
│     ├── HAYIR → Kurmuyoruz, fallback ile devam:
│     │     "<plugin> kurulmadi. <fallback-tool> ile devam ediyorum."
│     │
│     └── ATLA → Bu yetenegi gerektiren adimi atla
│
└── [4] Kurulum sonrasi
      Bash: /reload-plugins (Claude Code'a aktif et)
      Memory'e kaydet: "kullanici '<plugin>' kurmayi onayladi"
```

## MCP Kurulum: `claude mcp add` Komutu

MCP server'lar plugin **degil**, ayri bir CLI komutuyla yonetilir:

```bash
# Genel format
claude mcp add <server-name> <command-or-package>

# Memory MCP ornegi
claude mcp add memory "npx -y @modelcontextprotocol/server-memory"

# Sequential thinking
claude mcp add sequential-thinking "npx -y @modelcontextprotocol/server-sequential-thinking"

# Brave Search (API key gerekli)
claude mcp add brave-search "npx -y @modelcontextprotocol/server-brave-search" \
  --env BRAVE_API_KEY="$BRAVE_API_KEY"

# Project-scope kurulum (.mcp.json'a yazar)
claude mcp add --scope project <server> <command>
```

Sonra `/reload-plugins` veya yeni oturum acmasi gerekir.

## Plugin Kurulum: `claude plugin install` Komutu

```bash
# Onerilen marketplace'ten kurulum
claude plugin install <plugin-name>@claude-plugins-official

# Belirli scope
claude plugin install <plugin-name>@<marketplace> --scope user|project|local

# Marketplace henuz kayitli degilse once:
claude plugin marketplace add <owner>/<repo>
```

## Detect-Then-Suggest: Tipik Senaryolar

### Senaryo 1: Slack mesaj gonderme

**Algilanan**: kullanici "Slack'e ozet gonder" dedi
**Eksik**: `mcp__slack__*` araclari sessionda yok
**Aksiyon**:
```
AskUserQuestion: "Slack MCP gerekli. Kuralim mi?"
├── Evet → Bash:
│   claude plugin install slack@claude-plugins-official --scope user
│   /reload-plugins
│   memory.add: "slack plugin: kullanici kabul etti"
└── Hayir → "Slack'siz devam — sana metin uretirim, sen kopyala-yapistir"
```

### Senaryo 2: Postgres sorgu

**Algilanan**: "users tablosunda kayit say"
**Eksik**: `mcp__postgres__query` yok
**Aksiyon**:
```
AskUserQuestion: "Postgres MCP gerekli. Hangisi?"
├── Resmi (db credential ister) → claude mcp add postgres "..." + userConfig prompt
├── Skip → Kullaniciya: "DB credential paylas, ben curl ile cagiririm"
└── Iptal → Gorevi sorgu metni uretmekle sinirla
```

### Senaryo 3: Figma'dan komponent

**Algilanan**: "Figma dosyamdan React komponent uret"
**Eksik**: figma plugin yok
**Aksiyon**: AskUserQuestion → claude plugin install figma@claude-plugins-official

## Beyaz Liste (Whitelist Modu)

Kullanici `auto_install_policy = "whitelist"` secerse asagidaki MCP'ler ONAYSIZ kurulur:

| MCP | Neden Beyaz Listede |
|-----|--------------------|
| memory | Anthropic resmi, hicbir credential gerektirmez |
| sequential-thinking | Anthropic resmi, hicbir credential gerektirmez |
| fetch | Anthropic resmi, sadece HTTP GET |

Beyaz liste **disindaki** her sey hala AskUserQuestion gerektirir.

## Otonom (Autonomous) Modu

`auto_install_policy = "autonomous"` durumunda **TUM** kurulumlar sormadan yapilir. Kullanici bu modu actiginda asagidaki uyari bir kez gosterilir:

```
UYARI: Otonom mod aktif. LogosFortuna-Skill, gorev sirasinda gerekli gordugu
plugin/MCP'leri sormadan kuracak. Bu, suuru indirme + RCE riski tasiyabilir.
Onayliyor musunuz? (evet/hayir)
```

## Telemetri ve Geri Bildirim

Her kurulum onerisi loglanir (`telemetry_enabled = true` ise):

```jsonl
{
  "ts": "2026-05-12T13:55:00Z",
  "event": "install_proposal",
  "plugin": "slack@claude-plugins-official",
  "trigger_phrase": "Slack'e ozet gonder",
  "user_response": "accepted",
  "install_succeeded": true,
  "fallback_used": null
}
```

Bu sayede:
- Hangi plugin onerileri en cok kabul ediliyor (mevcut workflow'a uygun)
- Hangi reddediliyor (gereksiz oneri, kullanici tercih etmiyor)
- Hangi kurulum hata veriyor (marketplace sorunu, paket sorunu)

## Iptal Senaryolari

Kurulum sirasinda hata olursa:

```
Bash exit code != 0
├── Marketplace bulunamadi → Bash: claude plugin marketplace update <name> + tekrar dene
├── Plugin ismi yanlis → AskUserQuestion ile alternatif oner
├── Network hatasi → Kullaniciya bildir, manuel kurulum komutu sun
└── Permission denied → "Lutfen kendi makinanizda calistirin:" + komut goster
```

## Constitution Uyumu

| Madde | Uyum |
|-------|------|
| 1. Understand before changing | Eksik tespiti Faz 1'de yapilir |
| 6. Explicit fallback behavior | Reddedildiginde fallback aciktir |
| 7. Preserve operator control | Onayli-Otomatik her zaman onay alir |
| 8. Iddia uyumu | Kurulum basarisi/basarisizligi raporlanir |

## Iliskili Belgeler

- [Skill Kesif Tablosu](./skill-kesif-tablosu.md) — yuklu skill'leri tarama
- [Arac Orkestrasyon](./arac-orkestrasyon.md) — fallback tablosu
- [Kaynak Guven Skorlama](./kaynak-guven-skorlama.md) — marketplace guvenilirligi
