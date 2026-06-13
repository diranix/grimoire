# LaC — LLM as Code

[![version](https://img.shields.io/github/v/tag/diranix/lac?label=version&sort=semver&color=blue)](https://github.com/diranix/lac/releases)
[![license](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE)

A file-based protocol for driving an LLM through structured Markdown. Your rules, commands, context, and memory live on disk — not in a chat history that vanishes. The LLM loads itself from those files, runs commands, and writes state back. One source of truth, version-controllable, editor-agnostic.

> **Status: alpha.** Built for **Claude Code** (terminal CLI or desktop app). Claude Code reads and writes files natively and is scoped to the folder you open, so no Docker, no MCP server, and no memory hook are required. The engine loads automatically every session via `CLAUDE.md`.

> ⚠️ Not accepting contributions at this time.

## How it works

Four layers plus a persistent file store (the Grimoire):

- `llm_compose.md` (L1) — entry point. Defines levels, context, and paths. Immutable, alongside `limits.md`. Loaded automatically every session via `CLAUDE.md`.
- `limits.md` (L1) — immutable rules. The safety and integrity floor.
- `commands.md` (L2) — the command set: `!reboot`, `!save`, `!load`, `!tree`, `!compress`, and more.
- `personas/` (L3) — the engine's personalities, one file per persona (`<name>_persona.md`). The active one is whichever `llm_compose.md` points to — swap by repointing. Since the active persona loads every session, it's also where you record *your own* in-world identity for roleplay (how you're addressed, backstory, relationships) — the engine then knows it from the first message, no `!load` needed.
- `grimoire/` — persistent memory, organized into topic folders.

On boot the engine also scans `grimoire/` and loads its folder tree (directory names only). Knowing the existing topics up front lets the LLM route a conversation into an already-existing folder on `!save` instead of spawning near-duplicate topics.

A chat session is a draft; `!save` is what makes memory canonical. Close the chat — lose nothing that was saved.

To keep token usage in check, a passive size guard watches each topic's `memory.md` on `!load` and `!save`: once it grows past a threshold, the engine suggests `!compress` (condense old session blocks into a digest, keeping recent ones verbatim) or `!cleanup`. Nothing is ever compressed or deleted without an explicit command.

Locked files — `llm_compose.md` and `limits.md` (L1, immutable) plus `commands.md` (L2, admin-only) — are enforced at the tool level via `.claude/settings.json` deny rules, so the engine cannot overwrite its own governance — even if asked.

## Requirements

- **Claude Code** (terminal CLI or the desktop app — both work)
- A dedicated folder for LaC, opened as your Claude Code project (that folder is the LaC root)

That's it. No Docker, no MCP filesystem server, no client memory hook.

## Install

Hand `lac-setup.md` to Claude Code in your LaC folder and tell it to execute the file. It builds the structure, writes `CLAUDE.md` (the auto-boot file), and locks the immutable layer. Full steps live inside `lac-setup.md`.

After install, just start a Claude Code session in that folder — it enters LaC mode on its own. Use `!reboot` to refresh after editing LaC files outside the session.

## License

AGPL-3.0. Commercial licensing available on request.
