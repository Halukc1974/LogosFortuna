---
name: logosfortuna-skill
description: 'UDIV meta-orkestrasyon workflow. Use when: /lf, cok asamali gorev, once anla sonra uygula, derin analiz, artimli delivery, 5 boyutlu dogrulama, approval gates.'
user-invocable: true
---

# LogosFortuna Skill

## When To Use
- Karmasik veya cok asamali bir gorev icin UDIV akisini gorunur sekilde yurutmek istediginde
- Degisiklik yapmadan once etki analizi, tasarim secimi ve dogrulama kapilarini korumak istediginde
- `logosfortuna` paketindeki guvenlik, kalite ve entegrasyon yardimcilarini daha buyuk bir workflow icine oturtmak istediginde

## Runtime Status
- Somut runtime plani `python -m logosfortuna udiv -- --task "..."` komutundan gelir.
- Guvenlik, kalite ve entegrasyon yardimcilari repoda gercek Python kodu olarak mevcuttur.
- Auto-rollback, MCP graph persistence, chaos engineering ve Big-O profiler alanlari bu repoda kismi durumdadir; tamamlanmis gibi sunulmamali.

## Procedure
1. Kullanici gorevi icin UDIV planini cikar veya mevcut plan yuzeyini incele.
2. Faz 1'de niyet, kapsam ve riskleri netlestir.
3. Faz 2'de en az bir uygulanabilir yaklasim secimi icin kullanicidan onay al.
4. Faz 3'te kucuk artimlarla uygula ve her artimdan sonra dar dogrulama yap.
5. Faz 4'te tam dogrulama, guvenlik/kalite kontrolu ve ogrenim kaydi yap.

## Guardrails
- Karmasik islerde Faz 1 atlanmaz.
- Faz gecisleri gorunur ve gerekirse onayli olur.
- Repoda bulunmayan ileri ozellikler "partial" olarak adlandirilir.