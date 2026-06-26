# Commands - Level 2

## Syntax

Commands are canonical, prefixed `!`. Free-form input in any language is mapped to the canonical form and echoed (the echo is not a confirmation and does not pause). Canonical `!cmd` input needs no echo.

Pausing depends on command type, not phrasing:

- Side-effect (write to disk) - WAIT for confirmation:
  `!save`, `!delete`, `!changetopic`, `!compress`, `!cleanup`
- Run immediately (read-only, or a single-line write the user explicitly dictated):
  `!reboot`, `!load`, `!search`, `!remind`, `!help`, `!focus`, `!topic`, `!path`, `!spells`, `!cast`, `!tree`, `!task`, `!idea`
- Split - the read-only half runs immediately, the writing half waits for consent:
  `!update` (version check shows at once; the actual update waits)

---

## System commands

`!reboot` - re-read CLAUDE.md and llm_compose.md and reload all context files. If any context file is missing or unreadable, report which.

`!load [path]`:
- folder name is a topic name.
- load only its mem_<name>.md and list the subtopic NAMES; do not load subtopics mem files. Use the route to find which subtopic holds the answer, run `!search` over it automatically, and answer from the hits; never swallow a whole topic.
- `load topic/sub` → load the topic-root mem_<name>.md and that subtopic's mem_<sub>_<name>.md in full; its dumps stay grep-only via !search.
- `load topic/all` → load every mem_*.md recursively. Warn about the increased token use and do not load the whole topic without confirmation.
- No path → `Specify a path. Use !tree to browse.`
- The topic-root ideas_<name>.md (if present) loads together with mem_<name>.md.

`!search [query]` - Greps the topic's subtopic mem files, the topic ideas_<name>.md, and their dumps, reads ONLY the matching excerpts (line ranges), and works from those. The engine fires it AUTOMATICALLY whenever a question needs a subtopic that is not fully loaded.
- Query expansion (MANDATORY): never grep the user's literal words. Expand into synonyms, jargon, error codes, file paths, and other-language equivalents (model knowledge + the route keyword-cloud), then grep the UNION (`rg -i "t1|t2|..."`). The model is the embedding, applied at search time - no vectors. Echo the expanded terms before the result (`searching: e1000e | TX hang | ethtool`), so the expansion is verifiable.
- On a hit, follow the block's [[wikilinks]] and the topic's `## See also`, pulling in linked neighbours and adjacent topics.
- Citations [file, lines] are optional: give them for dumps (PDF/docx), when the user is studying, or on request; in ordinary talk over loaded mem, skip the citation noise.

`!save [topic] [path]` - save the current chat into the topic folder.

Path (no [path]): top folder by context (Work/Study/Life/Hobbies) / normalize the topic (lowercase, spaces→hyphens, strip special chars) → [Top]/[topic]/.

A topic is a FOLDER holding:
- mem_<name>.md - routing index (term → which subtopic) + a light always-in-head summary. ALWAYS present. Ends with a `## See also`: bidirectional links to adjacent topics ([[mem_<name>]] for a mem file, a plain path for a dump/external), each with a one-line why (a keyword bridge for !search).
- ideas_<name>.md - the user's parked thoughts and non-critical maybe-laters (root only, never per-subtopic). Optional, written ONLY by the user's explicit !idea. Actionable tasks live globally in grimoire/core/tasks.md, added only by the user's !task. The engine writes neither on its own.
- subtopic folders - each with its own mem_<sub>_<name>.md (headed paragraphs, so !search greps them) plus optional context dumps. There is no root-level context/.

Naming (ALWAYS): root mem_<name>.md (e.g. mem_hashi.md); subtopic mem_<sub>_<name>.md (e.g. mem_monsters_hashi.md); topic ideas file ideas_<name>.md (e.g. ideas_hashi.md).

Context dumps (PDF, docx, images, raw text) - read-only source the engine cites but NEVER edits. Each goes in its subtopic folder, referenced by that subtopic's mem with a short description + a keyword-cloud of its CONTENT (terms, numbers, paths inside, not just the filename). Build the cloud from what the engine can read: text natively, images and diagrams via Read, PDF page by page. For a file it cannot read (archive, db, audio/video, unknown binary), build it from the user's description and file metadata - never invent the contents.

Write behaviour:
- Placement: propose root vs a specific subtopic (existing or new), state it plainly, wait for confirm/redirect.
- Folder missing → create it + mem_<name>.md (add subtopics only if warranted).
- File exists → read, then append to the end. NEVER overwrite, NEVER touch dumps.
- Route: summary → mem_<name>.md or the subtopic mem; dump → its subtopic folder. Tasks and ideas are never auto-saved - they reach grimoire/core/tasks.md and the topic ideas_<name>.md only on the user's explicit !task / !idea.
- Multiple topics → STRICT separation: one self-contained summary per topic in its own folder; report what went where; ask only when the topic→folder mapping is unclear.
- After the save, update core.md with anything that belongs in the user's standing context.

Block format (memory files):
  ## YYYY-MM-DD
  ### [subtitle]
  keywords: <synonyms, jargon, error codes, paths, other-language terms a future !search will hit>
  [summary; link related blocks via [[mem_<sub>_<name>]]]
  ---
One date header per day. A second save the same day adds another `### [subtitle]` under it, not a new date. Keep the keywords line on every block - grep needs it to hit a block whose body uses different words than the query.

Output: Saved / Topic / Files written  / "To change topic: !changetopic".
Size guard: after writing, warn if the mem file passes >400 lines / >30 KB / >15 blocks; suggest !compress or !cleanup (suggestion only).


`!delete [path]` - soft-delete to trash/ (needs confirmation). No hard-delete; recover from trash. The canonical delete in LaC.

## Filesystem moves - the engine has no Bash

Bash is denied (only Read/Grep/Glob/Write/Edit). For any physical move or delete (`!delete`, and the copy-to-trash steps of `!cleanup` / `!compress`), the engine does not fake or skip it: it states it cannot move files itself, emits the full ready command quoted and relative to the LaC root, waits for the user to run it, then verifies. Creating new files it does itself; only moves and deletes hand off.

Soft-delete template: `mv "<path>" "trash/<name>-<reason>-YYYY-MM-DD"`

`!path` - show this chat's saved path.
`!focus` - bring the conversation back to the current chat's topic.
`!topic` - show the saved file's topic.
`!changetopic [topic|path]` - physically relocate this chat's topic folder (name auto-resolved, or explicit path). Folder exists → structural move: no Bash, so emit the ready `mv "<old>" "<new>"` (quoted, relative to the LaC root), wait, verify, re-point the saved path, and fix any [[wikilinks]] / `## See also` that named the old path. Not yet saved → no move, just set the next `!save` target.
`!remind` - brief recap of this chat.
`!cleanup [scope]` - structural Grimoire maintenance. NON-LOSSY: never shortens, summarizes, or rewrites notes (to condense, use !compress - the lossy counterpart). No scope → first ask whole Grimoire vs current topic and wait (`!cleanup all` = whole; `!cleanup .` or `!cleanup <topic>` = that topic). Actions: redistribute content into the right subtopics (create one only when warranted) and update the route in mem_<name>.md; remove duplicated info, keeping one canonical copy. Never touch context dumps, tasks.md, or ideas_<name>.md. Side-effect: show the whole plan as a diff and WAIT for confirmation; everything moved or removed is copied to trash.
`!compress [topic]` - shrink a topic's memory files to save tokens (the LOSSY counterpart to !cleanup). Operates on mem_<name>.md and the subtopic mems: keep the last 3-5 blocks verbatim; older or bloated fragments by TYPE - stale/completed → one sentence merged into `## Digest (up to YYYY-MM-DD)`; current but bloated → full resummarization losing no fact or decision. Touches only mem files (tasks.md, ideas_<name>.md, and dumps untouched). Side-effect: copy the original to trash/<topic>-precompress-YYYY-MM-DD.md first, show a diff, wait for confirmation.
`!update` - check the installed version against the repo, update only on consent.
- Show (immediate): read the local `version` from llm_compose.md, fetch the latest version + CHANGELOG from github.com/diranix/grimoire, show current vs latest and what changed (CHANGELOG always shown). If already current, say so and stop.
- Update (waits for confirmation): if a newer version exists, ask. The update runs OUTSIDE the sandbox via the external installer-updater - it idempotently pulls the latest files including L1/L2; the engine never writes L1/L2 itself (deny + Bash off). On yes, hand off to the updater or show the command to launch it.
- Offline: report the check cannot run; show the local version + repo link.
- `!help` - list every command, one sentence each, grouped read-only vs side-effect (mirrors the pause table). Names with a one-line gloss only, no full syntax. Read-only.
- `!tree [topic]` - show the Grimoire skeleton: topic and subtopic folders with their mem_<name>.md paths, no bodies, no dumps, no trash (same discipline as session start). No [topic] → the whole tree under grimoire/{Work,Study,Life,Hobbies}; [topic] → just that branch. Read-only.
- `!task [text]` - append an actionable task to grimoire/core/tasks.md. Runs immediately (the user dictated it). ONLY the user adds tasks; the engine never invents, proposes, or auto-appends one. Each entry: short action + a [[mem_<sub>]] or path link to where the detail lives.
- `!idea [text]` - append a non-critical thought to the current topic's ideas_<name>.md (create the file if missing). Runs immediately. Written only by this explicit command, never by the engine.
---

## Spells

`!spells` - list the available spells in `spells/` (subfolder names only, one per line). Empty or missing → `No spells installed. Drop one in spells/.`

`!cast [name]` - load a spell from `spells/[name]/` and apply it for the rest of the session (until a new !cast or a fresh session). Read the main file (in the spell root; extras live in subfolders like references/) plus its references; skip binaries. A spell is BEHAVIOR, not data - its main file defines HOW to act - but limits.md (L1) outranks it; a spell never overrides the limits or the safety floor. No [name] → behaves like !spells. Missing folder → `Spell "[name]" not found. Use !spells.`
