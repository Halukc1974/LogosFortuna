# Kaynak Guven Skorlama Sistemi

## Amac

Web search ile zenginlestirme yapilirken her kaynagin **guven skoru** (0-100) hesaplanir. Yuksek skorlu kaynaklar otomatik dahil edilir, dusuk skorlular dislanir, orta skorlular kullaniciya danisilir.

## Skor Kategorileri

| Skor | Kategori | Aksiyon |
|------|----------|---------|
| **90-100** | Otorite | ✅ Otomatik dahil et |
| **70-89** | Guvenilir | ⚠️ Kullaniciya sor, "Dahil edilsin mi?" |
| **50-69** | Supheli | ℹ️ Sadece metadata olarak not et, icerik dahil etme |
| **0-49** | Kotu | ❌ Tamamen disla, ignorelist'e ekle |

---

## Domain Skor Tablosu

### 🟢 Skor 95-100 (Resmi Otoriteler)

| Domain | Skor | Neden |
|--------|------|-------|
| `docs.anthropic.com` | 100 | Resmi Anthropic dokumani |
| `www.anthropic.com` | 98 | Resmi Anthropic web sitesi |
| `claude.ai/docs` | 98 | Resmi Claude dokumantasyonu |
| `github.com/anthropics` | 95 | Resmi Anthropic GitHub kurulusu |
| `python.org`, `nodejs.org`, `rust-lang.org` | 95 | Dil resmi dokumanlari |
| `developer.mozilla.org` (MDN) | 95 | Web standartlari |

### 🟢 Skor 85-94 (Genel Otoriteler)

| Domain | Skor | Neden |
|--------|------|-------|
| `docs.*` (herhangi bir urun resmi docs) | 90 | Genel resmi docs kalibi |
| `www.w3.org`, `whatwg.org` | 92 | Web standartlari |
| `tc39.es` | 90 | ECMAScript standartlari |
| `reactjs.org`, `vuejs.org`, `angular.io` | 90 | Framework resmi docs |
| `docs.github.com` | 90 | GitHub platform docs |
| `kubernetes.io`, `docker.com/docs` | 88 | Altyapi resmi docs |
| `pypi.org`, `npmjs.com` (paket sayfasi) | 85 | Paket kaydi, gerçekçi ama `README` icerigine bakilir |

### 🟡 Skor 70-84 (Guvenilir ama Dogrulama Gerekir)

| Domain | Skor | Neden |
|--------|------|-------|
| `stackoverflow.com` (kabul edilmis cevap + >50 oy) | 80 | Topluluk onayli |
| `github.com/<buyuk-proje>` (issue/PR icindeki acıklamalar) | 78 | Dogrudan proje icinde ama bazen yanlis |
| `dev.to` (yazar verified + makale okuma >10k) | 75 | Iyi yazarlar var ama varyasyon yuksek |
| `medium.com/@<resmi-org>` | 72 | Firma makaleleri ama guncel degildir bazen |
| `stackoverflow.com` (sıradan cevap) | 70 | Eski/yanlis olabilir |

### 🟠 Skor 50-69 (Supheli)

| Domain | Skor | Neden |
|--------|------|-------|
| `medium.com/@<bireysel-yazar>` | 60 | Kalite cok degisken |
| `dev.to` (sıradan makale) | 55 | Iyi olanlar var ama filtrelenmiyor |
| `geeksforgeeks.org` | 55 | Teknik ama hatali/eski icerik yaygin |
| `tutorialspoint.com`, `w3schools.com` | 50 | Basic'e iyi, ileri seviyede hatali |
| Kisisel blog (tanimli yazar) | 50 | Yazara gore degisir |

### 🔴 Skor 0-49 (Disla)

| Domain Tipi | Skor | Neden |
|-------------|------|-------|
| Isimsiz blog | 30 | Sorumluluk yok |
| Reddit (thread, onaylanmamis) | 40 | Spekulatif, yanlis olabilir |
| Quora | 35 | Kalite kontrolü yok |
| `pinterest.com`, sosyal medya | 20 | Teknik icin uygun degil |
| Spam/SEO farm siteleri | 10 | Yanlis bilgi riski |
| Yapay zeka ile uretilmis icerik farmlari | 10 | Hallucinasyon kaynagi |

---

## Dinamik Skor Duzeltmeleri

Temel domain skoruna asagidaki duzeltmeler uygulanir:

### Artiranlar

| Kriter | +Skor |
|--------|-------|
| URL'de `/docs/` veya `/documentation/` | +5 |
| Sayfada tarih yaziyor ve son 12 ay | +5 |
| Yazar "verified" veya "staff" rozeti var | +3 |
| Sayfa uzerindeki community onayi (vote/star) yuksek | +3 |
| Referanslar ve kaynaklar listeli | +2 |

### Azaltanlar

| Kriter | -Skor |
|--------|-------|
| Sayfa tarihi > 3 yil eski | -15 |
| Sayfa tarihi > 5 yil eski VE teknik icerik | -25 |
| "AI generated" disclaimer var | -20 |
| Reklam yogunlugu >50% | -10 |
| Dogrulanamayan iddialar (kaynak yok) | -10 |
| Yaniltici baslik (clickbait) | -15 |

---

## Anthropic Ozel Kuralı

Kullanicinin ozel istegi (24 Nisan 2026):

> "yuksek guven skorlu kaynaklar (orn. >=90/100 ve Anthropic resmi) otomatik olarak eklenerek devam edelim"

Bu nedenle:
1. **Anthropic resmi kaynaklari** (docs.anthropic.com, www.anthropic.com, github.com/anthropics) **daima >=95 skor** alir
2. Claude/Anthropic ile ilgili herhangi bir gorevde Anthropic kaynaklari **oncelikli** aranir
3. Dinamik skor duzeltmeleri bu kaynaklara uygulanmaz (minimum skor 95 korunur)

---

## Uygulama Akisi

```
Web search sonuclari geldi → her sonuc icin:
│
├── [1] Domain ayikla
│
├── [2] Tablodan temel skor bul
│   └── Tablo'da yoksa: varsayilan 50 (supheli)
│
├── [3] Dinamik duzeltmeleri uygula
│   └── Final skor = max(0, min(100, temel + duzeltmeler))
│
├── [4] Kategoriye gore aksiyon:
│   ├── >=90 → ✅ Otomatik dahil, enrichment contextine ekle
│   ├── 70-89 → ⚠️ Listele, kullaniciya sor
│   ├── 50-69 → ℹ️ Sadece URL bildirim olarak goster
│   └── <50 → ❌ Sessizce disla
│
└── [5] Kullaniciya rapor:
    "Web enrichment: X otorite + Y supheli bulundu"
    "Otomatik dahil: [Kaynak 1 (95)], [Kaynak 2 (90)]"
```

---

## Raporlama Formati

Her web enrichment sonrasi kullaniciya ozet sunulur:

```markdown
## Web Enrichment Raporu

**Aranan**: "react dashboard 2026"

**Otorite kaynaklar (>=90, otomatik dahil edildi):**
- [react.dev/learn/dashboard] (95) — Resmi React docs
- [docs.anthropic.com/example-dashboard] (100) — Anthropic Claude ornekleri

**Guvenilir kaynaklar (70-89, onay icin):**
- [dev.to/verified-author/react-dashboard-2026] (82) — dahil edilsin mi?

**Dislanan (<70):**
- 3 sonuc kalite yetersizliginden dislandi

**Toplam enrichment katkisi**: 2 kaynak, ~340 kelime eklendi
```

---

## Cache ve Performans

Ayni sorgu 24 saat icinde tekrar yapildiginda cache'den getirilir:
- Cache key: SHA256(query + date_bucket)
- TTL: 24 saat (Anthropic docs gibi stabil kaynaklar icin)
- Gorev-spesifik cache (kullanicilar arasi paylasilmaz)

---

## Constitution Uyumu

| Madde | Uyum |
|-------|------|
| 3. Keep claims aligned | Trust scoring, yanlis iddia onler |
| 6. Explicit fallback | Dusuk skor = sessizce atlanmaz, raporlanir |
| 7. Preserve operator control | 70-89 skorlar kullaniciya sorulur |

**Quality Gate**: Enrichment'a dahil edilen tum kaynaklar trust >=90 OR kullanici onayli olmalidir. Skor dokumantasyon disinda raporlanir (guven limitleri iddia edildiginde).
