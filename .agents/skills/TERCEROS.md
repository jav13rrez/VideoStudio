# Skills de terceros

Junto a las skills propias (`crear-loop`, `crear-grafo`, `modo-riguroso`) hay skills de terceros copiadas tal cual, con su licencia dentro de su carpeta. Viven aquí, en `.agents/skills/`, y no en `~/.claude/skills/` ni solo en `.claude/skills/` (decidido el 2026-11-10):

- `scripts/sincronizar-skills.sh` borra `.claude/skills/` y la copia desde aquí, así que lo que solo esté en `.claude/skills/` se pierde en la siguiente sincronización.
- Con el proyecto quedan fijadas en la misma versión que usa la herramienta del estudio, y viajan a cualquier PC con un `git clone`.
- Las leen todas las herramientas, no solo Claude Code.

No se tocan a mano. Para actualizar una, se sustituye su carpeta por la de la nueva versión (con su `LICENSE`), se cambia la tabla y se ejecuta `bash scripts/sincronizar-skills.sh`.

| Skill | Origen | Versión | Licencia |
| --- | --- | --- | --- |
| `hyperframes` | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes), `skills/hyperframes` | `v0.9.26` (commit `0c6c7fc`), la misma que fija `HYPERFRAMES` en `src/estudio/montaje.py` | Apache-2.0 |
| `hyperframes-cli` | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes), `skills/hyperframes-cli` | `v0.9.26` (commit `0c6c7fc`) | Apache-2.0 |
| `motion-design` | [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill), `skills/motion-design` | commit `f9a8a04` (2026-05-18) | MIT |

## Lo que no se instaló, y por qué

- **`media-use`** (la de HyperFrames para voz, música, efectos y transcripción): manda iniciar sesión en HeyGen y gastar créditos antes que usar lo local, y el estudio no gasta dinero (spec, historia 62). Lo local que trae (`npx hyperframes tts` con Kokoro y `npx hyperframes transcribe` con whisper.cpp) lo llamará la herramienta del estudio directamente, en el ticket 13.
- **`hyperframes-registry`**, **`figma`**, **`slideshow`** y el resto: el estudio no los necesita. Las skills de HyperFrames las mencionan (`/media-use`, `/hyperframes-registry`); si el agente no las encuentra, es por esto.

## Telemetría

Las skills de HyperFrames piden ejecutar `npx hyperframes events` al arrancar, y `mcp-for-blender` también envía datos de uso. En el PC del estudio se apaga las dos: ver "Instalar el estudio" en `DEBT_TECH.md`.
