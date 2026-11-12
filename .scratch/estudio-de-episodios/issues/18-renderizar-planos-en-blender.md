# 18: Renderizar planos en Blender

**What to build:** Cada plano del piloto se monta en Blender (escenario enlazado de la biblioteca, cámara con su encuadre y movimiento, personajes colocados) y se renderiza por rangos de fotogramas desde la línea de comandos. La versión previa pasa de carteles a imagen real en calidad rápida, y se puede volver a renderizar solo un rango sin tocar el resto.

**Dónde:** PC de casa (ADR 0005).

**Blocked by:** 07 (Versión previa de cartón), 14 (Primer escenario de la biblioteca), 15 (Personajes: Tutor y Perro)

**Status:** done (2026-11-12)

- [x] Cada plano renderiza su rango con la cámara que dice la lista de planos.
- [x] Se puede volver a renderizar un rango sin tocar el resto.
- [x] La versión previa muestra imagen real en calidad rápida.
- [x] La cámara solo hace acercamientos lentos o desplazamientos con motivo, sin derivas.
- [x] El agente ha revisado la hoja de contactos de esta versión previa.

## Comments

**2026-11-09, agente (desde el ticket 07).** La composición ya lleva una capa de imagen por plano. Para que un plano pase de cartel a imagen real, basta con dejar su render en `planos/<id>.png`, con el `id` de la lista de planos, y volver a montar. Si el render de un plano es un vídeo (cámara en movimiento) o una secuencia de imágenes, hay que ampliar `imagen_del_plano` en `src/estudio/montaje.py` para que lo encuentre, y su capa pasará de `<img>` a `<video>`. El resto de la composición no cambia. Ver "Planos: carteles e imágenes" en `docs/montaje.md`.

**2026-11-12, agente (al cerrar el 18).** La orden es `uv run estudio renderizar-planos <carpeta> [--planos 03,05-07] [--fotogramas 5-8] [--calidad rapida|final]`, y la cámara y la colocación de cada plano salen de `tomas.toml` ([docs/tomas.md](../../../docs/tomas.md)). Los planos de cámara fija dejan una imagen (`planos/<id>.png`) y los de movimiento, un vídeo (`planos/<id>.mp4`), que la composición usa en lugar del cartel. Los 28 planos del piloto, en calidad rápida, tardan 2 min 36 s en el PC.

Hoja de contactos de la versión previa, revisada. Lo que se ve:
- Los personajes siguen sintiéndose «pegados» a la escena (recortes de foto, sin sombreado, contra un decorado 3D). El contorno y la sombra de contacto ayudan, pero el creador ya lo ha dicho; la actuación del ticket 19 es lo que más puede arreglarlo.
- El recibidor (planos 15 a 17) es provisional: el rellano sale casi quemado y la silueta del plano 17 parece un pictograma. Falta la aprobación del creador.
- El bocadillo y el móvil son provisionales (ticket 17); el bocadillo flota sobre la rodilla del Tutor en el plano 01.
- Faltan vistas: el Tutor solo tiene cabeza de frente y el Perro no tiene de espaldas ni tumbado; se han sustituido por el perfil (planos 04, 09, 15 y 27).
- Solo 5 de los 28 planos se mueven (los de cámara que se acerca o se desplaza); el resto son imágenes fijas hasta que haya actuación.
