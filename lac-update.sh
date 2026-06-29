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
  "limits.md" "commands.md" "rules.md" "CLAUDE.md"
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

# map.md is the route map - user data, never overwritten. But it is a file LaC
# introduced, so restore an empty template only when missing (an install from
# before the map existed), giving boot a map to load until the next !save
# reconciles it. An existing map is left untouched.
MAP="grimoire/core/map.md"
if [ ! -e "$PROJECT_DIR/$MAP" ] && [ -f "$TMP/repo/$MAP" ]; then
  mkdir -p "$PROJECT_DIR/grimoire/core"; cp "$TMP/repo/$MAP" "$PROJECT_DIR/$MAP"
  echo "restored (was missing): $MAP"
fi

# llm_compose.md carries two user choices - the admin name and the persona
# pointer - but the rest is engine-owned and can change structurally between
# versions (removed keys, renamed levels). Refresh it from the repo, then
# re-inject the two local values, so a structural change propagates without losing
# them. This replaces the old version-only bump, which left structural edits behind.
LC="$PROJECT_DIR/llm_compose.md"
if [ -f "$LC" ] && [ -f "$TMP/repo/llm_compose.md" ]; then
  admin_line="$(grep -m1 '^[[:space:]]*admin:' "$LC" || true)"
  persona_line="$(grep -m1 '^[[:space:]]*persona:' "$LC" || true)"
  cp -p "$LC" "$BK/llm_compose.md"
  had="$(unlock "$LC")"
  cp "$TMP/repo/llm_compose.md" "$LC"
  [ -n "$admin_line" ] && { sed -i.tmp "s|^[[:space:]]*admin:.*|${admin_line}|" "$LC"; rm -f "$LC.tmp"; }
  [ -n "$persona_line" ] && { sed -i.tmp "s|^[[:space:]]*persona:.*|${persona_line}|" "$LC"; rm -f "$LC.tmp"; }
  relock "$LC" "$had"
  echo "refreshed llm_compose.md -> ${repo_ver} (admin name and persona kept)"
fi

echo "Done. Backup of replaced files: $BK"
echo "Now run !reboot in the LaC session (or start a fresh one)."
echo
echo "----- Grimoire format note -----"
echo "This update refreshes the ENGINE only - it never rewrites your notes."
echo "Notes written before 0.5.0 may use the old block format (no 'keywords:'"
echo "line, single '## date' header). They still load, but !search hits them"
echo "worse without a keywords line. To bring a topic to the current standard,"
echo "do it yourself or ask the LLM in a session, e.g.:"
echo "  \"migrate <topic> to the current block format (add a keywords line to"
echo "   each block, back up to trash first, show a diff, wait for my OK)\"."
echo "--------------------------------"
