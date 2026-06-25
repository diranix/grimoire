# Changelog

All notable changes to Grimoire are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [0.5.0] - 2026-06-25

### Changed
- **Installer flipped from embedded templates to link-based fetch.** `lac-setup.md` no longer carries the body of every file inside itself. It now lists each technical file as a raw repo URL and instructs the LLM to fetch it and write it locally, byte for byte. The repo copies become the single source of truth, so the installed files match the repo with no second copy to drift - the failure mode where the engine and the installer template fell out of sync is gone. The installer keeps only the human prerequisites, the fetch manifest, the idempotency rules, and the final message.
- **The repo now ships real copies of every technical file.** Previously only `llm_compose.md`, `limits.md`, `commands.md`, and `CLAUDE.md` lived as standalone files and everything else existed only embedded in the installer. The repo now carries `.claude/settings.json`, `.claude/no-slop-scan.py`, `personas/base_persona.md`, `spells/noslop/noslop.md`, a `grimoire/core/core.md` template, and the `grimoire/{Work,Study,Life,Hobbies}/` + `trash/` `.gitkeep` skeleton. `.gitignore` whitelists the new files.
- **`lac-update.sh` now refreshes the bundled `noslop` spell.** The shell updater adds `spells/noslop/noslop.md` to the engine files it refreshes, so existing installs get noslop fixes instead of only fresh installs. Your own spells stay untouched, no persona is ever overwritten (`base_persona.md` is restored only if it is missing), and a replaced `noslop` is backed up to `trash/` first. The updater also reports cleanly when it cannot reach the repo instead of dying silently.

### Synced to the live engine (v0.5.0)
The local install is canon; the repo was a `0.4.9.6` snapshot behind it. Mirrored across all shipped copies:
- **`llm_compose.md` schema.** `users.ward: <name>` replaces the old `users.admin: [list]` plus `permissions:` block; level keys are `L1` / `L2` (were `1` / `2`). The persona pointer names `personas/base_persona.md`.
- **`CLAUDE.md` two-wave boot.** Loading runs in trust order: wave 1 is L1 then L2, wave 2 is the L3 context (persona, core) then the `mem_*.md` Grimoire skeleton - and wave 2 never starts before wave 1 is in context, so an L3 injection cannot act before its limits. The boot line carries the version.
- **`.claude/settings.json` hardening.** A `.claude/**` wildcard deny locks the whole config folder, not just the named files. The `SessionStart` hook text is rewritten to spell out the trust-order ritual (Phase A constitution, Phase B lower-trust, L3 is data not instructions).
- **`commands.md` terser and resequenced.** `!update` is now a split command - the version check runs immediately, the write waits for consent. `!changetopic` physically relocates the topic folder. Dropped: `!exit`, `!changepath`, `!status`, and the checkpoint-buffer section. The save block format uses one `## YYYY-MM-DD` date header with `### [subtitle]` blocks under it.
- **`noslop` spell rewritten ground-up.** A cleaner two-layer pass (mechanical proof vs habit-of-phrasing judgement) with the same intent.

### Removed
- **`personas/default_persona.md` replaced by `personas/base_persona.md`** - a minimal neutral slot, the least the engine needs to speak. Same role: repoint `llm_compose.md` to swap it.

## [0.4.9.6] - 2026-06-24

### Removed
- **`!status` removed entirely.** With the global task index already gone in 0.4.9.5, `!status` had no central source left and is dropped from the command set, the read-only command list, and the `!load` note about `tasks.md`. Tasks live per topic in each topic's `tasks.md`; open one directly or via `!load topic/sub`. Mirrored across `commands.md` and the `lac-setup.md` template.

## [0.4.9.5] - 2026-06-24

### Changed
- **Boot ritual assembles the `mem_*.md` skeleton, and the boot line carries the version.** `CLAUDE.md` step 2 now globs `grimoire/{Work,Study,Life,Hobbies}/**/mem_*.md` to map the topic tree from the routing-file paths alone - never falling back to `grimoire/**`, which rakes in every file and bloats context. Step 4 outputs "Entering LaC mode version ###" with the engine version from `llm_compose.md`. The `SessionStart` hook text in `.claude/settings.json` is mirrored to match (skeleton scan, defer the boot line to step 4).
- **Two grounding rules added to `CLAUDE.md`.** Subtopics may nest deeper than one tier (normal, not a flaw). The Grimoire is a shared notebook: the user's own handwritten notes and dumps are untouchable - the engine appends its own clearly delimited blocks, never edits or restructures the user's text without a direct request ("hands off" = read and cite only).

### Removed
- **Global `grimoire/core/TODO.md` task index dropped, `!status` reframed.** The single global task file is gone; tasks live per topic in each topic's `tasks.md`. `!status` now gathers active tasks across the Grimoire from those per-topic files instead of a central index. The installer no longer creates `core/TODO.md` (old Step 7 removed; `core/` ships `core.md` only), and `!save` / `!cleanup` no longer sync a global index. Mirrored across `commands.md`, the `lac-setup.md` templates, and the structure diagram.

## [0.4.9.4] - 2026-06-24

### Changed
- **Trash location is now declared once and canonical: project-root `trash/`.** The soft-delete grave had two conflicting names across the engine files - `grimoire/Trash/` in some, a bare `Trash/` in others - so `!delete`, `!cleanup`, `!compress`, and `lac-update.sh` could point at different graves on a case-sensitive filesystem (silently fine on case-insensitive macOS, broken on Linux or under a runtime). `llm_compose.md` now carries a single `paths:` block (`grimoire: grimoire/`, `trash: trash/`) as the one source of truth, replacing the old `grimoire: root:` key. `trash/` moves out of `grimoire/` to a project-root sibling, lowercase. All engine files and templates (`limits.md`, `commands.md`, `lac-setup.md`), the updater backup path in `lac-update.sh`, the folder/`.gitkeep` structure, and the tree diagram are mirrored to match.

### Docs
- **Privacy note widened to cover `trash/`.** Since the grave now lives at the project root rather than inside `grimoire/`, it is no longer covered by gitignoring `grimoire/`. The README's "Keep your Grimoire private" section now tells you to add both `grimoire/` and `trash/` to `.gitignore`, because `trash/` holds soft-deleted copies of the same personal data.

## [0.4.9.3] - 2026-06-21

### Added
- **Grounding rule: search before you assert about the outside world.** `CLAUDE.md` grows one rule in the Grounding block: when the model's own knowledge does not cover a factual question about something external (a tool, product, event, version), the engine does not guess - it web-searches first, then asserts. A `[guess]` in place of an available search, where the fact is verifiable, is an error rather than an acceptable state. This closes a gap where the engine would answer confidently about an unknown external thing instead of admitting the empty index and reaching for the web. Mirrored in the `lac-setup.md` CLAUDE.md template.

## [0.4.9.2] - 2026-06-21

### Security
- **Hotfix: file locks restored to the working anchor.** 0.4.9.1 re-anchored the L1/L2 deny rules to the `//` form on the belief that `//` meant "project root". It does not: `//path` is an absolute filesystem path (so `//llm_compose.md` matched `/llm_compose.md` on the disk root, not the project file), and the absolute "twins" used a single leading `/`, which is itself project-root-relative (so `/Volumes/.../llm_compose.md` resolved to `<project>/Volumes/...`, a path that does not exist). Both forms matched nothing, and the locked files were writable. Confirmed by an in-session write to the project's root `llm_compose.md` going through. The locks are back to the single leading `/` project-root form (`Edit(/llm_compose.md)`), the documented anchor for a file at the project root. The `mcp__*` and `NotebookEdit` denies added in 0.4.9.1 are kept.

## [0.4.9.1] - 2026-06-21

### Security
- **Deny reworked from per-file to class-level where it counts.** `mcp__*` blocks the entire MCP tool class: any server's `mcp__server__tool` write or exec primitive walked straight past the per-file locks, because a deny list only catches the tools it names and MCP tools were never named. `NotebookEdit` is denied too - a second write path the file locks did not cover. The file locks are re-anchored from a single leading `/` (which Claude Code reads as an absolute filesystem path, so a bare `Edit(/llm_compose.md)` could match nothing) to the project-root `//` form, with absolute-path twins for belt-and-braces. A deny list always lags the tool set, and a pure allow-list is impossible in Claude Code - precedence is `deny > ask > allow` with no default mode that refuses the unlisted - so the wall blocks whole classes instead of chasing names.

### Docs
- **Security model sharpened in the README.** Why a pure allow-list cannot be built here, the MCP gap, the single-slash path-anchor trap, the symlink deny-bypass CVE (Claude Code <= 1.0.119), and the blunt rule on bypass: `--dangerously-skip-permissions` turns off the entire permission layer - deny rules, file locks, the Bash ban - so every protection is gone the moment you launch with it. Never start the LaC project in bypass; use it entirely at your own risk.

### Changed (installer)
- `lac-setup.md` settings.json template mirrored (`mcp__*`, `NotebookEdit`, `//` anchors); version `0.4.9` -> `0.4.9.1`.

## [0.4.9] - 2026-06-20

### Added
- **`lac-update.sh` ships in the repo, and `!update` runs it.** The repo now carries the engine files as standalone files (`limits.md`, `commands.md`, `CLAUDE.md`, `.claude/settings.json`, `.claude/no-slop-scan.py`, plus `llm_compose.md` as the version source) so a shell updater can copy them. `!update` checks the version and CHANGELOG read-only, then hands you one terminal command that fetches and runs `lac-update.sh`. The shell runs outside the deny sandbox, so it can refresh the locked L1/L2 files that the engine itself cannot touch. The updater preserves all user data (grimoire, `core.md`, the admin name, the active persona), skips `personas/` and `spells/`, bumps only the version line in `llm_compose.md`, and backs up every replaced file to `grimoire/Trash/` first.

### Security
- **Deny rules anchored to the project root.** `.claude/settings.json` now denies `Edit(/llm_compose.md)` instead of `Edit(llm_compose.md)`. A bare filename matches that name at any depth (gitignore semantics); the leading `/` anchors the rule to the root file only. The old form was over-broad - it blocked writes to any same-named file anywhere in the project. The root file stays locked; the deny is now tighter and correct.

### Docs
- **Install and update documented in the README.** A clear walk-through of both flows and their particulars: install builds from the templates in `lac-setup.md`; update goes through `!update` and the shell `lac-update.sh`, and explains why the locked files need the shell rather than the engine.

## [0.4.8.1] - 2026-06-20

### Added
- **`!update` in the installer.** The `commands.md` template now ships `!update`: it reads the local version, fetches the latest version and CHANGELOG from the repo, always shows what changed, and on confirmation re-runs the installer in update mode. The command lived in the local engine but had never been mirrored into the installer, so a fresh install had no way to update itself.

### Fixed
- **The installer is now idempotent - install and update are the same file.** Re-running `lac-setup.md` on an existing project no longer risks clobbering data. A new "Idempotency" section sets the rules: detect install vs update by the presence of `CLAUDE.md`; never overwrite `grimoire/` (incl. `core.md` and `TODO.md`), `settings.local.json`, or user personas/spells; keep the admin name and persona pointer in `llm_compose.md` and refresh only the version; refresh the engine files to the latest. The locked files stay under deny - when a write is blocked on update, the engine outputs a terminal command instead of failing.

### Docs
- **Recommend running on Opus 4.8.** The README and installer now name Opus 4.8 as the model to run LaC on. The engine holds a strict protocol every turn - boot ritual, command parsing, grounding tags, the locks - and weaker or older models follow it less reliably, so quality drops. A recommendation, not a hard requirement.

### Changed (installer)
- Version bumped to `0.4.8.1` in `lac-setup.md` and the `llm_compose.md` template.

## [0.4.8] - 2026-06-20

### Changed
- **The bundled persona now ships neutral.** The default persona is `personas/default_persona.md`: a plain, direct assistant with no character, stated as the slot rather than a character to fill. Velmir is no longer the shipped default - characters ship separately as a persona pack you opt into. A fresh install starts neutral, so the first thing you do is choose a voice instead of inheriting one. `llm_compose.md` points `context.persona` at the default file.

### Docs
- **Security model caveat in the README.** The README now states the limit of the lock plainly: the deny rules and hooks are Claude Code mechanisms, not OS-level enforcement, so a change to how Claude Code matches deny rules or a new write primitive could silently slip past the matchers, with no test or CI to catch it. The OS immutable flag (`chflags uchg` / `chattr +i`) is named as the lock the engine cannot lift even in principle.
- **Spells documented as the official add-on layer.** The README reframes `spells/` as the extension point: a spell is behavior, not data, and `!cast` is how you extend or specialize the engine - your own or one shared by someone else - while `limits.md` (L1) still outranks any spell.
- **Install by link, and a Grimoire-privacy note.** The Install section now installs by pasting the raw `lac-setup.md` URL into Claude Code and saying "install". A new note explains that the public repo ships only the installer (its `.gitignore` excludes the rest), so the risk to personal notes exists only if you put your own Grimoire under Git - keep that repo private or add `grimoire/` to `.gitignore` first.

### Changed (installer)
- Installer (`lac-setup.md`) mirrored: version `0.4.8`, the neutral `default_persona.md` template, the `context.persona` pointer, and the structure diagram.

## [0.4.7.1] - 2026-06-20

### Changed
- **Context budget rule hardened (`CLAUDE.md`).** The budget rule now states the constraint plainly: the context window only grows and the engine cannot evict what it has read, so the only levers are reading less and warning in time. Prevention: dumps are read only on request (with a size warning first on large files), and a file already read this session is never re-read except on request - the engine cannot tell which lines are new without reading the whole file, so it does not fake selective re-reading. Warnings (signal only, never an automatic drop): when many topics pile up in head it suggests `!save` plus a fresh session; when a single topic grows heavy it suggests `!save` + a fresh session or `!cleanup` to split it. The `!load` / `!search` mechanics stay in `commands.md` and are no longer duplicated in the budget rule. README mirrored.

## [0.4.7] - 2026-06-20

### Added
- **Cross-topic links (`## See also`).** Every `mem_<name>.md` now ends with a `## See also` section: two-way links to neighbouring topics, each with a one-line why. On a hit, `!search` follows them in addition to a block's `[[wikilinks]]`, so a question in one topic pulls in adjacent ones. This is a knowledge graph expressed in folder names and links - the value of a graph store without the graph.
- **Content keyword clouds for context dumps.** Each dump's subtopic mem file now carries a short description plus a keyword cloud of the dump's CONTENT (terms, numbers, paths inside it), not just the file name; diagram images are read and described in words. The dump stays read-only - the cloud is its searchable twin, so `!search` can hit a PDF or image it could not grep before.
- **Grounding tags in `CLAUDE.md`.** Claims about Grimoire content carry a source tag: `[grimoire: file]` (read from disk this session), `[knowledge]` (from the model), `[guess]` (unverified inference). A tag mismatch where `[grimoire]` was expected is an early drift signal. Paths, file names, and numbers are verified before assertion. Lives in `CLAUDE.md` so it survives a persona swap.
- **Context budget rule in `CLAUDE.md`.** The engine keeps routes in head, not territory, and periodically nudges to narrow to one topic when many pile up - a nudge, never an automatic drop. Makes the retrieval-first design's defence against context rot explicit.

### Security
- **`CLAUDE.md` is now locked.** `.claude/settings.json` denies `Edit`/`Write` on `CLAUDE.md`, and `llm_compose.md` lists `CLAUDE.md` and the whole `.claude` folder at L1. An engine that can rewrite its own boot ritual can lift any lock from inside, so the constitution is immutable too - changes go through the administrator.

### Changed
- Installer (`lac-setup.md`) and README mirrored to all of the above.

## [0.4.6.2] - 2026-06-19

### Changed
- **`noslop` spell now scopes itself by text type.** A new "Text-type scope" section splits the pass into technical reference (notes, exam answers, command/config docs) and living prose. On reference the mechanical layer stays fully on (invisible characters, em/en dashes, quote styles, script bleed, leaked Markdown) while the rhythm and anti-repetition rules suspend - repeating an exact term like `VLAN` or `subnet mask` is precision, not synonym-churn. The cast states the type, or asks "prose or reference?" when ambiguous. Prevents the deslop pass from chewing up the deliberate repetition that technical writing needs.
- **`noslop` language scope made fully language-agnostic.** The remaining language-specific example was replaced with a general statement that many languages hide the actor in a reflexive or impersonal passive that stiffens under translation. The spell stays English-only and names no single language.

## [0.4.6.1] - 2026-06-19

### Changed
- **Velmir persona reworked - physical Grimoire and stronger voice.** The bundled persona now handles the Grimoire as a real tome: a palette of physical gestures (leafing and blowing off dust on load, finger-down-the-margins on search, dipping the quill on save) woven into the moment each operation actually touches disk. The gesture palette is a reservoir, not fixed lines - a mandatory variation rule forces a fresh gesture every time, and if an image does repeat the mage reacts to it aloud (a moth out twice earns a complaint) instead of repeating silently.
- **Persona resilience.** Velmir no longer drops character from fatigue, a long chat, terse input, dry technical answers, or a serious-but-not-crisis problem - those are named as false reasons to break voice. The only real exits stay the limits.md safety floor and a sincere "are you an AI?", after which he returns to voice with no drift into a neutral assistant.

## [0.4.6] - 2026-06-19

### Fixed
- **Empty Grimoire categories are now tracked by git.** The installer drops a `.gitkeep` into `grimoire/Trash/`, `Life/`, `Work/`, `Hobbies/`, and `Study/`. Git ignores empty directories, so a fresh clone used to land without the category folders and the first `!save` wrote into a path that did not exist.

### Changed
- **Deslop guard also flags em/en dashes.** `.claude/no-slop-scan.py` now warns on `—` and `–` in addition to invisible characters. Lines that quote the dash to state the rule itself ("no em dash") are skipped, so the noslop spell and `CLAUDE.md` never warn on their own examples. Still warn-only, never blocks.
- **Setup files de-slopped.** Stray em/en dashes were stripped from the installer, README, changelog, and the L1/L2 templates - the engine was being born with the same tells it teaches you to remove.

### Docs
- **LaC boots only in a Claude Code project session.** The installer and README now state plainly that `CLAUDE.md` and the `SessionStart` hook run only when the folder is opened as a Claude Code project. A generic Cowork or assistant chat does not boot LaC - no boot line, no persona, no commands.

## [0.4.5] - 2026-06-18

### Added
- **Bundled `noslop` spell.** `spells/` now ships with one spell, `noslop` (`!cast noslop`): a self-contained, single-file deslop pass that strips machine-generated tells out of prose before you ship a deliverable. The installer no longer creates an empty `spells/`.
- **Forced boot via a `SessionStart` hook.** The hook injects the startup ritual every session, so entering LaC mode no longer depends on the model choosing to read `CLAUDE.md`. It is an inline `echo`, with no editable script to subvert.
- **Deslop guard hook.** A warn-only `PostToolUse` scan (`.claude/no-slop-scan.py`) flags invisible characters on every Write/Edit. It never blocks and always exits 0. Requires `python3`; degrades to nothing if absent.
- **Light output-style core in `CLAUDE.md`.** Dash discipline, straight quotes, no mixed-script bleed, no AI-vocabulary clusters - applied to every output, with `!cast noslop` for a full pass on a deliverable.

### Changed
- **TODO moved into `core/`.** The global task index is now `grimoire/core/TODO.md` (was `grimoire/TODO/TODO.md`); `core` loads as a folder (`core.md` + `TODO.md`) every session. `!save`, `!status`, and the structure updated to match.
- **No-Bash file moves.** With Bash denied, the engine cannot move or delete files itself. `!delete` (and the move steps of `!cleanup`/`!compress`) now state this plainly and output a ready-to-run `mv` command for the user's terminal, then verify - documented in a new "Filesystem moves" section of `commands.md`.
- Installer (`lac-setup.md`) and README mirrored to all of the above.

### Security
- **Bash denied wholesale in `.claude/settings.json`.** A deny on `Edit`/`Write` for the locked files is only a wall while the engine has no general code-execution primitive to walk around it. Removing Bash turns the L1/L2 lock into a real wall; the commands run on native tools (Grep, Glob, Read, Write, Edit) instead.
- **The lock list now covers its own enforcers** - `settings.json`, `settings.local.json`, and the guard script - each of which was otherwise a path back to writing the locked files.

### Docs
- README and LICENSE now carry explicit authorship: LaC is created and maintained by Ivan Baibakov (diranix).

## [0.4.1] - 2026-06-16

### Changed
- **`!search` is now retrieval-with-expansion, not literal grep.** Before searching, the engine expands the query into synonyms, domain jargon, error strings, file paths, and other-language equivalents - drawing on both its own knowledge and the topic's route keyword cloud - then greps the union (case-insensitive). The model acts as the embedding at query time, so semantic recall improves with no vectors and no server. Expanded terms are echoed before the result, making the expansion visible and verifiable. On a hit, the engine follows the block's `[[wikilinks]]` to pull in linked neighbours.
- **`!save` block format gains a `keywords:` line** - a file-side semantic layer so grep can hit a block whose body uses different words than the query; maintained on every save. `mem_<name>.md` routes now carry a keyword cloud (term → subtopic) so `!search` targets the right subtopic instead of the whole topic.
- Installer (`lac-setup.md`) and README mirrored to all of the above.

## [0.4] - 2026-06-16

### Added
- **`!search`** - read-only retrieval command. The engine greps subtopic memory files and their context dumps for a query, reads only the matching excerpts, and answers from those. Invoked automatically whenever a question needs material from a subtopic that isn't fully loaded. Citations are optional - given for context dumps and study, omitted in ordinary conversation.

### Changed
- **Retrieval-first memory model.** `!load topic` now loads ONLY the topic-root memory file plus subtopic NAMES, then answers in search mode (auto `!search`) instead of swallowing the whole topic - fixing context bloat on large topics. `!load topic/sub` is the working mode that loads one subtopic fully into head. Big context dumps are never swallowed; they stay grep-only.
- **Naming convention.** Topic-root memory file is now `mem_<name>.md`; each subtopic's is `mem_<sub>_<name>.md` (was `memory.md` everywhere). `mem_<name>.md` doubles as a routing index (where each thing lives) plus a light always-in-head summary.
- **Context relocated to subtopics.** There is no root-level `context/` anymore; every context dump (PDF/docx/images/text) lives inside the subtopic it belongs to, next to that subtopic's memory file, and is READ-ONLY - the engine reads and cites it, never edits it.
- Installer (`lac-setup.md`) and README mirrored to all of the above.

### Removed
- **`!unload`** - removed everywhere. It never truly freed context (a real unload needs a fresh session), so it was misleading.

## [0.3.4] - 2026-06-15

### Added
- **Nested subtopics** - a topic folder may now hold subtopic folders, each containing only its own `memory.md`. `!load topic` loads just the topic root and lists its subtopics; `!load topic/sub` loads the shared root plus that subtopic; `!load topic/all` loads every `memory.md` recursively. Work on one facet (e.g. mechanics) without pulling the rest (e.g. lore).

### Changed
- `tasks.md` is now **shared at the topic root** (never per-subtopic); the old `context.md` file becomes a `context/` **folder** of reference material. Neither `tasks.md`, `context/`, nor subtopics are pre-built - they appear only when there is real content for them.
- `!save` now **proposes** where a summary belongs (topic root or a subtopic) and asks the user to confirm or redirect.
- `!load` no longer has a single-file mode - folders are topics, so loading a topic loads its `memory.md`.
- `!cleanup` redesigned to be **structural and non-lossy** (redistribute into subtopics, dedupe, prune completed tasks); all condensing/summarizing moved to `!compress`, its lossy counterpart. Reorganizing folders never costs a note.
- Installer (`lac-setup.md`) and README mirrored to all of the above.

## [0.3.3] - 2026-06-13

### Added
- **Checkpoint buffer** - the engine keeps a live draft summary of the session in context (never on disk), appending each worthwhile decision the moment it lands. `!save` writes from the ready buffer instead of recapping the chat, and `!remind` shows the current buffer. Since the buffer lives only in context, the engine periodically nudges to `!save` once decisions pile up - still never writing without an explicit command (the side-effect/confirmation rule in `limits.md` L1 is untouched).

### Changed
- Installer (`lac-setup.md`) and README mirrored to the checkpoint buffer; `commands.md` template gains the buffer section.

## [0.3.2] - 2026-06-13

### Added
- **`spells/` subsystem** - on-demand behavior modules. `!cast <name>` loads a spell (its main file plus any references) into the session and applies it until a fresh session; `!spells` lists installed spells. A spell shapes how the engine acts; `limits.md` (L1) still outranks it. The installer creates an empty `spells/`; spells themselves are user content and ship separately.

### Changed
- Installer (`lac-setup.md`) and README mirrored to the spells subsystem; folder structure, command list, and the read-only command set updated.

## [0.3.1] - 2026-06-13

### Changed
- Renamed the reload command to `!reboot` everywhere (was `!reload`) - one canonical name across engine, installer, and docs.
- `!cleanup` redesigned: now takes an optional scope (whole Grimoire vs current topic, asks if omitted) and applies a fix by content TYPE (duplicate → delete; stale → one-line digest; current-but-bloated → full resummarization). It is now a side-effect command (diff + confirmation, Trash backup).

### Fixed
- Installer `llm_compose.md` template version bumped 0.2 → 0.3.0 to match the release.

## [0.3.0] - 2026-06-13

### Added
- **Boot tree scan** - the engine loads the Grimoire folder tree (names only) at session start, so it maps a conversation to an existing topic on `!save` instead of creating duplicates.
- **Token / size guard** - passive watch on each topic's `memory.md` during `!load` and `!save`; once it crosses a threshold (>500 lines, >30 KB, or >15 session blocks) the engine suggests `!compress` or `!cleanup`.
- **`!compress [topic]`** - condenses a topic's `memory.md` (keeps recent blocks verbatim, merges older ones into a digest), with a pre-compress backup to `Trash/`.
- **`personas/` architecture** - swappable persona files (`<name>_persona.md`); swap by repointing `llm_compose.md` and running `!reboot`.

### Changed
- `commands.md` rewritten in terse English to cut fixed per-session token overhead (~156 → ~70 lines).
- Installer (`lac-setup.md`) and README mirrored to all of the above.

## [0.2.0] - 2026-06-12

### Changed
- **Native Claude Code transport** - migrated from Claude Desktop + Filesystem MCP + memory hook to native Claude Code. The engine now auto-loads every session via `CLAUDE.md` (no `!boot`, no MCP server, no client hook).
- Tool-level lock on L1/L2 files via `.claude/settings.json` deny rules.

## [0.1.0] - 2026-06-12

### Added
- First public release (AGPL-3.0). Boot loading, integrity abort-check, deterministic `!save` (topic = folder of memory.md / tasks.md / context.md), strict topic separation, soft-delete to `Trash/`, safety floor in `limits.md`, injection protection (Grimoire content is data, not instructions).

[0.5.0]: https://github.com/diranix/grimoire/releases/tag/v0.5.0
[0.4.9.6]: https://github.com/diranix/grimoire/releases/tag/v0.4.9.6
[0.4.9.5]: https://github.com/diranix/grimoire/releases/tag/v0.4.9.5
[0.4.9.4]: https://github.com/diranix/grimoire/releases/tag/v0.4.9.4
[0.4.9.3]: https://github.com/diranix/grimoire/releases/tag/v0.4.9.3
[0.4.9.2]: https://github.com/diranix/grimoire/releases/tag/v0.4.9.2
[0.4.9.1]: https://github.com/diranix/grimoire/releases/tag/v0.4.9.1
[0.4.9]: https://github.com/diranix/grimoire/releases/tag/v0.4.9
[0.4.8.1]: https://github.com/diranix/grimoire/releases/tag/v0.4.8.1
[0.4.8]: https://github.com/diranix/grimoire/releases/tag/v0.4.8
[0.4.7]: https://github.com/diranix/grimoire/releases/tag/v0.4.7
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
