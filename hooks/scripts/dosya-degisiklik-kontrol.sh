#!/bin/bash
# LogosFortuna-Skill Stop Hook - Dosya degisikligi kontrolu
# Oturum sonunda git diff ile degisiklik var mi kontrol eder

set -euo pipefail

if ! command -v git &>/dev/null || ! git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  exit 0
fi

# Staged + unstaged degisiklikleri kontrol et
CHANGED_FILES=$(git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null)

if [ -n "$CHANGED_FILES" ]; then
  echo "📋 Oturumda dosya degisiklikleri tespit edildi:"
  echo "$CHANGED_FILES" | sort -u | head -20
  echo ""
  echo "💡 Degisiklikleri dogrulamak icin '/lf-dogrula' komutunu kullanabilirsiniz."
fi

exit 0
