# 06 — La boca del Tutor en las palabras acentuadas

Spec: [estudio-2d](../spec.md). Requisito de partida: ticket 19 de `estudio-de-episodios`.

**What to build:** el Tutor mueve la boca solo en las palabras acentuadas y sincronizada con la línea de tiempo, como exige el ticket 19. En 2D la boca es una zona blanda de la mandíbula de cada pose del Tutor: se abre en las palabras acentuadas y está cerrada el resto del tiempo. El Perro, que habla en voz en off, nunca la mueve.

**Blocked by:** 04 — Gestos con zonas blandas en un plano con movimiento.

**Status:** ready-for-agent

- [ ] La ficha de cada pose del Tutor (sentado y de pie) lleva su zona blanda de la mandíbula, calibrada.
- [ ] La boca se abre solo dentro de las palabras acentuadas del Tutor según la línea de tiempo y está cerrada fuera de ellas.
- [ ] La sincronía es fotograma a fotograma, comprobada con la línea de tiempo del episodio de ejemplo.
- [ ] El Perro no mueve la boca en ningún fotograma.
- [ ] Un plano donde el Tutor no habla no cambia la boca en ningún fotograma.
- [ ] Los tests usan una zona de mandíbula sintética y comprueban los fotogramas que cambian.
