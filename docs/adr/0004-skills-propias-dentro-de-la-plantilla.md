# Las skills propias viajan dentro de la plantilla, no como plugin

Las skills propias (`crear-loop`, `crear-grafo`, `modo-riguroso`) se copian en cada proyecto creado desde la plantilla, en lugar de publicarse como plugin. Así funcionan en cualquier herramienta que soporte el estándar `SKILL.md`, sin instalar nada, que es lo más simple para un usuario no técnico. El precio es que una mejora no llega sola a los proyectos ya creados. Para traer una versión nueva a un proyecto ya creado, se copia `.agents/skills/` desde la plantilla y se ejecuta `bash scripts/sincronizar-skills.sh` (o se le pide al agente que lo haga). Las skills de Matt Pocock sí se instalan como plugin, porque son externas y se actualizan solas.

## Opciones consideradas

- **Plugin propio con marketplace**: se aplaza. Tiene sentido cuando las skills estén estables, pero añade un paso de instalación y solo funciona en las herramientas con plugins.

## Dónde viven

Las herramientas no se ponen de acuerdo sobre dónde buscar las skills:

- Codex y Gemini CLI solo leen `.agents/skills/`.
- Claude Code solo lee `.claude/skills/`.
- Cursor, Copilot, OpenCode y Amp leen las dos.

El original vive en `.agents/skills/`, el estándar abierto, y `.claude/skills/` es una copia exacta que mantiene `scripts/sincronizar-skills.sh`. Se descartó un enlace simbólico porque en Windows, sin modo desarrollador, git lo convierte en un archivo de texto y Claude Code se quedaría sin skills. Contrapartida: las herramientas que leen las dos carpetas pueden mostrar cada skill dos veces, con idéntico contenido.
