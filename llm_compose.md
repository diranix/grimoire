# LLM Compose

> System entry point.
> Defines levels, context, and paths to all LaC files.
> Loaded automatically every session via CLAUDE.md.
> Only the administrator may edit this file.

```yaml
version: "0.4.9.6"

model:
  # Claude Code chooses the model; this block is documentation only.

users:
  admin:
    - YOUR_NAME_HERE
  permissions:
    admin:
      - read: all
      - write: all

levels:
  1: [llm_compose.md, limits.md, CLAUDE.md, .claude]   # immutable - locked in .claude/settings.json
  2: commands.md                   # admin only
  # everything else = level 3      # user, changeable

context:
  limits: limits.md
  commands: commands.md
  persona: personas/default_persona.md
  core: grimoire/core

paths:
  grimoire: grimoire/
  trash: trash/
```
