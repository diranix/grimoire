#!/usr/bin/env bash
# LaC updater. Run from the root of your LaC project: bash lac-update.sh
# Refreshes the engine files from the repo, idempotently, WITHOUT touching your
# data. The engine cannot run this itself (Bash is denied) - !update hands you
# the command and you run it here, outside the deny sandbox, so it can rewrite
# the locked L1/L2 files legitimately.
set -euo pipefail

REPO="https://github.com/diranix/grimoire.git"
PROJECT_DIR="$(pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# Engine files LaC owns and refreshes wholesale. NONE of the user's content is
# here: grimoire/, personas/, and spells/ are never touched, so your notes,
# your active persona, and your own spells survive every update.
SYSTEM_FILES=(
  "limits.md" "commands.md" "CLAUDE.md"
  ".claude/settings.json" ".claude/no-slop-scan.py"
)

echo "Fetching latest LaC ..."
git clone --depth 1 "$REPO" "$TMP/repo" >/dev/null 2>&1

ver() { grep -m1 'version:' "$1" 2>/dev/null | sed 's/[^0-9.]//g' || true; }
local_ver="$(ver "$PROJECT_DIR/llm_compose.md")"
repo_ver="$(ver "$TMP/repo/llm_compose.md")"
echo "Local: ${local_ver:-?}   Latest: ${repo_ver:-?}"

[ -f "$TMP/repo/CHANGELOG.md" ] && { echo "----- CHANGELOG -----"; sed -n '1,40p' "$TMP/repo/CHANGELOG.md"; echo "---------------------"; }

[ "$local_ver" = "$repo_ver" ] && { echo "Already up to date. Nothing to do."; exit 0; }

read -r -p "Update to ${repo_ver}? [y/N] " ans
[ "$ans" = "y" ] || { echo "Aborted. Nothing changed."; exit 0; }

BK="$PROJECT_DIR/trash/lac-preupdate-$(date +%F)"; mkdir -p "$BK"
HAS_CHFLAGS=0; command -v chflags >/dev/null 2>&1 && HAS_CHFLAGS=1

write_file() {  # $1 = path relative to both repo and project root
  local f="$1" src="$TMP/repo/$1" dst="$PROJECT_DIR/$1"
  [ -f "$src" ] || { echo "skip (not in repo): $f"; return; }
  [ -f "$dst" ] && { mkdir -p "$BK/$(dirname "$f")"; cp -p "$dst" "$BK/$f"; }
  local had_uchg=0
  if [ "$HAS_CHFLAGS" -eq 1 ] && ls -lO "$dst" 2>/dev/null | grep -q uchg; then
    chflags nouchg "$dst"; had_uchg=1
  fi
  mkdir -p "$(dirname "$dst")"; cp "$src" "$dst"
  [ "$had_uchg" -eq 1 ] && chflags uchg "$dst"
  echo "updated: $f"
}

for f in "${SYSTEM_FILES[@]}"; do write_file "$f"; done

# llm_compose.md is NEVER overwritten wholesale - it carries the admin name and
# the persona pointer (your choices). Only the version line is bumped in place.
LC="$PROJECT_DIR/llm_compose.md"
if [ -f "$LC" ] && [ -n "$repo_ver" ]; then
  mkdir -p "$BK"; cp -p "$LC" "$BK/llm_compose.md"
  had_uchg=0
  if [ "$HAS_CHFLAGS" -eq 1 ] && ls -lO "$LC" 2>/dev/null | grep -q uchg; then
    chflags nouchg "$LC"; had_uchg=1
  fi
  sed -i.tmp "s/^\(version:[[:space:]]*\).*/\1\"${repo_ver}\"/" "$LC" && rm -f "$LC.tmp"
  [ "$had_uchg" -eq 1 ] && chflags uchg "$LC"
  echo "bumped version in llm_compose.md -> ${repo_ver} (admin name and persona kept)"
fi

echo "Done. Backup of replaced files: $BK"
echo "Now run !reboot in the LaC session (or start a fresh one)."
