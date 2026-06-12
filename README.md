# LaC — LLM as Code

A file-based protocol for driving an LLM through structured Markdown. Your rules, commands, context, and memory live on disk — not in a chat history that vanishes. The LLM boots from those files, runs commands, and writes state back. One source of truth, version-controllable, editor-agnostic.

> **Status: early alpha.** Currently tested only with **Claude Desktop** + the Filesystem MCP. Other MCP-capable clients may work but are unverified. The `!boot` hook lives in the client's memory feature, so a client without persistent memory will not boot LaC as-is.

> ⚠️ Not accepting contributions at this time.

## How it works

Four layers plus a persistent file store (the Grimoire):

- `llm_compose.md` — entry point. Defines levels, context, and paths. Read first on `!boot`.
- `limits.md` (L1) — immutable rules. The safety and integrity floor.
- `commands.md` (L2) — the command set: `!boot`, `!save`, `!load`, `!tree`, and more.
- `persona.md` (L3) — the engine's personality. Swap it freely.
- `grimoire/` — persistent memory, organized into topic folders.

A chat session is a draft; `!save` is what makes memory canonical. Close the chat — lose nothing that was saved.

## Requirements

- **Claude Desktop** with a persistent memory feature (this is where the boot hook lives)
- An MCP filesystem server connected to the client (e.g. Docker MCP Toolkit, or npx)
- A dedicated folder for LaC, with the filesystem server scoped to exactly that folder

## Install

Hand `lac-setup.md` to an LLM with filesystem access and tell it to execute the file. It discovers the root, builds the structure, generates the boot hook, and tells you what to paste into your client's memory. Full steps live inside `lac-setup.md`.

## License

AGPL-3.0. Commercial licensing available on request.
