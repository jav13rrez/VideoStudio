# Dibujo 2D de los planos

La imagen del estudio es 2D ilustrada y plana ([ADR 0008](adr/0008-estudio-2d-ilustrado-con-exteriores.md)). Las reglas de estilo y de apoyo de los personajes están en [estilo-2d.md](estilo-2d.md); aquí está cómo se le dice a la herramienta del estudio qué lleva cada plano y cómo se dibuja. Es la spec [estudio-2d](../.scratch/estudio-2d/spec.md); este documento recoge lo que hacen los tickets [01](../.scratch/estudio-2d/issues/01-plano-fijo-en-2d.md) y [02](../.scratch/estudio-2d/issues/02-dos-personajes-lado-a-lado.md).

```bash
uv run estudio renderizar-planos ruta/a/la/carpeta-del-episodio
uv run estudio renderizar-planos ruta/a/la/carpeta-del-episodio --planos 03,05-07
```

## Cómo se elige el motor

`renderizar-planos` sigue siendo la misma orden, con los mismos argumentos. Mira si el episodio tiene un `reparto.toml` junto a `planos.toml`:

- **Con `reparto.toml`:** dibuja los planos en 2D, sin Blender. Cada plano deja `planos/<id>.png`, de 1080x1920.
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

La ficha solo dice lo que no se puede medir. La silueta y la línea de suelo se miden de la ilustración, con los píxeles de transparencia mayor que 128: el borde casi transparente que deja un recorte no cuenta, porque no se ve y haría parecer que el personaje flota.

## Cómo se coloca

- **Escala:** todas las poses se dibujan con la misma escala (0,66 sobre su ilustración): las ilustraciones siguen una misma convención de píxeles por metro.
- **Horizontal, un personaje:** la silueta, la cola incluida, queda centrada en la imagen.
- **Horizontal, dos personajes:** van en fila, de izquierda a derecha en el orden de `personajes` (así se elige por plano cuál va a la izquierda). Las siluetas, con la cola incluida, guardan una separación fija de 20 píxeles: se rozan sin taparse, y la cola de uno no pisa al vecino. El grupo queda centrado en la imagen.
- **Si no caben a lo ancho:** los dos se reducen juntos a una escala común, sin deformarlos, hasta un mínimo de 0,45. Más abajo, la orden no dibuja. Un personaje solo no se reduce: si no cabe, se rechaza.
- **Suelo:** lo más bajo que apoya (sin las partes que la ficha ignora) cae en la línea de suelo del escenario, y la misma para los dos: ninguno va adelantado. Se baja al personaje: nunca se sube el terreno ([estilo-2d.md](estilo-2d.md)).
- **Sombra de contacto:** una elipse oscura bajo cada pose, en la línea de suelo.
- **Si no cabe:** unas poses cuya silueta, ya escalada y colocada, se sale de la imagen se rechazan en vez de dibujarlas recortadas.

## Escenarios

Un escenario 2D es una receta que dibuja un paisaje exterior con formas planas y contorno uniforme, y dice cuál es su línea de suelo. Se dibuja con código, sin imágenes generadas, y sale siempre igual (las flores usan una semilla fija). Un escenario con receta cuenta como de la biblioteca: no hace falta carpeta ni marcarlo como nuevo en `planos.toml`.

| Escenario | Qué es |
| --- | --- |
| `lago` | Un día junto a un lago: cielo con sol y nubes, montañas con nieve, lago, prado con flores y pinos. |

## Errores

La orden junta todos los errores antes de dibujar y, si hay alguno, no escribe ninguna imagen. Rechaza:

- un plano elegido sin reparto en `reparto.toml`, o un reparto mal escrito (campos que no existen, falta la `pose`, un plano que no está en `planos.toml`);
- una pose que no está en la biblioteca, con una ficha mal escrita, con una ilustración que no existe o sin nada opaco, o con todo lo opaco dentro de partes que se ignoran;
- un escenario sin receta 2D, y dice cuáles hay;
- un plano que no es de cámara fija, o con más de dos personajes, o con `--fotogramas`;
- dos personajes que no caben juntos ni reducidos a la escala mínima.

## Lo que todavía no hace

Solo planos de cámara fija, con uno o dos personajes y sin gestos: una sola imagen por plano. Faltan sentarse en un soporte ([03](../.scratch/estudio-2d/issues/03-sentarse-en-una-roca.md)), los gestos y el vídeo ([04](../.scratch/estudio-2d/issues/04-gestos-con-zonas-blandas.md)), el movimiento de cámara ([05](../.scratch/estudio-2d/issues/05-camara-acercamiento-y-desplazamiento.md)) y la boca del Tutor ([06](../.scratch/estudio-2d/issues/06-boca-del-tutor.md)).
