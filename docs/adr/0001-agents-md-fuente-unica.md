# AGENTS.md es la única fuente de verdad de las instrucciones

La plantilla tiene que funcionar igual con cualquier herramienta de agentes (Claude Code, Codex, Gemini CLI, Cursor, Copilot…), y cada una lee un archivo distinto. Por eso todas las reglas viven en `AGENTS.md`, el estándar abierto. `CLAUDE.md` y `GEMINI.md` son stubs que solo importan `@AGENTS.md` y añaden lo que sea exclusivo de esa herramienta. No se duplican reglas en `.cursor/rules`, `.github/copilot-instructions.md` ni similares: una regla repetida en varios sitios acaba desincronizada.

## Consecuencias

- Una regla nueva se añade **solo** en `AGENTS.md`.
- Si se vuelve a ejecutar `/setup-matt-pocock-skills`, editará `CLAUDE.md` porque existe. Hay que mover su bloque `## Agent skills` a `AGENTS.md` y dejar `CLAUDE.md` como stub.
