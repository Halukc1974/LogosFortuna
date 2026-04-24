# Skill Kesif Tablosu — Otomatik Orkestrasyon

## Amac

LogosFortuna-Skill her UDIV islemesinde ortamda yuklu skill'leri tarar ve goreve uygun olani **hibrit otomasyon** kurallariyla orkestre eder.

## Skill Tarama Mekanizmasi

### Nasil Calisir

1. **Kaynak**: Session `<system-reminder>` blogunda yer alan "available skills" listesi
2. **Tetik**: Faz 1'in ilk araç cagrisi olarak (memory'den once)
3. **Ekspress**: Her skill'in `name` ve `description` alanlari okunur
4. **Eslestirme**: Kullanici prompt'undaki anahtar kavramlarla semantik eslestirme

### Eslestirme Heuristikleri

```
Prompt icindeki kavramlar → Skill description'lari ile karsilastir
├── Dogrudan anahtar kelime eslesmesi (ornek: "frontend" → frontend-design)
├── Sinonim eslesmesi (ornek: "UI component" → ui-ux-pro-max, shadcn-ui)
├── Domain eslesmesi (ornek: "video" → remotion, "pdf" → pdf)
└── Negatif filter: SKILL.md'de "DO NOT TRIGGER" belirtilmisse ATLA
```

---

## Skill Siniflandirma: BASIT vs KARMASIK

Hibrit otomasyon icin her skill iki sinfa ayrilir:

### 🟢 BASIT (Otomatik Calistir + Bildir)

**Kriter**: Dusuk risk, geri donusu kolay, sadece icerik/format uretir, harici sistem degistirmez.

| Skill | Neden Basit |
|-------|-------------|
| `brand-guidelines` | Sadece stil uygular, mantik degistirmez |
| `theme-factory` | Tema onerisi, kod etkilemez |
| `doc-coauthoring` | Dokuman yazimi, geri alinabilir |
| `enhance-prompt` | Prompt iyilestirme, cikti metin |
| `keybindings-help` | Sadece rehberlik |
| `remotion-documentation` | Dokuman okuma |
| `simplify` | Kod sadelestirme ama ayri gozden gecirme var |
| `skills` (list) | Sadece listeleme |

### 🔴 KARMASIK (Kullaniciya Sor + Onay Bekle)

**Kriter**: Yuksek etki, mimari kararlar, harici sistemler, coklu dosya degisimi.

| Skill | Neden Karmasik |
|-------|----------------|
| `frontend-design` | Genis kapsamli UI uretir, mimari etki |
| `ui-ux-pro-max` | 161 palette/57 font — stil karari buyuk |
| `shadcn-ui` | Bagimlilik yukler, kurulum gerektirir |
| `react-components` | Vite/React altyapisi gerektirir |
| `stitch-design` | Harici Stitch MCP entegrasyonu |
| `stitch-loop` | Iteratif buyuk degisiklikler |
| `remotion` | Video render, maliyet |
| `mcp-builder` | MCP server insa, altyapi etki |
| `claude-api` | API kodu yazimi, model secimi |
| `agent-sdk-dev:new-sdk-app` | Tum proje iskeleti kurar |
| `plugin-dev:create-plugin` | Plugin olusturma |
| `commit-commands:commit-push-pr` | GIT PUSH + PR — geri donusu zor |
| `security-review` | Inceleme ama geniş rapor |
| `review` | PR inceleme kapsami buyuk |
| `webapp-testing` | Browser baslatir, port kullanir |
| `pptx`, `docx`, `xlsx`, `pdf` | Dosya uretimi, format bagimli |
| `algorithmic-art`, `canvas-design` | Yaratici karar |
| `skill-creator` | Yeni skill olusturma |

### 🟡 BILINMIYOR (Guvenli Varsayim: KARMASIK)

Tablo'da listelenmemis **yeni veya user-installed** skill'ler guvenlik icin KARMASIK varsayilir ve kullaniciya sorulur.

---

## Karar Akisi

```
Kullanici prompt'u → Faz 1 baslar
│
├── [1] Ortamdaki skill listesi okunur (system-reminder)
│
├── [2] Prompt'tan anahtar kavramlar cikarilir
│
├── [3] Eslestirme
│   ├── Eslesme yok → Normal UDIV, skill'siz devam
│   ├── 1 eslesme → [4]'e git
│   └── 2+ eslesme → Kullaniciya multi-select sun
│
├── [4] Skill sinif kontrolu
│   ├── BASIT → Otomatik dahil et, bildir
│   │   "ℹ️ '<skill>' otomatik kullaniliyor"
│   │
│   └── KARMASIK → Kullaniciya sor (AskUserQuestion)
│       "Eslesen skill: '<skill>' — '<description>'"
│       "Kullanilsin mi?"
│       ├── Evet → Skill dahil edilir
│       └── Hayir → Normal UDIV devam
│
└── [5] Eger dahil edildiyse: Faz 3 UYGULA fazinda skill'in
        kendi Skill tool ile cagirilmasi icin prompt hazirlanir
        (bkz. prompt-enrichment.md "Skill-Aware Context Injection")
```

---

## Eslestirme Ornekleri

### Ornek 1: Basit eslesme

**Kullanici**: "Landing page tasarla"
**Eslesen**: `frontend-design` (KARMASIK) + `ui-ux-pro-max` (KARMASIK)
**Aksiyon**: Kullaniciya sor — 2 skill adayi var, hangisi?

### Ornek 2: Otomatik basit

**Kullanici**: "Bu metni Anthropic brand stiliyle formatla"
**Eslesen**: `brand-guidelines` (BASIT)
**Aksiyon**: Otomatik dahil edilir + bildirim

### Ornek 3: Eslesme yok

**Kullanici**: "Bu Python fonksiyonunun return type'ini degistir"
**Eslesen**: Yok
**Aksiyon**: Normal UDIV, skill delegasyonu yok

### Ornek 4: Coklu eslesme

**Kullanici**: "Slack icin GIF olustur ve Anthropic brand kullan"
**Eslesen**: `slack-gif-creator` (KARMASIK) + `brand-guidelines` (BASIT)
**Aksiyon**: 
- `brand-guidelines` otomatik dahil (basit)
- `slack-gif-creator` icin onay sor (karmasik)

---

## Yeni Skill Ekleme Politikasi

Ortam degistiginde (yeni plugin yuklendiginde):
1. Bu tablo **manuel guncellenir** (su an otomatik guncellemez)
2. Yeni skill tablo'da yoksa varsayilan KARMASIK
3. Kullanici bir skill'i "basit" olarak isaretleyebilir (yasin: MEMORY.md'de not tutulur)

**Memory entegrasyonu**:
```
mcp__memory__create_entities → "skill_siniflandirma"
  observations:
    - "ui-ux-pro-max: KARMASIK (kullanici boyle istedi)"
    - "my-custom-skill: BASIT (deneyimden ogrenilmis)"
```

---

## Constitution Uyumu

| Madde | Uyum |
|-------|------|
| 1. Understand before changing | Skill tespiti FAZ 1'de, anlama ONCE |
| 2. Small, verifiable increments | Her skill eklemesi ayri degerlendirilir |
| 6. Explicit fallback behavior | Eslesme yoksa normal UDIV fallback |
| 7. Preserve operator control | KARMASIK skill'ler kullanici onayi ister |
