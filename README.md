# Grimoire

[![version](https://img.shields.io/github/v/tag/diranix/grimoire?label=version&sort=semver&color=blue)](https://github.com/diranix/grimoire/releases)
[![license](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE)

*Created by [Ivan Baibakov (diranix)](https://github.com/diranix)*

___

## What it is and why

**Grimoire is the first application built on the LaC protocol.** Grimoire began as a memory upgrade for Claude Code between sessions and grew into something more. It is now a notebook that a human and an LLM keep together: you set the direction and write your own notes, and Grimoire reads, indexes, and voices them. Everything lives in plain markdown files on disk, so you can edit them in any editor, not only through the LLM. A chat session is a draft; `!save` writes the session's memory to disk, and once you close the chat you continue the next one from the same place.

**The next step is building a runtime** that turns the LLM's prose prohibitions into code and allows the use of any LLM, including local ones.

What Grimoire gives you:

 - optimization of memory and token use
 - improvement of LLM's work through persistent context
 - openness and control over the program
 - privacy - all files are stored locally on your machine

 
**Status: alpha.** For now it is a rule set that works only with Claude Code. All actions run natively, no extra applications needed. Grimoire launches in a dedicated folder of its own and does not affect your other projects.

⚠️ Not accepting contributions at this time.

___

## Link to LaC

When Grimoire was still my personal file system, I realized that an LLM does not always recognize and correctly carry out my prose requests. So I understood I needed a set of commands with a clear description of behavior for the LLM - one that recognizes the intent, translates it, and runs it as deterministic commands, asking the user first. After that I noticed my conversation with the LLM had turned into a set of commands and looked more like code than an ordinary conversation. That is how the idea of LaC - LLM as a Code - was born, which has now grown into a separate protocol.

The goal of LaC is to reduce LLM drift and make a user's commands almost always lead to the same result. In effect it is an attempt to turn prose into deterministic commands through sets of files of commands, permissions, and prohibitions.

As the basis for the LaC protocol I took IaC and Docker, because those are what I know best. The main file in LaC is llm_compose.md. It holds links to all the other files and assembles the system - the first step in the protocol, exactly where docker-compose sits in Docker. Next come the files of the highest level - the LLM limits, which carry the rules of restriction and security. Then the second-level files - the set of commands and rules that make the protocol a separate program. And last, the third level - the program's content.

Splitting into levels gives protection and a clear hierarchy of rights. Second-level rules override third-level rules but do not affect first-level rules. First-level rules dictate the behavior of levels 2 and 3, while level 3 carries no rules at all and cannot affect the other two. Users are split across the levels as well, holding edit rights to those levels. The administrator edits level 1 files and everything below - he configures the security and limits of the program built on LaC. The developer edits level 2 files and below - he is responsible for creating commands and the rules for running them, and shapes the logic and mechanics of the LLM's work, turning it into a standalone program. And the user, together with the LLM itself, fills level 3 with content. They cannot create new commands or change the security limits. Level 3 files are data, not instructions or commands to the engine: the engine quotes the text inside them, it does not execute it.

For now the level hierarchy is backed by the Claude Code runtime, and the files are locked from LLM editing through .claude/settings.json. Here it is worth drawing a line. The edit locks are already real enforcement: deny rules physically keep the LLM from rewriting levels 1 and 2. But the behavioral rules still rest more on a system of requests that the LLM chooses to heed. During the migration to its own runtime, it is this second part that will move to tool-level restrictions on the LLM, which will force it to follow the rules. Also, the current version of Grimoire is assembled from the CLAUDE.md file and is more of a layer on top of Claude Code; this too will be fixed in the future.

___

## How it works

On the first message in a new chat in Claude Code, opened in the Grimoire folder, the json files fire - they restrict the LLM's tools and handle security. Then the LLM reads CLAUDE.md, which holds only the command to read llm_compose and get the load order. After that the first-level files load, which guard the engine with limits and keep potentially harmful commands from L3 from firing if the engine reads them first. Then come the L2 files with the program's commands and rules. And last come the level-3 data. That is the basic LaC startup for now.

It is important to separate Grimoire as a program from the LaC protocol. Grimoire has files modified for its own needs. For example, all level-2 commands are built for working with text, and the rules - for better work with notes overall. Grimoire's startup is changed too: among the level-3 data the engine loads a ready topic map (core/map.md) at startup, which it then uses to navigate the whole grimoire. It does not rebuild the map every time - it keeps it in core/map.md and reconciles it with the tree on every `!save`.

Memory is arranged like this: in the home directory "grimoire" there is, by default, a service directory core and four categories - Work, Study, Life, Hobbies. The topics themselves are directories inside the categories. core holds files with the user's basic information, the topic map, and tasks. The user writes the tasks themselves, and the engine only reads them.

Each topic is a separate directory, and the engine writes a few files of its own in it. The root "mem_<name>.md" is a route to where everything lives, plus a short `## Overview` of the topic and an index of the notes - a link and a tag cloud for each. The decisions themselves go to "history_<name>.md", a dated archive the engine never loads into context: it is grep-only, reached through `!search`, so the whole chronology of a topic stays out of head until a question actually needs it. Large topics split into subtopics, each with its own mem_ holding only a short list of decisions; the full dated record for every subtopic lives in that one topic history file. The rest of the directory belongs to the user: notes under any names, which the engine reads, quotes, and indexes, but never edits. Dumps - PDF, docx, images - are read-only sources: the engine quotes them, does not change them.

Working with memory happens through commands: `!save` writes a summary of the chat into a topic, `!load` brings up a topic, `!search` searches within it, `!cleanup` and `!compress` tidy up, `!delete` hides things in trash, `!cast` turns on a spell. Spells are add-on skills for Grimoire - one (`noslop`) ships bundled, the rest come from third-party developers. Loading is on demand - `!load` pulls only the index, while note bodies are pulled in through `!search` when needed, so a large topic stays light on context. `!search` itself does not look for literal words: the engine expands the query into synonyms, jargon, error codes, and other-language equivalents and greps the union, that is, it becomes the "embedding" at search time. The engine cannot move files - on `!delete` or a move it dictates a ready `mv` command to the terminal, and the user runs it.

___

## Requirements

- **Claude Code** (terminal CLI or the desktop app - both should work, but the terminal version hasn't been tested yet)
- LaC asks the model to hold a strict protocol on every turn - the boot ritual, command parsing, the locks. **Stronger models hold it better**; weaker or older models follow it less reliably and the engine drifts.
- **A dedicated folder** for LaC, opened as your Claude Code project (that folder is the LaC root)
- **python3** powers the warn-only write guard - a style-tell check plus a secret scan. It is required only for that guard: without python3 the guard is off and everything else works.

___

## Install

Create and open a folder as a Claude Code project. Paste this link into the chat and say **install**:

```
https://raw.githubusercontent.com/diranix/grimoire/main/lac-setup.md
```

Claude Code reads `lac-setup.md` and runs it. It asks once for your admin name, then fetches every technical file from the repo by its raw URL and writes it locally - the four governance files, the `.claude/` lock and hooks, a neutral base persona, the bundled `noslop` spell, and a `grimoire/` holding its `core/` files and empty category folders.

The installer is idempotent. Run it again on a folder that already has LaC and it refreshes the engine files while leaving your data alone - it never overwrites `grimoire/`, `core.md`, your admin name, or your active persona.

After install, start a fresh session in the same folder and it enters LaC mode on its own. The boot lives in `CLAUDE.md` and a `SessionStart` hook, both of which run only inside a Claude Code project session for this folder. A generic Cowork or assistant chat that has not opened the folder stays an ordinary assistant - no boot line, no persona, no commands. Grimoire works only with Claude Code.

___

## Updating

Run `!update` in a LaC session. It reads your local version, fetches the latest version and CHANGELOG, and shows what changed - read-only, nothing written. If you are already current, it says so and stops.

If a newer version exists and you confirm, the engine hands you one terminal command - it cannot update itself, because .claude/settings.json denies Bash and locks the L1/L2 files. The same wall that stops a rogue agent stops the engine from rewriting its own governance. The command fetches lac-update.sh and runs it in your shell, outside that wall.

lac-update.sh refreshes only LaC's own engine files - limits.md, commands.md, rules.md, CLAUDE.md, .claude/settings.json, .claude/write-guard.py, and the bundled noslop spell (LaC maintains it) - and refreshes llm_compose.md while re-injecting your admin name and persona pointer, so structural changes land without losing your two choices. It leaves your data alone: it never overwrites anything under grimoire/, your active persona, or your own spells, and only restores core/map.md or base_persona.md when one is missing. Every replaced file is copied to trash/ first. When it finishes, run `!reboot`.

### Keep your Grimoire private

Your notes live on your machine and never leave it. Installing LaC publishes nothing of yours - the public repo carries only LaC's own files (installer, engine, updater), never your data.

The installer never sets up Git. So the only way your data could go public is if you decide to put your install folder under Git yourself. If you do, grimoire/ and trash/ hold everything personal - names, locations, server IPs, plans - so either keep that repository private, or add grimoire/, trash/, and any persona file with personal details to .gitignore before your first push.

___

## Author

LaC (LLM as Code) and Grimoire were created and are maintained by **Ivan Baibakov** (**diranix**).

## License

Copyright (C) 2026 Ivan Baibakov (diranix).

LaC and Grimoire are released under AGPL-3.0 - see [LICENSE](LICENSE). Commercial licensing available on request.
