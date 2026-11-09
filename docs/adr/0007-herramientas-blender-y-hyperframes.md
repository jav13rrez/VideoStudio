# Herramientas del estudio: Blender para la imagen, HyperFrames para el montaje

Los escenarios, los personajes y el render se hacen en Blender (4.2 o superior), manejado por el agente a través de `mcp-for-blender`. El montaje (unir planos, voces, subtítulos, música y el CTA final) se hace con HyperFrames, que describe cada episodio como una composición HTML y la renderiza a MP4. Las hojas de revisión se sacan con ffmpeg. El plan base usa Remotion para el montaje, y Remotion sería gratis para nosotros porque el canal es del usuario como particular, pero el usuario prefiere HyperFrames: licencia Apache-2.0, gratis para cualquiera, sin depender del tamaño de quien lo use. Es una desviación deliberada del plan; no hay que "arreglarla" volviendo a Remotion.

## Opciones consideradas

- **Remotion**: más maduro (versión 4.0.542 frente a la 0.9 de HyperFrames) y con skills oficiales para agentes. Gratis solo para particulares y empresas de hasta 3 empleados; rechazado por preferencia del usuario.

## Consecuencias

- HyperFrames es joven: conviene fijar su versión y probar el montaje completo en el PC antes de construir encima (ver `DEBT_TECH.md`).
- Se usan sus skills locales (`npx skills add heygen-com/hyperframes`), no el conector alojado de HeyGen, porque los episodios tienen que quedar como archivos en esta carpeta (ADR 0006).
