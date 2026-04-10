#!/bin/bash
# LogosFortuna-Skill SessionStart Hook
# Oturum basinda baglam ozeti yukler

set -euo pipefail

OUTPUT=""

# 1. Son git commit'leri
if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null; then
  RECENT_COMMITS=$(git log --oneline -5 2>/dev/null || echo "Git log alinamadi")
  BRANCH=$(git branch --show-current 2>/dev/null || echo "bilinmiyor")
  UNCOMMITTED=$(git diff --stat 2>/dev/null | tail -1)
  OUTPUT="🔧 LogosFortuna-Skill Baglam Ozeti\n"
  OUTPUT+="━━━━━━━━━━━━━━━━━━━━━━━━\n"
  OUTPUT+="Dal: ${BRANCH}\n"
  if [ -n "$UNCOMMITTED" ]; then
    OUTPUT+="Kaydedilmemis: ${UNCOMMITTED}\n"
  fi
  OUTPUT+="Son commitler:\n${RECENT_COMMITS}\n"
else
  OUTPUT="🔧 LogosFortuna-Skill Baglam Ozeti\n"
  OUTPUT+="━━━━━━━━━━━━━━━━━━━━━━━━\n"
  OUTPUT+="Git: mevcut degil veya git reposu disinda\n"
fi

# 2. Constitution durumu
CONSTITUTION_FILE=".specify/memory/constitution.md"
if [ -f "$CONSTITUTION_FILE" ]; then
  if command -v grep &>/dev/null; then
    VERSION=$(grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' "$CONSTITUTION_FILE" 2>/dev/null | tail -1 || echo "")
  else
    VERSION=""
  fi
  if [ -n "$VERSION" ]; then
    OUTPUT+="Constitution: ${VERSION}\n"
  else
    OUTPUT+="Constitution: mevcut (versiyon okunamadi)\n"
  fi
fi

# 3. Memory durumu - mevcut dizin bazli dinamik yol
PROJECT_HASH=$(echo "$PWD" | sed 's|/|-|g')
MEMORY_DIR="$HOME/.claude/projects/${PROJECT_HASH}/memory"
if [ -d "$MEMORY_DIR" ]; then
  MEMORY_COUNT=$(find "$MEMORY_DIR" -name "*.md" -not -name "MEMORY.md" 2>/dev/null | wc -l | tr -d ' ')
  OUTPUT+="Memory: ${MEMORY_COUNT} kayit\n"
fi

OUTPUT+="━━━━━━━━━━━━━━━━━━━━━━━━\n"
OUTPUT+="Komutlar: /lf (tam dongu) | /lf-anla | /lf-dogrula"

# Cikti olarak goster
if [ -n "$OUTPUT" ]; then
  echo -e "$OUTPUT" >&2
fi

exit 0
