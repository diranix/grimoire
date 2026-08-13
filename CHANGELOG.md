# Changelog

## 0.2.0 - 2026-08-06

The application stops writing memory of its own. Requires engine 0.3.0.

Removed:

- `save` as it was, `index`, and the hidden `.memory_` digest files. A model-written summary of the user's own material goes stale, invents, and returns at the next boot wearing the authority of a fact. Two campaigns in one afternoon showed it plainly: with a well-written digest in front of it the model fused two characters into one and invented a romance; reading the source file cured it.
- The session journals and the day-recap tool that briefly replaced them. A journal quietly becomes the memory again, and hand-editing chat transcripts into canon is not a workflow anyone wants.
- `read` - merged into `load`, which now returns a file's full text or a topic's file names.

Added or reworked:

- `save` returns as one narrow thing: a few short lines per topic appended to `core/core.md`, behind the user's y/N, showing the exact text first. It holds the surface of a topic - what it is, what stage it is at, what is open - and refuses to hold what a load or a search could find.
- `unload` drops loaded file text out of the window; the files on disk are untouched.
- `load` gained a size cap with a consent gate, and resolves a partial name when only one file can be meant.
- `core/` is invisible to `tree`, `search`, `load` and `delete`: it is the engine's boot memory, already in context, not a page to open.
- `core/tasks.md` is printed to the terminal at every boot by code, verbatim - the model has no hand in it.
- `map_update` now runs only on an explicit ask and waits for a y/N like every other write.
- The law names what the application is: a reader of the user's own files, not a source of general knowledge. Every substantive claim comes from a file it opened or searched; where the files are silent it says so instead of filling the gap with advice that would read the same without them.

Known to still fail: menus and headings keep returning despite the law, the first turn on a cold window drifts to English, and a plausible instruction planted in a note - one that imitates no framing - is met by prose alone.

## 0.1.0 - 2026-07-20

First release on the runtime engine: eight tools, hidden per-topic memory, session journals, and the Claude Code era frozen as [grimoire-legacy](https://github.com/diranix/grimoire-legacy).
