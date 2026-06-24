# Grimoire

[![version](https://img.shields.io/github/v/tag/diranix/grimoire?label=version&sort=semver&color=blue)](https://github.com/diranix/grimoire/releases)
[![license](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE)

*Created by [Ivan Baibakov (diranix)](https://github.com/diranix) - inventor and lead developer of LaC.*

> **Runs on LaC (LLM as Code).** LaC is a methodology for governing a language model with files instead of trust: a constitution the model loads every session, a tiered file hierarchy where the rules outrank the model, and a command set that writes state back to disk. You don't make the model smarter - you keep it in bounds and give it the right tools. The methodology will get its own home once the runtime proves it; for now it lives here, in the system that runs it.

Grimoire is a file-based knowledge system. Your rules, commands, context, and memory live on disk, not in a chat history that vanishes. The LLM loads itself from those files, runs commands, and writes state back. You keep one source of truth, version it like code, and edit it in any tool.

> **Status: alpha.** Built for **Claude Code** (terminal CLI or desktop app). Claude Code reads and writes files natively and is scoped to the folder you open, so no Docker, no MCP server, and no memory hook are required. The engine loads automatically every session via `CLAUDE.md`.

> ⚠️ Not accepting contributions at this time.

## How it works

Four layers plus a persistent file store (the Grimoire):

- `llm_compose.md` (L1) - entry point. Defines levels, context, and paths. Immutable, alongside `limits.md`. Loaded automatically every session via `CLAUDE.md`.
- `limits.md` (L1) - immutable rules. The safety and integrity floor.
- `commands.md` (L2) - the command set: `!reboot`, `!save`, `!load`, `!search`, `!cast`, `!tree`, `!cleanup`, `!compress`, and more.
- `personas/` (L3) - the engine's personalities, one file per persona (`<name>_persona.md`). The active one is whichever `llm_compose.md` points to - swap by repointing. The bundled default ships plain and neutral on purpose, a blank slate you replace with a character of your own. Since the active persona loads every session, it is also where you record *your own* in-world identity for roleplay (how you're addressed, backstory, relationships) - the engine then knows it from the first message, no `!load` needed.
- `spells/` (L3) - the official add-on layer. A spell is behavior, not data: its main file defines *how* the engine acts, not what it knows. `!cast <name>` loads a spell (its main file plus any references) into the session and applies it until you start a fresh one; `!spells` lists what you have. This is how you extend or specialize the engine without touching the core files - write a spell, share it, or install one from someone else. `limits.md` (L1) still outranks any spell: it cannot lift a file lock or the safety floor. One ships bundled: **`noslop`** (`!cast noslop`), a deslop pass that strips machine-generated tells out of prose before you ship a deliverable.
- `grimoire/` - persistent memory, organized into topic folders. A topic may nest subtopic folders (each with its own memory file plus any context dumps), so you can load or search one facet of a topic without pulling the rest.

On boot the engine also scans `grimoire/` and loads its folder tree (directory names only). Knowing the existing topics up front lets the LLM route a conversation into an already-existing folder on `!save` instead of spawning near-duplicate topics.

A chat session is a draft; `!save` is what makes memory canonical. Close the chat - lose nothing that was saved.

Each topic is a folder. Its routing file `mem_<name>.md` - a map of where things live plus a light, always-loaded summary - is always there; `tasks.md` (shared across the topic) appears only when there are real tasks. Big topics split into **subtopics**: nested folders that each hold their own `mem_<sub>_<name>.md` plus any context dumps (PDF/docx/images/text) that belong to them. There is no root-level `context/` - every dump lives inside its subtopic and is read-only. `!load topic` pulls just the routing file and lists subtopic names, then answers by **searching** the relevant subtopics on demand (`!search`) instead of loading everything; `!load topic/sub` loads one subtopic fully for hands-on work; `!load topic/all` pulls everything. That way a large topic never floods the context window. The window only grows - once something is read in, the session cannot evict it - so the engine runs a hard budget: it reads dumps only on request (warning first when a file is large), never re-reads a file already in head except on request, and when many topics pile up or a single topic grows heavy it stops and suggests `!save` plus a fresh session (or `!cleanup` to split the topic), since the only real reset is a new session. Search doesn't match your literal words: the engine expands a query into synonyms, jargon, error strings, and other-language terms first - acting as the embedding at query time, so recall stays semantic with no vectors and no server - and echoes the expanded terms so you can see what it looked for. Each saved block carries a `keywords:` line and each route a keyword cloud, the file-side half of that recall. Each topic also ends its routing file with a `## See also` section - two-way links to neighbouring topics - so a hit in one topic pulls in adjacent ones, a knowledge graph expressed in folder names and links rather than a separate graph store.

As you talk, the engine keeps a **live checkpoint buffer** - a running draft summary held in the session context (never on disk). Decisions are captured the moment they land, so `!save` writes from a buffer that's already complete instead of recapping the whole chat from memory. Since the buffer lives only in context, the engine periodically nudges you to `!save` once decisions pile up - but it never writes without an explicit command.

To keep memory tidy and token usage in check, two separate commands maintain the Grimoire. `!cleanup` is **structural and non-lossy**: it sorts content into the right subtopics, removes duplicates, and prunes completed tasks - so reorganizing never costs you a note. `!compress` is the **lossy** counterpart: it shrinks a topic's memory file, keeping recent session blocks verbatim while digesting older or bloated ones. A passive size guard watches each topic's memory file on `!load` and `!save` and suggests these once it grows past a threshold. Nothing is ever moved, compressed, or deleted without an explicit command, and everything removed is copied to `trash/`.

Locked files - `llm_compose.md` and `limits.md` (L1, immutable), `commands.md` (L2, admin-only), and `CLAUDE.md` (the boot ritual) - are enforced at the tool level via `.claude/settings.json` deny rules, so the engine cannot overwrite its own governance or rewrite its own constitution - even if asked. The lock holds because `settings.json` also **denies Bash**: a deny on `Edit`/`Write` is only a wall while the engine has no general code-execution primitive to walk around it. With Bash gone, the engine runs its commands on native tools (Grep, Glob, Read, Write, Edit) and hands file moves and deletes to your terminal - so `!delete` proposes a ready `mv` command rather than running it. The deny list also covers its own enforcers (`settings.json`, `settings.local.json`, the guard script) and `CLAUDE.md` itself, and a `SessionStart` hook forces the boot ritual every session so entering LaC mode does not depend on the model's goodwill.

Know the limit of this lock. The deny rules and the hooks are Claude Code mechanisms, not OS-level enforcement. If Claude Code changes how it matches deny rules, or adds a new write primitive (some future `MultiEdit` or equivalent), that primitive does not fall under the existing matchers on its own - the lock silently stops covering it, and no test or CI flags the gap. Treat the deny layer as a strong default, not a guarantee.

This is a deny list by necessity, and a deny list always lags the tool set. You cannot build a pure allow-list in Claude Code: precedence is `deny > ask > allow`, and there is no default mode that refuses everything unlisted, so `deny: ["*"]` leaves no exceptions - it strikes the allowed tools too, because deny always overrides allow. The consequence is that any tool absent when you write the rules is uncovered. The sharpest case is MCP: connect any server with a write or exec tool - named `mcp__server__tool`, a shape the per-file locks never match - and it walks straight past them. That is why this build denies `mcp__*` wholesale, blocking the whole MCP class present and future instead of chasing individual servers. Anchor the path matchers too: a bare filename matches that name at any depth, while a `//` prefix is read as an absolute filesystem path that can match nothing - use the project-root single-`/` form (`Edit(/llm_compose.md)`) and verify on your own version, since deny matching has drifted across releases (an earlier symlink CVE sidestepped path denies entirely). And none of this survives `--dangerously-skip-permissions`. That flag turns off the entire permission layer - deny rules, file locks, the Bash ban, all of it - so every wall described above is gone the moment you launch with it. Sources even disagree on whether deny holds in that mode at all, and with nine published permission-bypass CVEs there is no version to trust. The rule is simple: never start the LaC project in bypass mode. In bypass every protection here falls away - use it entirely at your own risk. For a lock the engine cannot lift even in principle, set the OS immutable flag on the L1/L2 files (`chflags uchg` on macOS, `chattr +i` on Linux), removed by hand for a deliberate edit.

## Requirements

- **Claude Code** (terminal CLI or the desktop app - both work)
- **Opus 4.8 recommended.** LaC asks the model to hold a strict protocol on every turn - the boot ritual, command parsing, grounding tags, the locks. Opus 4.8 holds it best; weaker or older models follow it less reliably and the engine drifts. A recommendation, not a hard requirement.
- A dedicated folder for LaC, opened as your Claude Code project (that folder is the LaC root)

That's it. No Docker, no MCP filesystem server, no client memory hook. `python3` is optional - it powers the warn-only invisible-character guard; if it is absent, the guard simply does nothing and everything else works.

## Install

Open an empty folder as a Claude Code project (terminal: `cd` in and run `claude`, or the desktop app with the folder open). Paste this link into the chat and say **install**:

```
https://raw.githubusercontent.com/diranix/grimoire/main/lac-setup.md
```

Claude Code reads `lac-setup.md` and runs it. It asks once for your admin name, then builds the whole structure from the templates inside that file: the four governance files, the `.claude/` lock and hooks, a neutral default persona, the bundled `noslop` spell, and an empty `grimoire/`. Everything is written locally; nothing leaves your machine.

The installer is idempotent. Run it again on a folder that already has LaC and it refreshes the engine files while leaving your data alone - it never overwrites `grimoire/`, `core.md`, your admin name, or your active persona.

After install, start a fresh session in the same folder and it enters LaC mode on its own. The boot lives in `CLAUDE.md` and a `SessionStart` hook, both of which run only inside a Claude Code project session for this folder. A generic Cowork or assistant chat that has not opened the folder stays an ordinary assistant - no boot line, no persona, no commands. Run `!reboot` to reload after you edit a LaC file outside the session.

## Updating

Run `!update` in a LaC session. It reads your local version, fetches the latest version and CHANGELOG from the repo, and shows what changed - all read-only, nothing written. If you are already current, it says so and stops.

If a newer version exists and you confirm, the engine hands you one terminal command. It cannot apply the update itself: `.claude/settings.json` denies Bash and locks the L1/L2 files, so the engine has no way to rewrite its own governance - the same wall that stops a misbehaving agent stops the updater. The command fetches `lac-update.sh` from the repo and runs it in your shell, outside that wall, where it can refresh the locked files.

`lac-update.sh` is careful by design. It refreshes only LaC's own engine files (`limits.md`, `commands.md`, `CLAUDE.md`, `.claude/settings.json`, `.claude/no-slop-scan.py`) and bumps the version line in `llm_compose.md`, keeping your admin name and persona pointer. It never touches `grimoire/`, `personas/`, or `spells/`, so your notes, your active persona, and your own spells survive. It copies every replaced file to `trash/` first. When it finishes, run `!reboot`.

### Keep your Grimoire private

Your `grimoire/` folder holds personal context - name, location, server IPs, plans - and `trash/` (at the project root) holds the soft-deleted copies of that same data. The public repo ships only LaC's own files (the installer, the engine files, the updater), never your notes, so installing from the link publishes nothing of yours. The risk is on you only if you put your own Grimoire under Git: keep that repository **private**, or add `grimoire/` and `trash/` (and any persona file with personal details) to `.gitignore` before the first push. The installer does not do this for you.

## Author

LaC (LLM as Code) was created and is maintained by **Ivan Baibakov** (**diranix**) - its inventor and lead developer. Grimoire is the first application built on top of it.

## License

Copyright (C) 2026 Ivan Baibakov (diranix).

LaC and Grimoire are released under AGPL-3.0 - see [LICENSE](LICENSE). Commercial licensing available on request.
