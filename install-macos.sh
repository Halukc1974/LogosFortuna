#!/bin/bash
# LogosFortuna-Skill - macOS Kurulum Script'i
# Kullanim: curl -sSL <URL> | bash  VEYA  bash install-macos.sh
#
# Bu script:
# 1. Plugin'i ~/.claude/plugins/local/logosFortuna-skill dizinine klonlar
# 2. installed_plugins.json'a kaydeder
# 3. settings.json'da etkinlestirir

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  LogosFortuna-Skill - UDIV Meta-Orkestrasyon      ${NC}"
echo -e "${BOLD}  macOS Kurulum Araci                      ${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

CLAUDE_DIR="$HOME/.claude"
PLUGIN_DIR="$CLAUDE_DIR/plugins/local/logosFortuna-skill"
INSTALLED_PLUGINS="$CLAUDE_DIR/plugins/installed_plugins.json"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
REPO_URL="https://github.com/Halukc1974/LogosFortuna.git"

# 1. Onkosuller
echo -e "${YELLOW}[1/5]${NC} Onkosullar kontrol ediliyor..."

if ! command -v git &> /dev/null; then
    echo -e "${RED}HATA: git bulunamadi. Xcode Command Line Tools yukleyin:${NC}"
    echo "  xcode-select --install"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo -e "${RED}HATA: Claude Code CLI bulunamadi.${NC}"
    echo "  npm install -g @anthropic-ai/claude-code"
    exit 1
fi

if [ ! -d "$CLAUDE_DIR" ]; then
    echo -e "${RED}HATA: ~/.claude dizini bulunamadi. Once Claude Code'u en az bir kez calistirin.${NC}"
    exit 1
fi

echo -e "  ${GREEN}OK${NC} git, claude, ~/.claude mevcut"

# 2. Plugin'i klonla
echo -e "${YELLOW}[2/5]${NC} Plugin klonlaniyor..."

mkdir -p "$CLAUDE_DIR/plugins/local"

if [ -d "$PLUGIN_DIR" ]; then
    echo -e "  ${YELLOW}Mevcut kurulum bulundu, guncelleniyor...${NC}"
    cd "$PLUGIN_DIR" && git pull origin main 2>/dev/null || git pull 2>/dev/null
    echo -e "  ${GREEN}OK${NC} Guncellendi"
else
    git clone "$REPO_URL" "$PLUGIN_DIR"
    echo -e "  ${GREEN}OK${NC} Klonlandi: $PLUGIN_DIR"
fi

# 3. Hook script'lerini calistirilabilir yap
echo -e "${YELLOW}[3/5]${NC} Hook script izinleri ayarlaniyor..."

chmod +x "$PLUGIN_DIR/hooks/scripts/"*.sh 2>/dev/null || true
echo -e "  ${GREEN}OK${NC} Script izinleri ayarlandi"

# 4. installed_plugins.json'a kaydet
echo -e "${YELLOW}[4/5]${NC} Plugin registry'ye kaydediliyor..."

mkdir -p "$CLAUDE_DIR/plugins"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

if [ -f "$INSTALLED_PLUGINS" ]; then
    # Mevcut dosyada logosFortuna-skill var mi kontrol et
    if python3 -c "
import json, sys
with open('$INSTALLED_PLUGINS') as f:
    data = json.load(f)
if 'logosFortuna-skill@local' in data.get('plugins', {}):
    sys.exit(0)
else:
    sys.exit(1)
" 2>/dev/null; then
        echo -e "  ${GREEN}OK${NC} Zaten kayitli"
    else
        # logosFortuna-skill@local ekle
        python3 -c "
import json
with open('$INSTALLED_PLUGINS') as f:
    data = json.load(f)
if 'plugins' not in data:
    data['plugins'] = {}
data['plugins']['logosFortuna-skill@local'] = [{
    'scope': 'user',
    'installPath': '$PLUGIN_DIR',
    'version': '1.0.0',
    'installedAt': '$TIMESTAMP',
    'lastUpdated': '$TIMESTAMP'
}]
with open('$INSTALLED_PLUGINS', 'w') as f:
    json.dump(data, f, indent=2)
print('Eklendi')
"
        echo -e "  ${GREEN}OK${NC} Registry'ye eklendi"
    fi
else
    # Yeni dosya olustur
    python3 -c "
import json
data = {
    'version': 2,
    'plugins': {
        'logosFortuna-skill@local': [{
            'scope': 'user',
            'installPath': '$PLUGIN_DIR',
            'version': '1.0.0',
            'installedAt': '$TIMESTAMP',
            'lastUpdated': '$TIMESTAMP'
        }]
    }
}
with open('$INSTALLED_PLUGINS', 'w') as f:
    json.dump(data, f, indent=2)
print('Olusturuldu')
"
    echo -e "  ${GREEN}OK${NC} Yeni registry olusturuldu"
fi

# 5. settings.json'da etkinlestir
echo -e "${YELLOW}[5/5]${NC} Plugin etkinlestiriliyor..."

if [ -f "$SETTINGS_FILE" ]; then
    python3 -c "
import json
with open('$SETTINGS_FILE') as f:
    data = json.load(f)
if 'enabledPlugins' not in data:
    data['enabledPlugins'] = {}
if data['enabledPlugins'].get('logosFortuna-skill@local') is True:
    print('Zaten etkin')
else:
    data['enabledPlugins']['logosFortuna-skill@local'] = True
    with open('$SETTINGS_FILE', 'w') as f:
        json.dump(data, f, indent=2)
    print('Etkinlestirildi')
"
else
    python3 -c "
import json
data = {
    'enabledPlugins': {
        'logosFortuna-skill@local': True
    }
}
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
print('Yeni settings olusturuldu')
"
fi
echo -e "  ${GREEN}OK${NC}"

# Sonuc
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  KURULUM TAMAMLANDI!${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Konum: ${BOLD}$PLUGIN_DIR${NC}"
echo ""
echo -e "  ${BOLD}Kullanim:${NC}"
echo -e "    /lf [gorev]           Tam UDIV dongusu"
echo -e "    /lf-anla [alan]       Sadece derin anlama"
echo -e "    /lf-dogrula           5 boyutlu dogrulama"
echo ""
echo -e "  ${YELLOW}Claude Code'u yeniden baslatmayi unutmayin!${NC}"
echo ""
echo -e "  Guncelleme: cd ~/.claude/plugins/local/logosFortuna-skill && git pull"
echo ""
