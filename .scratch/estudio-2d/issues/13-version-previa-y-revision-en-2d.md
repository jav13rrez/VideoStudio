# 13 — La versión previa y la revisión con la imagen 2D

Spec: [estudio-2d](../spec.md).

**What to build:** un episodio de ejemplo hecho con la imagen 2D recorre `montar`, `renderizar` y `revisar` sin que esas tres órdenes cambien: los planos fijos entran como imagen y los que se mueven como vídeo, la duración y la línea de tiempo son las de siempre y la versión previa sale en 1080x1920 a 30 fotogramas. `revisar` añade a sus hojas el recorte ampliado del asiento y de los pies de las poses sentadas de cada plano, para comprobar el apoyo de un vistazo.

**Blocked by:** 02 — Los dos personajes, uno al lado del otro; 03 — Sentarse en una roca; 04 — Gestos con zonas blandas en un plano con movimiento.

**Status:** ready-for-agent

- [ ] Un episodio de ejemplo en 2D sale por `montar`, `renderizar` y `revisar` sin cambiar el uso de esas órdenes.
- [ ] Los planos fijos entran como imagen y los planos con movimiento como vídeo.
- [ ] La versión previa mide 1080x1920 a 30 fotogramas y su duración coincide con la línea de tiempo.
- [ ] `revisar` deja el recorte ampliado del asiento y de los pies de las poses sentadas de cada plano.
- [ ] Los tests actuales de montaje y de revisión siguen en verde.
