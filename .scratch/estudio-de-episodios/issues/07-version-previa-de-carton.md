# 07: Versión previa de cartón

**What to build:** El primer esqueleto completo de un episodio. La composición une un cartel por plano (número de plano y escenario sobre un color liso), las voces, los subtítulos y el cierre del CTA con el nombre y el logo de la App (un marcador si todavía no hay logo). Es la misma composición que después llevará imágenes reales: cambiar el cartel de un plano por su render no exige tocar nada más.

**Blocked by:** 05 (Lista de planos), 06 (Primer montaje: subtítulos)

**Status:** ready-for-agent

- [ ] La composición tiene una capa de imagen por plano, con los tiempos de la línea de tiempo.
- [ ] El último plano muestra el nombre y el logo de la App mientras el Perro dice el CTA.
- [ ] Sustituir la imagen de un plano no obliga a cambiar nada más de la composición.
- [ ] Probado sin renderizar a través de la herramienta; hay un MP4 de una carpeta de ejemplo renderizado y revisado en fotogramas.

## Comments

**2026-11-09, agente (desde el ticket 05).** Los planos ya están en `linea-de-tiempo.json` (`planos`, con `id`, `inicio` y `final`). El escenario de cada cartel se lee de `planos.toml` por su `id` con `leer_planos` (`src/estudio/planos.py`). Nombrar la imagen de cada plano por su `id` evita que se descoloquen si se inserta un plano.

**2026-11-09, agente (desde el ticket 06).** La composición la escribe `montar` (`src/estudio/montaje.py`) con la plantilla `_COMPOSICION`; `_linea_de_tiempo` (`src/estudio/cli.py`) ya devuelve los planos de `planos.toml`. Al añadir una capa de imagen por plano:

- con `data-start`/`data-duration` en segundos, igual que las voces y los subtítulos; `z-index` por debajo de los subtítulos, porque el orden de pintado es el `z-index` y no `data-track-index`;
- las rutas, relativas a la carpeta del episodio, y nada de internet: el render tiene que salir igual sin red (ver "Todo sale de la carpeta del episodio" en `docs/montaje.md`);
- si se anima con GSAP, hay que llevarlo dentro de la carpeta y quitar `data-no-timeline` de la raíz. Si no, mejor CSS, como la entrada de los subtítulos.

