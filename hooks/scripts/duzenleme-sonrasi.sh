#!/bin/bash
# LogosFortuna-Skill PostToolUse Hook - Edit/Write sonrasi hafif dogrulama
# stdin'den JSON alir, duzenlenen dosyayi kontrol eder

set -euo pipefail

# Guvenli temp dosya olustur ve cikista temizle
TEMP_ERR=$(mktemp) || exit 0
trap 'rm -f "$TEMP_ERR"' EXIT

# stdin'den tool input'u oku (max 64KB)
INPUT=$(head -c 65536)

# python3 mevcut degilse sessizce cik (dogrulama yapilamaz ama engelleme)
if ! command -v python3 &>/dev/null; then
  exit 0
fi

# Dosya yolunu cikar (Edit ve Write tool'lari icin)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Edit tool
    path = data.get('tool_input', {}).get('file_path', '')
    if not path:
        # Write tool
        path = data.get('tool_input', {}).get('file_path', '')
    print(path)
except:
    print('')
" 2>/dev/null || echo "")

# Dosya yolu bos ise cik
if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Dosya uzantisini al
EXT="${FILE_PATH##*.}"

# Uzantiya gore hafif kontrol
case "$EXT" in
  py)
    if command -v python3 &>/dev/null; then
      if ! python3 -m py_compile "$FILE_PATH" 2>"$TEMP_ERR"; then
        ERR=$(cat "$TEMP_ERR")
        echo "{\"decision\": \"block\", \"reason\": \"Python syntax hatasi: ${ERR}\"}"
        exit 2
      fi
    fi
    ;;
  json)
    if command -v python3 &>/dev/null; then
      if ! python3 -m json.tool "$FILE_PATH" > /dev/null 2>"$TEMP_ERR"; then
        ERR=$(cat "$TEMP_ERR")
        echo "{\"decision\": \"block\", \"reason\": \"Gecersiz JSON: ${ERR}\"}"
        exit 2
      fi
    fi
    ;;
  ts|tsx)
    # TypeScript icin sadece dosya mevcudiyeti kontrol et
    # (tsc --noEmit tum projeyi kontrol eder, cok yavas olabilir)
    if [ ! -f "$FILE_PATH" ]; then
      echo "{\"decision\": \"block\", \"reason\": \"Dosya bulunamadi: ${FILE_PATH}\"}"
      exit 2
    fi
    ;;
  *)
    # Diger dosya tipleri icin kontrol yok
    ;;
esac

# Basarili - sessizce gec
exit 0
