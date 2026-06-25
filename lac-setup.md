# LaC Setup
> LLM as Code - installer for Claude Code (terminal or desktop app)
> Version: 0.5.0

---

## For humans - prerequisites

LaC is a set of plain files that govern a language model. To install it you hand this file to Claude Code and it builds the structure for you. Before you do:

1. Install **Claude Code** - the terminal CLI or the desktop app, either works. Run it on **Opus 4.8** if you can: LaC asks the model to hold a strict protocol every turn, and weaker or older models follow it less reliably.
2. Create an empty folder for LaC and open it **as a Claude Code project**. That folder becomes the LaC root - the engine can only touch what is inside it.
3. Paste this file's raw link into the chat and say **install**:
   `https://raw.githubusercontent.com/diranix/grimoire/main/lac-setup.md`

No Docker, no MCP server, no memory hook. Claude Code reads and writes files natively.

**LaC only boots inside a Claude Code project session for this folder.** The boot ritual lives in `CLAUDE.md` and a `SessionStart` hook in `.claude/settings.json`; both run only when the folder is opened as a project (terminal, desktop app, or an IDE window rooted here). A generic Cowork or assistant chat that has not opened this folder stays an ordinary assistant - no boot line, no persona, no `!commands`. If you never saw "Entering LaC mode", you are in a plain chat: open the folder as a project and start fresh.

---

## For the LLM - execution instructions

You are reading this file as the installer. **It carries no file bodies on purpose.** Do not write engine files from memory or from any embedded template - there are none here. Instead **fetch each technical file from the repo by its raw URL** and write it to the local path shown, byte for byte. The repo copies are the single source of truth; this installer only says what to fetch and where it lands. That is what keeps the installed files identical to the repo with no second copy to drift.

Raw base for every fetch: `https://raw.githubusercontent.com/diranix/grimoire/main/`

So for a manifest entry `limits.md`, fetch `https://raw.githubusercontent.com/diranix/grimoire/main/limits.md` and write it to `limits.md` in the project root.

**Detect the mode first.** If `CLAUDE.md` and `llm_compose.md` already exist in the root, this is an UPDATE - follow the Idempotency rules below. Otherwise it is a FRESH install - build everything.

**Fresh install, first action:** ask once - "What name should be set as the ward (administrator)?" Hold the answer for Step 2. On an update, do NOT ask; read the existing ward name and persona pointer from `llm_compose.md` and keep them.

On a fresh install do not pause for confirmation - run the steps in order and report what each one created.

### Step 1 - folder structure

Create these folders in the project root:

```
personas/
spells/
spells/noslop/
grimoire/
grimoire/core/
grimoire/Work/
grimoire/Study/
grimoire/Life/
grimoire/Hobbies/
trash/
.claude/
```

`trash/` sits at the project root, a sibling of `grimoire/` - it is the soft-delete grave (`!delete`, plus the backup copies of `!cleanup` / `!compress` / the updater). It holds deleted copies of your data, so it is private just like `grimoire/`.

The repo ships a `.gitkeep` in each empty category folder (`Work/`, `Study/`, `Life/`, `Hobbies/`) and in `trash/` so Git tracks the empty directories. On a local install you only need those `.gitkeep` files if you will put your own copy under Git - otherwise the folders are enough.

### Step 2 - fetch and write the technical files

Fetch each raw URL (base + the path) and write the bytes to the local path. Most are verbatim; the two marked otherwise need one substitution.

| Fetch (append to raw base) | Write to | Handling |
|---|---|---|
| `llm_compose.md` | `llm_compose.md` | After writing, replace `YOUR_NAME` on the `ward:` line with the administrator name from the first action. Keep everything else. |
| `limits.md` | `limits.md` | Verbatim. |
| `commands.md` | `commands.md` | Verbatim. |
| `CLAUDE.md` | `CLAUDE.md` | Verbatim. |
| `personas/base_persona.md` | `personas/base_persona.md` | Verbatim. The neutral default the `llm_compose.md` persona pointer names. |
| `spells/noslop/noslop.md` | `spells/noslop/noslop.md` | Verbatim. The one bundled spell (`!cast noslop`). |
| `grimoire/core/core.md` | `grimoire/core/core.md` | Fresh install only. If it already exists, leave it untouched - it holds the user's context. Fill `YOUR_NAME` / `YOUR_LOCATION` / `YOUR_LANGUAGE` if you have them, else leave the placeholders. |
| `.claude/no-slop-scan.py` | `.claude/no-slop-scan.py` | Verbatim. |
| `.claude/settings.json` | `.claude/settings.json` | Verbatim. **Write this one LAST** - see the note below. |

**Write `.claude/settings.json` last.** It denies Bash and locks the L1/L2 files. Once it is in effect the engine can no longer freely write the rest, so writing it last keeps the fetch-and-write loop open until everything else is in place. After it lands, the locks take effect on the next session.

### Idempotency - install vs update

Re-running this installer must never duplicate files or clobber data. Same path means overwrite-or-skip, never a second copy.

- **Never overwrite user data.** Leave exactly as they are: everything under `grimoire/` (including `grimoire/core/core.md`), `.claude/settings.local.json`, any persona the user added, any user-added spell.
- **Preserve choices in `llm_compose.md`.** On update keep the existing `ward:` name and the `context.persona` pointer; refresh only the rest of the file from the repo copy.
- **Refresh engine files to the latest.** These are not user-editable, so refreshing them is the point of an update: `limits.md`, `commands.md`, `CLAUDE.md`, `.claude/settings.json`, `.claude/no-slop-scan.py`, and the bundled `spells/noslop/noslop.md`.
- **Personas are user space.** Never overwrite a persona on update. Restore `personas/base_persona.md` only if it is missing (a broken install); if it is present, leave it exactly as it is, edited or not. This matches what `lac-update.sh` does.
- **The locked-file caveat.** On a project that already has `.claude/settings.json`, its deny rules block the engine from rewriting the locked files (`llm_compose.md`, `limits.md`, `commands.md`, `CLAUDE.md`, `.claude/**`). That is the security model working, not a failure. When a write is denied during an update, do not error out: report it and output a ready-to-run terminal command that writes the fetched content, the same way `!delete` hands off `mv`, so the user applies it outside the sandbox. The standalone updater (`lac-update.sh`) does this wholesale.
- **Folders:** create only if missing.

---

## Final - after installation

Tell the user:

```
LaC installed in this project.

It loads automatically when this folder is opened AS a Claude Code project -
start a fresh session here (terminal, desktop app, or IDE rooted in this folder)
and it enters LaC mode. A generic chat that has not opened this folder will NOT
boot LaC: no "Entering LaC mode" line, no persona, no commands.

Commands: !reboot (refresh after manual edits), !save, !load, !tree, !help, !cast noslop.
Locked files (llm_compose.md, limits.md, commands.md, CLAUDE.md, .claude/**) are denied
in .claude/settings.json, which also denies Bash so the lock cannot be walked around.
File moves and deletes are handed to your terminal.

Structure:
├── CLAUDE.md             ← auto-loaded boot file
├── llm_compose.md        ← entry point: levels, context, paths (carries your ward name)
├── limits.md
├── commands.md
├── personas/
│   └── base_persona.md   ← active persona (neutral default; repoint llm_compose.md to swap)
├── spells/
│   └── noslop/noslop.md  ← bundled deslop spell (!cast noslop)
├── .claude/
│   ├── settings.json     ← hardened lock (L1/L2 + .claude + Bash off) + boot hook
│   └── no-slop-scan.py   ← warn-only invisible-char guard (PostToolUse)
├── grimoire/
│   ├── core/core.md      ← your personal context (loaded every session)
│   └── Work/ Study/ Life/ Hobbies/   (each with a .gitkeep until first !save)
│       └── [topic]/                  ← created on first !save
│           ├── mem_<topic>.md         ← routing index + light summary
│           ├── tasks.md               ← only if there are tasks
│           └── [subtopic]/            ← optional, with its own mem + dumps
└── trash/                ← soft-delete grave (keep private)
```
