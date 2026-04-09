---
description: Mevcut degisiklikleri 5 boyutlu dogrula
argument-hint: [dogrulanacak alan - opsiyonel]
---

# LogosFortuna-Skill - Dogrulama Fazi

Dogrulanacak alan:
```
$ARGUMENTS
```

Sadece UDIV dongusunun Faz 4 (DOGRULA ve OGREN) asamasini calistir.

## Protokol

### 1. Degisiklikleri Belirle
- `git diff` ve `git status` ile son degisiklikleri gozden gecir
- Arguman verilmisse sadece o alandaki degisikliklere odaklan
- Arguman verilmemisse tum son degisiklikleri dogrula

### 2. 5 Boyutlu Dogrulama
`dogrulama-ajansi` agent'ini calistir:

- **Fonksiyonel**: Testler geciyor mu? Edge case'ler kapsanmis mi?
- **Anayasal**: Constitution prensipleriyle uyumlu mu?
- **Niyetsel**: Kullanicinin istedigi sey yapildi mi?
- **Yapisal**: Proje mimarisi ve konvansiyonlarina uygun mu?
- **Regresyon**: Mevcut islevsellik bozuldu mu?

### 3. Rapor Sun
```
## Dogrulama Raporu

| Boyut | Skor | Durum |
|-------|------|-------|
| Fonksiyonel | XX | ✅/⚠️/❌ |
| Anayasal | XX | ✅/⚠️/❌ |
| Niyetsel | XX | ✅/⚠️/❌ |
| Yapisal | XX | ✅/⚠️/❌ |
| Regresyon | XX | ✅/⚠️/❌ |

### Kritik Sorunlar
[varsa listele]

### Iyilestirme Onerileri
[varsa listele]
```

### 4. Ogrenme (opsiyonel)
Eger onemli ogrenimler varsa `ogrenme-ajansi`'ni calistir ve memory'ye kaydet.
