# 09 — Las cinco poses reales en la biblioteca

Spec: [estudio-2d](../spec.md). Reglas: `docs/estilo-2d.md`.

**What to build:** las cinco poses de las hojas del creador, ilustradas y listas para el motor: Javier sentado y de pie, y Merlín sentado, de pie y tumbado ("esfinge"), todas de perfil. Cada una lleva su ficha con las medidas que pide el motor y las zonas blandas calibradas a mano. Las ilustraciones ya salieron del prototipo (fuera de git, porque llevan el rostro del creador) y se reutilizan; si alguna no convence, se repite con `generar-poses`. El creador aprueba cada pose.

**Blocked by:** 03 — Sentarse en una roca, 04 — Gestos con zonas blandas en un plano con movimiento.

**Status:** ready-for-agent. La aprobación de cada pose es del creador.

- [ ] Las cinco poses tienen ficha con su silueta opaca y su línea de suelo (en Merlín, las patas y no la cola).
- [ ] Las poses sentadas llevan `asiento` y `trasero`.
- [ ] Las tres poses de Merlín llevan calibradas la oreja cercana, la oreja lejana y la cola, y su ojo para el párpado.
- [ ] Cada pose tiene un recorte ampliado del asiento y de los pies, o de las patas, para revisarla de un vistazo.
- [ ] El creador aprueba cada pose y la aprobación queda registrada con su fecha.
- [ ] Ninguna ilustración con el rostro del creador entra en git (comprobado con git).
