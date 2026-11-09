# 07: Versión previa de cartón

**What to build:** El primer esqueleto completo de un episodio. La composición une un cartel por plano (número de plano y escenario sobre un color liso), las voces, los subtítulos y el cierre del CTA con el nombre y el logo de la App (un marcador si todavía no hay logo). Es la misma composición que después llevará imágenes reales: cambiar el cartel de un plano por su render no exige tocar nada más.

**Blocked by:** 05 (Lista de planos), 06 (Primer montaje: subtítulos)

**Status:** ready-for-agent (solo falta el MP4 renderizado; ver el último comentario)

- [x] La composición tiene una capa de imagen por plano, con los tiempos de la línea de tiempo.
- [x] El último plano muestra el nombre y el logo de la App mientras el Perro dice el CTA.
- [x] Sustituir la imagen de un plano no obliga a cambiar nada más de la composición.
- [ ] Probado sin renderizar a través de la herramienta (hecho); hay un MP4 de una carpeta de ejemplo renderizado y revisado en fotogramas (pendiente: ver el comentario).

## Comments

**2026-11-09, agente (desde el ticket 05).** Los planos ya están en `linea-de-tiempo.json` (`planos`, con `id`, `inicio` y `final`). El escenario de cada cartel se lee de `planos.toml` por su `id` con `leer_planos` (`src/estudio/planos.py`). Nombrar la imagen de cada plano por su `id` evita que se descoloquen si se inserta un plano.

**2026-11-09, agente (desde el ticket 06).** La composición la escribe `montar` (`src/estudio/montaje.py`) con la plantilla `_COMPOSICION`; `_linea_de_tiempo` (`src/estudio/cli.py`) ya devuelve los planos de `planos.toml`. Al añadir una capa de imagen por plano:

- con `data-start`/`data-duration` en segundos, igual que las voces y los subtítulos; `z-index` por debajo de los subtítulos, porque el orden de pintado es el `z-index` y no `data-track-index`;
- las rutas, relativas a la carpeta del episodio, y nada de internet: el render tiene que salir igual sin red (ver "Todo sale de la carpeta del episodio" en `docs/montaje.md`);
- si se anima con GSAP, hay que llevarlo dentro de la carpeta y quitar `data-no-timeline` de la raíz. Si no, mejor CSS, como la entrada de los subtítulos.


**2026-11-09, agente.** Hecho todo menos el MP4 renderizado con HyperFrames.

- `uv run estudio montar <carpeta>` monta la versión previa de cartón, y `renderizar` la monta y la renderiza. Formato: [docs/montaje.md](../../../docs/montaje.md), "Planos: carteles e imágenes" y "El cierre del CTA".
- **Una capa de imagen por plano** (`plano-01`, `plano-02`…), con los tiempos de `linea-de-tiempo.json`. Si el plano tiene su render en `planos/<id>.png`, lleva esa imagen; si no, un cartel que genera la herramienta en `assets/carteles/<id>.svg`.
- **El cartel** lleva el número del plano y su escenario sobre un color liso.
- **Sustituir un cartel por su imagen**: se deja la imagen en `planos/` y se vuelve a montar. En `index.html` solo cambia la imagen de esa capa (lo comprueba un test, línea a línea).
- **El cierre del CTA**: logo y nombre de la App arriba en el centro, desde el primer fotograma del CTA hasta el final. Si faltan, un marcador y un aviso.
- 15 casos de test nuevos (12 en `tests/test_version_previa.py` y 3 en `tests/test_lista_de_planos.py`), todos a través de la herramienta y sin renderizar. 126 tests en verde y mypy sin errores.
- **Revisado a la vista sin HyperFrames**: la composición abierta en Chromium, mostrando solo las capas de cada momento, como hace HyperFrames, en los segundos 0,5, 2,4, 26 y 59. Lo que se ve:
  - cartel, subtítulos y cierre en su sitio y sin tocarse;
  - un color por escenario;
  - con una imagen de prueba en `planos/05.png`, el plano 05 la muestra a pantalla completa con los subtítulos encima.

Pendiente, con su motivo:

- **El MP4 renderizado con HyperFrames.** En esta sesión, el sistema de permisos bloqueó la descarga de `hyperframes@0.9.26` con `npx`. Hay que renderizar una copia de `001-olfato` (con `tests/episodios/estudio.toml`, `biblioteca/` y `app/` encima) y revisar en fotogramas:
  - los cortes de plano;
  - el cierre del CTA en el fotograma 1736;
  - que los carteles SVG salen en el render.
- **Imágenes que no midan 1080x1920**: se recortan sin avisar. Si llega a pasar, que `montar` avise.

Decidido por el agente, además de lo que pedía el ticket:

- **La documentación de la App vive en la carpeta `app/`**, junto a `estudio.toml`, como la biblioteca. La herramienta lee `app/app.toml` (hoy `nombre` y `logo`). Allí añadirá el ticket 09 el enlace, y el creador dejará el resto (ticket 01). Así hay un solo sitio para todo lo de la App. Queda en la spec, en "Guion y fuentes".
- **Un color por escenario en los carteles**, para ver en la versión previa y en la hoja de contactos dónde cambia el escenario.
- **El cierre dura lo que el CTA**, y la lista de planos avisa si el último plano no empieza en la primera palabra del CTA. Así el cierre cae entero en el último plano.
- **Mientras falte el nombre o el logo de la App**, `montar` avisa y pone un marcador en su lugar, y monta igualmente; solo se niega si no entiende `app/app.toml`. Si el guion no tiene CTA, no hay cierre y la App no se lee.
- **Los carteles y el logo son imágenes SVG**, que no necesitan nada instalado. Llevan una letra del sistema, porque una imagen SVG no puede cargar letras.
- **Los planos con movimiento son cosa del ticket 18**: una imagen PNG es un fotograma fijo, que basta para la versión previa. Si el render final de un plano es un vídeo, el ticket 18 amplía `imagen_del_plano` (`src/estudio/montaje.py`) y su capa pasa a ser de vídeo, sin tocar el resto.
- **`assets/carteles/` y `assets/app/` se regeneran enteras** en cada montaje, para que no queden carteles ni logos viejos.
