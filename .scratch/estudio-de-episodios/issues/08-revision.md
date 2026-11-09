# 08: Revisión

**What to build:** La herramienta saca de cualquier versión de un episodio la hoja de contactos (un fotograma por segundo en una sola imagen) y la prueba de móvil (el episodio a 360 px de ancho). También comprueba la exportación: 1080x1920, 30/1 y la misma duración que la línea de tiempo, con un fotograma de margen.

**Blocked by:** 04 (Voces de prueba y cronometraje)

**Status:** ready-for-agent

- [ ] La hoja de contactos sale con el tamaño esperado.
- [ ] La prueba de móvil se genera.
- [ ] La comprobación de la exportación falla con un mensaje claro si no cuadran el tamaño, la velocidad o la duración, y pasa si cuadran.
- [ ] Probado con vídeos minúsculos generados con ffmpeg dentro de los propios tests.

## Comments

**2026-11-09, agente (desde el ticket 06).** Pendiente del creador: medir en Photoshop, sobre un pantallazo real de TikTok e Instagram, si la interfaz tapa los subtítulos. Ahora la línea de texto se apoya a 480 px del borde de abajo, entre los 1350 y los 1440 px desde arriba (ver "Sitio" en `docs/montaje.md`). Si hay que rectificar, se cambia `bottom: 480px` en `src/estudio/montaje.py`. La prueba de móvil de este ticket sirve para enseñárselo.
