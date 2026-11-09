# 18: Renderizar planos en Blender

**What to build:** Cada plano del piloto se monta en Blender (escenario enlazado de la biblioteca, cámara con su encuadre y movimiento, personajes colocados) y se renderiza por rangos de fotogramas desde la línea de comandos. La versión previa pasa de carteles a imagen real en calidad rápida, y se puede volver a renderizar solo un rango sin tocar el resto.

**Dónde:** PC de casa (ADR 0005).

**Blocked by:** 07 (Versión previa de cartón), 14 (Primer escenario de la biblioteca), 15 (Personajes: Tutor y Perro)

**Status:** ready-for-agent

- [ ] Cada plano renderiza su rango con la cámara que dice la lista de planos.
- [ ] Se puede volver a renderizar un rango sin tocar el resto.
- [ ] La versión previa muestra imagen real en calidad rápida.
- [ ] La cámara solo hace acercamientos lentos o desplazamientos con motivo, sin derivas.
- [ ] El agente ha revisado la hoja de contactos de esta versión previa.

## Comments

**2026-11-09, agente (desde el ticket 07).** La composición ya lleva una capa de imagen por plano. Para que un plano pase de cartel a imagen real, basta con dejar su render en `planos/<id>.png`, con el `id` de la lista de planos, y volver a montar. Si el render de un plano es un vídeo (cámara en movimiento) o una secuencia de imágenes, hay que ampliar `imagen_del_plano` en `src/estudio/montaje.py` para que lo encuentre, y su capa pasará de `<img>` a `<video>`. El resto de la composición no cambia. Ver "Planos: carteles e imágenes" en `docs/montaje.md`.
