# Dibujo 2D de los planos

La imagen del estudio es 2D ilustrada y plana ([ADR 0008](adr/0008-estudio-2d-ilustrado-con-exteriores.md)). Las reglas de estilo y de apoyo de los personajes están en [estilo-2d.md](estilo-2d.md); aquí está cómo se le dice a la herramienta del estudio qué lleva cada plano y cómo se dibuja. Es la spec [estudio-2d](../.scratch/estudio-2d/spec.md); este documento recoge lo que hacen los tickets [01](../.scratch/estudio-2d/issues/01-plano-fijo-en-2d.md), [02](../.scratch/estudio-2d/issues/02-dos-personajes-lado-a-lado.md), [03](../.scratch/estudio-2d/issues/03-sentarse-en-una-roca.md), [04](../.scratch/estudio-2d/issues/04-gestos-con-zonas-blandas.md), [05](../.scratch/estudio-2d/issues/05-camara-acercamiento-y-desplazamiento.md), [06](../.scratch/estudio-2d/issues/06-boca-del-tutor.md) y [07](../.scratch/estudio-2d/issues/07-generar-poses-con-proveedor-falso.md).

```bash
uv run estudio renderizar-planos ruta/a/la/carpeta-del-episodio
uv run estudio renderizar-planos ruta/a/la/carpeta-del-episodio --planos 03,05-07
```

## Cómo se elige el motor

`renderizar-planos` sigue siendo la misma orden, con los mismos argumentos. Mira si el episodio tiene un `reparto.toml` junto a `planos.toml`:

- **Con `reparto.toml`:** dibuja los planos en 2D, sin Blender. Un plano deja `planos/<id>.png`, de 1080x1920, o, si tiene línea en [`actuacion.toml`](actuacion.md) y algún personaje, o si su cámara se mueve, o si en él habla el Tutor, un vídeo `planos/<id>.mp4` (véanse «Gestos, párpado y respiración» y «Cámara»).
- **Sin él:** renderiza con Blender desde `tomas.toml`, como antes ([tomas.md](tomas.md)).

`--calidad` solo cuenta con Blender: el dibujo 2D sale siempre a tamaño real. La carpeta `planos/` no va a git, se puede volver a generar, y `montar` y `renderizar` usan la imagen de cada plano en lugar de su cartel ([montaje.md](montaje.md)). Dos renders del mismo plano salen idénticos.

## `reparto.toml`

Dice qué poses lleva cada plano.

```toml
[[plano]]
id = "03"                                  # el id de un plano de planos.toml
personajes = [{ pose = "perro_de_pie" }]   # una pose por personaje (hasta dos); vacío si no hay ninguno
```

| Campo | ¿Obligatorio? | Qué es |
| --- | --- | --- |
| `id` | sí | El plano al que corresponde: tiene que estar en `planos.toml`. |
| `personajes` | no (vacío) | Lista de personajes del plano, cada uno con su `pose`. Hasta dos; el orden de la lista es el orden en el plano, de izquierda a derecha. |
| `desde`, `hasta` | solo con cámara en movimiento | La vista al empezar y al acabar el plano (véase «Cámara»). |

Solo hace falta el reparto de los planos que se renderizan: los demás pueden esperar. El escenario de cada plano sale del campo `escenario` de `planos.toml`, y el tipo de cámara de su campo `camara`.

## Biblioteca de poses

Cada pose es una ilustración con transparencia y su ficha, en `biblioteca/personajes/<personaje>/poses/`. El nombre de la pose es `<personaje>_<pose>`, con minúsculas, números y guiones bajos (`perro_de_pie`, `tutor_sentado`), y el personaje es lo que va antes del primer guion bajo.

```
biblioteca/personajes/perro/poses/perro_de_pie.png     # la ilustración (PNG con transparencia)
biblioteca/personajes/perro/poses/perro_de_pie.toml    # su ficha
```

Las ilustraciones del Tutor llevan el rostro del creador y van fuera de git; las del Perro no.

### La ficha

```toml
ilustracion = "perro_de_pie.png"   # el PNG, junto a la ficha

# Partes que no cuentan para apoyar en el suelo: la cola cuelga más abajo que las patas.
[[ignora]]
parte = "cola"
caja = [820, 790, 1100, 896]       # x0, y0, x1, y1 en píxeles de la ilustración; x1 e y1, el primero de fuera
```

| Campo | ¿Obligatorio? | Qué es |
| --- | --- | --- |
| `ilustracion` | sí | El nombre del PNG, junto a la ficha y sin carpetas. |
| `ignora` | no | Lista de partes que no cuentan al apoyar, cada una con su `parte` (un nombre) y su `caja`, que tiene que caer dentro de la ilustración. |
| `asiento` | solo en poses sentadas (con `trasero`) | Los píxeles de la ilustración que sube el asiento sobre las suelas: un número mayor que 0 y menor que lo que mide la pose de alto sobre el suelo. |
| `trasero` | solo en poses sentadas (con `asiento`) | Dónde cae el trasero, como fracción del ancho de la silueta contada desde la espalda: un número entre 0 y 1, sin llegar a ellos. |
| `zona` | no | Una zona blanda que se mueve (véase «Gestos, párpado y respiración»). Puede haber varias: una por cada oreja y una para la cola del Perro, y una para la boca de cada pose del Tutor. |
| `ojo` | no | La caja del ojo `[x0, y0, x1, y1]`, en píxeles de la ilustración, para el párpado. Sin ella, la pose no parpadea. |
| `generacion` | no | La tabla que anota `generar-poses` con el `modelo` que hizo la ilustración, el `texto` que se le mandó y la `fecha` (AAAA-MM-DD). La herramienta no la usa para dibujar; sirve para repetir o corregir la ilustración. |

Una pose con `asiento` y `trasero` es sentada y se coloca sola sobre una roca (véase «Sentarse en una roca»). Van los dos o ninguno: con uno solo, la orden lo dice y no dibuja. Sin ninguno, la pose apoya en el suelo como siempre.

La ficha solo dice lo que no se puede medir. La silueta y la línea de suelo se miden de la ilustración, con los píxeles de transparencia mayor que 128: el borde casi transparente que deja un recorte no cuenta, porque no se ve y haría parecer que el personaje flota.

## Cómo se coloca

- **Escala:** todas las poses se dibujan con la misma escala (0,66 sobre su ilustración): las ilustraciones siguen una misma convención de píxeles por metro.
- **Horizontal, un personaje:** la silueta, la cola incluida, queda centrada en la imagen.
- **Horizontal, dos personajes:** van en fila, de izquierda a derecha en el orden de `personajes` (así se elige por plano cuál va a la izquierda). Las siluetas, con la cola incluida, guardan una separación fija de 20 píxeles: se rozan sin taparse, y la cola de uno no pisa al vecino. El grupo queda centrado en la imagen.
- **Si no caben a lo ancho:** los dos se reducen juntos a una escala común, sin deformarlos, hasta un mínimo de 0,45. Más abajo, la orden no dibuja. Un personaje solo no se reduce: si no cabe, se rechaza.
- **Suelo:** lo más bajo que apoya (sin las partes que la ficha ignora) cae en la línea de suelo del escenario, y la misma para los dos: ninguno va adelantado. Se baja al personaje: nunca se sube el terreno ([estilo-2d.md](estilo-2d.md)).
- **Sombra de contacto:** una elipse oscura bajo cada pose, en la línea de suelo.
- **Si no cabe:** unas poses cuya silueta, ya escalada y colocada, se sale de la imagen se rechazan en vez de dibujarlas recortadas.

### Sentarse en una roca

Una pose sentada (con `asiento` y `trasero` en su ficha) lleva debajo una roca que dibuja la orden, sin más trabajo que esas dos medidas:

- **Centrada en el trasero:** la roca se centra en el trasero y sobresale 60 píxeles por detrás de la espalda, para que se vea roca detrás. No pasa por delante de la silueta.
- **Techo tapado:** el techo de la roca queda 10 píxeles por encima del asiento, de modo que el cuerpo va algo hundido y el trasero va siempre encima: la superficie de la roca nunca asoma.
- **Suelo:** las suelas y la base de la roca comparten la línea de suelo, y la roca lleva su propia sombra de contacto, que sobresale unos 20 píxeles por cada lado. Se baja al personaje: no se sube el terreno con hierba ni objetos.
- **Con otro personaje:** una pose sentada comparte plano con otra en fila, con las reglas de siempre.

## Gestos, párpado y respiración

Un plano con línea en `actuacion.toml` y al menos un personaje deja un vídeo (`planos/_fotogramas/<id>/` y `planos/<id>.mp4`) con un fotograma por fotograma de su tramo de la línea de tiempo, a 1080x1920 y 30 fotogramas por segundo. Sin línea en `actuacion.toml` (o sin el archivo), el plano sigue siendo una sola imagen. Dos renders del mismo plano salen idénticos.

**Zonas blandas.** Las orejas y la cola son partes de la propia ilustración, no piezas pegadas: la ficha de la pose dice dónde están y la herramienta las dobla.

```toml
ojo = [252, 158, 292, 188]

[[zona]]
parte = "cola"                    # orejas o cola (las mueven los gestos) o boca (solo en el Tutor)
caja = [780, 600, 1100, 896]      # x0, y0, x1, y1 en píxeles de la ilustración: fuera de ella no cambia ningún píxel
union = [850, 745]                # donde se junta con el cuerpo: el peso vale 0 y es el pivote del giro
punta = [1040, 760]               # hacia dónde crece el peso: vale 1 en la punta
```

El peso de cada píxel de la zona crece suavemente (con una curva suave de pendiente 0 en los dos extremos) desde 0 en la `union` hasta 1 en la `punta`, a lo largo de la línea que las une; además baja a 0 en los 12 píxeles de dentro del borde de la caja, así que no hay corte en su borde. La zona gira el ángulo del gesto por ese peso, alrededor de la `union`. Cada píxel sale del que el giro contrario trae hasta él, mezclando los vecinos, así que no quedan huecos. Con el ángulo positivo el giro es contra el reloj. Una oreja necesita su propia zona; los gestos de `orejas` mueven todas las zonas que se llamen así. Dos gestos de la misma parte a la vez se suman. La `caja` tiene que dejar sitio alrededor de la punta (más de 12 píxeles) o la punta pierde peso.

**Los gestos** son los de [`actuacion.md`](actuacion.md): `pieza` es el nombre de la pose del reparto (`perro_de_pie`), `parte` es `orejas` o `cola`, y la curva es la misma de siempre (anticipación de 6 fotogramas, acción de 8, pausa de 10 y vuelta de 12 sin rebote). Por la flexión, la punta no recorre el ángulo entero: con el máximo, 30 grados, una cola larga sube en la punta algo menos de lo que subiría girando rígida.

**Párpado.** `parpadeos = [24, 120]` en la línea del plano dice en qué fotogramas empieza cada parpadeo. Cada uno dura 6 fotogramas: el párpado baja sobre el ojo con el color del pelo de al lado, deja una línea al cerrar y sube. Lo llevan las poses que tienen `ojo` en la ficha.

**Respiración.** Todos los personajes de un plano animado respiran: la figura se estira un 0,7 % de su alto (un ciclo cada 3 segundos, cada personaje con su fase) con el estiramiento anclado en la línea de suelo, así que lo que apoya no se despega. Una pose sentada sobre una roca se estira igual y la roca no se mueve.

**La boca del Tutor.** La ficha de una pose del Tutor lleva una zona `parte = "boca"`: la mandíbula, con la `union` en la bisagra (el peso vale 0 y es el pivote) y la `punta` en la barbilla. La mandíbula se abre, con el giro de siempre, solo dentro de las palabras acentuadas (`*así*` en el guion) que dice el Tutor, con los fotogramas de la línea de tiempo: alterna 16° (abierta grande) y 8° (abierta pequeña) cada 3 fotogramas y, fuera de ellas, está cerrada. Para que se abra hacia abajo en una pose que mira a la izquierda, la barbilla va a la izquierda de la bisagra (el ángulo positivo gira contra el reloj). No hay que escribir nada en `actuacion.toml`: un plano en el que habla el Tutor, con una pose suya que tenga zona de boca, se anima solo y deja un vídeo; si no habla en él, la boca no cambia en ningún fotograma. Una pose del Tutor sin zona de boca no mueve la boca (no es un error: aún no está calibrada).

**La boca del Perro no se mueve en ningún fotograma:** el Perro habla en voz en off. Una ficha del Perro con zona de boca, o un gesto de boca, se rechaza.

## Cámara

El tipo de cámara de cada plano sale del campo `camara` de `planos.toml` (empieza por `fija`, `acercamiento` o `desplazamiento`); los números van en `reparto.toml`, como `desde` y `hasta`. Una vista se dice en **fracciones del escenario**: `ancho` es la fracción de su ancho que cabe en la imagen (1 es el escenario entero) y `centro` es el punto al que mira, `[x, y]`, también como fracción (`[0.5, 0.5]` es el medio). Lo que no se escribe en `desde` es la vista entera; lo que no se escribe en `hasta` se queda como en `desde`.

```toml
[[plano]]                       # acercamiento lento
id = "01"
personajes = [{ pose = "perro_de_pie" }]
hasta = { ancho = 0.8 }         # acaba viendo el 80 % del ancho, con el mismo centro

[[plano]]                       # desplazamiento
id = "12"
personajes = [{ pose = "tutor_de_pie" }, { pose = "perro_de_pie" }]
desde = { ancho = 0.8, centro = [0.45, 0.5] }
hasta = { centro = [0.55, 0.5] }   # el centro se mueve una décima del escenario hacia la derecha
```

| Tipo | Lo que exige la herramienta |
| --- | --- |
| `fija` | Sin `desde` ni `hasta`: ve el escenario entero. |
| `acercamiento` | Lleva `hasta`; el ancho acaba entre el 70 % y el 100 % del inicial y el centro no se mueve más de 0,02 del escenario. |
| `desplazamiento` | Lleva `desde` (con un ancho menor que 1: sobre el escenario entero no hay por dónde moverse) y `hasta`; el centro no se mueve más de 0,1 del escenario (en cada eje) y el ancho no cambia más de un 10 %. |

Son los límites de siempre de la cámara lenta ([tomas.md](tomas.md)), en fracciones. Además, toda vista tiene un `ancho` de entre 0,7 y 1 y tiene que caber dentro del escenario (con ancho 0,8, el centro va entre 0,4 y 0,6).

**Cómo se hace.** Escenario, sombras, rocas y personajes se componen en un lienzo 1,5 veces mayor que la imagen, y cada fotograma es un recorte suyo reescalado a 1080x1920. Como la vista nunca baja de 0,7 del lienzo, el recorte mide siempre más de 1080 píxeles y solo se reduce: el acercamiento no pierde nitidez. Personajes y escenario son una misma imagen, así que se mueven juntos y la base de cada personaje sigue sobre su línea de suelo. El movimiento es una línea recta de `desde` a `hasta` (ancho y centro a la vez) con un suavizado al principio y al final (la misma curva suave de los gestos): el primer fotograma es `desde`, el último es `hasta`. Los personajes respiran y gesticulan igual que en un plano de cámara fija con actuación.

## Generar las poses

`uv run estudio generar-poses <carpeta> <pose> [--proveedor falso|fal] [--confirmar] [--reemplazar]` genera la ilustración de una pose a partir de la hoja de su personaje. La carpeta es la de un episodio y solo sirve para encontrar el `estudio.toml` y la biblioteca. La pose se escribe `<personaje>_<postura>`: los personajes son `tutor` y `perro`, y las posturas, `de_pie`, `sentado` y `tumbado`.

1. **La hoja:** cada pose necesita su vista de perfil en `biblioteca/personajes/_trabajo/hojas/<pose>_perfil_izq.png` (por ejemplo `tutor_sentado_perfil_izq.png`). Si falta, la orden lo dice, con el nombre del archivo que espera, antes de enseñar el coste y sin generar nada. Esa carpeta queda fuera de git: las hojas llevan el rostro del creador.
2. **El texto:** una plantilla fija del estilo de la casa (plano, contorno de grosor uniforme, dos tonos, fondo liso, mirando a la izquierda). Solo cambian el sujeto (el hombre o el perro), la postura y, en el Perro, que se vean la cola y las dos orejas. La misma pose da siempre el mismo texto.
3. **La cuenta antes de gastar:** la orden enseña el texto, cuántas imágenes va a generar (una por pose) y cuánto costarían, y termina con código 1 sin escribir nada. **Genera solo con `--confirmar`.** Una generación de pago la confirma el creador: el agente no pasa `--confirmar` sin su visto bueno explícito.
4. **Lo que deja:** la ilustración en `biblioteca/personajes/<personaje>/poses/<pose>.png` y su ficha `<pose>.toml`, con una tabla `[generacion]` al final que anota el modelo, el texto y la fecha. Si la ficha ya existía, conserva todo lo demás (`asiento`, `trasero`, `ignora`) y solo cambia esa tabla. Una pose recién generada espera la aprobación del creador.
5. **No pisa lo que hay:** si la pose ya tiene ilustración, la orden se niega, porque puede estar aprobada. Con `--reemplazar` la vuelve a generar, y si la generación falla, la ilustración anterior queda como estaba.

| Proveedor | Qué hace |
| --- | --- |
| `falso` (por defecto) | Dibuja una ilustración de prueba (una elipse sobre fondo transparente) sin gastar y sin clave. Los tests usan solo este. |
| `fal` | Genera de verdad con Fal. Lee su clave, `FAL_KEY`, solo del entorno o del archivo `.env` del estudio y no la escribe nunca, ni en pantalla ni en archivos. Todavía no genera: se conecta en el [ticket 08](../.scratch/estudio-2d/issues/08-generar-poses-con-fal.md), y hasta entonces la orden lo dice. |

## Escenarios

Un escenario 2D es una receta que dibuja un paisaje exterior con formas planas y contorno uniforme, y dice cuál es su línea de suelo. Se dibuja con código, sin imágenes generadas, y sale siempre igual (las flores usan una semilla fija). Un escenario con receta cuenta como de la biblioteca: no hace falta carpeta ni marcarlo como nuevo en `planos.toml`.

| Escenario | Qué es |
| --- | --- |
| `lago` | Un día junto a un lago: cielo con sol y nubes, montañas con nieve, lago, prado con flores y pinos. |

## Errores

La orden junta todos los errores antes de dibujar y, si hay alguno, no escribe ninguna imagen. Rechaza:

- una ficha con una zona mal escrita (una parte que no se mueve, la boca, una caja que se sale de la ilustración, una `union` o `punta` que falta, cae fuera de la caja o que son el mismo punto) o con un `ojo` que se sale de la ilustración;
- un gesto de una pose que no está en el reparto del plano, de una zona que la pose no tiene (`«perro_de_pie» no tiene cola que mover`), o que no cabe en el plano; y un parpadeo que no cabe, que pisa a otro o en un plano cuyas poses no tienen `ojo`;
- un plano elegido sin reparto en `reparto.toml`, o un reparto mal escrito (campos que no existen, falta la `pose`, un plano que no está en `planos.toml`);
- una pose sentada con solo una de sus dos medidas (`asiento` o `trasero`) o con una que no vale;
- una pose que no está en la biblioteca, con una ficha mal escrita, con una ilustración que no existe o sin nada opaco, o con todo lo opaco dentro de partes que se ignoran;
- un escenario sin receta 2D, y dice cuáles hay;
- una cámara que no concuerda con el tipo del plano (con `hasta` en un plano fijo, sin `hasta` en uno que se mueve), que se sale de los límites del tipo, cuya vista es más pequeña de 0,7 o se sale del escenario, o una vista mal escrita (campos que no existen, `ancho` que no es mayor que 0, `centro` que no son dos números);
- un plano con más de dos personajes, o con `--fotogramas` (el 2D siempre dibuja el plano entero);
- dos personajes que no caben juntos ni reducidos a la escala mínima.

## Lo que todavía no hace

Solo planos con uno o dos personajes. Las cámaras 2D solo hacen líneas rectas con los dos tipos lentos; ni giros ni escenarios más anchos que el lienzo. Las zonas, el ojo y la mandíbula de las poses reales se miden cuando existan esas ilustraciones ([09](../.scratch/estudio-2d/issues/09-las-cinco-poses-reales.md)); los números del prototipo están en `.scratch/prototipo-2d/animar.py`.
