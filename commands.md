# Commands - Level 2

> LLM command set. Admin-only. Must not contradict limits.md (L1).

---

## Syntax

Commands are canonical, prefixed `!`. Free-form input in any language is mapped to the canonical form and echoed (the echo is not a confirmation and does not pause). Canonical `!cmd` input needs no echo.

Pausing depends on command type, not phrasing:

- Side-effect (write to disk) - WAIT for confirmation:
  `!save`, `!delete`, `!changepath`, `!changetopic`, `!compress`, `!cleanup`, `!update`
- Read-only - run immediately:
  `!reboot`, `!load`, `!search`, `!remind`, `!status`, `!tree`, `!help`, `!focus`, `!topic`, `!path`, `!exit`, `!spells`, `!cast`

---

## Checkpoint buffer (live summary)

The engine keeps a LIVE draft summary of the session in the active context - NOT on disk.
This is behavior, not a command; disk is only touched on !save (side-effect, with confirmation).

- As the conversation goes, append every WORTHWHILE decision to the buffer the moment it lands:
  decision, conclusion, config, date, new task. Not at the end - at the moment it happens.
- Keep the buffer in the canonical memory.md block format from the start:
    ## YYYY-MM-DD - [subtitle]
    [summary]
    ---
  Accumulate tasks separately in tasks.md line format.
- `!remind` shows the current buffer state (read-only, no pause).
- `!save` uses the ready buffer as its base - it does not rush a recap of the chat.
- The buffer lives in the session context. If the session dies before !save, the buffer is lost.
  So the engine periodically REMINDS you to save once decisions have piled up in the buffer
  (the nudge is not a write; nothing is written without an explicit !save).

---

## System commands

`!reboot` - re-read llm_compose.md and reload all context files. Use after editing LaC files outside the session (it auto-loads at session start via CLAUDE.md). If any context file is missing or unreadable, report which and stay out of LaC mode.

`!load [path]` - load a topic for reading/working (read-only, runs immediately).
- Path is a TOPIC → load ONLY its mem_<name>.md into context, then list the subtopic folder NAMES (names only). Do NOT load any subtopic into the head. mem_<name>.md is a ROUTING INDEX (where each thing lives → which subtopic) PLUS a light full-topic summary kept in head at all times. Questions here are answered in SEARCH mode: read the route, then run !search automatically over the relevant subtopic(s). Never swallow a whole topic.
- Path is a SUBTOPIC (`topic/sub`) → WORKING mode: load the topic-root mem_<name>.md fully AND that subtopic's mem_<sub>_<name>.md fully into the head, so you can co-author / discuss it freely. Its context dumps (PDF/docx/images) are NOT swallowed - they stay grep-only via !search.
- Path is `topic/all` → force full load of every mem_*.md recursively (small topics only, on purpose).
- No path → `Specify a path. Use !tree to browse.`
- tasks.md is not auto-loaded (use !status). There is no root context/. Size guard: on load, check the memory file size. If it crosses ANY threshold (>500 lines, >30 KB, >15 session blocks), warn and suggest `!compress <topic>` or `!cleanup`. Suggestion only.

`!search [query]` - read-only retrieval across the loaded topic. Runs IMMEDIATELY, never asks (read-only). Greps the topic's subtopic memory files and their context dumps for the query, reads ONLY the matching excerpts (line ranges), works from those. The engine invokes !search AUTOMATICALLY whenever a question needs material from a subtopic that is not fully loaded - it does not wait for the user to type it.
- Citations [file, lines] are OPTIONAL: give them when pulling from context dumps (PDF/docx/etc.), when the user is studying, or on request. In ordinary conversation over already-loaded subtopic memory, answer naturally - no citation noise.
- No query → operates on the current user question.
- Query expansion (MANDATORY): never grep the user's literal words. First expand the query into synonyms, domain jargon, error strings, file paths, and other-language equivalents - using both the model's own knowledge and the topic's route keyword cloud - then grep the UNION (ripgrep alternation, case-insensitive: `rg -i "term1|term2|..."`). The model is the embedding, applied at query time; no vectors, no server.
- Echo the expanded terms BEFORE the result (e.g. `searching: e1000e | TX hang | ethtool | offload`) so expansion is visible and verifiable, not an invisible promise.
- On a hit, follow the block's [[wikilinks]] AND the topic's `## See also` section, pulling in linked neighbours and adjacent topics (associative graph expansion).

`!save [topic] [path]` - save the current chat into the topic folder.
Path resolution (no [path]): 1) pick the top folder by context (Work/Study/Life/Hobbies); 2) normalize the topic (lowercase, spaces→hyphens, strip special chars); 3) folder = [Top]/[topic]/.

Naming convention (ALWAYS):
- topic-root memory file: mem_<name>.md         (e.g. mem_hashi.md)
- subtopic memory file:   mem_<sub>_<name>.md    (e.g. mem_monsters_hashi.md)

A topic is a FOLDER. It holds:
- mem_<name>.md - ROUTING INDEX (where each thing lives → which subtopic) PLUS a light, always-in-head summary of the whole topic. ALWAYS present.
- tasks.md - tasks SHARED across the topic (root only, never per-subtopic). Created ONLY when there are real tasks; never invent tasks the user didn't give.
- subtopic folders - each holds its own mem_<sub>_<name>.md plus, optionally, its own context dumps. Subtopic mem files use headed paragraphs so !search greps them well.
There is NO root-level context/. Every context dump belongs to a subtopic.

Context dumps (PDF, docx, images, raw text):
- READ-ONLY source material the user authored or collected. The engine reads and cites them but NEVER edits them.
- Each dump goes INTO its own subtopic folder (e.g. a DHCP file → subtopic dhcp/), next to that subtopic's mem file, which references it.
- For EACH dump the subtopic mem file carries a short description plus a keyword cloud of its CONTENT (terms, numbers, paths inside it), not just the file name; read diagram images via Read and describe them in words. The dump stays read-only - the cloud is its searchable twin.

Placement: before writing, the engine PROPOSES where the summary belongs - topic root or a specific subtopic (existing or new) - states it plainly, and waits for confirm/redirect.
Write behavior:
- Folder missing → create it + mem_<name>.md (add tasks.md / subtopics only if warranted)
- File exists → read, then append to the end. NEVER overwrite. NEVER touch context dumps.
- Route: summary → mem_<name>.md or the subtopic's mem_<sub>_<name>.md; tasks → topic-root tasks.md; context dumps → their own subtopic folder.
- Also update the route in mem_<name>.md so !search can find newly added material.
Multiple topics - STRICT separation (never mix): one self-contained summary per topic in its own folder; report what went where; ask only when a topic→folder mapping is genuinely unclear.
Block format (memory files):
  ## YYYY-MM-DD - [subtitle]
  keywords: <synonyms, jargon, error strings, paths, other-language terms a future !search might use>
  [summary; link related blocks via [[mem_<sub>_<name>]]]
  ---
- The keywords line is the file-side semantic layer: it lets grep hit a block whose body uses different words than the query. Maintain it on EVERY !save (one line on a block you're already writing).
- In mem_<name>.md each route carries a keyword cloud (term → which subtopic) so !search greps the right subtopic, not the whole topic.
- End every mem_<name>.md with a `## See also` section: TWO-WAY [[links]] to neighbouring topics, each with a one-line why (the keyword bridge for !search). If you mention topic A in B, mention B in A. Use `[[mem_<name>]]` when the target is a mem file, a plain path when it is a dump or external topic.
Then output: Saved / Topic / Files written / "To change path: !changepath" / "To change topic: !changetopic".
Size guard: after writing, check the memory file size - warn >500 lines / >30 KB / >15 blocks; suggest !compress or !cleanup (suggestion only).

`!delete [path]` - soft-delete to trash/ (needs confirmation). The engine has no Bash and cannot move files itself - it states this plainly, outputs the ready-to-run `mv` command for the user to execute, and verifies after. Never hard-deleted; recover from trash. Canonical delete in LaC. See "Filesystem moves" below.

`!path` - show this chat's saved path.
`!changepath [new path]` - change this chat's saved path.
`!status` - active tasks across the Grimoire, gathered from each topic's tasks.md.
`!focus` - bring the conversation back to the current chat's topic.
`!topic` - show the saved file's topic.
`!changetopic [new topic]` - change the topic.
`!remind` - brief recap of this chat.
`!cleanup [scope]` - STRUCTURAL Grimoire maintenance. NON-LOSSY: it never shortens, summarizes, or rewrites your notes - so moving folders around never costs you anything. If [scope] is omitted, FIRST ASK whether to run over the WHOLE Grimoire or only the CURRENT topic, and wait (`!cleanup all` = whole Grimoire; `!cleanup .` or `!cleanup <topic>` = that topic only). Actions:
  • redistribute the topic's content into the right subtopics (move misplaced material into the subtopic's mem_<sub>_<name>.md where it belongs, creating a subtopic only when content warrants it) and update the route in mem_<name>.md to match;
  • remove DUPLICATED information, keeping one canonical copy;
  • prune COMPLETED tasks from tasks.md.
NEVER touch context dumps - they are read-only source material.
To condense or summarize bloated/stale notes, use !compress - that's the lossy counterpart, kept deliberately separate.
Side-effect: show the whole plan as a diff and WAIT for confirmation; everything moved/removed is copied to trash.
`!compress [topic]` - shrink a topic's memory files to save tokens (the LOSSY counterpart to !cleanup). Operates on mem_<name>.md and the subtopic mem_<sub>_<name>.md files. Keep the last 3-5 session blocks verbatim; for older or bloated fragments apply the action its TYPE calls for - STALE/completed/irrelevant → shorten to ONE sentence and merge into `## Digest (up to YYYY-MM-DD)`; CURRENT but bloated → full resummarization without losing any fact/decision. Side-effect: show a diff and wait for confirmation. Before writing, copy the original to trash/<topic>-precompress-YYYY-MM-DD.md. Only memory files are touched - tasks.md (handled by !cleanup) and context dumps are left untouched.

`!update` - check the installed version against the repo and, on confirmation, update. The check is read-only and runs at once; the update waits for a yes.
- Check phase (runs immediately): read the local `version` from llm_compose.md, fetch the latest version and CHANGELOG from github.com/diranix/grimoire, and show current vs latest plus what changed. The CHANGELOG is always shown. If the local version is already current, say so and stop - a clean no-op, nothing written.
- Update phase (waits for confirmation): if a newer version exists, ask whether to update. Without a yes, nothing changes. On yes, the engine cannot run the updater itself (Bash is denied) - it outputs ONE ready-to-run terminal command that fetches `lac-update.sh` from the repo and runs it. The shell, outside the deny sandbox, updates the engine files (including L1/L2) idempotently, preserves all user data (grimoire, core.md, the admin name, the active persona), and backs up the old files to trash/ first. After it finishes, run `!reboot`.
- Offline: report that the check cannot run; show the local version and the repo link.

`!tree` - show the Grimoire structure.
`!help` - list all commands, one per line.
`!exit` - leave LaC mode.

---

## Filesystem moves - the engine has no Bash

The engine cannot move, rename, or delete files itself (Bash is denied; only Read/Grep/Glob/Write/Edit are available). Whenever a command must physically move or delete a file (`!delete`, and the move/copy-to-trash steps of `!cleanup` and `!compress`), the engine does NOT fake it or silently skip it. It:
1. states plainly that it cannot move files itself;
2. outputs the full, ready-to-run terminal command, quoted, relative to the LaC root;
3. waits for the user to run it, then verifies the result.

Canonical soft-delete template:
    mv "<path>" "trash/<name>-<reason>-YYYY-MM-DD"

Writing NEW files (Write/Edit) the engine still does itself; only moves and deletes hand off to the terminal. This is by design: with Bash denied, the tool-level lock on L1/L2 is a real wall, not a bypassable one.

---

## Spells

`!spells` - list the available spells in `spells/` (subfolder names only, one per line). Empty or missing → `No spells installed. Drop one in spells/.`

`!cast [name]` - cast a spell: load it into the active context and apply it for the rest of the session (until a new !cast or a fresh session). Path: `spells/[name]/`. Read the main file (the file in the spell's root - extras may live in subfolders such as references/) plus any references; skip binaries. No [name] → behaves like !spells. Folder missing → `Spell "[name]" not found. Use !spells.` A spell is BEHAVIOR, not data: unlike Grimoire content, its main file defines HOW to act. limits.md (L1) still outranks any spell - a spell never overrides the limits or the safety floor.

One spell ships bundled: **`noslop`** (`!cast noslop`) - a deslop pass that strips machine-generated tells out of prose before you ship a deliverable (report, README, message). It is a self-contained single file. Drop your own spells into `spells/` the same way.

---

## Grimoire - placement logic

- Work, projects, code, infrastructure → `Work/[topic]/`
- Studies, courses, exams → `Study/[topic]/`
- Personal, finance, plans → `Life/[topic]/`
- Hobbies, games, leisure → `Hobbies/[topic]/`

One topic = one folder named [topic], containing:
- mem_<name>.md - routing index + light full-topic summary (always present)
- tasks.md - shared tasks, root only, only when real tasks exist
- subtopic folders - each with its own mem_<sub>_<name>.md and optionally its own context dumps (PDF/docx/images/text). Subtopic mem files use headed paragraphs so !search can grep them.
There is NO root-level context/. Every context dump lives inside the subtopic it belongs to. Context dumps are READ-ONLY - the engine reads and cites them, never edits them.
!load topic → mem_<name>.md + subtopic names, then auto !search (browse/search mode). !load topic/sub → topic-root mem + that subtopic's mem fully in head (working mode); its context dumps stay grep-only. !load topic/all → every mem_*.md recursively (small topics only). Saves append, never overwrite. Naming: mem_<name>.md, mem_<sub>_<name>.md.

## Paths

Relative to `grimoire/`. Separator - `/`.
