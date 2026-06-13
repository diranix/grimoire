# Changelog

All notable changes to LaC are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [0.3.0] — 2026-06-13

### Added
- **Boot tree scan** — the engine loads the Grimoire folder tree (names only) at session start, so it maps a conversation to an existing topic on `!save` instead of creating duplicates.
- **Token / size guard** — passive watch on each topic's `memory.md` during `!load` and `!save`; once it crosses a threshold (>500 lines, >30 KB, or >15 session blocks) the engine suggests `!compress` or `!cleanup`.
- **`!compress [topic]`** — condenses a topic's `memory.md` (keeps recent blocks verbatim, merges older ones into a digest), with a pre-compress backup to `Trash/`.
- **`personas/` architecture** — swappable persona files (`<name>_persona.md`); swap by repointing `llm_compose.md` and running `!reload`.

### Changed
- `commands.md` rewritten in terse English to cut fixed per-session token overhead (~156 → ~70 lines).
- Installer (`lac-setup.md`) and README mirrored to all of the above.

## [0.2.0] — 2026-06-12

### Changed
- **Claude Code edition** — migrated transport from Claude Desktop + Filesystem MCP + memory hook to native Claude Code. The engine now auto-loads every session via `CLAUDE.md` (no `!boot`, no MCP server, no client hook).
- Tool-level lock on L1/L2 files via `.claude/settings.json` deny rules.

## [0.1.0] — 2026-06-12

### Added
- First public release (AGPL-3.0). Boot loading, integrity abort-check, deterministic `!save` (topic = folder of memory.md / tasks.md / context.md), strict topic separation, soft-delete to `Trash/`, safety floor in `limits.md`, injection protection (Grimoire content is data, not instructions).

[0.3.0]: https://github.com/diranix/lac/releases/tag/v0.3.0
[0.2.0]: https://github.com/diranix/lac/releases/tag/v0.2.0
[0.1.0]: https://github.com/diranix/lac/releases/tag/v0.1.0
