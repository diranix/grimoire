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

# Engine files LaC owns and refreshes wholesale, including the bundled noslop
# spell (LaC maintains it, it is not user content). Your data is left alone:
# grimoire/, every persona, and any spell you added yourself are never
# overwritten. The one exception is repair: base_persona.md is restored only if
# it is missing. Every replaced file is copied to trash/ first.
SYSTEM_FILES=(
  "limits.md" "commands.md" "CLAUDE.md"
  ".claude/settings.json" ".claude/write-guard.py"
  "spells/noslop/noslop.md"
)

ver() { grep -m1 'version:' "$1" 2>/dev/null | sed 's/[^0-9.]//g' || true; }
local_ver="$(ver "$PROJECT_DIR/llm_compose.md")"

echo "Fetching latest LaC ..."
if ! git clone --depth 1 "$REPO" "$TMP/repo" >/dev/null 2>&1; then
  echo "Cannot reach the repo - offline, or git is unavailable. Nothing changed."
  echo "Local version: ${local_ver:-?}   Repo: $REPO"
  exit 0
fi

repo_ver="$(ver "$TMP/repo/llm_compose.md")"
echo "Local: ${local_ver:-?}   Latest: ${repo_ver:-?}"
[ -f "$TMP/repo/CHANGELOG.md" ] && { echo "----- CHANGELOG -----"; sed -n '1,40p' "$TMP/repo/CHANGELOG.md"; echo "---------------------"; }
[ "$local_ver" = "$repo_ver" ] && { echo "Already up to date. Nothing to do."; exit 0; }

read -r -p "Update to ${repo_ver}? [y/N] " ans
[ "$ans" = "y" ] || { echo "Aborted. Nothing changed."; exit 0; }

BK="$PROJECT_DIR/trash/lac-preupdate-$(date +%F)"; mkdir -p "$BK"
HAS_CHFLAGS=0; command -v chflags >/dev/null 2>&1 && HAS_CHFLAGS=1

# If you OS-locked the L1/L2 files with the macOS immutable flag (chflags uchg),
# clear it to write and put it back after. unlock echoes 1 when it had to clear.
unlock() {
  if [ "$HAS_CHFLAGS" -eq 1 ] && ls -lO "$1" 2>/dev/null | grep -q uchg; then
    chflags nouchg "$1"; echo 1
  fi
}
relock() { if [ "${2:-}" = 1 ]; then chflags uchg "$1"; fi; }

# Copy one repo file over its local twin: back up the old one, keep any uchg lock.
write_file() {
  local f="$1" src="$TMP/repo/$1" dst="$PROJECT_DIR/$1" had
  [ -f "$src" ] || { echo "skip (not in repo): $f"; return; }
  [ -f "$dst" ] && { mkdir -p "$BK/$(dirname "$f")"; cp -p "$dst" "$BK/$f"; }
  had="$(unlock "$dst")"
  mkdir -p "$(dirname "$dst")"; cp "$src" "$dst"
  relock "$dst" "$had"
  echo "updated: $f"
}

for f in "${SYSTEM_FILES[@]}"; do write_file "$f"; done

# Engine files retired or renamed in a past version. Pulling the latest only
# writes the new name, so the stale live copy would sit orphaned next to it (and
# stay writable once settings.json no longer denies it). Back it up and remove
# it. 0.5.1: no-slop-scan.py became write-guard.py.
RETIRED_FILES=( ".claude/no-slop-scan.py" )
for f in "${RETIRED_FILES[@]}"; do
  dst="$PROJECT_DIR/$f"
  [ -e "$dst" ] || continue
  mkdir -p "$BK/$(dirname "$f")"; cp -p "$dst" "$BK/$f"
  unlock "$dst" >/dev/null
  rm -f "$dst"
  echo "removed (retired): $f"
done

# Personas are user space - never overwrite one. Restore base_persona.md only
# when it is missing (a broken install); an edited or replaced persona survives.
BP="personas/base_persona.md"
if [ ! -e "$PROJECT_DIR/$BP" ] && [ -f "$TMP/repo/$BP" ]; then
  mkdir -p "$PROJECT_DIR/personas"; cp "$TMP/repo/$BP" "$PROJECT_DIR/$BP"
  echo "restored (was missing): $BP"
fi

# llm_compose.md is never overwritten wholesale - it carries your ward name and
# persona pointer. Only the version line is bumped in place. A structural change
# (new keys, renamed levels) is rare and goes through the installer path instead.
LC="$PROJECT_DIR/llm_compose.md"
if [ -f "$LC" ] && [ -n "$repo_ver" ]; then
  cp -p "$LC" "$BK/llm_compose.md"
  had="$(unlock "$LC")"
  sed -i.tmp "s/^\(version:[[:space:]]*\).*/\1\"${repo_ver}\"/" "$LC" && rm -f "$LC.tmp"
  relock "$LC" "$had"
  echo "bumped version in llm_compose.md -> ${repo_ver} (ward name and persona kept)"
fi

echo "Done. Backup of replaced files: $BK"
echo "Now run !reboot in the LaC session (or start a fresh one)."
