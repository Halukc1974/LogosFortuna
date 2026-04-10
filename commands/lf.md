---
description: Tam UDIV dongusu baslat (Anla → Tasarla → Uygula → Dogrula)
argument-hint: [gorev aciklamasi]
---

# LogosFortuna-Skill - Tam UDIV Dongusu

Kullanicinin gorevi:
```
$ARGUMENTS
```

Bu gorev icin tam UDIV (Anla → Tasarla → Uygula → Dogrula) dongusunu baslat.

## Protokol

LogosFortuna-Skill meta-orkestrasyon skill'ini etkinlestir ve asagidaki donguyu kesinlikle takip et:

### Faz 1: ANLA
1. Memory graph'i kontrol et (`mcp__memory__search_nodes` ile gorevle ilgili anahtar kelimeleri ara)
2. CLAUDE.md ve varsa `.specify/memory/constitution.md` dosyalarini oku
3. `anlama-ajansi` agent'ini calistir — ilgili kod yollarini kesfet, bagimliliklari haritalandir
4. Karmasik isteklerde `mcp__sequential-thinking__sequentialthinking` kullan
5. Belirsizliklerde kullaniciya soru sor
6. **Anlama Ozeti sun ve KULLANICI ONAYINI BEKLE**

Kullanici onayi olmadan Faz 2'ye gecme. "Devam et", "tamam", "evet" gibi acik onay bekle.

### Faz 2: TASARLA
1. En az 2 yaklasim uret
2. Her yaklasimi constitution prensipleriyle degerlendir
3. Trade-off'lari acikca sun
4. **Oneri sun ve KULLANICI ONAYINI BEKLE** (yaklasim secimi)

Kullanici bir yaklasim secmeden Faz 3'e gecme.

### Faz 3: UYGULA
1. Secilen yaklasimi kucuk artimlara bol
2. `uygulama-ajansi` agent'ini calistir
3. Her artimdan sonra dogrula (syntax, test, lint)
4. Tum artimlar tamamlaninca **ilerleme raporu sun ve KULLANICI ONAYINI BEKLE**

### Faz 4: DOGRULA ve OGREN
1. `dogrulama-ajansi` agent'ini calistir — 5 boyutlu dogrulama
2. Kritik sorunlar varsa → Faz 3'e geri don
3. `ogrenme-ajansi` agent'ini calistir — ogrenimleri cikar
4. Ogrenimleri `mcp__memory__create_entities` ve `mcp__memory__add_observations` ile kaydet
5. **Son rapor sun**

## Faz Basarisizlik Geri Donus

```
Faz 4 basarisiz → Faz 3 (duzelt)
Faz 3 basarisiz → Faz 2 (revize et)
Faz 2 basarisiz → Faz 1 (derinlestir)
Faz 1 basarisiz → Kullaniciya daha fazla bilgi sor
```

Her geri donuste neden geri donuldugunu acikla.

## Onemli Kurallar

- Her faz gecisinde acik kullanici onayi zorunlu
- Asla anlamadan uygulama
- Kucuk artimlarla calis
- Constitution prensiplerini her zaman referans al
- Oturum sonunda her zaman ogrenimleri kaydet
- **Dongu Koruma**: Faz geri donus max 2, artim deneme max 3, dogrulama turu max 2
- **Iptal**: Kullanici "dur/iptal/vazgec" derse hemen durdur ve Iptal Protokolunu uygula
