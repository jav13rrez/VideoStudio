# 08: Revisión

**What to build:** La herramienta saca de cualquier versión de un episodio la hoja de contactos (un fotograma por segundo en una sola imagen) y la prueba de móvil (el episodio a 360 px de ancho). También comprueba la exportación: 1080x1920, 30/1 y la misma duración que la línea de tiempo, con un fotograma de margen.

**Blocked by:** 04 (Voces de prueba y cronometraje)

**Status:** done

- [x] La hoja de contactos sale con el tamaño esperado.
- [x] La prueba de móvil se genera.
- [x] La comprobación de la exportación falla con un mensaje claro si no cuadran el tamaño, la velocidad o la duración, y pasa si cuadran.
- [x] Probado con vídeos minúsculos generados con ffmpeg dentro de los propios tests.

## Comments

**2026-11-09, agente (desde el ticket 06).** Pendiente del creador: medir en Photoshop, sobre un pantallazo real de TikTok e Instagram, si la interfaz tapa los subtítulos. Ahora la línea de texto se apoya a 480 px del borde de abajo, entre los 1350 y los 1440 px desde arriba (ver "Sitio" en `docs/montaje.md`). Si hay que rectificar, se cambia `bottom: 480px` en `src/estudio/montaje.py`. La prueba de móvil de este ticket sirve para enseñárselo.

**2026-11-09, agente (desde el ticket 07).** La aplicación con la que el creador sigue las sesiones no reproduce vídeos MP4, pero sí muestra imágenes. La hoja de contactos de este ticket es la forma de enseñarle cada versión, y conviene que la prueba de móvil también salga como imagen (o como GIF). Para hacerse una idea, una hoja de contactos de 8 columnas a 216x384 por fotograma, hecha con ffmpeg (`fps=1,scale=216:384,tile=8x8`), se leyó bien con los 62 s del ejemplo.

**2026-11-11, agente (hecho).** `uv run estudio revisar <carpeta>` deja en `revision/` la hoja de contactos (`<versión>-contactos.png`) y la prueba de móvil (`<versión>-movil.png`, una imagen a 360 px de ancho, un fotograma cada 3 s) de cada vídeo de `versiones/`. `uv run estudio comprobar-exportacion <carpeta>` comprueba `exportacion/<carpeta>.mp4` contra la línea de tiempo. Probado también con la versión previa real del piloto (59 s): 1728x3072 y 2160x2560, y los subtítulos se leen. Detalle en [docs/revision.md](../../../docs/revision.md). Copiar la versión final a `exportacion/` queda para el ticket 20.
