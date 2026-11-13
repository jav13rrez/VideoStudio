# 15 — Limpieza del código de Blender

Spec: [estudio-2d](../spec.md). Decisión: [ADR 0008](../../../docs/adr/0008-estudio-2d-ilustrado-con-exteriores.md).

**What to build:** que el motor 2D sea el único. Se borran el código y los tests de Blender que dejan de usarse y se actualiza la configuración y el ADR 0007. Los archivos aprobados por el creador (`.blend` del salón, del recibidor y de los objetos, y los renders) son suyos: no se borran sin su confirmación explícita, y se propone archivarlos en vez de eliminarlos.

**Blocked by:** 09 — Las cinco poses reales en la biblioteca; 13 — La versión previa y la revisión con la imagen 2D.

**Status:** ready-for-agent. Borrar los archivos del creador es una compuerta humana.

- [ ] Se borran el código de Blender de los planos y sus tests, y la suite completa sigue en verde con los tipos limpios.
- [ ] `estudio.toml` deja de pedir la ruta de Blender para renderizar planos.
- [ ] El ADR 0007 refleja que Blender ya no hace la imagen.
- [ ] Los `.blend` del salón, del recibidor y de los objetos, y las carpetas de renders, no se tocan hasta que el creador lo confirme; el agente propone archivarlos.
