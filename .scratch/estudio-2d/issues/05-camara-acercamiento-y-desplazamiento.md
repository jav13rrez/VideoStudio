# 05 — Cámara: acercamiento y desplazamiento

Spec: [estudio-2d](../spec.md).

**What to build:** los tres tipos de cámara que ya existen (fija, acercamiento lento y desplazamiento con motivo) con los mismos límites que hoy comprueba la orden, expresados como fracciones del encuadre. En 2D son recortes y escalados suavizados de un lienzo más grande, siempre en línea recta, que mueven a la vez los personajes y el escenario. El plano deja un vídeo con un fotograma por fotograma de la línea de tiempo.

**Blocked by:** 04 — Gestos con zonas blandas en un plano con movimiento.

**Status:** ready-for-agent

- [ ] Hay tres tipos de cámara: fija, acercamiento y desplazamiento, y cada plano usa el que dice su lista de planos.
- [ ] En el acercamiento, el ancho acaba entre el 70 % y el 100 % del inicial, con el centro casi quieto; en el desplazamiento, el centro se mueve una fracción pequeña fija y el ancho cambia como mucho un 10 %.
- [ ] El movimiento se suaviza al principio y al final y es una línea recta entre el principio y el final del plano.
- [ ] Un movimiento fuera de límites o que no concuerda con el tipo de cámara se rechaza con un mensaje claro.
- [ ] El lienzo es lo bastante grande para que el acercamiento no pierda nitidez.
- [ ] Personajes y escenario se mueven juntos y la unión con el suelo no se separa.
- [ ] Los tests miden la posición y el tamaño del encuadre en los fotogramas inicial, medio y final.
