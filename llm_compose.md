# LLM Compose

```yaml
version: "0.5.1.4"

users:
  admin: YOUR_NAME

levels:
  L1: [llm_compose.md, limits.md, CLAUDE.md, .claude]   # admin: the frame - immutable, locked
  L2: [commands.md, rules.md]                           # dev: command set built per app
  # L3 = everything else - user + llm, freely editable (engine writes here only)

context:
  limits: limits.md
  commands: commands.md
  persona: personas/base_persona.md
  rules: rules.md
  core: grimoire/core

paths:
  grimoire: grimoire/
  trash: trash/

engine:
  activity: normal   # active | normal | passive
```
