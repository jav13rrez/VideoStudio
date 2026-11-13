# Estilo 2D: cómo se dibuja y cómo se apoyan los personajes

La imagen del estudio es 2D ilustrada y plana ([ADR 0008](adr/0008-estudio-2d-ilustrado-con-exteriores.md)). Este documento fija las reglas que cumple **cada plano y cada pose**. El creador las dio al ver el prototipo (2026-11-13) y valen para todas las poses sentadas, de pie y tumbadas, presentes y futuras.

## Cómo se ve

- Formas planas con contorno oscuro de grosor uniforme y color liso; como mucho, sombreado de dos tonos. Nada fotográfico, sin luz realista ni profundidad de campo.
- Escenarios siempre exteriores y naturales (mar, bosque, lago, montaña, monte, prado), dibujados con código.
- El Tutor y Merlín van **siempre juntos y uno al lado del otro (side by side)**, lo más pegados posible. Los dos están a la misma distancia de la cámara: misma escala, misma línea de suelo y ninguno adelantado. Se rozan, pero no se tapan (la cola de Merlín puede tocar un zapato, no esconderlo).

## Dónde se apoya cada personaje

1. **Los pies (o el cuerpo) tocan el suelo bajando el cuerpo, nunca subiendo el terreno.** Si hay un hueco entre el personaje y el suelo, se baja al personaje. No se tapa con hierba, piedras ni objetos.
2. **Una sola línea de suelo.** Lo más bajo de la silueta (las suelas, las patas, el vientre) y la base de lo que haya al lado (roca, banco, tronco) están en la misma línea. Debajo de cada uno va su sombra de contacto.
3. **El suelo se mide con lo opaco.** La silueta se mide con los píxeles de transparencia mayor que 128 y no con la caja del recorte, porque el borde translúcido no se ve y hace parecer que el personaje flota.
4. **Sentado sobre un soporte (roca, banco, tronco):**
   - El cuerpo se coloca **sobre el centro del soporte y algo adelantado**, hacia su borde exterior. Detrás de la espalda se ve soporte.
   - El **techo del soporte queda a la altura del asiento y lo tapa el cuerpo**: el trasero siempre va encima. El soporte nunca asoma sobre el asiento.
   - El cuerpo va **un poco hundido**: el asiento queda algo por debajo del techo del soporte y los pies ya están sobre el suelo.
5. **Sentado directamente en el suelo, tumbado ("esfinge") y de pie:** lo más bajo de la silueta que apoya (las suelas, las patas, el vientre) va en la línea de suelo, con su sombra. En Merlín la línea de suelo son **las patas, no la cola**: la cola cuelga más abajo (en la pose sentada de perfil, 57 px de la ilustración por debajo de las patas) y no cuenta.
6. **Juntos, uno al lado del otro:** los dos comparten línea de suelo y escala. Se colocan en fila, uno junto al otro, y no se solapan para que uno tape al otro.

## Lo que cada pose debe llevar medido

Para que la regla se aplique sola, cada pose lleva en su ficha:

| Dato | Para qué | Valor medido (Tutor sentado de perfil) |
| --- | --- | --- |
| `asiento` | Píxeles que sube el asiento sobre lo más bajo de la silueta, en la ilustración original: da la altura del techo del soporte. | 157 px |
| `trasero` | Dónde cae el trasero, como fracción del ancho de la silueta contada desde la espalda: da el centro del soporte. | 0,17 |
| `suelo` | La caja de la silueta opaca. | calculada de la imagen |

Medidas del prototipo, en píxeles de la ilustración original:

| Pose | Silueta opaca (izquierda a derecha) | Línea de suelo | Notas |
| --- | --- | --- | --- |
| Merlín sentado de perfil | 169 a 1042 | patas en 778 (la cola llega a 835) | zonas blandas calibradas: oreja cercana, oreja lejana y cola |
| Javier sentado de perfil | 114 a 712 | suelas en 1066 | `asiento` 157 y `trasero` 0,17 |
| Javier de pie de perfil | pendiente de medir | pendiente | ilustrado el 2026-11-13 |
| Merlín de pie de perfil | pendiente de medir | pendiente | ilustrado el 2026-11-13 |
| Merlín tumbado ("esfinge") de perfil | pendiente de medir | pendiente | ilustrado el 2026-11-13 |

Las ilustraciones están en `.scratch/prototipo-2d/generado/` (fuera de git porque llevan el rostro del creador). La de Javier de pie salió sin cabeza a la primera, porque su hoja no trae la cabeza de perfil, y se arregló dándole a Fal la cabeza ya ilustrada de la versión sentada como segunda referencia.

Al añadir una pose sentada, se miden `asiento` y `trasero` sobre su ilustración, se coloca el soporte con las reglas de arriba y se comprueba con un recorte ampliado del asiento y de los pies antes de darla por buena.

## Movimiento: zonas blandas

Las orejas, la cola y cualquier parte que se mueva son **zonas de la propia ilustración** con un pivote y un peso por píxel: 0 en la unión con el cuerpo, 1 en la punta y una transición suave entre ambos. La zona gira con el ángulo del gesto multiplicado por ese peso. Así no hay piezas pegadas, cortes ni huecos. Los gestos usan la curva de [`actuacion.md`](actuacion.md) (anticipación, acción, pausa y vuelta sin rebote). El prototipo con los números de Merlín sentado de perfil está en `.scratch/prototipo-2d/animar.py` (`ZONAS`).
