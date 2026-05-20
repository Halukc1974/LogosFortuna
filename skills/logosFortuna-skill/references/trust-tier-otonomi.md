# Trust-Tier Otonomi Sistemi

**Constitution referansi**: Prensip 10 (v2.0.0).
**Esin kaynagi**: Anthropic'in Mythos Preview otonom yurutme yetenegi + Glasswing erisim modeli + Opus 4.7 differential capability reduction. LF, bu uc modelin bilesik dersini operasyonel hale getirir.

## Felsefe

Otonomi binary degildir. "Insan her seyde onaylar" ile "AI tek basina karar verir" arasinda dort kademe vardir. Operator hangi kademede calisilacagini **gorev basinda** beyan eder; sistem risk artislarinda kademeyi otomatik **dusurebilir** ama asla yukseltemez.

## Dort Kademe

### L0 — Tam Denetimli (default)

**Anlam**: Klasik UDIV. Her faz sonunda kullanici onayi beklenir.

**Ne zaman**: 
- Yeni operator, sistem ile ilk calismalar
- Production-touching gorevler (default)
- Risk profili belirsiz gorevler
- Operator explicit beyan etmediginde

**Davranis**: Mevcut LF davranisi aynen — Faz 1 oza, Faz 2 yaklasimlar, Faz 3 artim raporlari, Faz 4 sonuc raporu her biri ayri onay.

### L1 — Yari Otonom (Tasarim Fazi Atlanir)

**Anlam**: Faz 1 ve Faz 2 ardiSik otomatik (operator Faz 1 ozetinden sonra direkt Faz 2 onerisini de gorur). Faz 3 ve Faz 4 ayri onay.

**Ne zaman**:
- Operator UDIV'i tanir, anlamayi yorgun beklemiyor
- Net kapsamlı orta gorevler
- Risk: orta

**Davranis**: Anlama Ozeti ve Tasarim Onerisi tek mesajda birlestirilir. Operator "approve" derse Faz 3'e gecilir.

### L2 — Otonom Yapim (Adversarial Gate'li)

**Anlam**: Faz 1 → Faz 2 → Faz 3 → Faz 4 kesintisiz akar. Operator sadece final raporu gorur. **Ancak**: 
- `kirik-ajansi` (self-red-teamer) Faz 4'te zorunlu calisir
- Critical/High bulgu varsa otomatik L0'a duser, operatore eskale eder
- Constitution Quality Gate "Self-red-team pass for elevated tiers" enforce edilir

**Ne zaman**:
- Tanidik kod tabani, sade refactor
- Test coverage iyi olan kodda
- Operator beyan etmis (`/lf L2` veya prompt'ta "L2'de calis")
- Risk: dusuk-orta

**Davranis**: 
- Faz gecislerinde bekleme yok
- Her faz sonunda ozet log (telemetri JSONL)
- kirik-ajansi GREEN ise final rapor + commit onerisi
- kirik-ajansi RED ise: dur, raporla, L0'a dus

### L3 — Tam Otonom (Glasswing-Equivalent Trust)

**Anlam**: L2 + ek olarak `git commit` ve `git push` (sadece feature branch'lere) otomatik. Ana branch'e merge ASLA otomatik degildir.

**Ne zaman**:
- Operator "elevated-trust" rolünü acik vermistir
- Telemetride bu kod tabaninda son 5 UDIV runu GREEN
- Risk: dusuk
- Asla: production deploy, DB migration, auth/crypto, dependency major upgrade, force push (Constitution Operational Defaults)

**Davranis**:
- L2'nin tum davranislari
- + feature branch commit/push otomatik
- + sonraki gorev icin Faz 1'i pre-warm eder (memory'den hazirlik)

## Auto-Downgrade Tetikleyicileri

Asagidaki sinyallerden HERHANGI BIRI tespit edilirse sistem **bir kademe asagi** duser ve operatore neden bildirilir:

| Sinyal | Hangi kademeden ne kademeye |
|--------|------------------------------|
| `kirik-ajansi` critical bulgu | L1/L2/L3 → L0 |
| `kirik-ajansi` high bulgu (>2) | L2/L3 → L1 |
| `dogrulama-ajansi` constitution ihlali | L1/L2/L3 → L0 |
| `guvenlik-ajansi` OWASP critical | L1/L2/L3 → L0 |
| Artim 3. denemede de basarisiz | L1/L2/L3 → L0 |
| Geri donus sayaci limit asti | herhangi → L0 |
| Operator "dur"/"iptal" yazdi | herhangi → durdur |
| Constitution Prensip 8 ihlali (finding without remediation) | L2/L3 → L1 |
| Elevated-trust gerektiren islem talep edildi ama beyan yok | L3 → L1 (talep iptal) |
| Bilinmeyen MCP/skill talep edildi | L2/L3 → L1 (onay ister) |

Downgrade her zaman **acik bildirim** ile: operatöre "X sebebiyle L2'den L0'a indi" mesaji.

### Cakisan Sinyallerde Davranis

Bir UDIV rununda birden fazla downgrade tetikleyicisi ayni anda atesleyebilir (orn. kirik-ajansi critical + constitution ihlali). Bu durumda:

- **En dusuk hedef tier kazanir** — fazlalik birikmez, tek seferlik downgrade
- Tum tetikleyiciler operatore raporlanir (bir digerinin gorunmemesi icin)
- L3 → L0 dahi tek seferde yapilabilir (iki ayri sinyalden bagimsiz)

Ornek log:
```
Otonomi: L2 → L0 (en dusuk hedef kazandi)
  Tetikleyiciler:
    - kirik-ajansi critical bulgu (V3 prompt injection calisti)
    - dogrulama-ajansi constitution ihlali (Prensip 8: finding without remediation)
```

## Operator Beyan Sintaksi

Gorev basinda **acik beyan**:
```
/lf L2 — şu API endpoint'ini ekle
/lf L1 patching velocity opt-out
/lf L3 elevated-trust — feature branch'e otomatik commit yap
```

Ya da prompt icinde:
```
L2'de calisabilirsin, ben sadece final raporu gorecegim.
```

Beyan yoksa **default L0**.

## Elevated-Trust Rolu (Constitution Operational Defaults)

L3 dahi su islemler icin yeterli **degildir**:
- Production deploy (`*.prod.*` config, deployment scripts)
- Database migration (`migrations/`, `alembic/`, `prisma migrate deploy`)
- Auth/crypto degisiklik (`auth/`, `crypto/`, `*.pem`, secret rotation)
- Dependency major upgrade (semver major bump)
- Force push, rebase to public branches
- File deletion >100 LoC veya >5 dosya
- External API key rotation
- Third-party message gonderme (Slack/Discord/email)

Bu islemler icin operatorun **session basinda** acik beyani gerekir:
```
elevated-trust: db-migration prod-deploy
```

Ya da operator anlik onay verir (one-shot). Hicbir beyan yoksa, L3 dahi bu islemler icin operatore sorar.

## Telemetri Etkilesimi

Her UDIV runu telemetriye **otonomi kademesi**ni yazar:
```jsonl
{"run_id": "...", "tier": "L2", "auto_downgrades": ["L2→L0 at phase=4 reason=kirik_critical"], ...}
```

`/lf-rapor` raporlari icine yeni metrik: 
- Kademe basari orani (her kademede ne kadar GREEN bitti)
- Auto-downgrade siklik haritasi (hangi tetikleyici en cok ates aliyor)

## Karar Akisi (operator gorur)

```
[Operator] /lf L2 — soru kategorize edici ekle
   ↓
[Faz 1 Anla] enrichment + memory + kesfetme → ozet (log only, no wait)
   ↓
[Faz 2 Tasarla] yaklasim sec (constitution skoruyla en yuksek) → log only
   ↓
[Faz 3 Uygula] artimlar otomatik → her artim test+lint
   ↓
[Faz 4 Dogrula] 5 boyut + kirik-ajansi (mandatory)
   ↓
[GREEN?] 
   ├── EVET → final rapor + operator gozler
   └── HAYIR → otomatik L0'a indi, raporla, operatordan karar iste
```

## Implementasyon Notu

LF'nin Python runtime'i (`logosfortuna/`) tier yonetimini henuz tam zorlamaz; bu referans **target state**'i tanimlar. Hangi davranislar bugun aktif:

| Davranis | Bugun | Hedef |
|----------|-------|-------|
| Operator beyani okuma | manuel (prompt icinde) | parse + persist |
| Faz gecislerinde otomatik akis | manuel skip (operator "devam") | tier'a gore otomatik |
| Auto-downgrade | manuel (operator bildirir) | sinyal-tabanli otomatik |
| Telemetri tier alani | yok | jsonl alanina ekle |
| kirik-ajansi mandatory enforcement | yeni (bu surum) | runtime'da assert |

Constitution Prensip 3 geregi: bu farklar SKILL.md ve dokumantasyonda "kismi" olarak isaretlenir.
