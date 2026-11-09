# 08: Revisión

**What to build:** La herramienta saca de cualquier versión de un episodio la hoja de contactos (un fotograma por segundo en una sola imagen) y la prueba de móvil (el episodio a 360 px de ancho). También comprueba la exportación: 1080x1920, 30/1 y la misma duración que la línea de tiempo, con un fotograma de margen.

**Blocked by:** 04 (Voces de prueba y cronometraje)

**Status:** ready-for-agent

- [ ] La hoja de contactos sale con el tamaño esperado.
- [ ] La prueba de móvil se genera.
- [ ] La comprobación de la exportación falla con un mensaje claro si no cuadran el tamaño, la velocidad o la duración, y pasa si cuadran.
- [ ] Probado con vídeos minúsculos generados con ffmpeg dentro de los propios tests.
