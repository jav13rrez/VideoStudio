# Herramientas del estudio: Blender para la imagen, HyperFrames para el montaje

Los escenarios, los personajes y el render se hacen en Blender (versión fija 5.2, en Windows), manejado por el agente a través del MCP oficial de Blender Lab. El montaje (unir planos, voces, subtítulos, música y el CTA final) se hace con HyperFrames, que describe cada episodio como una composición HTML y la renderiza a MP4. Las hojas de revisión se sacan con ffmpeg. El plan base usa Remotion para el montaje, y Remotion sería gratis para nosotros porque el canal es del usuario como particular, pero el usuario prefiere HyperFrames: licencia Apache-2.0, gratis para cualquiera, sin depender del tamaño de quien lo use. Es una desviación deliberada del plan; no hay que "arreglarla" volviendo a Remotion.

## Opciones consideradas

- **Remotion**: más maduro (versión 4.0.542 frente a la 0.9 de HyperFrames) y con skills oficiales para agentes. Gratis solo para particulares y empresas de hasta 3 empleados; rechazado por preferencia del usuario.

## Consecuencias

- HyperFrames es joven: conviene fijar su versión y probar el montaje completo en el PC antes de construir encima (ver `DEBT_TECH.md`).
- Se usan sus skills locales (`npx skills add heygen-com/hyperframes`), no el conector alojado de HeyGen, porque los episodios tienen que quedar como archivos en esta carpeta (ADR 0006).
- **MCP de Blender (cambiado el 2026-11-10).** El plan base usa `mcp-for-blender` (de un tercero). Se cambió al MCP oficial de Blender Lab (`projects.blender.org/lab/blender_mcp`, GPL-3.0, versión 1.0.3) porque lo hace la propia Blender, no envía datos de uso, el creador ya lo tenía instalado en su Blender y en la app de escritorio, y los dos complementos chocan en el mismo puerto (9876). Lo que se pierde:
  - La herramienta de vistas (`look`). La hoja de vistas se hace con un render EEVEE de un fotograma desde cada cámara de la escena (con `bpy.ops.render.render` a través del MCP), unidos en una sola imagen con ffmpeg (filtro `tile`). Muestra la luz real del render.
  - La búsqueda en Poly Haven (`search_assets`). Los HDRI y las texturas se bajan de su API pública (`dl.polyhaven.org`).
