# 06 — La boca del Tutor en las palabras acentuadas

Spec: [estudio-2d](../spec.md). Requisito de partida: ticket 19 de `estudio-de-episodios`.

**What to build:** el Tutor mueve la boca solo en las palabras acentuadas y sincronizada con la línea de tiempo, como exige el ticket 19. En 2D la boca es una zona blanda de la mandíbula de cada pose del Tutor: se abre en las palabras acentuadas y está cerrada el resto del tiempo. El Perro, que habla en voz en off, nunca la mueve.

**Blocked by:** 04 — Gestos con zonas blandas en un plano con movimiento.

**Status:** code done (2026-11-14); calibration of the real poses pending

- [ ] La ficha de cada pose del Tutor (sentado y de pie) lleva su zona blanda de la mandíbula, calibrada.
- [x] La boca se abre solo dentro de las palabras acentuadas del Tutor según la línea de tiempo y está cerrada fuera de ellas.
- [x] La sincronía es fotograma a fotograma, comprobada con la línea de tiempo del episodio de ejemplo.
- [x] El Perro no mueve la boca en ningún fotograma.
- [x] Un plano donde el Tutor no habla no cambia la boca en ningún fotograma.
- [x] Los tests usan una zona de mandíbula sintética y comprueban los fotogramas que cambian.

Notas de lo hecho: la zona `boca` de la ficha (solo en poses del Tutor), la lógica común en `boca_del_tutor.py` y el dibujo en `dibujar_planos.py`. Queda sin marcar el primer criterio (calibrar la mandíbula de las poses reales del Tutor, sentado y de pie): las ilustraciones reales se generan en los tickets 08 y 09, y los retratos de perfil del creador sirven de referencia.
