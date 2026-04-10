# Kalite Kapilari - Dogrulama Kriterleri

## Amac

Bu belge, LogosFortuna-Skill'in Faz 4 (DOGRULA) asamasinda ve PostToolUse hook'larinda kullanilan dogrulama kriterlerini tanimlar.

---

## Genel Kalite Kapilari (Tum Projeler)

### Kapi 1: Syntax ve Derleme

| Dosya Tipi | Kontrol Komutu | Gecme Kriteri |
|------------|----------------|---------------|
| Python (.py) | `python3 -m py_compile dosya.py` | Hatasiz cikis (exit 0) |
| TypeScript (.ts/.tsx) | `npx tsc --noEmit` | Hatasiz cikis |
| JavaScript (.js/.jsx) | `node --check dosya.js` | Hatasiz cikis |
| JSON (.json) | `python3 -m json.tool dosya.json` | Gecerli JSON |
| YAML (.yml/.yaml) | `python3 -c "import yaml; yaml.safe_load(open('dosya.yaml'))"` | Gecerli YAML |

### Kapi 2: Lint ve Stil

| Dil | Arac | Konfigurasyona Bak |
|-----|------|--------------------|
| Python | `ruff check .` | pyproject.toml, ruff.toml |
| TypeScript/JS | `npx eslint .` | .eslintrc, eslint.config |
| CSS | `npx stylelint "**/*.css"` | .stylelintrc |

**Kural**: Lint uyarilari kabul edilebilir, lint HATALARI kabul edilemez.

### Kapi 3: Test Kapsamai

| Durum | Beklenti |
|-------|----------|
| Mevcut testler var | Tum testler gecmeli |
| Yeni islevsellik eklendi | En az temel test yazilmali |
| Bug fix | Regresyon testi eklenmelidir |
| Refactoring | Mevcut testler degismeden gecmeli |

**Komutlar:**
- Python: `pytest` veya `pytest dosya_test.py`
- TypeScript/JS: `npm test` veya `npx jest`

### Kapi 4: Guvenlik

- Hassas veri yok (API key, sifre, credential hardcoded degil)
- SQL injection korumasai (parametreli sorgular)
- XSS korumasl (cikti sanitizasyonu)
- Command injection korumasl (shell komutlarinda degisken kacirma)

---

## Soruuetici Projesine Ozel Kapilar

### Pedagojik Dogruluk (Constitution Prensip I)

- Soru metni bilimsel olarak dogru mu?
- Tek bir kesin dogru cevap var mi?
- Distraktorlar mantikli ama yanlis mi?
- Matematiksel hesaplamalar dogrulanmis mi? (SymPy)

### Coklu Seviye Uyum (Constitution Prensip II)

- Zorluk seviyesi (kolay/orta/zor/cok_zor) icerikle uyumlu mu?
- Egitim seviyesi (ilkogretim/lise/universite) dogru mu?
- Dil karmasikligi seviyeye uygun mu?

### Yapisal Tutarlilik (Constitution Prensip III)

- JSON sema uyumlu mu? (question, choices, correct_answer, difficulty, category, subcategory, education_level, curriculum, explanation alanlari)
- Schema versiyonlama kurallarina uyuluyor mu?

### Kapsamli Aciklama (Constitution Prensip IV)

- Adim adim cozum var mi?
- Formul/teorem referanslari var mi?
- Ara hesaplama adimlari gosteriliyor mu?

### Kalite Dogrulama (Constitution Prensip V)

- Matematiksel dogrulama yapildi mi?
- Duplikasyon kontrolu yapildi mi?
- Dogrulanmamis icerik uretim hattina gecirilmedi mi?

---

## Boyut Bazli Skor Esikleri ve Karar Matrisi

| Boyut | GECTI (✅) | KOSULLU (⚠️) | KALDI (❌) | KRITIK DURDUR (🛑) |
|-------|-----------|-------------|-----------|-------------------|
| Fonksiyonel | >= 80 | 65-79 | 50-64 | < 50 |
| Anayasal | >= 90 | 80-89 | 70-79 | < 70 |
| Niyetsel | >= 85 | 70-84 | 60-69 | < 60 |
| Yapisal | >= 75 | 60-74 | 50-59 | < 50 |
| Regresyon | >= 95 | 85-94 | 80-84 | < 80 |

### Karar Kurallari

- **GECTI (✅)**: Devam et, sorun yok
- **KOSULLU (⚠️)**: Kullaniciya bildir, devam etme karari kullanicida
  - Format: "Su boyutlar kosullu gecti: [boyut: skor]. Bilinen eksikler: [...]. Devam edilsin mi?"
  - Kullanici "devam" derse → kabul et ve ilerle
  - Kullanici "duzelt" derse → Faz 3'e geri don (geri donus sayaci dahilinde)
- **KALDI (❌)**: Otomatik olarak Faz 3'e geri don (geri donus sayaci kontrolu ile)
- **KRITIK DURDUR (🛑)**: Hemen dur, kullaniciya eskalasyon. Geri donus sayaci ne olursa olsun durdur.

### Birlesik Karar

- Herhangi bir boyut KRITIK DURDUR → tum dogrulama basarisiz
- 2+ boyut KALDI → tum dogrulama basarisiz
- 1 boyut KALDI + diger hepsi GECTI → o boyutu duzelt (kismi geri donus)
- Sadece KOSULLU'lar var → kullaniciya sun, karar kullanicida

---

## PostToolUse Hafif Dogrulama

Edit/Write sonrasi calisan hafif kontroller (< 5 saniye):

1. **Dosya tipi tanima** → uzantiya gore
2. **Syntax kontrolu** → yukaridaki tablo
3. **Import kontrolu** → yeni import var mi, mevcut mu?
4. **Sonuc bildirimi** → ✅ gecti veya ❌ hata detayi

Agir kontroller (test, lint) SADECE Faz 4'te calisir, PostToolUse'da calismaz.

---

## Dogrulama Rapor Formati

```
## Dogrulama Raporu

| Boyut | Skor | Durum | Notlar |
|-------|------|-------|--------|
| Fonksiyonel | 95 | ✅ GECTI | Tum testler basarili |
| Anayasal | 90 | ✅ GECTI | Constitution uyumlu |
| Niyetsel | 88 | ✅ GECTI | Kullanici istegine uygun |
| Yapisal | 85 | ✅ GECTI | Mevcut kaliplara uyumlu |
| Regresyon | 100 | ✅ GECTI | Mevcut testler etkilenmedi |

**Genel Durum**: ✅ BASARILI
**Toplam Skor**: 91.6 / 100

### Iyilestirme Onerileri (opsiyonel)
- [kucuk oneri varsa]
```
