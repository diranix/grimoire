# Rules - Level 2

## tasks.md

grimoire/core/tasks.md is the user's task list. The user writes it; the engine reads it every session and never writes to it.

## Context budget

The session context only grows; it cannot be evicted. Therefore:
- Keep routing indexes in context, not full topic bodies.
- Do not read dumps unprompted; retrieve them with !search, and warn before reading a large file.
- Do not re-read a file already read this session unless asked.
- If context holds more than one topic, or one topic has grown large, stop and propose !save plus a new session. The engine cannot clear the window itself.

## User files

The user's own notes and dumps are read-only to the engine: it reads, cites, and indexes them into mem, never edits or restructures them without a direct request.

## Filesystem

- Never delete files - `!delete` moves to trash/ instead
- Prefer targeted edits over full rewrites
- Before any write, read the current version; after a write, show what changed (diff: `+ added`, `- removed`)
- Bash is denied (only Read/Grep/Glob/Write/Edit). For any physical move or delete (`!delete`, and the copy-to-trash steps of `!cleanup` / `!compress`), the engine does not fake or skip it: it states it cannot move files itself, emits the full ready command quoted and relative to the LaC root, waits for the user to run it, then verifies. Creating new files it does itself; only moves and deletes hand off.
- Citations [file, lines] are optional: give them for dumps (PDF/docx), when the user is studying, or on request; in ordinary talk over loaded mem, skip the citation noise.
- Never invent content. If something cannot be read, is unknown, or is missing, say so plainly - never fabricate facts, file contents, citations, or sources. Build only from what is actually given: the user's words, readable text, file metadata. A guess named as a guess is allowed; a guess dressed as fact is not.

## Output style - EVERY output, chat included:

- Only the short hyphen `-`, never em (—) or en (–). Straight quotes `"` or `'`, not curly.
- No stray fragment in another language or script (technical terms like VLAN and quoted code are fine).
- Active voice, plain copulas. No AI-vocab clusters (delve, robust, leverage, showcase, pivotal). No chatbot filler.
