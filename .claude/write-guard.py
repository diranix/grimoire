#!/usr/bin/env python3
# write-guard: deterministic PostToolUse scan on every Write/Edit. Two warn-only
# passes, never blocks, never fails the tool call, always exits 0:
#   1. style tells - invisible characters and em/en dashes that leak from LLM
#      output or copy-paste (the old no-slop-scan job).
#   2. secrets - high-confidence key/token prefixes, private-key blocks, JWTs,
#      and high-entropy values sitting next to a secret keyword.
# This is engine infrastructure, not the noslop spell: the spell is a subjective
# style pass you cast by hand, this hook is a fixed mechanical net that runs
# always. It only nudges - the hard secret block belongs to a pre-commit
# gitleaks pass on the repo. Reads the hook JSON on stdin, scans the just-written
# file, prints a warning (systemMessage + additionalContext) only on a hit.
import json
import math
import os
import re
import sys
from collections import Counter

# --- style pass: invisible characters ---------------------------------------
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

# --- secret pass ------------------------------------------------------------
# High-confidence prefixes and structural markers. Each is shaped so the pattern
# string here does not match itself, and a placeholder/example line is skipped
# below, so this file and the docs that describe these prefixes do not warn.
SECRET_PATTERNS = [
    (re.compile(r"(?:AKIA|ASIA)[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "GitHub token"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"sk-(?:ant-)?[A-Za-z0-9]{20,}"), "API secret key (sk-)"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{35}"), "Google API key"),
    (re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}"), "JWT"),
]
# Entropy path: only flag a long high-entropy value when a secret keyword is on
# the same line. This keyword gate keeps the noise down - infra notes are full of
# hashes, IDs, and base64 blobs that are not secrets.
KEY_HINT = re.compile(
    r"(?i)(?:pass(?:word|wd)?|secret|token|api[_\-]?key|access[_\-]?key|"
    r"client[_\-]?secret|credential|private[_\-]?key|bearer|auth[_\-]?token)"
)
TOKENISH = re.compile(r"[A-Za-z0-9+/=_\-]{16,}")
# Skip a line that is plainly a placeholder or documented example, not a live key.
PLACEHOLDER = re.compile(
    r"(?i)example|redacted|placeholder|changeme|dummy|your[_\-]|xxxx|<[^>]+>|\.\.\."
)

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
    ".env",
}


def shannon(s):
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


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
    if ext not in TEXT_EXT and not base.startswith(".gitignore") and not base.startswith(".env"):
        sys.exit(0)
    hits = []  # (line, name) invisible characters
    dashes = []  # (line, name) em/en dash
    secrets = {}  # line -> set(labels)
    with open(fp, encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            skip_dash = bool(DASH_SKIP.search(line))
            for ch in line:
                cp = ord(ch)
                if cp in FLAG:
                    hits.append((ln, FLAG[cp]))
                elif cp in DASH and not skip_dash:
                    dashes.append((ln, DASH[cp]))
            if PLACEHOLDER.search(line):
                continue  # documented example or placeholder, not a live secret
            for rx, label in SECRET_PATTERNS:
                if rx.search(line):
                    secrets.setdefault(ln, set()).add(label)
            if KEY_HINT.search(line):
                for tok in TOKENISH.findall(line):
                    if len(tok) >= 16 and shannon(tok) >= 3.5:
                        secrets.setdefault(ln, set()).add(
                            "high-entropy value near a secret keyword"
                        )
                        break
    messages = []
    if secrets:
        items = "; ".join(
            f"line {ln}: {', '.join(sorted(v))}" for ln, v in sorted(secrets.items())
        )
        messages.append(
            f"write-guard (secrets): {base} may carry a secret - {items}. "
            "Warn-only. Move it to an env var or a secret store and keep it out of "
            "the note; if it already reached git, rotate it. A pre-commit gitleaks "
            "pass is the real block."
        )
    style_parts = []
    if hits:
        by_name = Counter(name for _, name in hits)
        lines = sorted({ln for ln, _ in hits})
        summary = ", ".join(f"{n}x {name}" for name, n in by_name.items())
        style_parts.append(f"invisible characters ({summary}) on lines {lines[:20]}")
    if dashes:
        by_name = Counter(name for _, name in dashes)
        lines = sorted({ln for ln, _ in dashes})
        summary = ", ".join(f"{n}x {name}" for name, n in by_name.items())
        style_parts.append(f"em/en dash ({summary}) on lines {lines[:20]}")
    if style_parts:
        messages.append(
            f"write-guard (style): {base} contains "
            + "; ".join(style_parts)
            + ". These are machine-assembly tells; use the short hyphen (-) and "
            "strip invisibles before publishing."
        )
    if messages:
        msg = "\n".join(messages)
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
