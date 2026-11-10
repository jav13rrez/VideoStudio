# 02: Preparar el PC

**What to build:** En el PC de casa, el estudio tiene todo instalado y probado: Blender 4.2 o superior (queda fijo el 5.2), un MCP de Blender (el oficial de Blender Lab en lugar de `mcp-for-blender`, ADR 0007), las skills locales de HyperFrames (con la versión fijada), la skill de motion design, Whisper o lo que cubra HyperFrames, y earshot. Se decide dónde van las skills de terceros para que la sincronización de skills no las borre. Se pasan las pruebas de humo de `DEBT_TECH.md`.

**Dónde:** PC de casa (ADR 0005).

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Sistema operativo, tarjeta gráfica, RAM y disco libre anotados en `DEBT_TECH.md`.
- [x] Desde Claude Code se crea un escenario mínimo en Blender a través del MCP y llega su hoja de vistas.
- [x] Un fotograma 1080x1920 con EEVEE en la tarjeta gráfica, con el tiempo medido; y otro con un escenario de naturaleza mínimo (hierba, árboles, agua, cielo HDRI), también medido.
- [x] HyperFrames renderiza una composición mínima a MP4 1080x1920 a 30 fps.
- [x] 10 s de audio transcritos con marcas de tiempo por palabra.
- [x] Las skills de terceros siguen ahí después de una sincronización de skills.
- [x] Todos los puntos de "Pendiente en el PC" de `DEBT_TECH.md` marcados con su resultado.

## Comments

**2026-11-10, agente (desde la nube).** El creador ya tiene el PC (RTX 4060 de 8 GB, 32 GB de RAM), pero la sesión corría en la nube y no podía llegar a él. Se adelantó lo que no necesita el PC: las skills de HyperFrames (`hyperframes` y `hyperframes-cli`, versión 0.9.26) y la de motion design están en `.agents/skills/` y sobreviven a la sincronización; `mcp-for-blender` y earshot están leídos; y se comprobó que HyperFrames cubre la voz (Kokoro, con tres voces en español) y las marcas por palabra (whisper.cpp), así que no hace falta Whisper aparte. Lo que queda, todo en el PC, está en `DEBT_TECH.md`, "Pendiente en el PC".

**2026-11-10, agente (en el PC).** Hecho todo menos la prueba del MCP de Blender (detalle y tiempos en `DEBT_TECH.md`). Blender corre en Windows, porque dentro de WSL no llega a la tarjeta: EEVEE tarda 1,7 s por fotograma en Windows y 29 s en WSL. Se usa el MCP oficial de Blender Lab en lugar de `mcp-for-blender`: es de la propia Blender, no envía datos de uso y el creador ya lo tenía. Para que WSL llegue a Blender se puso la red de WSL en modo `mirrored`. Falta reiniciar WSL (`wsl --shutdown`) y probar desde Claude Code a crear un escenario mínimo por el MCP y recibir su captura.

**2026-11-10, agente (en el PC), cierre.** Tras reiniciar WSL con la red `mirrored`, el MCP oficial de Blender creó un escenario mínimo en el Blender de Windows y devolvió la captura del visor; el render vertical tardó 0,78 s. Ticket hecho; los avisos para los tickets 14 y 18 están en `DEBT_TECH.md`.

**2026-11-10, agente (en el PC), hoja de vistas.** Como el MCP oficial no tiene herramienta de vistas, la hoja se hace con un render EEVEE de un fotograma desde cada cámara de la escena (con `bpy.ops.render.render` a través del MCP), unidos en una sola imagen con ffmpeg (filtro `tile`). Probado con el escenario mínimo: cuatro cámaras (frente, tres cuartos, lateral y cenital), entre 0,6 y 0,8 s por render.
