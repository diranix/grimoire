# Grimoire

[![version](https://img.shields.io/github/v/tag/diranix/grimoire?label=version&sort=semver&color=blue)](https://github.com/diranix/grimoire/releases)
[![license](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE)

> **Runs on LaC (LLM as Code).** LaC is a methodology for governing a language model with files instead of trust: a constitution the model loads every session, a tiered file hierarchy where the rules outrank the model, and a command set that writes state back to disk. You don't make the model smarter — you keep it in bounds and give it the right tools. The methodology will get its own home once the runtime proves it; for now it lives here, in the system that runs it.

Grimoire is a file-based knowledge system. Your rules, commands, context, and memory live on disk, not in a chat history that vanishes. The LLM loads itself from those files, runs commands, and writes state back. You keep one source of truth, version it like code, and edit it in any tool.

> **Status: alpha.** Built for **Claude Code** (terminal CLI or desktop app). Claude Code reads and writes files natively and is scoped to the folder you open, so no Docker, no MCP server, and no memory hook are required. The engine loads automatically every session via `CLAUDE.md`.

> ⚠️ Not accepting contributions at this time.

## How it works

Four layers plus a persistent file store (the Grimoire):

- `llm_compose.md` (L1) — entry point. Defines levels, context, and paths. Immutable, alongside `limits.md`. Loaded automatically every session via `CLAUDE.md`.
- `limits.md` (L1) — immutable rules. The safety and integrity floor.
- `commands.md` (L2) — the command set: `!reboot`, `!save`, `!load`, `!search`, `!cast`, `!tree`, `!cleanup`, `!compress`, and more.
- `personas/` (L3) — the engine's personalities, one file per persona (`<name>_persona.md`). The active one is whichever `llm_compose.md` points to — swap by repointing. Since the active persona loads every session, it's also where you record *your own* in-world identity for roleplay (how you're addressed, backstory, relationships) — the engine then knows it from the first message, no `!load` needed.
- `spells/` (L3) — on-demand behavior modules. `!cast <name>` loads a spell (its main file plus any references) into the session and applies it until you start a fresh one; `!spells` lists what you have. A spell shapes how the engine acts, but `limits.md` still outranks it.
- `grimoire/` — persistent memory, organized into topic folders. A topic may nest subtopic folders (each with its own memory file plus any context dumps), so you can load or search one facet of a topic without pulling the rest.

On boot the engine also scans `grimoire/` and loads its folder tree (directory names only). Knowing the existing topics up front lets the LLM route a conversation into an already-existing folder on `!save` instead of spawning near-duplicate topics.

A chat session is a draft; `!save` is what makes memory canonical. Close the chat — lose nothing that was saved.

Each topic is a folder. Its routing file `mem_<name>.md` — a map of where things live plus a light, always-loaded summary — is always there; `tasks.md` (shared across the topic) appears only when there are real tasks. Big topics split into **subtopics**: nested folders that each hold their own `mem_<sub>_<name>.md` plus any context dumps (PDF/docx/images/text) that belong to them. There is no root-level `context/` — every dump lives inside its subtopic and is read-only. `!load topic` pulls just the routing file and lists subtopic names, then answers by **searching** the relevant subtopics on demand (`!search`) instead of loading everything; `!load topic/sub` loads one subtopic fully for hands-on work; `!load topic/all` pulls everything. That way a large topic never floods the context window. Search doesn't match your literal words: the engine expands a query into synonyms, jargon, error strings, and other-language terms first — acting as the embedding at query time, so recall stays semantic with no vectors and no server — and echoes the expanded terms so you can see what it looked for. Each saved block carries a `keywords:` line and each route a keyword cloud, the file-side half of that recall.

As you talk, the engine keeps a **live checkpoint buffer** — a running draft summary held in the session context (never on disk). Decisions are captured the moment they land, so `!save` writes from a buffer that's already complete instead of recapping the whole chat from memory. Since the buffer lives only in context, the engine periodically nudges you to `!save` once decisions pile up — but it never writes without an explicit command.

To keep memory tidy and token usage in check, two separate commands maintain the Grimoire. `!cleanup` is **structural and non-lossy**: it sorts content into the right subtopics, removes duplicates, and prunes completed tasks — so reorganizing never costs you a note. `!compress` is the **lossy** counterpart: it shrinks a topic's memory file, keeping recent session blocks verbatim while digesting older or bloated ones. A passive size guard watches each topic's memory file on `!load` and `!save` and suggests these once it grows past a threshold. Nothing is ever moved, compressed, or deleted without an explicit command, and everything removed is copied to `Trash/`.

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
