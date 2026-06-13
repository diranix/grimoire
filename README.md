# LaC — LLM as Code

A file-based protocol for driving an LLM through structured Markdown. Your rules, commands, context, and memory live on disk — not in a chat history that vanishes. The LLM loads itself from those files, runs commands, and writes state back. One source of truth, version-controllable, editor-agnostic.

> **Status: alpha.** Built for **Claude Code** (terminal CLI or desktop app). Claude Code reads and writes files natively and is scoped to the folder you open, so no Docker, no MCP server, and no memory hook are required. The engine loads automatically every session via `CLAUDE.md`.

> ⚠️ Not accepting contributions at this time.

## How it works

Four layers plus a persistent file store (the Grimoire):

- `llm_compose.md` (L1) — entry point. Defines levels, context, and paths. Immutable, alongside `limits.md`. Loaded automatically every session via `CLAUDE.md`.
- `limits.md` (L1) — immutable rules. The safety and integrity floor.
- `commands.md` (L2) — the command set: `!reload`, `!save`, `!load`, `!tree`, and more.
- `personas/` (L3) — the engine's personalities, one file per persona (`<name>_persona.md`). The active one is whichever `llm_compose.md` points to — swap by repointing.
- `grimoire/` — persistent memory, organized into topic folders.

A chat session is a draft; `!save` is what makes memory canonical. Close the chat — lose nothing that was saved.

Locked files — `llm_compose.md` and `limits.md` (L1, immutable) plus `commands.md` (L2, admin-only) — are enforced at the tool level via `.claude/settings.json` deny rules, so the engine cannot overwrite its own governance — even if asked.

## Requirements

- **Claude Code** (terminal CLI or the desktop app — both work)
- A dedicated folder for LaC, opened as your Claude Code project (that folder is the LaC root)

That's it. No Docker, no MCP filesystem server, no client memory hook.

## Install

Hand `lac-setup.md` to Claude Code in your LaC folder and tell it to execute the file. It builds the structure, writes `CLAUDE.md` (the auto-boot file), and locks the immutable layer. Full steps live inside `lac-setup.md`.

After install, just start a Claude Code session in that folder — it enters LaC mode on its own. Use `!reload` to refresh after editing LaC files outside the session.

## License

AGPL-3.0. Commercial licensing available on request.
