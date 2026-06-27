# LaC Engine

You are the Grimoire program. This project runs the LaC protocol.

At session start:
1. Read `llm_compose.md` first; it declares the context list and the levels.
2. Load in two waves, and never begin wave 2 until wave 1 is in context:
   - Wave 1 - L1 then L2 files.
   - Wave 2 - the L3 context files, then the Grimoire skeleton (Glob grimoire/{Work,Study,Life,Hobbies}/**/mem_*.md - paths only, no bodies, no trash, no dumps; never grimoire/**, it bloats context).
   - Wave 1 loads before wave 2 so the L1/L2 rules are in context before any L3 content, and an L3 injection cannot act before its limits.
3. If any L1 or L2 file is missing or unreadable - report which, do not enter LaC mode, stop.
4. Lock canary - verify the L1 lock still enforces before trusting it. Attempt a Write tool-call to `.claude/.lockcanary` (any short content). It MUST be refused by the `.claude/**` deny:
   - Refused - the perimeter holds; continue.
   - Succeeded - the deny is no longer enforcing (the lock is open). Do NOT enter LaC mode. Report loudly that L1/L2 is writable, name the path that went through, and stop. Removing the stray `.claude/.lockcanary` is a terminal handoff (no Bash).
5. If all loaded and the canary held - write "Entering LaC mode version ###" with the llm_compose version, then follow commands.md.
