# Differential Capability per Agent Role

**Constitution referansi**: Prensip 9 (v2.0.0).
**Esin kaynagi**: Opus 4.7'nin Mythos'a kiyasla "differential capability reduction" yontemi — Anthropic, ayni temel modeli aldi, siber yetenekleri kasitli olarak kapatti, sonra genel kullanima sundu. Ayni prensip *bir agentic sistem icindeki agent'lara* uygulandiginda: her agent sadece **isini yapacak en dar tool yuzeyi** ile yetkilendirilir.

## Niye Onemli

LF su anda 14 agent kullaniyor. Eger hepsi ayni tool setine (read+write+edit+execute+web) sahipse:

1. **Separation of concerns yikilir**: dogrulama-ajansi kendi inceledigi dosyayi sessizce duzeltebilir — bu false PASS yaratir
2. **Saldiri yuzeyi genisler**: bir agent prompt injection ile manipule edilirse, hepsi ayni gucle calisir
3. **Auditability azalir**: "kim ne yapti?" sorusuna tutarli yanit verilemez
4. **Trust-tier sistemi zayiflar**: L2/L3'te otonom calisan agent'larin yetkileri ayni ise risk kontrolu yapilamaz

## Tool Allowlist Matrisi (Normative)

Her agent **yalnizca** bu kolondaki tool'lara erisir. `tools:` frontmatter alani bu matrisi yansitir.

| Agent | read | search (grep/glob) | execute | edit/write | web | mcp_memory | git_write |
|-------|:----:|:---:|:---:|:---:|:---:|:---:|:---:|
| **anlama-ajansi** | ✅ | ✅ | scan-only (test/lint) | ❌ | ✅ | read-only | ❌ |
| **uygulama-ajansi** | ✅ | ✅ | ✅ test+lint+build | ✅ | ❌ | read-only | feature-branch only |
| **dogrulama-ajansi** | ✅ | ✅ | test+lint+scan | ❌ | ❌ | read-only | ❌ |
| **kirik-ajansi** *(yeni)* | ✅ | ✅ | test+scan+fuzz | ❌ | ❌ | read-only | ❌ |
| **guvenlik-ajansi** | ✅ | ✅ | security-scan tools | ❌ | ❌ | read-only | ❌ |
| **kalite-ajansi** | ✅ | ✅ | lint+complexity | ❌ | ❌ | read-only | ❌ |
| **ogrenme-ajansi** | ✅ | ✅ | ❌ | ❌ | ❌ | read+write | ❌ |
| **skill-classifier-ajansi** | ✅ | ✅ | ❌ | ❌ | minimal | read+write | ❌ |
| **entegrasyon-ajansi** | ✅ | ✅ | CI/CD scripts | ✅ config-only | ✅ | read-only | feature-branch only |
| **dil-ajansi** | ✅ | ✅ | i18n-tools | ✅ locale files only | ❌ | read-only | ❌ |
| **ux-ajansi** | ✅ | ✅ | preview-server | ✅ ui files only | ❌ | read-only | ❌ |

### Onemli kisitlamalar

- **Sadece `uygulama-ajansi` ve sinirli durumlarda `entegrasyon-ajansi` yazar.** Diger agent'lar bulgu/oneri uretir; yamayi uygulama-ajansi yapar.
- **Hicbir agent default'ta `git push` yapmaz.** L3 + elevated-trust + feature branch sarti hep beraber gerekir.
- **`execute` her zaman whitelist'lidir**: agent'in kendi calistirabilecegi komutlar SKILL.md veya agent dosyasinda listelidir.

## Onaylanmis Execute Komutlari (Whitelist)

Her kategorinin sadece bu komutlari calistirilabilir; `execute` tool'una sahip agent **bu listenin disina cikamaz**.

### scan-only (anlama-ajansi)
- `find`, `ls`, `tree` (read-only filesystem)
- `git status`, `git log`, `git diff` (no write)
- `wc`, `head`, `tail` (file metadata)

### test+lint+build (uygulama-ajansi)
- `pytest`, `npm test`, `cargo test`, `go test`
- `ruff check`, `eslint`, `prettier --check`, `mypy`, `tsc --noEmit`
- `npm run build`, `cargo build`, `make build`
- ⚠ `npm install`, `pip install`: sadece L0/L1'de operator onayi ile

### test+lint+scan (dogrulama-ajansi)
- yukaridakilerin tumu (scan-only mode)
- `coverage report`, `pytest --cov`
- `ruff check --statistics`

### test+scan+fuzz (kirik-ajansi)
- yukaridakilerin tumu
- `bandit`, `semgrep`, `safety check`
- Fuzz: `atheris`, `cargo fuzz`, custom property tests
- ⚠ Asla production endpoint'ine istek atmaz

### security-scan (guvenlik-ajansi)
- `bandit -r`, `semgrep --config auto`, `trivy fs`
- `snyk test`, `dependency-check`
- ⚠ Network egress'i yoktur; tarama lokaldir

### lint+complexity (kalite-ajansi)
- `ruff`, `eslint`, `prettier`, `mypy`, `tsc`
- `radon`, `lizard`, `scc` (complexity)
- `git log --stat` (churn analizi)

### CI/CD scripts (entegrasyon-ajansi)
- `.github/workflows/*.yml`, `gitlab-ci.yml` okuma/yazma
- `gh pr create`, `gh pr view` (PR olusturma)
- ⚠ `gh pr merge` ASLA otomatik; operator onayi sarti

### preview-server (ux-ajansi)
- `npm run dev`, `vite`, `next dev`
- `python -m http.server` (local preview only)
- ⚠ Port baglama: 1024-9999 araliginda kalir

## Enforcement Mekanizmasi

### Bugun (manuel)

Agent dosyalarinin `tools:` frontmatter'i yukaridaki matrisi yansitir. Host (Claude Code) bu listeyi okur ve agent'a sadece o tool'lari verir.

```yaml
# agents/kirik-ajansi.agent.md
tools: ["read", "search", "execute"]
```

`execute` icin whitelist enforcement henuz **kismi** — agent dosyasinin metin govdesinde "asagidaki komut listesinden disari cikma" talimati var ama runtime'da assert edilmiyor.

### Hedef (gelecek surum)

LF Python runtime'i (`logosfortuna/`) agent cagirisini interceptr edip:
1. Tool allowlist'i doğrulayacak
2. Shell whitelist'i regex ile kontrol edecek
3. Ihlal durumunda agent'i durduracak + telemetriye yazacak

Constitution Prensip 3 geregi bu su an "kismi" olarak isaretli.

## Yeni Agent Eklerken Karar Agaci

```
Yeni agent ne yapar?
├── Sadece okur/analiz eder
│   └── read + search + (varsa scan-only execute), edit/write/web YOK
├── Yazar/degistirir
│   ├── Kod yazar → uygulama-ajansi'na ekle yeni rol; yeni agent yaratma
│   ├── Sadece config → edit (config-only); execute YOK
│   └── Sadece docs → edit (docs-only); execute YOK
├── Harici sistemle konusur
│   ├── Web → web; mcp_memory write YOK
│   ├── CI/CD → entegrasyon-ajansi'na rol ekle; yeni agent yaratma
│   └── Diger → kullaniciya sor, default deny
└── LLM siniflandirma yapar
    └── ogrenme-ajansi veya skill-classifier-ajansi'na ekle; yeni agent yaratma
```

**Genel kural**: Yeni agent eklemek yerine mevcut agent'in rolunu genislet, eger genisletme baska bir agent'in iznine ihtiyac duymuyorsa.

## Kontrol Listesi (yeni/degisen agent icin)

- [ ] `tools:` frontmatter yukaridaki matrise uyuyor mu?
- [ ] Agent metin govdesinde "calistirabilecegim komut listesi" var mi?
- [ ] Agent kendisinin **degistiremeyecegi** seyi degistirmiyor mu? (separation of concerns)
- [ ] Agent baska agent'in roluyle cakisiyor mu? (genisletme mi gerek, yeni agent mi?)
- [ ] L2/L3 otonomi seviyelerinde nasil davranir, dokumante edildi mi?

## Telemetri

Her agent calismasi telemetriye **kullanilan tool listesi**ni yazar:
```jsonl
{"agent": "kirik-ajansi", "tools_used": ["read", "search", "bash:pytest", "bash:bandit"], ...}
```

Allowlist disi tool kullanimi anomaly olarak isaretlenir.
