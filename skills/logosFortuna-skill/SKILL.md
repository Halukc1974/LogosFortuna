---
name: logosFortuna-skill
description: "Bu skill, kullanici lf mode, derin analiz yap, bunu dikkatli uygula, once anla sonra yap, iteratif gelistir, tam dongu baslat, orkestre et, UDIV veya karmasik bir gorev icin cok asamali anlama ve dogrulanmis uygulama gerektiren herhangi bir istekte bulunuldugunda kullanilmalidir. Tum mevcut Claude Code yeteneklerini tek bir iteratif dongude birlestiren meta-orkestrasyon sistemidir."
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

## UDIV Dongusu

### Faz 1: ANLA

Amac: Kullanicinin gercekte ne istedigini ve mevcut sistemin nasil calistigini derinlemesine kavra.

**Adimlar:**

1. **Baglam Yukle**
   - Memory graph'i oku: `mcp__memory__read_graph` ve `mcp__memory__search_nodes` ile bu proje/alan hakkinda onceki bilgileri cek
   - CLAUDE.md dosyasini oku (proje kurallari ve teknolojiler)
   - Varsa `.specify/memory/constitution.md` oku (proje prensipleri)

2. **Derin Kesfet**
   - `anlama-ajansi` agent'ini calistir — kod yollarini iz, bagimliliklari haritalandir, etki analizi yap
   - Birden fazla Explore agent'i paralel calistir (farkli odak alanlari)
   - Mevcut kaliplari, utility'leri ve yeniden kullanilabilir yapilari tespit et

3. **Yapilandirilmis Dusunme**
   - `mcp__sequential-thinking__sequentialthinking` ile karmasik isteklerde adim adim akil yurutme yap
   - Belirsiz noktalari, varsayimlari ve riskleri belirle

4. **Netlistirme**
   - Belirsiz veya cok anlamli noktalarda kullaniciya soru sor (AskUserQuestion)
   - Asla buyuk varsayimlar yapma

5. **Anlama Ozeti Sun**
   - Kullanicinin niyeti (ne istedi vs ne soyledi)
   - Mevcut sistem durumu (ilgili dosyalar, mimari, bagimliliklar)
   - Etki alani (hangi dosyalar/moduller etkilenecek)
   - Risk ve kisitlar
   - Onerilen yaklasimlarin on gorunumu

6. **→ KULLANICI ONAYI BEKLE**

### Faz 2: TASARLA

Amac: Birden fazla yaklasim uret, trade-off'lari degerlendir, en iyisini oner.

**Adimlar:**

1. **Yaklasim Uretimi**
   - En az 2, en fazla 3 farkli yaklasim belirle
   - Her yaklasimdaki dosya degisikliklerini, yeni dosyalari ve silmeleri listele

2. **Degerlendirme**
   - Her yaklasimi constitution prensipleriyle karsilastir
   - Memory'deki gecmis kararlarla uyum kontrol et
   - Basitlik vs genisletilebilirlik vs performans trade-off'larini sun

3. **Oneri**
   - En iyi yaklasimi nedeniyle birlikte oner
   - Uygulama adimlarini kucuk artimlar olarak sirala

4. **→ KULLANICI ONAYI BEKLE** (yaklasim secimi)

### Faz 3: UYGULA

Amac: Onaylanmis tasarimi kucuk, dogrulanmis artimlarla hayata gecir.

**Adimlar:**

1. **Artim Planlama**
   - Onaylanmis tasarimi en kucuk bagimsiz artrimlara bol
   - Her artimin dogrulama kriterini belirle

2. **Artimsal Uygulama Dongusu** (her artim icin):
   - `uygulama-ajansi` agent'ini calistir
   - Kod degisikligi yap
   - Hemen dogrula (syntax, test, lint)
   - Basarili → sonraki artrima gec
   - Basarisiz → analiz et, duzelt veya geri al

3. **Ilerleme Raporu**
   - Tamamlanan ve kalan artimlari goster
   - Karsilasilan sorunlari ve cozumleri listele

4. **→ KULLANICI ONAYI BEKLE**

### Faz 4: DOGRULA ve OGREN

Amac: Sonucu cok boyutlu dogrula ve ogrenimleri kaydet.

**Adimlar:**

1. **Kapsamli Dogrulama**
   - `dogrulama-ajansi` agent'ini calistir
   - 5 boyut: fonksiyonel, anayasal, niyetsel, yapisal, regresyon
   - Her boyut icin gecti/kaldi ve guven skoru (0-100)

2. **Sorun Cozumu** (varsa)
   - Kritik sorunlar → Faz 3'e geri don
   - Kucuk sorunlar → yerinde duzelt

3. **Ogrenme**
   - `ogrenme-ajansi` agent'ini calistir
   - Kullanici tercihleri, proje kaliplari, basarili yaklasimlar cikar
   - `mcp__memory__create_entities` ve `mcp__memory__add_observations` ile kaydet

4. **Son Rapor**
   - Ne yapildi, nasil dogrulandi, ne ogrendi ozeti

## Arac Orkestrasyon Kurallari

Detayli arac secim mantigi icin: `references/arac-orkestrasyon.md`

**Hizli Referans:**
- **Bilgi kaliciligi** → `mcp__memory__*` (entity, observation, relation)
- **Karmasik akil yurutme** → `mcp__sequential-thinking__sequentialthinking`
- **Kod kesfetme** → Explore agent veya dogrudan Glob/Grep
- **Harici bilgi** → `mcp__brave-search__brave_web_search` veya WebSearch
- **GitHub islemleri** → `mcp__github__*`
- **Dosya islemleri** → Read, Write, Edit (dogrudan tool'lar oncelikli)

## Kalite Kapilari

Detayli kriterler icin: `references/kalite-kapilari.md`

**Minimum Esikler:**
- Testler gecmeli (varsa)
- Syntax hatasiz olmali
- Constitution prensipleriyle uyumlu olmali
- Kullanicinin orijinal niyetini karsilamali

## Faz Basarisizlik Protokolu

```
Faz 4 basarisiz → Faz 3'e don (sorunlu artimlari duzelt)
Faz 3 basarisiz → Faz 2'ye don (yaklasimi revize et)
Faz 2 basarisiz → Faz 1'e don (anlamayi derinlestir)
Faz 1 basarisiz → Kullaniciya daha fazla bilgi sor
```

Her geri donuste neden geri donuldugunu acikla ve onceki fazin ciktisini guncelle.
