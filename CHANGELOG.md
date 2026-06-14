# Changelog

All notable changes to LaC are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

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

[0.3.3]: https://github.com/diranix/grimoire/releases/tag/v0.3.3
[0.3.2]: https://github.com/diranix/grimoire/releases/tag/v0.3.2
[0.3.1]: https://github.com/diranix/grimoire/releases/tag/v0.3.1
[0.3.0]: https://github.com/diranix/grimoire/releases/tag/v0.3.0
[0.2.0]: https://github.com/diranix/grimoire/releases/tag/v0.2.0
[0.1.0]: https://github.com/diranix/grimoire/releases/tag/v0.1.0
