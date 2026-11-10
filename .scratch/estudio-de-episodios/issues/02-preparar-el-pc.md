# 02: Preparar el PC

**What to build:** En el PC de casa, el estudio tiene todo instalado y probado: Blender 4.2 o superior, `mcp-for-blender`, las skills locales de HyperFrames (con la versión fijada), la skill de motion design, Whisper o lo que cubra HyperFrames, y earshot. Se decide dónde van las skills de terceros para que la sincronización de skills no las borre. Se pasan las pruebas de humo de `DEBT_TECH.md`.

**Dónde:** PC de casa (ADR 0005).

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Sistema operativo, tarjeta gráfica, RAM y disco libre anotados en `DEBT_TECH.md`.
- [ ] Desde Claude Code se crea un escenario mínimo en Blender a través del MCP y llega su hoja de vistas.
- [ ] Un fotograma 1080x1920 con EEVEE en la tarjeta gráfica, con el tiempo medido; y otro con un escenario de naturaleza mínimo (hierba, árboles, agua, cielo HDRI), también medido.
- [ ] HyperFrames renderiza una composición mínima a MP4 1080x1920 a 30 fps.
- [ ] 10 s de audio transcritos con marcas de tiempo por palabra.
- [x] Las skills de terceros siguen ahí después de una sincronización de skills.
- [ ] Todos los puntos de "Pendiente en el PC" de `DEBT_TECH.md` marcados con su resultado.

## Comments

**2026-11-10, agente (desde la nube).** El creador ya tiene el PC (RTX 4060 de 8 GB, 32 GB de RAM), pero la sesión corría en la nube y no podía llegar a él. Se adelantó lo que no necesita el PC: las skills de HyperFrames (`hyperframes` y `hyperframes-cli`, versión 0.9.26) y la de motion design están en `.agents/skills/` y sobreviven a la sincronización; `mcp-for-blender` y earshot están leídos; y se comprobó que HyperFrames cubre la voz (Kokoro, con tres voces en español) y las marcas por palabra (whisper.cpp), así que no hace falta Whisper aparte. Lo que queda, todo en el PC, está en `DEBT_TECH.md`, "Pendiente en el PC".
