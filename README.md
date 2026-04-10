# LogosFortuna-Skill - UDIV Meta-Orkestrasyon Sistemi

Kisisel iteratif anlama ve uygulama plugin'i. Her gorevi dort fazli UDIV dongusuyle cozer:

**Anla → Tasarla → Uygula → Dogrula**

## Kurulum

```bash
git clone https://github.com/Halukc1974/LogosFortuna.git ~/.claude/plugins/local/logosFortuna-skill
```

Claude Code'u yeniden baslat. Plugin otomatik olarak taninacak.

## Komutlar

| Komut | Aciklama |
|-------|----------|
| `/lf [gorev]` | Tam UDIV dongusu baslat |
| `/lf-anla [alan]` | Sadece derin anlama fazi |
| `/lf-dogrula [alan]` | 5 boyutlu dogrulama |

## Bilesenleri

- **4 Uzman Agent**: anlama, uygulama, ogrenme, dogrulama
- **3 Slash Komutu**: /lf, /lf-anla, /lf-dogrula
- **3 Hook**: SessionStart (baglam), PostToolUse (syntax), Stop (ogrenme)
- **3 Referans**: UDIV protokol, arac orkestrasyon, kalite kapilari
- **Memory Entegrasyonu**: Oturum arasi ogrenme

## Dongu Koruma

Kisir dongu ve sonsuz tekrarlarl onlemek icin yerlesik limitler:

| Mekanizma | Limit | Davranis |
|-----------|-------|----------|
| Faz geri donusu | Max 2 / faz cifti | Kullaniciya eskalasyon |
| Artim denemesi | Max 3 / artim | Durdur ve raporla |
| Dogrulama-Uygulama turu | Max 2 tur | Kalan sorunlari kullaniciya sun |
| Faz 1 kesfetme | Max 5 arac cagrisi | Mevcut bilgiyle ilerle |

## Gorev Siniflandirma

UDIV dongusu gorev karmasikligina gore adapte olur:

| Seviye | Akis |
|--------|------|
| **Basit** | Anla (hafif) → Uygula → Dogrula |
| **Orta** | Anla → Tasarla (tek oneri) → Uygula → Dogrula |
| **Karmasik** | Tam UDIV dongusu (2-3 yaklasim) |

## Farkli Makinede Guncelleme

```bash
cd ~/.claude/plugins/local/logosFortuna-skill && git pull
```
