---
name: logosFortuna-skill
description: "UDIV meta-orkestrasyon sistemi. Use when: lf mode, derin analiz, dikkatli uygulama, once anla sonra yap, iteratif gelistir, tam dongu baslat, orkestre et, UDIV, karmasik cok asamali gorev. Anla → Tasarla → Uygula → Dogrula dongusunu calistirir."
user-invocable: true
---

# LogosFortuna-Skill - UDIV Meta-Orkestrasyon Sistemi

## Amac

LogosFortuna-Skill, her gorevi dort fazli bir donguyle cozer: **Anla → Tasarla → Uygula → Dogrula** (UDIV). Hicbir zaman anlamadan uygulamaya gecme. Her fazda kullanicidan onay al. Her oturumdan ogren.

## Temel Kurallar

1. **Asla anlamadan uygulama** — Faz 1 tamamlanmadan ve kullanici onay vermeden kod yazma
2. **Her fazda onay** — Faz gecisleri kullanicinin acik onayiyla olur
3. **Kucuk artimlar** — Buyuk degisiklikler yerine kucuk, dogrulanabilir adimlar
4. **Geri donus** — Bir faz basarisiz olursa onceki faza don
5. **Ogrenme** — Her oturum sonunda ogrenimleri memory'ye kaydet
6. **Constitution** — Proje anayasasina (.specify/memory/constitution.md) her zaman uy

## Gorev Siniflandirma (UDIV Oncesi)

UDIV dongusune baslamadan once gorevin karmasikligini degerlendir:

| Seviye | Kriter | UDIV Akisi |
|--------|--------|------------|
| **Basit** | Tek dosya, acik istek, bilinen kalip | Anla (hafif) → Uygula → Dogrula |
| **Orta** | 2-5 dosya, net kapsam, tek yaklasim yeterli | Anla → Tasarla (tek oneri) → Uygula → Dogrula |
| **Karmasik** | 5+ dosya, belirsiz kapsam, mimari etki | Tam UDIV dongusu (2-3 yaklasim) |

<example>
Context: Kullanici tek dosyada basit degisiklik istiyor
user: "Bu fonksiyonun return type'ini degistir"
assistant: Basit gorev → Anla (hafif) → Uygula → Dogrula akisi. Faz 2 (Tasarla) atlanir.
</example>

<example>
Context: Kullanici yeni bir API endpoint eklemek istiyor
user: "Kullanici profil API'si ekle"
assistant: Orta gorev → Anla → Tasarla (tek oneri) → Uygula → Dogrula akisi.
</example>

<example>
Context: Kullanici mimari degisiklik planliyor
user: "Monolitten mikroservise gec"
assistant: Karmasik gorev → Tam UDIV dongusu (2-3 yaklasim karsilastirmasi) baslatilir.
</example>

## Dongu Koruma Limitleri

Kisir donguyu onlemek icin asagidaki limitler **kesinlikle** uygulanir:

| Limit | Deger | Asim Durumunda |
|-------|-------|----------------|
| Faz geri donusu (ayni faz cifti) | Max **2** | Kullaniciya eskale et |
| Artim deneme sayisi (ayni artim) | Max **3** | DURDUR, kullaniciya raporla |
| Dogrulama-Uygulama turu | Max **2** | Kalan sorunlari kullaniciya sun |
| Faz 1 kesfetme adimi | Max **5** arac cagrisi | Mevcut bilgiyle ilerle |
| Toplam UDIV dongu tekrari | Max **1** tam tekrar | Tamamen dur |

**Sayac Takibi**: Her faz basinda geri_donus_sayaci=0 olarak basla. Her geri donuste +1 artir. Limite ulasinca kullaniciya acikla ve karar iste.

## UDIV Dongusu

### Faz 1: ANLA

Kullanicinin gercekte ne istedigini ve mevcut sistemin nasil calistigini derinlemesine kavra. Maksimum 5 arac cagrisi. "Yeterli Anlama Kriterleri"nin en az 4/5'i karsilaninca dur.

1. **Baglam Yukle** — Memory graph, CLAUDE.md, constitution.md
2. **Derin Kesfet** — `anlama-ajansi` agent'ini calistir, kod yollarini iz, bagimliliklari haritalandir
3. **Yapilandirilmis Dusunme** — Karmasik isteklerde `mcp__sequential-thinking__sequentialthinking` kullan
4. **Netlistirme** — Belirsiz noktalarda kullaniciya soru sor
5. **Anlama Ozeti Sun** — Niyet, mevcut durum, etki alani, risk, on yaklasim
6. **→ KULLANICI ONAYI BEKLE**

→ Detay: [references/udiv-protokol.md](./references/udiv-protokol.md)

### Faz 2: TASARLA

Birden fazla yaklasim uret (min 2, max 3), trade-off'lari degerlendir, en iyisini oner.

1. **Yaklasim Uretimi** — Her yaklasimdaki dosya degisikliklerini listele
2. **Görsel Mimari Tasarımı** — Seçilen veya önerilen yaklaşımın mimarisini Mermaid.js ile görselleştir
3. **Degerlendirme** — Constitution prensipleri, gecmis kararlar, trade-off analizi
4. **Oneri** — En iyi yaklasimi nedeniyle birlikte oner
5. **→ KULLANICI ONAYI BEKLE** (yaklasim secimi)

→ Detay: [references/udiv-protokol.md](./references/udiv-protokol.md)

### Faz 3: UYGULA

Onaylanmis tasarimi kucuk, dogrulanmis artimlarla hayata gecir. Her artim max 3 deneme.

1. **Self-Healing (Auto-Rollback) Hazırlığı** — Kritik değişiklikler öncesi otomatik `git stash` veya temp branch (`logos-fortuna-temp`) oluştur
2. **Artim Planlama** — En kucuk bagimsiz artimlara bol
3. **Akıllı Bağlam Budama (Context Pruning)** — Uzun döngülerde token tasarrufu için geçmiş logları temizleyip kararları özetata bağla
4. **Artimsal Uygulama** — `uygulama-ajansi` calistir, her artimdan sonra dogrula (syntax, test, lint)
5. **Ilerleme Raporu** — Tamamlanan/kalan artimlar, sorunlar ve cozumler
6. **→ KULLANICI ONAYI BEKLE**

→ Detay: [references/udiv-protokol.md](./references/udiv-protokol.md)

### Faz 4: DOGRULA ve OGREN

Sonucu cok boyutlu dogrula ve ogrenimleri kaydet.

1. **Kapsamli Dogrulama** — `dogrulama-ajansi` ile 5 boyut: fonksiyonel, anayasal, niyetsel, yapisal, regresyon
2. **Canlı Maliyet/Performans Profiler** — Big-O notasyon analizi ve zaman/alan karmaşıklığı ile performans ölçümü
3. **Proaktif Tehdit Avcılığı (Chaos Engineering)** — Kod kırılganlığını test etmek için Chaos ve Mutation Testing senaryoları tasarla
4. **Guvenlik Tarama** — `guvenlik-ajansi` ile OWASP Top 10 ve SANS Top 25 kontrolu
5. **Kalite Analizi** — `kalite-ajansi` ile kod kalitesi skoru (0-100) ve iyileştirme önerileri
6. **Sorun Cozumu** — Kritik → Faz 3'e don (max 2 tur), kucuk → yerinde duzelt
7. **Ogrenme** — `ogrenme-ajansi` ile tercihleri, kaliplari, basarili yaklasimlari kaydet
8. **Son Rapor** — Ne yapildi, nasil dogrulandi, ne ogrendi

→ Detay: [references/udiv-protokol.md](./references/udiv-protokol.md)

## Arac Orkestrasyon

Detayli arac secim mantigi ve fallback tablosu: [references/arac-orkestrasyon.md](./references/arac-orkestrasyon.md)

**Hizli Referans:**
- **Bilgi kaliciligi** → `mcp__memory__*`
- **Karmasik akil yurutme** → `mcp__sequential-thinking__sequentialthinking`
- **Kod kesfetme** → Explore agent veya Glob/Grep
- **Harici bilgi** → `mcp__brave-search__brave_web_search` veya WebSearch
- **GitHub islemleri** → `mcp__github__*`
- **Dosya islemleri** → Read, Write, Edit

## Arac Erisilebilirlik

MCP araclari her ortamda mevcut olmayabilir. Bir arac "tool not found" hatasi verirse:
1. [Fallback tablosuna](./references/arac-orkestrasyon.md) bak ve alternatife gec
2. Ayni araci tekrar deneme, fallback'te kal
3. Kullaniciya bildir: "X araci mevcut degil, Y ile devam ediyorum"

## Faz Basarisizlik Protokolu

```
Faz 4 basarisiz → sayac[4→3] += 1 → sayac <= 2: Faz 3'e don | sayac > 2: DURDUR
Faz 3 basarisiz → sayac[3→2] += 1 → sayac <= 2: Faz 2'ye don | sayac > 2: DURDUR
Faz 2 basarisiz → sayac[2→1] += 1 → sayac <= 2: Faz 1'e don | sayac > 2: DURDUR
Faz 1 basarisiz → Kullaniciya daha fazla bilgi sor
```

Her geri donuste neden geri donuldugunu acikla ve onceki fazin ciktisini guncelle.
3. Geri donus sayacini raporla: "Bu faz ciftinde X/2 geri donus kullanildi"

## Iptal Protokolu

Kullanici "iptal", "dur", "vazgec", "birak" gibi ifadeler kullandiginda:

1. **Mevcut calismay hemen durdur** — yarim kalmis islem varsa tamamla veya geri al
2. **Durum raporu sun**:
   ```
   ## Iptal Raporu
   - Tamamlanan fazlar: [liste]
   - Aktif faz: [faz adi] — [ilerleme %]
   - Yapilan degisiklikler: [dosya listesi]
   - Geri alinmasi gereken degisiklik: [varsa]
   ```
3. **Secenekler sun**:
   - "Yapilanlari koru, sadece dur"
   - "Tum degisiklikleri geri al (`git checkout .`)"
   - "Farkli bir noktadan devam et"
4. Kullanicinin secimini uygula

## Çoklu Dil Desteği

LogosFortuna uluslararası kullanım için çoklu dil desteği sağlar. Desteklenen diller: Türkçe (ana dil), İngilizce, Almanca, Fransızca. Otomatik n-gram tabanlı dil algılama ve kültür-spesifik adaptasyon (naming conventions, tarih formatları, iletişim tarzı) sağlanır.

## Entegrasyon ve Otomasyon

Detaylı entegrasyon yetenekleri için scriptlere bakın: [scripts/entegrasyon-sistemi.py](./scripts/entegrasyon-sistemi.py)

**Desteklenen Entegrasyonlar:**
- **GitHub**: PR otomasyonu, issue takibi, branch protection, workflow tetikleme
- **Slack/Discord**: Gerçek zamanlı bildirimler, batch gruplama, sessiz saatler
- **CI/CD**: Jenkins/GitLab CI entegrasyonu, kalite gate'leri, rollback otomasyonu
- **Webhook**: Özel webhook desteği, retry mekanizması, event filtreleme

## Güvenlik ve Kalite Kapıları

Detaylı doğrulama kriterleri: [references/kalite-kapilari.md](./references/kalite-kapilari.md)

**Özet:**
- **Güvenlik**: OWASP Top 10 + SANS Top 25 regex tabanlı tarama
- **Kalite**: Çok boyutlu skorlama (teknik %40, bakım %30, test %20, dokümantasyon %10)
- **Kapılar**: Minimum skor zorunlulukları, istisna yönetimi, sürekli izleme

## Performans

- **Caching**: Analiz sonuçları 24h TTL ile cache'lenir, dosya değişikliklerinde invalidation
- **Lazy Loading**: Sadece aktif/modified dosyalar analiz edilir
- **Paralel İşleme**: Çok çekirdekli sistemlerde paralel analiz

## Hata Yönetimi

- **Sınıflandırma**: Kritik, kurtarılabilir, uyarı, bilgilendirme seviyeleri
- **Otomatik Kurtarma**: Retry mekanizması, fallback sistemleri, state recovery, rollback
- **İzleme**: Gerçek zamanlı monitoring, hata loglama, alert sistemi
