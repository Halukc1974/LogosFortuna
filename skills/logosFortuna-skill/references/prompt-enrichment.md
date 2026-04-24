# Prompt Enrichment Protokolu

## Amac

Her UDIV dongusunde kullanici prompt'u, skill'lere ve agent'lere gonderilmeden **once** zenginlestirilir. Bu katman uc asamadan olusur:

1. **Default Suffix Injection** — her islemede sabit meta-prompt eklenir
2. **Skill-Aware Context Injection** — eslesen skill'lerin uzmanligi prompt'a katilir
3. **Web-Search-Based Enrichment** — guncel bilgi ve terminoloji ile zenginlestirme

---

## 1. Default Suffix (Her Islemde)

Asagidaki cumle her UDIV islemesinde otomatik eklenir:

```
Think step by step and challenge your own assumptions.
```

### Nerede Eklenir

| Konum | Eklenme Sekli |
|-------|--------------|
| Agent system prompt'u (anlama-ajansi, tasarim-ajansi, uygulama-ajansi, dogrulama-ajansi) | Prompt sonuna ek |
| Kullaniciya sunulan Anlama Ozeti | Son paragraf olarak degil, i**c** rehber olarak uygulanir |
| Sequential-thinking cagrilari | Ilk dusunme adimina ek |
| Karmasik karar noktalari (Faz 2 yaklasim degerlendirme, Faz 4 dogrulama) | Degerlendirme baslangicina ek |

### Nerede Eklenmez

- Basit tool cagrilarinda (Read, Grep, Glob) — gereksiz token
- Bash komutlarinda — anlamsiz
- Saf bilgi aktarim mesajlarinda (ilerleme raporu) — tekrar

### Onemli Kural

Suffix **Ingilizce** olarak eklenir cunku:
- LLM'lerin meta-prompt'lara Ingilizce'de daha iyi yanit vermesi belgelenmistir
- Cogu skill dokumantasyonu Ingilizce terimler kullanir
- Uluslararasi skill ekosistemi (ui-ux-pro-max, frontend-design vb.) Ingilizce yazilmis

---

## 2. Skill-Aware Context Injection

Skill tarama (bkz. [skill-kesif-tablosu.md](./skill-kesif-tablosu.md)) sonrasinda eslesen skill'in uzmanligi prompt'a entegre edilir.

### Entegrasyon Sablonu

```
[Kullanicinin orijinal istegi]

[Eger eslesen skill varsa]:
CONTEXT: Bu gorev icin projede yuklu olan "<skill-ismi>" skill'i uygun tespit edildi.
Skill tanimi: "<skill-description>"
Bu skill'in dokumantasyon kaliplarini ve terminolojisini takip et.

Think step by step and challenge your own assumptions.
```

### Hibrit Otomasyon Karar Akisi

```
Eslesen skill tespit edildi
├── Skill sinifi = BASIT (dusuk risk) → Otomatik entegre et + kullaniciya bildir
│   "ℹ️ '<skill>' skill'i otomatik kullaniliyor"
├── Skill sinifi = KARMASIK (yuksek etki) → Kullaniciya sor
│   "'<skill>' skill'i gorevle eslesiyor. Kullanilsin mi? [Evet/Hayir]"
└── Skill sinifi = BILINMIYOR → Varsayilan KARMASIK (guvenli taraf) → sor
```

---

## 3. Web-Search-Based Enrichment

Her UDIV islemesinde (basit gorevler dahil) web search ile prompt zenginlestirilir.

### Pipeline

```
1. Kullanici prompt'undan ANAHTAR KAVRAMLAR cikar (maks 3-5 kavram)
   Ornek: "React dashboard tasarla" → ["React", "dashboard", "2026 UI trends"]

2. Her kavram icin arama yap:
   - Birincil: mcp__brave-search__brave_web_search
   - Fallback: WebSearch tool
   - Fallback 2: Kullaniciya "web search kullanilamadi" bildir

3. Sonuclari GUVEN SKORU ile filtrele
   (bkz. [kaynak-guven-skorlama.md](./kaynak-guven-skorlama.md))

4. Otomatik dahil: >= 90 skor
   Onay sor: 70-89 skor
   Disla: < 70 skor

5. Zenginlestirilmis prompt'u olustur
```

### Zenginlestirilmis Prompt Formati

```
[ORIJINAL KULLANICI ISTEGI]

---

AUTO-ENRICHED CONTEXT (Trust Score >= 90):
- [Kaynak 1 — URL]: [Ozet 1-2 cumle]
- [Kaynak 2 — URL]: [Ozet 1-2 cumle]

DOMAIN TERMINOLOGY:
- [Tespit edilen 2026-guncel teknik terim 1]
- [Tespit edilen 2026-guncel teknik terim 2]

Think step by step and challenge your own assumptions.
```

### Budgeting

Web search **her islemede** yapilir ama maliyet kontrolu altinda:

| Gorev Tipi | Max Arama Sayisi | Max Sonuc/Arama |
|------------|------------------|-----------------|
| Basit (tek dosya, acik istek) | 1 | 3 |
| Orta (2-5 dosya) | 2 | 5 |
| Karmasik (mimari) | 3 | 7 |

Bu limit **Faz 1 araç limiti**ne (7'ye cikarildi) dahildir.

---

## Hata ve Fallback Senaryolari

### Web Search Basarisiz
```
mcp__brave-search__brave_web_search hata
├── Tekrar dene (1 kez)
│   └── Yine hata → WebSearch tool'a gec
│       └── Yine hata → Enrichment ATLAMA, kullaniciya bildir:
│           "ℹ️ Web enrichment kullanilamadi, memory + mevcut bilgiyle ilerliyorum"
```

### Default Suffix Ihtilaf
Eger kullanicinin orijinal prompt'u zaten "step by step" veya "challenge" iceriyorsa:
- Suffix eklenmez (tekrar onleme)
- Log'a not dusulur: "Suffix atlandi: kullanici promptu zaten iceriyor"

### Skill Eslesme Belirsizligi
Iki veya daha fazla skill ayni gorevle eslesiyorsa:
- Kullaniciya tum adaylar sunulur (multi-select)
- Kullanici 1 veya daha fazlasini secer
- Hepsi onay-gerektiren sinifa alinir (otomatik calismaz)

---

## Constitution Uyumu

Bu protokol asagidaki maddelerle uyumlu:

| Madde | Uyum |
|-------|------|
| 1. Understand before changing | Web enrichment "anlama"yi guclendirir |
| 2. Small, verifiable increments | Her enrichment adimi ayri dogrulanir |
| 3. Keep claims aligned | Trust scoring ile yanlis bilgi riski azalir |
| 6. Explicit fallback behavior | Web search icin 2 fallback tanimli |
| 7. Preserve operator control | Karmasik skill'ler icin onay zorunlu |

**Istisna**: Constitution Operational Defaults ("search locally first, then memory, then inform the user before external lookup") bu yeni ozellikle **bilincli olarak revize edilmistir**: Web enrichment artik OTOMATIK ve HER GOREVDE, ancak trust scoring ve fallback ile korunur.
