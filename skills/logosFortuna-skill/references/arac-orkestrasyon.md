# Arac Orkestrasyon Rehberi

## Amac

Bu belge, LogosFortuna-Skill'in hangi durumda hangi araci kullanacagini tanimlar. Dogru arac secimi, hem hiz hem de kalite icin kritiktir.

---

## MCP Tool Secim Matrisi

### Bilgi Kaliciligi → Memory MCP

| Arac | Ne Zaman |
|------|----------|
| `mcp__memory__read_graph` | Oturum basinda tum bilgi grafini yuklemek |
| `mcp__memory__search_nodes` | Spesifik bir konu/alan hakkinda onceki bilgileri aramak |
| `mcp__memory__create_entities` | Yeni bilgi birimlerini (proje, tercih, karar) kaydetmek |
| `mcp__memory__add_observations` | Mevcut entity'lere yeni gozlemler eklemek |
| `mcp__memory__create_relations` | Entity'ler arasi iliskileri tanimlamak |
| `mcp__memory__open_nodes` | Belirli entity'lerin detaylarini gormek |

**Entity Tipleri:**
- `kullanici_tercihi` — Kullanicinin calisma tercihleri
- `proje_kalibi` — Projede kesfedilen kaliplar
- `karar_kaydi` — Alinan tasarim/mimari kararlar
- `alan_bilgisi` — Spesifik alan/modul hakkinda bilgi

**Relation Tipleri:**
- `UYGULANIR` — tercih → proje/alan
- `SONUCLANDI` — karar → cikti
- `ICINDE_BULUNDU` — kalip → dosya/modul
- `BAGIMLI` — modul → modul

### Karmasik Akil Yurutme → Sequential Thinking MCP

| Durum | Kullanim |
|-------|----------|
| Belirsiz kullanici istegi | Adim adim niyeti cozumle |
| Birden fazla yaklasim | Trade-off analizini yapilandir |
| Karmasik bagimliliklar | Etki zincirini haritalandir |
| Constitution uyum kontrolu | Her prensibi sirayla degerlendir |

**Ne Zaman KULLANMA:**
- Basit, tek dosya degisiklikleri
- Acik ve net kullanici istekleri
- Tekrarli/sablonlu islemler

### Harici Bilgi → Arama Araclari

| Arac | Ne Zaman |
|------|----------|
| `mcp__brave-search__brave_web_search` | Teknoloji/kutuphane arastirmasi |
| `WebSearch` | Genel web aramasl |
| `WebFetch` | Belirli bir URL'den bilgi cekmek |
| `mcp__fetch__fetch` | API dokumantasyonu okumak |

**Siralama**: Once proje icinde ara (Grep/Glob) → bulamazsan memory'de ara → bulamazsan web'de ara

### GitHub Islemleri → GitHub MCP

| Arac | Ne Zaman |
|------|----------|
| `mcp__github__create_pull_request` | PR olusturma |
| `mcp__github__create_issue` | Issue olusturma |
| `mcp__github__list_issues` | Mevcut issue'lari kontrol |
| `mcp__github__get_pull_request` | PR detaylarini okuma |

**Kural**: GitHub MCP'yi sadece kullanici acikca istediginde veya UDIV Faz 4'te cikti olarak kullan.

---

## Dahili Tool Secim Kurallari

### Dosya Islemleri

| Islem | Dogru Arac | YANLIS Arac |
|-------|-----------|-------------|
| Dosya okuma | `Read` | `cat`, `head`, `tail` |
| Dosya duzenleme | `Edit` | `sed`, `awk` |
| Dosya olusturma | `Write` | `echo >`, `cat <<EOF` |
| Dosya arama (isim) | `Glob` | `find`, `ls` |
| Icerik arama | `Grep` | `grep`, `rg` |

### Shell Islemleri (Bash)

Bash SADECE su durumlarda kullan:
- Test calistirma (`pytest`, `npm test`)
- Lint/format (`ruff`, `eslint`, `prettier`)
- Git islemleri (`git status`, `git log`, `git diff`)
- Build islemleri (`npm run build`, `pip install`)
- Sistem komutlari (`mkdir`, `ls` dizin icin)

### Agent vs Dogrudan Tool

```
Gorev karmasikligi?
├── Basit (tek dosya, bilinen konum) → Dogrudan tool (Read, Grep, Glob)
├── Orta (birden fazla dosya, bilinen alan) → 1 Explore agent
├── Karmasik (belirsiz kapsam, coklu alan) → 2-3 paralel Explore agent
└── Cok karmasik (mimari degisiklik) → Plan agent + Explore agent'lar
```

---

## Faz Bazli Arac Kullanimi

### Faz 1 (ANLA) Araclari
- `mcp__memory__search_nodes` — onceki bilgi
- `Read` — CLAUDE.md, constitution.md
- `Explore` agent — kod kesfetme
- `Grep`/`Glob` — spesifik arama
- `mcp__sequential-thinking__sequentialthinking` — karmasik akil yurutme
- `AskUserQuestion` — belirsizlik giderme

### Faz 2 (TASARLA) Araclari
- `mcp__sequential-thinking__sequentialthinking` — yaklasim karsilastirma
- `Read` — referans dosyalari okuma
- `mcp__memory__search_nodes` — gecmis kararlar

### Faz 3 (UYGULA) Araclari
- `Write`/`Edit` — kod degisiklikleri
- `Bash` — test, lint, build
- `Read` — dogrulama icin dosya okuma
- `TaskCreate`/`TaskUpdate` — ilerleme takibi

### Faz 4 (DOGRULA ve OGREN) Araclari
- `Bash` — test, lint calistirma
- `Read`/`Grep` — constitution kontrolu
- `mcp__memory__create_entities` — bilgi kaydi
- `mcp__memory__add_observations` — gozlem ekleme
- `mcp__memory__create_relations` — iliski tanimlama

---

## Paralel vs Sirali Calistirma

**Paralel calistir:**
- Birbirinden bagimsiz dosya okumalari
- Farkli alanlarda Explore agent'lar
- Bagimsiz test calistirmalari

**Sirali calistir:**
- Bir dosyanin ciktisi digerinin girdisi ise
- Edit'ten sonra dogrulama
- Faz gecisleri (her zaman sirali)

---

## Hata Durumunda Arac Degistirme

```
Arac basarisiz oldu
├── MCP timeout → Dahili alternatife gec
│   (memory MCP → dosya bazli memory)
│   (fetch MCP → WebFetch)
├── Tool izin reddedildi → Kullaniciya neden gerektigini acikla
├── Bos sonuc → Arama terimlerini genislet veya farkli arac dene
└── Hata mesaji → Hataya ozel cozum uygula
```
