# 04 — Gestos con zonas blandas en un plano con movimiento

Spec: [estudio-2d](../spec.md). Actuación de partida: ticket 19 de `estudio-de-episodios`.

**What to build:** un plano en el que las orejas y la cola del Perro se doblan con un peso que vale 0 en la unión con el cuerpo y 1 en la punta, con transición suave, siguiendo la actuación (anticipación, acción, pausa y vuelta sin rebote). El Perro parpadea con un párpado dibujado y los dos respiran con un estiramiento mínimo sobre la línea de suelo. El plano deja un vídeo con un fotograma por fotograma de la línea de tiempo.

**Prefactor primero.** La actuación de hoy habla de piezas de Blender. Antes de nada, se separa la curva de gestos y la lectura del archivo de actuación de lo que es de Blender, de modo que las partes que se mueven pasen a ser las zonas blandas de la ficha de pose.

La regla de la zona blanda, que salió del prototipo:

```
peso(x, y) = 0 en la unión, 1 en la punta, con transición suave (smoothstep)
ángulo(x, y) = ángulo del gesto × peso(x, y)
píxel de salida(x, y) = píxel de origen girado -ángulo(x, y) alrededor del pivote
```

**Blocked by:** 01 — Un plano fijo en 2D.

**Status:** ready-for-agent

- [ ] El prefactor se hace primero y los tests de la actuación existente siguen verdes.
- [ ] Una zona gira el ángulo del gesto por su peso y no cambia ningún píxel fuera de su caja; en la unión no hay huecos ni cortes (comprobado en la salida).
- [ ] Anticipación, acción, pausa y vuelta sin rebote ocurren en los fotogramas que dice la actuación.
- [ ] El párpado cierra y abre en pocos fotogramas, y los dos respiran con un movimiento muy leve sin separarse del suelo.
- [ ] El Perro no mueve la boca en ningún fotograma.
- [ ] Un gesto de una zona que la pose no tiene se rechaza con un mensaje claro.
- [ ] El vídeo mide 1080x1920 a 30 fotogramas, con un fotograma por fotograma de la línea de tiempo, y dos renders salen idénticos.
- [ ] Los tests usan una pose sintética con zonas conocidas.
