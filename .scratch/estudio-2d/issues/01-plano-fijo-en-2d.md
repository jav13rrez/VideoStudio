# 01 — Un plano fijo en 2D: Merlín de pie junto al lago

Spec: [estudio-2d](../spec.md). Es la bala trazadora: fija los formatos sobre los que cuelga todo lo demás.

**What to build:** `renderizar-planos` dibuja un plano fijo con el escenario del lago (cielo, montañas, lago, prado y una línea de suelo bien definida) y una pose del Perro (Merlín de pie, de perfil) tomada de la biblioteca con su ficha, y deja la imagen del plano. La pose apoya con lo más bajo de su silueta en la línea de suelo y lleva una sombra de contacto. Dos renders seguidos salen idénticos. Este ticket define el formato de la ficha de pose, el de la biblioteca de poses y el del archivo que dice qué lleva cada plano. Los tests usan una biblioteca de poses sintéticas, con siluetas conocidas.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `renderizar-planos` dibuja un plano con el escenario del lago y una pose, y deja la imagen de 1080x1920.
- [ ] Lo más bajo que apoya de la pose, medido con la transparencia mayor que 128 y no con la caja del recorte, cae en la línea de suelo del escenario, con una sombra de contacto debajo.
- [ ] La ficha de pose recoge la ilustración, la silueta opaca, qué partes apoyan en el suelo y cuáles se ignoran (como la cola del Perro), y el formato queda documentado.
- [ ] Dos renders del mismo plano salen idénticos: los elementos al azar del paisaje usan una semilla fija.
- [ ] Un plano fijo y sin gestos deja una sola imagen.
- [ ] Si falta la pose, su ficha o una medida, la orden lo dice con claridad y no dibuja a medias.
- [ ] Los tests usan figuras sintéticas y pasan junto con todos los anteriores.
- [ ] Las ilustraciones reales no entran en git.
