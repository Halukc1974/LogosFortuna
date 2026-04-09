# UDIV Protokolu - Detayli Faz Rehberi

## Genel Bakis

UDIV (Anla-Tasarla-Uygula-Dogrula) dongusu, her gorevi dort fazda cozer. Bu belge her fazin detayli protokolunu, karar agaclarini ve basarisizlik senaryolarini tanimlar.

---

## Faz 1: ANLA - Detayli Protokol

### Baglam Yukleme Sirasi

1. **Memory Graph Kontrolu** (her zaman ilk)
   - `mcp__memory__search_nodes` ile gorevle ilgili anahtar kelimeleri ara
   - Bulunan entity'lerin observation'larini oku
   - Onceki oturumlardaki kararlar, tercihler ve kaliplari not et

2. **Proje Baglami**
   - CLAUDE.md → aktif teknolojiler, proje yapisi, komutlar
   - constitution.md → prenspler (varsa)
   - Son git log → yakin zamandaki degisiklikler

3. **Kod Kesfetme Stratejisi**
   - Bilinen dosya/fonksiyon → dogrudan Read/Grep
   - Belirsiz kapsam → Explore agent (quick/medium/very thorough)
   - Birden fazla alan → paralel Explore agent'lar (max 3)

### "Yeterli Anlama" Kriterleri

Asagidakilerin HEPSINI cevaplayabilmelisin:
- [ ] Kullanicinin asil amaci ne? (soyledigi vs gercekte istedigi)
- [ ] Hangi dosyalar/moduller etkilenecek?
- [ ] Mevcut kodda bu islevi yapan veya benzer bir sey var mi?
- [ ] Degisikligin yan etkileri ne olabilir?
- [ ] Constitution prensiplerinden hangisi ilgili?

Herhangi biri cevaplanamiyorsa → daha fazla kesfet veya kullaniciya sor.

### Soru Sorma Karar Agaci

```
Belirsizlik var mi?
├── Hayir → Anlama ozeti sun
└── Evet → Belirsizlik tipi?
    ├── Teknik (hangi yaklasim?) → Kesfetmeye devam et
    ├── Niyet (ne istiyor?) → Kullaniciya sor
    ├── Kapsam (ne kadar?) → Kullaniciya sor
    └── Oncelik (hangisi once?) → Kullaniciya sor
```

### Anlama Ozeti Formati

```
## Anlama Ozeti

**Gorev**: [kullanicinin istedigi, kendi kelimelerimle]
**Etki Alani**: [etkilenecek dosyalar ve moduller listesi]
**Mevcut Durum**: [ilgili kodun su anki hali]
**Bagimliliklar**: [bu degisikligin bagimli oldugu diger parcalar]
**Riskler**: [dikkat edilmesi gereken noktalar]
**On Yaklasim**: [ilk yaklasim fikri, detay Faz 2'de]

Bu anlamayi onayliyor musun, yoksa duzeltme/ekleme var mi?
```

---

## Faz 2: TASARLA - Detayli Protokol

### Yaklasim Uretme Kurallari

- **Minimum 2 yaklasim**: Basit/hizli vs kapsamli/saglam
- **Maximum 3 yaklasim**: Fazlasi karar yorgunlugu yaratir
- Her yaklasim icin:
  - Degistirilecek dosyalar ve tahmini satir sayisi
  - Yeni olusturulacak dosyalar
  - Silinecek/kaldirilacak kod
  - Karmasiklik seviyesi (dusuk/orta/yuksek)

### Degerlendirme Matrisi

Her yaklasimi su boyutlarda puanla (1-5):

| Boyut | Aciklama |
|-------|----------|
| Basitlik | Daha az kod, daha az dosya degisikligi |
| Saglamlik | Hata dayanikliligi, edge case kapsamasi |
| Genisletilebilirlik | Gelecek ihtiyaclara uyum |
| Mevcut Kaliplar | Projenin mevcut mimarisine uyum |
| Constitution Uyumu | Prensiplerle uyumluluk |

### Oneri Sunma Formati

```
## Tasarim Onerileri

### Yaklasim A: [isim] ⭐ Onerilen
[Kisa aciklama]
- Dosyalar: [liste]
- Artilari: [...]
- Eksileri: [...]
- Karmasiklik: [dusuk/orta/yuksek]

### Yaklasim B: [isim]
[Kisa aciklama]
- Dosyalar: [liste]
- Artilari: [...]
- Eksileri: [...]
- Karmasiklik: [dusuk/orta/yuksek]

**Onerim**: Yaklasim A, cunku [neden].
Hangi yaklasimi tercih ediyorsun?
```

---

## Faz 3: UYGULA - Detayli Protokol

### Artim Buyuklugu Kurallari

- **Ideal artim**: 1 dosya, 10-50 satir degisiklik
- **Maksimum artim**: 3 dosya, 100 satir degisiklik
- **Asla**: 5+ dosyayi ayni anda degistirme

### Artim Dogrulama Kontrol Listesi

Her artimdan sonra:
1. **Syntax**: Dosya tipi kontrol (py_compile, tsc --noEmit)
2. **Import**: Yeni import'lar dogru mu?
3. **Test**: Ilgili testler geciyormu? (`pytest dosya.py`, `npm test`)
4. **Lint**: Stil kurallari saglaniyor mu? (`ruff check`, `eslint`)

### Geri Alma Protokolu

```
Artim basarisiz oldu
├── Syntax hatasi → Hemen duzelt (basit typo)
├── Test basarisizligi → Analiz et
│   ├── Yeni testin kendisi yanlis → Testi duzelt
│   ├── Mevcut test kirildi → Kodu geri al, tasarimi revize et
│   └── Ilgisiz test basarisizligi → Not et, devam et
└── Lint hatasi → Hemen duzelt
```

### Ilerleme Takibi

Her artim sonrasi TaskUpdate ile ilerlemeyi guncelle:
```
Artim 1/5: ✅ Model dosyasi olusturuldu
Artim 2/5: ✅ Schema tanimlandi
Artim 3/5: 🔄 Service katmani yaziliyor...
Artim 4/5: ⏳ API endpoint
Artim 5/5: ⏳ Frontend entegrasyonu
```

---

## Faz 4: DOGRULA ve OGREN - Detayli Protokol

### 5 Boyutlu Dogrulama

**1. Fonksiyonel Dogrulama**
- Tum testler geciyor mu?
- Manuel test senaryolari basarili mi?
- Edge case'ler ele aliniyor mu?

**2. Anayasal Dogrulama**
- constitution.md prensipleri saglanyor mu?
- Her prensip icin spesifik kontrol yap
- Ihlal varsa → KRITIK, Faz 3'e geri don

**3. Niyetsel Dogrulama**
- Kullanicinin Faz 1'de onayladigi niyet karsilaniyor mu?
- Ekstra veya eksik islevsellik var mi?
- Kullanici "X istiyorum" demisse, tam olarak X yapildi mi?

**4. Yapisal Dogrulama**
- Projenin mevcut mimarisine uygun mu?
- Isimlendirme kurallari takip ediliyor mu?
- Dosya organizasyonu tutarli mi?

**5. Regresyon Dogrulama**
- Mevcut islevsellik bozuldu mu?
- Diger modullere yan etki var mi?
- Performans etkisi var mi?

### Guven Skorlama

Her boyut icin 0-100 skalasinda skor:
- **90-100**: Kesinlikle uyumlu, sorun yok
- **70-89**: Buyuk olcude uyumlu, kucuk iyilestirmeler mumkun
- **50-69**: Kismi uyum, dikkat gerektiren noktalar var
- **0-49**: Ciddi sorunlar, geri donus gerekli

Sadece guven >= 80 olan sorunlari raporla (false positive onleme).

### Ogrenme Cikartma Sablonu

```
## Oturum Ogrenimleri

### Kullanici Tercihleri
- [gozlemlenen tercih]: [baglam]

### Proje Kaliplari
- [kesfedilen kalip]: [nerede/nasil]

### Basarili Yaklasimlar
- [ne yapildi]: [neden isledi]

### Kacinilacak Yaklasimlar
- [ne denendi]: [neden islemedi]
```

---

## Iterasyon Sayaci ve Yakinlasma

- Her faz gecisinde iterasyon sayacini artir
- **Maksimum 3 iterasyon** ayni faz icinde → kullaniciya escalate et
- Yakinlasma isareti: Her iterasyonda sorun sayisi azaliyor
- Iraksamsa isareti: Sorun sayisi artiyorsa → dur, kullaniciya danist

---

## Ozel Durumlar

### Kucuk Gorevler (tek dosya, < 20 satir)
- Faz 1 ve 2'yi kisalt (ozet + oneri tek adimda)
- Faz 3 tek artim
- Faz 4 hafif dogrulama

### Acil Duzeltmeler (bug fix)
- Faz 1: Hatanin kok nedenini bul
- Faz 2: Atla (tek yaklasim yeterli)
- Faz 3: Duzeltmeyi uygula
- Faz 4: Regresyon testi oncelikli

### Buyuk Ozellikler (5+ dosya, yeni modul)
- Faz 1: Kapsamli kesfet (very thorough Explore)
- Faz 2: Mutlaka 3 yaklasim sun
- Faz 3: Alt gorevlere bol, her biri kendi UDIV mini-dongusu
- Faz 4: Kapsamli 5 boyutlu dogrulama
