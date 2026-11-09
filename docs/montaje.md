# Montaje y render

Con las voces generadas, la herramienta del estudio monta el episodio: escribe la composición de HyperFrames con las voces y los subtítulos, y la renderiza a un MP4 vertical. Hoy la composición lleva un fondo liso; los planos y el cierre del CTA llegan en el ticket 07. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Subtítulos" y "Montaje (HyperFrames)", y [ADR 0007](adr/0007-herramientas-blender-y-hyperframes.md).

```bash
uv run estudio montar ruta/a/la/carpeta-del-episodio
```

```bash
uv run estudio renderizar ruta/a/la/carpeta-del-episodio
```

Las dos órdenes cronometran antes de montar (vuelven a escribir `linea-de-tiempo.json`), así que la composición siempre corresponde al guion, las voces y la lista de planos de ese momento. Se niegan a seguir por lo mismo que `cronometrar` (ver [voces-y-linea-de-tiempo.md](voces-y-linea-de-tiempo.md)), y entonces terminan con código de salida 1 sin escribir nada.

## Subtítulos

Las tarjetas de subtítulo salen en la línea de tiempo, en `subtitulos` (formato en [voces-y-linea-de-tiempo.md](voces-y-linea-de-tiempo.md)).

- Cada tarjeta lleva una o dos palabras de una misma frase. Una tarjeta no sigue después de una palabra que acaba en `.` `,` `;` `:` `?` `!` o `…`, para que se lea como se dice: «Vale, me ganas por goleada.» sale como «Vale,» · «me ganas» · «por goleada.».
- Cada tarjeta empieza en el fotograma en que empieza su primera palabra y acaba donde empieza la siguiente tarjeta de su frase; la última, donde acaba la frase. En la pausa entre frases no hay subtítulo.
- **Estilo**:
  - Tutor: texto blanco (`#FFFFFF`) con borde negro (`#000000`).
  - Perro: texto lightcyan (`#E0FFFF`) con borde maroon (`#800000`).
  - Los dos: Montserrat en su grosor más negro (900), a 88 px, con un borde de 20 px pintado por fuera de cada letra.
- **Sitio**: abajo en el centro, dentro de la zona segura del 9:16. La línea de abajo acaba a 1330 px del borde de arriba (por debajo, las aplicaciones ponen el texto del vídeo y sus botones) y deja 120 px a cada lado, fuera de la columna de botones de la derecha. Si una tarjeta no cabe en una línea, crece hacia arriba.
- **Animación**: solo las tarjetas con alguna palabra acentuada entran animadas. Crecen del 60 % al 100 % de su tamaño en 6 fotogramas, con un pequeño rebote. Las demás aparecen sin más.

Los colores están en `COLORES`, en `src/estudio/montaje.py`, y el resto del estilo, en la hoja de estilo de esa misma plantilla.

## `montar`

La carpeta del episodio es el proyecto de HyperFrames: `montar` deja en ella `index.html`, la composición. Lleva:

- 1080x1920, los fotogramas por segundo de `estudio.toml` y la duración total del episodio;
- un fondo liso (`#3B4A5A`, gris azulado);
- una capa de audio por frase (`voz-01`, `voz-02`…), que suena desde el principio de su frase hasta el final;
- una capa por tarjeta de subtítulo (`subtitulo-001`, `subtitulo-002`…), con el estilo de su personaje.

Los tiempos van en segundos, que es lo que lee HyperFrames, con seis decimales. HyperFrames los ajusta al fotograma, así que cada capa empieza y acaba en el fotograma exacto de la línea de tiempo. Es un archivo generado: no se edita a mano.

**Sin descargas**: la composición no carga nada de internet. La animación de entrada es CSS, que HyperFrames también lleva fotograma a fotograma, en lugar de la librería GSAP que suele cargar de una web externa. La letra Montserrat viene dentro de HyperFrames.

## `renderizar`

Monta el episodio y lo renderiza con HyperFrames a `versiones/previa.mp4`: 1080x1920 a 30 fps, con las voces. Es la versión previa: calidad de borrador, que es la más rápida.

- **Versión fijada**: `hyperframes@0.9.26`, en `HYPERFRAMES`, en `src/estudio/montaje.py`. HyperFrames saca versiones casi a diario; fijarla evita que un cambio suyo cambie los episodios. Para subirla: cambiar esa línea, renderizar el episodio de ejemplo y revisarlo en fotogramas.
- **Hace falta** Node.js 22 o más nuevo y ffmpeg. La primera vez, `npx` descarga HyperFrames; después lo usa de su caché.
- No renderiza si la composición tiene errores para HyperFrames (`--strict`).
- HyperFrames deja también en la carpeta del episodio una carpeta `.hyperframes/` con su historial; se puede borrar.
- En la nube (4 núcleos, sin tarjeta gráfica), los 62 s del episodio de ejemplo tardan unos 30 s.
