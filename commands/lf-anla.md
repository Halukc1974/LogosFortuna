---
description: Sadece derin anlama fazi calistir
argument-hint: [anlasilacak alan veya soru]
---

# LogosFortuna-Skill - Anlama Fazi

Anlasilacak konu:
```
$ARGUMENTS
```

Sadece UDIV dongusunun Faz 1 (ANLA) asamasini calistir. Kod yazmak veya degistirmek yok — sadece derin anlama ve raporlama.

## Protokol

1. **Baglam Yukle**
   - Memory graph'i kontrol et (`mcp__memory__search_nodes`)
   - CLAUDE.md oku
   - Varsa `.specify/memory/constitution.md` oku

2. **Derin Kesfet**
   - `anlama-ajansi` agent'ini calistir
   - Ilgili dosyalari, fonksiyonlari ve bagimliliklari haritalandir
   - Mevcut kaliplari ve yeniden kullanilabilir yapilari tespit et

3. **Yapilandirilmis Dusunme**
   - Karmasik konularda `mcp__sequential-thinking__sequentialthinking` kullan
   - Belirsiz noktalari belirle

4. **Kapsamli Anlama Raporu Sun**
   ```
   ## Anlama Raporu
   
   ### Konu/Alan: [...]
   ### Mevcut Durum: [...]
   ### Ilgili Dosyalar: [dosya listesi ve rolleri]
   ### Kod Akisi: [A → B → C]
   ### Bagimliliklar: [...]
   ### Riskler ve Dikkat Noktalari: [...]
   ### Constitution Uyumu: [ilgili prenspler]
   ```

5. **Belirsizliklerde soru sor**

Bu komut uygulama yapmaz. Sadece anlama uretir. Uygulama icin `/lf` kullan.
