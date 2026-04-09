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

## Farkli Makinede Guncelleme

```bash
cd ~/.claude/plugins/local/logosFortuna-skill && git pull
```
