# Revisión

La herramienta saca de cada versión de un episodio dos imágenes para revisarla de un vistazo, y comprueba la exportación antes de subirla. Usa ffmpeg y ffprobe (en WSL, `sudo apt install ffmpeg`).

## Hojas de revisión: `uv run estudio revisar <carpeta>`

Para cada vídeo de `versiones/` (`previa.mp4` y, cuando exista, `final.mp4`) deja en `revision/`:

- **`<versión>-contactos.png`**, la hoja de contactos: un fotograma por segundo, a 216x384, en filas de 8. Un episodio de 60 s da una imagen de 1728x3072.
- **`<versión>-movil.png`**, la prueba de móvil: el episodio a 360 px de ancho (360x640 por fotograma), uno cada 3 s, en filas de 6. Sirve para ver si los subtítulos se leen en un móvil y si la interfaz de TikTok o Instagram los taparía. Es una imagen, y no un vídeo, para que el agente también pueda revisarla.

Los huecos que sobran en la última fila salen en negro. Si una hoja no se puede sacar, se borra la de la vez anterior, para que no parezca nueva.

La crítica sobre estas hojas la hace el agente, siguiendo la skill del estudio. La herramienta solo las saca.

## Exportación: `uv run estudio comprobar-exportacion <carpeta>`

La exportación es el archivo que el creador sube a mano: `exportacion/<nombre de la carpeta>.mp4` (por ejemplo, `exportacion/001-olfato.mp4`). La comprobación pasa si:

- mide 1080x1920;
- va a 30/1 fotogramas por segundo;
- dura lo mismo que la línea de tiempo (`linea-de-tiempo.json`), con un fotograma de margen.

Si algo no cuadra, dice qué ha medido y qué esperaba, y avisa de todo lo que falla a la vez. La duración se mide en segundos y se pasa a fotogramas de la línea de tiempo, así que se compara aunque la velocidad esté mal. Hace falta haber cronometrado el episodio antes.

Copiar la versión final a `exportacion/` lo hace el paso de publicación (ticket 20).
