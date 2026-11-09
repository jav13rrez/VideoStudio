# 06: Primer montaje: subtítulos

**What to build:** La herramienta genera las tarjetas de subtítulo (1-2 palabras) a partir de las marcas de tiempo, y una composición de HyperFrames que las muestra sobre un fondo liso junto con las voces. Se renderiza a un MP4 vertical: es el primer vídeo que produce el estudio.

**Blocked by:** 04 (Voces de prueba y cronometraje)

**Status:** done

- [x] Tarjetas de 1-2 palabras; cada una empieza en el fotograma de su primera palabra y acaba donde empieza la siguiente o donde termina la frase.
- [x] Tutor: texto blanco con borde negro. Perro: texto lightcyan (`#E0FFFF`) con borde maroon (`#800000`). Los dos en negrita, con borde grueso alrededor de cada letra, abajo en el centro y dentro de la zona segura del 9:16.
- [x] Solo las tarjetas con palabras acentuadas tienen animación de entrada.
- [x] La composición generada tiene las capas de audio y de subtítulos con los tiempos de la línea de tiempo (probado sin renderizar).
- [x] Hay un MP4 1080x1920 a 30 fps renderizado con HyperFrames y revisado por el agente en fotogramas sueltos. Si en la nube no se puede renderizar, se comprueba en el PC.
- [x] La versión de HyperFrames queda fijada.

## Comments

**2026-11-09, agente.** Hecho.

- Las tarjetas salen en `linea-de-tiempo.json` (`subtitulos`). `uv run estudio montar <carpeta>` escribe la composición de HyperFrames (`index.html` en la carpeta del episodio). `uv run estudio renderizar <carpeta>` la monta y la renderiza a `versiones/previa.mp4`. Formato y reglas: [docs/montaje.md](../../../docs/montaje.md).
- 12 casos de test en `tests/test_subtitulos_y_montaje.py`, todos a través de la herramienta y sin renderizar.
- **Render revisado en la nube** (sí se puede: HyperFrames usa el Chrome del sistema). Con una copia de `001-olfato`, en unos 35 s:
  - el MP4 mide 1080x1920, va a 30 fps y tiene 1856 fotogramas, el total de la línea de tiempo;
  - con un pitido en lugar de cada voz falsa (que es silencio), cada silencio del MP4 empieza y acaba en el fotograma exacto en que acaba y empieza cada frase;
  - en fotogramas sueltos: el cambio de tarjeta cae en su fotograma (del 19 al 20, «¿Sabes por» → «qué te»); en la pausa entre frases no hay subtítulo; los colores, el borde y el sitio son los pedidos; «seis millones.» entra animada en el fotograma 454, cuando empieza «seis», y las tarjetas sin acento no se animan;
  - `hyperframes check`: 0 errores; zona segura (layout), contraste y audio sin avisos.
- **Versión fijada:** `hyperframes@0.9.26`, en `HYPERFRAMES` (`src/estudio/montaje.py`).

Decidido por el agente, además de lo que pedía el ticket:

- **Una tarjeta no cruza un signo de puntuación** («Vale,» va sola), para que se lea como se dice.
- **Una palabra acentuada abre su tarjeta**, salvo que siga a otra acentuada. Así la animación cae cuando se dice la palabra, y no una palabra antes, y cada tramo acentuado da una sola animación (historia 42).
- **Las tarjetas van dentro de la línea de tiempo**, como pide la spec en "Cronometraje".
- **`montar` y `renderizar` cronometran antes**, así que la composición nunca se queda atrás respecto al guion o las voces.
- **La carpeta del episodio es el proyecto de HyperFrames**: las voces se enlazan desde `voces/`, sin copiarlas.
- **Nada se descarga al renderizar.** La animación es CSS y no GSAP, que se carga de una web externa (bloqueada en la nube). La letra (Montserrat 900, OFL) va con el estudio en `src/estudio/letras/` y se copia en cada episodio con un nombre propio. Si no, HyperFrames la baja de Google Fonts y podría cambiar sin avisar.
- **Fondo liso gris azulado** (`#3B4A5A`), en el que se leen bien los dos colores de subtítulo.
- **El render de `renderizar` es en calidad de borrador**, la más rápida, porque es la versión previa.

Pendiente, con su motivo:

- **Tarjetas que duran poco.** Con la voz falsa (3 palabras por segundo), las 16 tarjetas de una palabra duran 0,33 s, y `hyperframes check` avisa de que son menos de los 0,4 s que recomienda para leer una palabra. Sale de la regla pedida (1-2 palabras que cambian con cada palabra), así que no se ha tocado. Lo juzga el creador en la parada 2, ya con voces reales.
- **Los colores y el estilo de los subtítulos están en `src/estudio/montaje.py`** y no en `estudio.toml`, aunque la spec ("Configuración") los pone en la configuración. Son reglas de la casa que no cambian de un episodio a otro. Si el creador quiere tocarlos a menudo, se pasan a `estudio.toml`.
- **La versión fija HyperFrames, no sus librerías ni el navegador.** Si hiciera falta un render idéntico en cualquier máquina, HyperFrames tiene `--docker`; se decide en el PC.
- **La prueba de móvil** (el episodio a 360 px de ancho) es del ticket 08.
- **Qué parte de la carpeta del episodio va a git** (`index.html`, `assets/`, `versiones/`) lo decide el ticket 10. La carpeta `.hyperframes/` que deja HyperFrames ya está en `.gitignore`.
- **Una palabra de más de unas 17 letras** no cabe en el ancho de los subtítulos: se sale por los dos lados, centrada, dentro de los márgenes. En el ejemplo no hay ninguna.
