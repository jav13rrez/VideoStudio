# Spec: imagen 2D ilustrada del estudio

Status: ready-for-agent

Vocabulario: [GLOSSARY.md](../../GLOSSARY.md). Decisión de partida: [ADR 0008](../../docs/adr/0008-estudio-2d-ilustrado-con-exteriores.md) (la imagen pasa de Blender a 2D ilustrado plano). Reglas que cumple cada plano: [docs/estilo-2d.md](../../docs/estilo-2d.md). Spec anterior, de la que esta sustituye la imagen: [estudio de episodios](../estudio-de-episodios/spec.md). El prototipo que la validó está en `.scratch/prototipo-2d/`.

## Problem Statement

El creador vio el piloto con la imagen hecha en Blender y la rechazó: "los personajes son ridículos, parecen recortes de papel sobre escenarios 3D". Los personajes eran láminas planas, sin sombreado, dentro de escenarios 3D con luz y profundidad de campo; dos estilos que chocaban. Pulir gestos o luz no lo arregla: el problema es de estilo.

Además, el flujo de Blender es caro y frágil para un creador que no programa: cada escenario se construye por pasadas, cada personaje necesita su montaje, y el resultado todavía no convence.

## Solution

Una imagen 2D ilustrada y plana en toda la producción: personajes y paisajes con formas lisas y contorno de grosor uniforme. El creador ya vio un prototipo de un plano ("has dado con la clave") y fijó las reglas:

- **Escenarios siempre exteriores y naturales:** mar, bosque, lago, montaña, monte y prado, dibujados con código.
- **El Tutor y el Perro siempre juntos, uno al lado del otro**, a la misma distancia de la cámara y sin taparse.
- **Todas las poses de sus hojas de personaje:** Tutor de pie y sentado; Perro sentado, de pie y tumbado.
- **Apoyo creíble:** los pies o el cuerpo tocan el suelo bajando el personaje, nunca subiendo el terreno; el trasero tapa siempre el techo del asiento; una sola línea de suelo.
- **Movimiento con zonas blandas:** orejas, cola y demás partes que se mueven son zonas de la propia ilustración que giran con un peso que se desvanece hacia el cuerpo, sin piezas pegadas ni cortes.

El estudio conserva todo lo demás: el guion, las voces, la línea de tiempo, los subtítulos, el montaje con HyperFrames, la revisión y la publicación. La imagen sale por la misma orden de siempre (`renderizar-planos`) y con los mismos archivos, así que lo que hay detrás no cambia.

## User Stories

### Estilo y escenarios

1. Como creador, quiero que personajes y paisajes compartan el mismo estilo plano con contorno uniforme, para que no parezcan recortes de papel sobre un decorado.
2. Como creador, quiero que los escenarios sean siempre exteriores y naturales, para que cada episodio parezca un día de un tutor y su perro.
3. Como creador, quiero escenarios de mar, bosque, lago, montaña, monte y prado, para que el entorno cambie según el tema.
4. Como creador, quiero que los escenarios se dibujen con formas planas hechas por el estudio y no se generen con IA, para que se vean limpios y siempre iguales.
5. Como creador, quiero que cada escenario tenga una línea de suelo bien definida, para que los personajes y los objetos apoyen en ella.
6. Como creador, quiero que cada escenario pueda llevar soportes (roca, banco, tronco) donde sentar a los personajes, para que ninguno parezca levitar.
7. Como creador, quiero aprobar cada escenario nuevo la primera vez que se crea, para que la biblioteca solo tenga paisajes que me gustan.
8. Como creador, quiero que el mismo escenario se reutilice entre planos y episodios, para que cada episodio cueste menos que el anterior.
9. Como creador, quiero que los elementos al azar del paisaje (flores, nubes) salgan siempre igual para un mismo plano, para que dos renders no cambien nada sin que yo lo pida.

### Personajes y poses

10. Como creador, quiero que el Tutor se dibuje a partir de mi hoja de personaje y se parezca a mí, para que sea reconocible.
11. Como creador, quiero que el Perro se dibuje a partir de la hoja de Merlín y conserve sus manchas y su pelaje, para que sea reconocible.
12. Como creador, quiero usar todas las poses de mis hojas (Tutor de pie y sentado; Perro sentado, de pie y tumbado), para poder elegir la que pide cada plano.
13. Como creador, quiero que cada pose lleve su propia ficha con sus medidas, para que el estudio la coloque sola sin que yo toque números.
14. Como creador, quiero que el estudio me avise si a una hoja le falta una vista que necesita una pose, antes de generar nada, para dársela yo.
15. Como creador, quiero que el Tutor de pie tenga cabeza aunque mi hoja no la traiga de perfil, para que la pose sirva.
16. Como creador, quiero aprobar cada pose la primera vez que se genera, para que no se use una versión que no me representa.
17. Como creador, quiero que las ilustraciones con mi rostro queden fuera de git, para que el repositorio pueda ser público sin exponerme.

### Generar las poses

18. Como creador, quiero una orden para generar las ilustraciones de pose a partir de mis hojas, para no pedirlas una a una a mano.
19. Como creador, quiero que esa orden me diga cuántas imágenes va a generar y cuánto costaría, antes de gastar, para decidir con la cuenta delante.
20. Como creador, quiero que no gaste nada sin mi confirmación explícita, para que nunca haya un cargo que no he aprobado.
21. Como creador, quiero que cada ilustración generada guarde con qué modelo y con qué texto se hizo, para poder repetirla o corregirla.
22. Como creador, quiero que la clave del proveedor se lea solo de `.env` y no se escriba nunca en pantalla, para no filtrarla.
23. Como agente, quiero un proveedor falso que genere ilustraciones de prueba sin gastar, para poder probar la orden en cada cambio.
24. Como creador, quiero que la orden me avise si una ilustración generada sale sin cabeza, sin cola o con un fondo que no se puede recortar, para repetirla antes de seguir.

### Colocación y composición

25. Como creador, quiero que el Tutor y el Perro vayan siempre juntos, uno al lado del otro y lo más pegados posible, para que se vea que son compañeros.
26. Como creador, quiero que los dos estén a la misma distancia de la cámara, con la misma escala y la misma línea de suelo, para que ninguno parezca adelantado.
27. Como creador, quiero que los dos se rocen sin taparse (la cola puede tocar un zapato, no esconderlo), para que ninguno pierda protagonismo.
28. Como creador, quiero que en cada plano se indique qué pose lleva cada personaje, para que la imagen esté decidida antes de dibujarla.
29. Como creador, quiero que el estudio coloque a los personajes en fila por reglas y no con coordenadas en píxeles, para no tocar números.
30. Como creador, quiero que el orden de los personajes en fila (cuál va a la izquierda) se pueda elegir por plano, para dirigir hacia dónde miran.
31. Como creador, quiero que, si los personajes y el soporte no caben a lo ancho, el estudio los reduzca a la misma escala, para que siempre quepan los dos.
32. Como creador, quiero que el estudio me avise si una combinación de poses no cabe o no se puede colocar, en lugar de dibujarla mal.

### Apoyo en el suelo y en el asiento

33. Como creador, quiero que los pies o el cuerpo de cada personaje toquen el suelo bajando al personaje y nunca subiendo el terreno, para que nadie flote ni haya hierba que tape huecos.
34. Como creador, quiero que lo más bajo de cada personaje que apoya (suelas, patas, vientre) esté en la línea de suelo, para que todos apoyen igual.
35. Como creador, quiero que en el Perro la línea de suelo sean las patas y no la cola, para que no se hunda por una cola que cuelga.
36. Como creador, quiero que la base de un soporte y las suelas compartan la misma línea de suelo, para que todo apoye en el mismo sitio.
37. Como creador, quiero que debajo de cada personaje y de cada soporte haya una sombra de contacto, para que se vea que tocan el suelo.
38. Como creador, quiero que, sentado en un soporte, el cuerpo vaya centrado y algo adelantado, con soporte visible detrás de la espalda, para que se vea que se sienta de verdad.
39. Como creador, quiero que el cuerpo tape siempre el techo del soporte, para que el trasero vaya encima y no asome la superficie.
40. Como creador, quiero que el cuerpo vaya un poco hundido en el soporte, para que se vea apoyado.
41. Como creador, quiero que la silueta se mida solo con lo opaco, para que el borde translúcido del recorte no haga parecer que flota.
42. Como creador, quiero que toda pose sentada nueva herede estas reglas sin que yo las repita, para no corregir lo mismo en cada pose.

### Movimiento y actuación

43. Como creador, quiero que las orejas y la cola del Perro se doblen de forma suave y continua desde el cuerpo, para que no se vean cortes ni piezas pegadas.
44. Como creador, quiero que la cara del Perro se vea siempre completa en cada fotograma, para que no se deforme al moverle las orejas.
45. Como creador, quiero que cada gesto empiece con una anticipación, siga con la acción, se mantenga y vuelva al reposo sin rebote, para que parezca que piensa.
46. Como creador, quiero que el Perro parpadee con un párpado dibujado, para que parezca vivo sin mover la cara.
47. Como creador, quiero que el Perro no mueva nunca la boca, porque habla en voz en off.
48. Como creador, quiero que el Tutor mueva la boca solo en las palabras acentuadas y sincronizada con la línea de tiempo, para que se vea que habla.
49. Como creador, quiero que los dos respiren con un movimiento muy leve sobre la línea de suelo, para que no parezcan una imagen fija.
50. Como creador, quiero que la actuación se siga escribiendo en una línea por plano (pensamiento, anticipación, acción y pausa) con los gestos del Perro, para no aprender un formato nuevo.
51. Como agente, quiero que el estudio rechace un gesto de una parte que la pose no tiene (por ejemplo, la cola en una pose de frente), para no dibujar movimientos imposibles.
52. Como creador, quiero que ningún personaje rebote ni se mueva sin motivo, para que no se note que es animación generada.

### Cámara y salida

53. Como creador, quiero que la cámara siga siendo fija, un acercamiento lento o un desplazamiento con motivo, para que el episodio se vea dirigido.
54. Como creador, quiero que los movimientos de cámara se suavicen al principio y al final, para que no haya tirones.
55. Como creador, quiero que un plano sin movimiento de cámara ni gestos deje una sola imagen, para que el render sea rápido.
56. Como creador, quiero que un plano con movimiento deje un vídeo de 1080x1920 a 30 fotogramas, con un fotograma por fotograma de la línea de tiempo, para que el montaje encaje.
57. Como creador, quiero que el montaje y la versión previa sigan funcionando sin cambios con la imagen nueva, para no rehacer lo que ya funciona.
58. Como creador, quiero que dos renders del mismo plano salgan idénticos, para comparar versiones sin ruido.
59. Como creador, quiero poder renderizar solo algunos planos o un rango de fotogramas, para revisar sin esperar a todo el episodio.
60. Como creador, quiero que la orden me diga con claridad qué falla (pose, medida, soporte, gesto) y no dibuje a medias, para saber qué corregir.

### Revisión y biblioteca

61. Como creador, quiero que el estudio guarde un recorte ampliado del asiento y de los pies de cada pose sentada, para comprobar el apoyo de un vistazo.
62. Como creador, quiero que la biblioteca guarde las poses y los escenarios aprobados, para reutilizarlos entre episodios.
63. Como creador, quiero que los documentos del proyecto (glosario, mapa, progreso) reflejen que la imagen es 2D, para que ningún agente trabaje con el Blender antiguo.

## Implementation Decisions

- **Un motor de dibujo en la herramienta del estudio.** Es Python puro y determinista, sin Blender: dibuja el paisaje, coloca las poses, aplica los gestos y escribe los mismos archivos que hoy deja el render de planos (imagen fija o vídeo de 1080x1920 a 30 fotogramas, un fotograma por fotograma de la línea de tiempo). Así el montaje, la versión previa, la revisión y la exportación no cambian. La orden pública sigue llamándose `renderizar-planos`.
- **El código de Blender se queda hasta que el motor 2D lo sustituya** y se borra en un ticket de limpieza aparte ([ADR 0008](../../docs/adr/0008-estudio-2d-ilustrado-con-exteriores.md)).
- **Biblioteca de poses.** Cada personaje tiene una ficha por pose con: la ilustración con transparencia, las medidas de su silueta, qué partes apoyan en el suelo (y cuáles se ignoran, como la cola del Perro), `asiento` y `trasero` si es una pose sentada, el ojo (para el párpado) y sus zonas blandas. Las poses iniciales son todas de perfil: Tutor de pie y sentado; Perro sentado, de pie y tumbado ("esfinge"). Las ilustraciones del Tutor llevan el rostro del creador y siguen fuera de git. Quedan fuera las vistas de frente.
- **Recorte y medida.** El fondo se quita con un relleno desde los bordes con tolerancia, y la silueta se mide con la transparencia mayor que 128. La caja del recorte, con su borde translúcido, nunca se usa para el suelo.
- **Escenarios como recetas de dibujo.** Cada escenario es una receta con parámetros (cielo, horizonte, línea de suelo, soportes disponibles) que se dibuja con formas planas de contorno uniforme. Los elementos al azar usan una semilla fija por escenario. El primero es el lago con montañas y prado del prototipo; mar, bosque y monte llegan en tickets posteriores y cada uno pasa por el creador.
- **Colocación por reglas.** Un plano indica el escenario, la cámara y, para cada personaje, su pose y, si va sentado, su soporte. Los personajes van en fila de izquierda a derecha, a la misma escala y con la misma línea de suelo, separados por una distancia mínima fija, y se reducen juntos si no caben. La orden rechaza una combinación que no cabe o que no se puede colocar. Las reglas de apoyo son las de `estilo-2d` (bajar al personaje, una línea de suelo, trasero sobre el techo del soporte, centrado y algo adelantado, un poco hundido, sombra de contacto).
- **Cámara.** Sigue habiendo tres tipos (fija, acercamiento, desplazamiento) con los límites que hoy ya se comprueban. En 2D son recortes y escalados suavizados de un lienzo más grande, en línea recta. Un plano sin cámara en movimiento y sin gestos deja una sola imagen.
- **Zonas blandas.** Cada parte que se mueve es una zona con un pivote, una caja y un peso por píxel: 0 en la unión con el cuerpo, 1 en la punta y una transición suave. El ángulo de cada píxel es el del gesto multiplicado por su peso, y cada píxel sale de girar su posición, alrededor del pivote, el ángulo contrario. Fuera de la caja de la zona no cambia ningún píxel. Esto salió del prototipo:

  ```
  peso(x, y) = 0 en la unión, 1 en la punta, con transición suave (smoothstep)
  ángulo(x, y) = ángulo del gesto × peso(x, y)
  píxel de salida(x, y) = píxel de origen girado -ángulo(x, y) alrededor del pivote
  ```

- **Actuación.** Se mantiene el formato de `actuacion.toml` y la curva del ticket 19: anticipación, acción, pausa y vuelta sin rebote. Cambia lo que mueve cada gesto: las piezas de un gesto pasan a ser las zonas blandas de la pose, y el estudio rechaza un gesto de una zona que la pose no tiene. El Perro no mueve nunca la boca. El párpado se dibuja sobre el ojo con el color del pelo de al lado y, cerrado, deja una línea. Los dos respiran con un estiramiento mínimo sobre la línea de suelo.
- **Boca del Tutor.** Se abre solo en las palabras acentuadas y sincronizada con la línea de tiempo, como exige el ticket 19. Hace falta una zona blanda de la mandíbula por pose del Tutor, que se calibra en un ticket aparte.
- **Orden `generar-poses`.** Recibe el personaje y la pose, lee la hoja del creador, comprueba que trae la vista necesaria y construye el texto con una plantilla fija del estilo de la casa. Antes de gastar muestra cuántas imágenes va a generar y cuánto costarían, y exige una confirmación explícita. Después guarda las ilustraciones y anota en la ficha qué modelo las hizo, con qué texto y cuándo. La clave del proveedor se lee solo de `.env`. Para una pose sin cabeza en la hoja (el Tutor de pie), usa como segunda referencia la cabeza ya ilustrada de otra pose. Hay un proveedor `fal` y un proveedor `falso`, que genera ilustraciones de prueba sin gastar.
- **Glosario y documentos.** Se actualizan el glosario (Escenario ya no es un decorado 3D; entran Pose, Zona blanda, Línea de suelo y Soporte), el mapa del repositorio y el estado del proyecto.
- **Montaje.** No cambia: HyperFrames sigue montando los planos ya dibujados ([ADR 0007](../../docs/adr/0007-herramientas-blender-y-hyperframes.md)).

## Testing Decisions

- **Qué es un buen test aquí:** solo mira lo que sale (los archivos de imagen y de vídeo, los mensajes de error y lo que se escribe en la ficha), nunca cómo se calcula por dentro. Si el cálculo cambia pero la imagen es la misma, el test sigue pasando.
- **Dos puntos de prueba, los dos a través de la línea de comandos**, como el resto del proyecto (se acordó con el creador):
  1. **`renderizar-planos`**, sobre una carpeta de episodio de ejemplo con una biblioteca de poses de prueba. Se comprueba:
     - las medidas y el número de fotogramas de la salida;
     - que lo más bajo que apoya de cada personaje cae en la línea de suelo compartida;
     - que los dos van uno al lado del otro, a la misma escala, sin taparse más allá de rozarse;
     - que el trasero tapa el techo del soporte y que el soporte se ve detrás de la espalda;
     - que las zonas blandas no cambian ningún píxel fuera de su caja y que no hay huecos ni cortes en la unión;
     - que los gestos, la boca del Tutor y el parpadeo cambian solo en los fotogramas que dice la actuación y la línea de tiempo;
     - que el Perro no mueve la boca en ningún fotograma;
     - que dos renders del mismo plano salen idénticos;
     - que un plano sin movimiento deja una sola imagen;
     - los mensajes de error de una pose que falta, una medida que falta, un gesto de una zona que no existe y una combinación que no cabe.
  2. **`generar-poses`**, con el proveedor `falso`. Se comprueba que no genera nada sin confirmación explícita, que muestra el coste antes, que deja las ilustraciones y la ficha con el modelo, que avisa si falta una vista en la hoja y que nunca escribe la clave en pantalla.
- **Los datos de prueba son figuras sintéticas** (rectángulos y elipses con una silueta y una línea de suelo conocidas), para que las medidas se puedan comprobar con exactitud. Las ilustraciones reales nunca entran en los tests, porque llevan el rostro del creador.
- **La revisión visual no es un test.** El agente mira las hojas y los recortes ampliados y el creador da el visto bueno; los tests cubren las reglas medibles.
- **Antecedentes en el repositorio:** los tests de `renderizar-planos` (Blender falso que anota sus llamadas), los de la actuación (boca del Tutor y gestos del Perro) y los de las voces (proveedor `falso`) siguen el mismo modelo: la orden sobre una carpeta de ejemplo copiada, y lo observable en lo que sale.

## Out of Scope

- Las vistas de frente de los dos personajes (hoy solo hay de perfil).
- Animar la cabeza y la mirada del Perro; hoy solo orejas, cola y párpado.
- Las expresiones de los ojos del Tutor (solo se mueve la boca).
- Escenarios interiores, que el creador descartó.
- Calibrar las zonas blandas de forma automática (cada pose se calibra a mano).
- Borrar el código de Blender (ticket de limpieza aparte).
- Elegir música y efectos del piloto.
- Replantear el piloto `001-mirada`, que se escribió con salón y recibidor (ver Further Notes).
- Generar con IA los paisajes.

## Further Notes

- **Prototipo.** En `.scratch/prototipo-2d/` están `generar.py` (llamadas a Fal), `piezas.py` (recorte) y `animar.py` (paisaje, zonas blandas, roca, párpado y composición). Es la base del código definitivo, pero está calibrado a mano para Merlín sentado de perfil.
- **Lo que el creador corrigió, y que esta spec convierte en regla:** no inventar hierba para tapar un hueco (bajar al personaje, no subir el terreno); sentar al Tutor centrado y algo adelantado sobre la roca, un poco hundido; que el trasero tape el techo de la roca; que Merlín y él vayan uno al lado del otro y no con Merlín adelantado.
- **Decisión por confirmar con el creador: el objeto protagonista.** El glosario dice que "siempre se construye en 3D, nunca se dibuja plano", y los objetos actuales (bocadillo, móvil, silueta) están en Blender. Con la imagen 2D, lo coherente es dibujarlos planos en el mismo estilo. No se ha hablado con el creador y esta spec no lo cierra.
- **El piloto.** El guion del piloto y su lista de planos usan el salón y el recibidor, y el creador ha decidido que los escenarios sean siempre exteriores. Hay que replantear sus planos (y quizá el guion) o elegir otro primer episodio. Es una decisión de producto, fuera de esta spec.
- **Coste.** Las ilustraciones generadas con Fal costaron, según mi estimación sin verificar, unos 0,3 a 0,8 € las diez del prototipo. Cada pose nueva cuesta una o dos llamadas más y pasa por la confirmación del creador.
- **Riesgos.** Fal puede redibujar una pose con otra cabeza o con otra grupa, y eso rompió las primeras piezas del prototipo; por eso las partes que se mueven se doblan sobre la ilustración original completa y no se generan por separado. El recorte por relleno asume un fondo liso; si una hoja no lo trae, la orden debe avisar.
