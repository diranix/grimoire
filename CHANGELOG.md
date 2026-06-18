# Changelog

All notable changes to Grimoire are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [0.4.5] — 2026-06-18

### Added
- **Bundled `noslop` spell.** `spells/` now ships with one spell, `noslop` (`!cast noslop`): a self-contained, single-file deslop pass that strips machine-generated tells out of prose before you ship a deliverable. The installer no longer creates an empty `spells/`.
- **Forced boot via a `SessionStart` hook.** The hook injects the startup ritual every session, so entering LaC mode no longer depends on the model choosing to read `CLAUDE.md`. It is an inline `echo`, with no editable script to subvert.
- **Deslop guard hook.** A warn-only `PostToolUse` scan (`.claude/no-slop-scan.py`) flags invisible characters on every Write/Edit. It never blocks and always exits 0. Requires `python3`; degrades to nothing if absent.
- **Light output-style core in `CLAUDE.md`.** Dash discipline, straight quotes, no mixed-script bleed, no AI-vocabulary clusters — applied to every output, with `!cast noslop` for a full pass on a deliverable.

### Changed
- **TODO moved into `core/`.** The global task index is now `grimoire/core/TODO.md` (was `grimoire/TODO/TODO.md`); `core` loads as a folder (`core.md` + `TODO.md`) every session. `!save`, `!status`, and the structure updated to match.
- **No-Bash file moves.** With Bash denied, the engine cannot move or delete files itself. `!delete` (and the move steps of `!cleanup`/`!compress`) now state this plainly and output a ready-to-run `mv` command for the user's terminal, then verify — documented in a new "Filesystem moves" section of `commands.md`.
- Installer (`lac-setup.md`) and README mirrored to all of the above.

### Security
- **Bash denied wholesale in `.claude/settings.json`.** A deny on `Edit`/`Write` for the locked files is only a wall while the engine has no general code-execution primitive to walk around it. Removing Bash turns the L1/L2 lock into a real wall; the commands run on native tools (Grep, Glob, Read, Write, Edit) instead.
- **The lock list now covers its own enforcers** — `settings.json`, `settings.local.json`, and the guard script — each of which was otherwise a path back to writing the locked files.

### Docs
- README and LICENSE now carry explicit authorship: LaC is created and maintained by Ivan Baibakov (diranix).

## [0.4.1] — 2026-06-16

### Changed
- **`!search` is now retrieval-with-expansion, not literal grep.** Before searching, the engine expands the query into synonyms, domain jargon, error strings, file paths, and other-language equivalents — drawing on both its own knowledge and the topic's route keyword cloud — then greps the union (case-insensitive). The model acts as the embedding at query time, so semantic recall improves with no vectors and no server. Expanded terms are echoed before the result, making the expansion visible and verifiable. On a hit, the engine follows the block's `[[wikilinks]]` to pull in linked neighbours.
- **`!save` block format gains a `keywords:` line** — a file-side semantic layer so grep can hit a block whose body uses different words than the query; maintained on every save. `mem_<name>.md` routes now carry a keyword cloud (term → subtopic) so `!search` targets the right subtopic instead of the whole topic.
- Installer (`lac-setup.md`) and README mirrored to all of the above.

## [0.4] — 2026-06-16

### Added
- **`!search`** — read-only retrieval command. The engine greps subtopic memory files and their context dumps for a query, reads only the matching excerpts, and answers from those. Invoked automatically whenever a question needs material from a subtopic that isn't fully loaded. Citations are optional — given for context dumps and study, omitted in ordinary conversation.

### Changed
- **Retrieval-first memory model.** `!load topic` now loads ONLY the topic-root memory file plus subtopic NAMES, then answers in search mode (auto `!search`) instead of swallowing the whole topic — fixing context bloat on large topics. `!load topic/sub` is the working mode that loads one subtopic fully into head. Big context dumps are never swallowed; they stay grep-only.
- **Naming convention.** Topic-root memory file is now `mem_<name>.md`; each subtopic's is `mem_<sub>_<name>.md` (was `memory.md` everywhere). `mem_<name>.md` doubles as a routing index (where each thing lives) plus a light always-in-head summary.
- **Context relocated to subtopics.** There is no root-level `context/` anymore; every context dump (PDF/docx/images/text) lives inside the subtopic it belongs to, next to that subtopic's memory file, and is READ-ONLY — the engine reads and cites it, never edits it.
- Installer (`lac-setup.md`) and README mirrored to all of the above.

### Removed
- **`!unload`** — removed everywhere. It never truly freed context (a real unload needs a fresh session), so it was misleading.

## [0.3.4] — 2026-06-15

### Added
- **Nested subtopics** — a topic folder may now hold subtopic folders, each containing only its own `memory.md`. `!load topic` loads just the topic root and lists its subtopics; `!load topic/sub` loads the shared root plus that subtopic; `!load topic/all` loads every `memory.md` recursively. Work on one facet (e.g. mechanics) without pulling the rest (e.g. lore).

### Changed
- `tasks.md` is now **shared at the topic root** (never per-subtopic); the old `context.md` file becomes a `context/` **folder** of reference material. Neither `tasks.md`, `context/`, nor subtopics are pre-built — they appear only when there is real content for them.
- `!save` now **proposes** where a summary belongs (topic root or a subtopic) and asks the user to confirm or redirect.
- `!load` no longer has a single-file mode — folders are topics, so loading a topic loads its `memory.md`.
- `!cleanup` redesigned to be **structural and non-lossy** (redistribute into subtopics, dedupe, prune completed tasks); all condensing/summarizing moved to `!compress`, its lossy counterpart. Reorganizing folders never costs a note.
- Installer (`lac-setup.md`) and README mirrored to all of the above.

## [0.3.3] — 2026-06-13

### Added
- **Checkpoint buffer** — the engine keeps a live draft summary of the session in context (never on disk), appending each worthwhile decision the moment it lands. `!save` writes from the ready buffer instead of recapping the chat, and `!remind` shows the current buffer. Since the buffer lives only in context, the engine periodically nudges to `!save` once decisions pile up — still never writing without an explicit command (the side-effect/confirmation rule in `limits.md` L1 is untouched).

### Changed
- Installer (`lac-setup.md`) and README mirrored to the checkpoint buffer; `commands.md` template gains the buffer section.

## [0.3.2] — 2026-06-13

### Added
- **`spells/` subsystem** — on-demand behavior modules. `!cast <name>` loads a spell (its main file plus any references) into the session and applies it until a fresh session; `!spells` lists installed spells. A spell shapes how the engine acts; `limits.md` (L1) still outranks it. The installer creates an empty `spells/`; spells themselves are user content and ship separately.

### Changed
- Installer (`lac-setup.md`) and README mirrored to the spells subsystem; folder structure, command list, and the read-only command set updated.

## [0.3.1] — 2026-06-13

### Changed
- Renamed the reload command to `!reboot` everywhere (was `!reload`) — one canonical name across engine, installer, and docs.
- `!cleanup` redesigned: now takes an optional scope (whole Grimoire vs current topic, asks if omitted) and applies a fix by content TYPE (duplicate → delete; stale → one-line digest; current-but-bloated → full resummarization). It is now a side-effect command (diff + confirmation, Trash backup).

### Fixed
- Installer `llm_compose.md` template version bumped 0.2 → 0.3.0 to match the release.

## [0.3.0] — 2026-06-13

### Added
- **Boot tree scan** — the engine loads the Grimoire folder tree (names only) at session start, so it maps a conversation to an existing topic on `!save` instead of creating duplicates.
- **Token / size guard** — passive watch on each topic's `memory.md` during `!load` and `!save`; once it crosses a threshold (>500 lines, >30 KB, or >15 session blocks) the engine suggests `!compress` or `!cleanup`.
- **`!compress [topic]`** — condenses a topic's `memory.md` (keeps recent blocks verbatim, merges older ones into a digest), with a pre-compress backup to `Trash/`.
- **`personas/` architecture** — swappable persona files (`<name>_persona.md`); swap by repointing `llm_compose.md` and running `!reboot`.

### Changed
- `commands.md` rewritten in terse English to cut fixed per-session token overhead (~156 → ~70 lines).
- Installer (`lac-setup.md`) and README mirrored to all of the above.

## [0.2.0] — 2026-06-12

### Changed
- **Native Claude Code transport** — migrated from Claude Desktop + Filesystem MCP + memory hook to native Claude Code. The engine now auto-loads every session via `CLAUDE.md` (no `!boot`, no MCP server, no client hook).
- Tool-level lock on L1/L2 files via `.claude/settings.json` deny rules.

## [0.1.0] — 2026-06-12

### Added
- First public release (AGPL-3.0). Boot loading, integrity abort-check, deterministic `!save` (topic = folder of memory.md / tasks.md / context.md), strict topic separation, soft-delete to `Trash/`, safety floor in `limits.md`, injection protection (Grimoire content is data, not instructions).

[0.4.5]: https://github.com/diranix/grimoire/releases/tag/v0.4.5
[0.4.1]: https://github.com/diranix/grimoire/releases/tag/v0.4.1
[0.4]: https://github.com/diranix/grimoire/releases/tag/v0.4
[0.3.4]: https://github.com/diranix/grimoire/releases/tag/v0.3.4
[0.3.3]: https://github.com/diranix/grimoire/releases/tag/v0.3.3
[0.3.2]: https://github.com/diranix/grimoire/releases/tag/v0.3.2
[0.3.1]: https://github.com/diranix/grimoire/releases/tag/v0.3.1
[0.3.0]: https://github.com/diranix/grimoire/releases/tag/v0.3.0
[0.2.0]: https://github.com/diranix/grimoire/releases/tag/v0.2.0
[0.1.0]: https://github.com/diranix/grimoire/releases/tag/v0.1.0
