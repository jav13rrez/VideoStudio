# 02 — Los dos personajes, uno al lado del otro

Spec: [estudio-2d](../spec.md).

**What to build:** un plano con el Tutor y el Perro en fila, uno al lado del otro: a la misma escala, con la misma línea de suelo y a la misma distancia de la cámara, rozándose sin taparse (la cola de Merlín puede tocar un zapato, no esconderlo). Se elige por plano cuál va a la izquierda. Si los dos no caben a lo ancho, se reducen juntos a una escala común; si ni así caben, la orden avisa y no dibuja.

**Blocked by:** 01 — Un plano fijo en 2D.

**Status:** ready-for-agent

- [x] Dos personajes salen en fila de izquierda a derecha, con la misma escala y la misma línea de suelo; ninguno va adelantado.
- [x] Hay una separación mínima fija entre ellos y sus siluetas no se solapan más allá de rozarse.
- [x] Si no caben a lo ancho, se reducen juntos a una escala común y los dos caben.
- [x] Si una combinación no cabe ni reducida, la orden lo dice con claridad y no dibuja.
- [x] Se elige por plano cuál va a la izquierda.
- [x] Cada uno lleva su sombra de contacto.
- [x] Los tests, con figuras sintéticas, comprueban escala, línea de suelo, separación y no solape.
