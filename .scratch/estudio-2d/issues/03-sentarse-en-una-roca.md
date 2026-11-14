# 03 — Sentarse en una roca

Spec: [estudio-2d](../spec.md). Reglas: `docs/estilo-2d.md`.

**What to build:** una pose sentada apoyada en un soporte del escenario (la roca). El cuerpo va centrado sobre la roca y algo adelantado, un poco hundido, con roca visible detrás de la espalda. El techo de la roca queda tapado por el cuerpo: el trasero siempre va encima y la superficie nunca asoma. Las suelas y la base de la roca comparten la misma línea de suelo, con su sombra de contacto, y no se sube el terreno con hierba ni objetos. Cada pose sentada nueva hereda estas reglas con solo llevar en su ficha las medidas `asiento` y `trasero`.

**Blocked by:** 01 — Un plano fijo en 2D.

**Status:** ready-for-agent

- [x] Una pose sentada con `asiento` y `trasero` en su ficha se coloca sola sobre el soporte "roca" del escenario.
- [x] El cuerpo queda centrado y algo adelantado, un poco hundido, y se ve roca detrás de la espalda.
- [x] El techo de la roca queda tapado por el cuerpo y no asoma sobre el asiento (comprobado por píxeles en la salida).
- [x] Las suelas y la base de la roca comparten línea de suelo y llevan sombra de contacto; no hay hierba ni objeto que suba el terreno.
- [x] Una pose sentada nueva cumple todo lo anterior sin más trabajo que sus dos medidas.
- [x] Si a una pose sentada le faltan `asiento` o `trasero`, la orden lo dice con claridad.
- [x] Los tests usan una pose sentada sintética con medidas conocidas y comprueban las reglas.
