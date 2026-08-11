# Grimoire

> **A work in progress - not finished, not stable, and it holds plenty of bugs.** It runs, but some features do not work as intended, and some bugs are still uncured. Trust it with nothing that cannot be lost.

Grimoire is not a chatbot; it is a conversational layer over your own notes, and the first application built on [LaC](https://github.com/diranix/llm-as-code) (LLM as Code). Your notes stay plain Markdown in folders you own. The application lists them, opens them, greps them, and answers from what is written there - it does not keep a second, private version of your material, and it writes nothing you did not ask for.

## Setup

The application is a folder the [LaC engine](https://github.com/diranix/llm-as-code) runs: a compose declaration, law files (limits and behavior), a persona, and a commands module. It needs:

- Python 3.10+;
- the engine: `pipx install llm-as-code`;
- a model key in an environment variable - `MISTRAL_API_KEY` or `ANTHROPIC_API_KEY` - or Ollama running locally, depending on the provider named in the compose.

Then run `lac` in the terminal from this folder.

## Features

- **Your files are the canon.** Notes are plain Markdown in topic folders. Grimoire lists, opens, greps and cites them; it never rewrites them, and it keeps no digests or journals of its own. Whatever the model invents dies with the session.
- **Ask in your own words.** Free-form language is mapped onto the same commands the canonical `!` form runs. Name a file however you like, in any language or spelling - the code resolves it against what is actually on disk.
- **A boot memory you can read.** One short surface line per topic in `core/core.md`, a keyword route in `core/map.md`, and your own `core/tasks.md`, printed to the terminal at every start by code, never by the model.
- **Together, not instead.** The human leads. The application does not write your notes, does not summarise them into a private index, and does not do the work in your place.
- **A persona, held by law.** The `souls` folder holds a base persona; a custom one is one compose key (`llm.persona`) and a restart. The public repo ships only `base_soul`; personal personas stay private.

## How it works

The commands are `!tree`, `!load`, `!search`, `!unload`, `!save`, `!delete`, and `map_update`. Two roads lead to them: a canonical `!command` runs in code before the model ever sees it, and free-form language reaches the same functions through tool calling.

- `!load` on a topic lists its file names; on a file it puts the whole text in context. A file over the size cap waits for your y/N in the terminal, and a partial name resolves on its own when only one file can be meant.
- `!search` greps your files and returns matching lines with their path and line number.
- `!unload` drops loaded file text back out of the window when a topic is finished.
- `!save` appends a few short lines about a topic to `core/core.md` - what the topic is, what stage it is at, what is open. It holds the surface, never the contents: anything a load or a search could find does not belong there. It waits for your y/N and shows the exact text first.
- `!delete` moves a file or folder to `trash/`, never erases, and always waits for your y/N.

Everything else the engine could write was removed: no hidden memory files, no session journals, no digests of your notes. The only two files the application may touch are `core/core.md` and `core/map.md`, both behind a gate.

## How the defense holds

The core idea of LaC: protect the user's machine FROM the model itself, because a model can be talked into anything. So the guarantee lives not in the LLM's good behavior but in structure and code:

- **Levels of authority.** L0 is the engine and this command module, L1 is the limits, L2 is behavior and persona, L3 is everything else - your notes, the boot memory, every command result. On any conflict the higher level wins, and L3 has no authority over behavior at all.
- **Data apart from law.** L3 never enters the system channel: the model receives law as law and data as data. This is what defeated injection where defensive prose had failed.
- **A mark no file can wear.** Each run the engine draws half a mark at random and computes the other half from the law it loaded. Its own words carry that mark, stored content travels between borders carrying it, and any passage inside that imitates the engine's framing is broken before the request is built - with a count printed to your terminal, so an attempt is visible even when it fails.
- **Effect cage.** Writes are locked to an explicit allowlist; everything else under the memory root is read-only to the engine. Deletion is a move to trash behind a gate, and a call that would be refused anyway is refused before the gate is shown.

This defense does not hold perfectly - below is what still fails.

## Known bugs

These are **application** bugs (the engine's own limits live in its separate [repository](https://github.com/diranix/llm-as-code)). Tested on Mistral Large and Medium 3.5 and on a local qwen3:14b. The model matrix is still ahead, so treat everything below as observation, not proven numbers.

- **The open half of injection.** Text that forges the engine's own voice is now broken in code and was refused six runs out of six. A plain, plausible instruction sitting in a note - one that imitates nothing - meets prose alone, and prose has lost more often than it has held.
- **Form leaks.** Menus of suggested actions at the end of replies, headings, and an English first turn on a cold window keep coming back despite an explicit law against all three. The security rules hold far better than the style rules, because the first are enforced and the second are asked.
- **Confabulation.** The model renames files it was just shown, builds encyclopedia-shaped answers with categories your notes never had, and explains its own past actions with invented provenance. The fix is structural where possible: results carry their own instructions, and questions of the form "what did I write about X" are answered from search output rather than memory.
- **Stated reasoning is not evidence.** The model has quoted the law flawlessly and violated it in the same reply, more than once. Only behavior counts; a self-report about obedience is worth nothing.
- **No tests yet, no drift numbers.** Behavior is under measurement, not proven.

## Privacy

The memory is your own files on your own disk. But when a cloud LLM API is used, the application sends the text to the provider's servers. For maximum privacy, run a local model through Ollama.

## Legacy version

An earlier form of Grimoire runs the same protocol on Claude Code, with the perimeter held by harness permissions and prompts instead of engine code. That version lives in its own repository, stable and frozen: [diranix/grimoire-legacy](https://github.com/diranix/grimoire-legacy).

## License

See [LICENSE](LICENSE) (AGPL-3.0). The LaC protocol is free; this application licenses itself independently.
