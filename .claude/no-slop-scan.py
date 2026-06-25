#!/usr/bin/env python3
# noslop PostToolUse guard: warn-only scan for invisible characters and em/en
# dashes that leak from LLM output / copy-paste. NEVER blocks, NEVER fails the
# tool call. Reads the hook JSON on stdin, scans the just-written file, prints a
# warning (systemMessage + additionalContext) only when junk is found. Exits 0.
import json
import os
import re
import sys
from collections import Counter

FLAG = {
    0x200B: "zero-width space",
    0x200C: "zero-width non-joiner",
    0x200D: "zero-width joiner",
    0xFEFF: "BOM/zero-width no-break",
    0x00A0: "non-breaking space",
    0x00AD: "soft hyphen",
    0x200E: "LRM",
    0x200F: "RLM",
    0x2028: "line separator",
    0x2029: "paragraph separator",
}
# Visible style tells: em/en dash. Warn-only, like FLAG. A line that quotes the
# character to describe the rule itself (e.g. "no em dash") is skipped so the
# noslop spell and CLAUDE.md do not warn on their own examples.
DASH = {0x2014: "em dash", 0x2013: "en dash"}
# Word-boundary match so "problem (" / "system (" do not count as an "em (" example.
DASH_SKIP = re.compile(r"\b(?:em|en)\s+(?:dash|\()")
TEXT_EXT = {
    ".md",
    ".txt",
    ".json",
    ".ps1",
    ".cs",
    ".py",
    ".sh",
    ".js",
    ".ts",
    ".yaml",
    ".yml",
    ".html",
    ".css",
    ".csv",
    ".xml",
    ".cfg",
    ".conf",
    ".ini",
    ".toml",
}

try:
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    ti = data.get("tool_input") or {}
    tr = data.get("tool_response") or {}
    fp = ti.get("file_path") or tr.get("filePath")
    if not fp or not os.path.isfile(fp):
        sys.exit(0)
    base = os.path.basename(fp)
    ext = os.path.splitext(fp)[1].lower()
    if ext not in TEXT_EXT and not base.startswith(".gitignore"):
        sys.exit(0)
    hits = []  # (line, name) invisible characters
    dashes = []  # (line, name) em/en dash
    with open(fp, encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            skip_dash = bool(DASH_SKIP.search(line))
            for ch in line:
                cp = ord(ch)
                if cp in FLAG:
                    hits.append((ln, FLAG[cp]))
                elif cp in DASH and not skip_dash:
                    dashes.append((ln, DASH[cp]))
    parts = []
    if hits:
        by_name = Counter(name for _, name in hits)
        lines = sorted({ln for ln, _ in hits})
        summary = ", ".join(f"{n}x {name}" for name, n in by_name.items())
        parts.append(f"invisible characters ({summary}) on lines {lines[:20]}")
    if dashes:
        by_name = Counter(name for _, name in dashes)
        lines = sorted({ln for ln, _ in dashes})
        summary = ", ".join(f"{n}x {name}" for name, n in by_name.items())
        parts.append(f"em/en dash ({summary}) on lines {lines[:20]}")
    if parts:
        msg = (
            f"noslop guard: {base} contains "
            + "; ".join(parts)
            + ". These are machine-assembly tells; use the short hyphen "
            "(-) and strip invisibles before publishing."
        )
        out = {
            "systemMessage": msg,
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": msg,
            },
        }
        print(json.dumps(out))
    sys.exit(0)
except Exception:
    # Never interfere with the tool call, whatever goes wrong.
    sys.exit(0)
