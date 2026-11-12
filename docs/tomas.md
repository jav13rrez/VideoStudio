# Tomas y render de los planos

La lista de planos (`planos.toml`) dice qué se ve en cada plano con palabras. Las **tomas** (`tomas.toml`, junto a ella) lo dicen con números, para que Blender pueda renderizarlo: dónde mira la cámara, cuánto se ve, qué piezas hay en escena y dónde. La escribe el agente, y el creador la puede leer. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Escenarios, personajes y objetos", y [lista-de-planos.md](lista-de-planos.md).

```bash
uv run estudio renderizar-planos ruta/a/la/carpeta-del-episodio
uv run estudio renderizar-planos ruta/a/la/carpeta-del-episodio --planos 03,05-07 --calidad final
uv run estudio renderizar-planos ruta/a/la/carpeta-del-episodio --planos 03 --fotogramas 20-35
```

| Opción | Qué hace |
| --- | --- |
| `--planos` | Los planos que se renderizan: `01`, `03,05` o `05-07`. Sin ella, todos. |
| `--fotogramas` | Solo un rango de un plano con movimiento, contado desde el principio del plano. El plano tiene que estar ya renderizado entero. |
| `--calidad` | `rapida` (por defecto: 32 muestras, a media resolución en los planos con movimiento) o `final` (128 muestras, a 1080x1920). Las imágenes de los planos fijos salen siempre a 1080x1920. |

Antes de renderizar, la orden cronometra el episodio (como `montar`), así que la duración de cada plano sale de la línea de tiempo.

## `tomas.toml`

```toml
[[toma]]
id = "03"                     # el id de un plano de planos.toml
mira = [0.5, 1.3, 0.95]       # el punto al que mira la cámara, en metros del escenario (x, y, z; z es la altura)
ancho = 0.55                  # metros de escena que caben a lo ancho en ese punto: más pequeño, más cerca
azimut = 0                    # grados alrededor del punto: 0 es de frente, positivo hacia la derecha
elevacion = 0                 # grados sobre la horizontal
hasta = { ancho = 0.42 }      # solo en planos con movimiento: cómo acaba la vista
personajes = [
  { pieza = "tutor_sentado_frente", en = [-0.38, 1.38, 0.42], ojos = "muy_abiertos", boca = "sonrisa" },
  { pieza = "perro_sentado_perfil", en = [0.5, 1.3, 0.42], espejo = true },
]
objetos = [{ pieza = "bocadillo", en = [-0.18, 1.25, 0.66] }]
```

| Campo | ¿Obligatorio? | Qué es |
| --- | --- | --- |
| `id` | sí | El plano al que corresponde: tiene que existir en `planos.toml`. |
| `mira`, `ancho` | sí | A dónde mira la cámara y cuánto se ve a lo ancho. La cámara tiene una lente de 40 mm y profundidad de campo (f/2.8) enfocada en `mira`; la distancia sale del `ancho`. |
| `azimut`, `elevacion` | no (0) | Desde qué lado y a qué altura mira. El escenario se construye con la cámara de frente en −Y. |
| `hasta` | solo con movimiento | La vista al final del plano: `mira`, `ancho`, `azimut` o `elevacion`, los que cambian. Lo que no se escribe se queda como estaba. |
| `personajes`, `objetos` | no | Las piezas de la escena. `pieza` es el nombre de una pieza de la biblioteca, `en` dónde se pone (la base de la pieza: el asiento o el suelo), `espejo = true` la da la vuelta, y `ojos` y `boca` eligen el juego de ojos y de bocas por su nombre (los de [`biblioteca/personajes`](../biblioteca/personajes/README.md)). |

Las piezas son personajes (`biblioteca/personajes/<nombre>/<nombre>.blend`, colección `PERSONAJE_<nombre>`) u objetos (`biblioteca/objetos/<nombre>/<nombre>.blend`, colección `OBJETO_<nombre>`). El nombre de la pieza empieza por el del archivo (`perro_de_pie_frente` está en `perro.blend`). El escenario es el de su plano.

## La cámara solo se mueve despacio y con motivo

El tipo de movimiento sale del campo `camara` de `planos.toml` (empieza por `fija`, `acercamiento` o `desplazamiento`) y la toma tiene que concordar:

- **Fija**: la toma no lleva `hasta`. Deja una sola imagen, `planos/<id>.png`.
- **Acercamiento**: lleva `hasta`, el ancho acaba entre el 70 % y el 100 % del inicial, el punto al que mira no se mueve más de 10 cm y la cámara no gira.
- **Desplazamiento**: lleva `hasta`; el punto al que mira no se mueve más de 60 cm, la cámara no gira más de 20° y el ancho no cambia más de un 10 %.

Si no se cumple, la orden dice qué falla y no renderiza. El movimiento se suaviza al principio y al final (sin tirones ni derivas), y siempre es una línea recta entre el principio y el final del plano.

## Qué deja

- Plano fijo: `planos/<id>.png`.
- Plano con movimiento: los fotogramas en `planos/_fotogramas/<id>/0000.png…` y el vídeo `planos/<id>.mp4` (1080x1920, 30 fps, un fotograma por fotograma de la línea de tiempo). Para volver a renderizar solo un rango se pide con `--fotogramas`: se rehacen esos fotogramas y se compone de nuevo el vídeo, sin tocar el resto.
- `planos/_trabajo.json`: lo que se le pasa a Blender en la última llamada.

La carpeta `planos/` no va a git: se puede volver a generar con esta orden. `montar` y `renderizar` usan el vídeo o la imagen de cada plano en lugar de su cartel ([montaje.md](montaje.md)).

## Blender

La orden llama a Blender en segundo plano (`blender -b --python src/estudio/blender/render_toma.py -- planos/_trabajo.json`). El programa se busca en la variable `ESTUDIO_BLENDER`, en `blender` de `estudio.toml` o en el `PATH`. En el PC del estudio es el Blender 5.2 de Windows, llamado desde WSL (ver [DEBT_TECH.md](../DEBT_TECH.md)), y la orden convierte las rutas con `wslpath -w`. Un Blender abierto con el complemento MCP no hace falta ni molesta.

Tiempos medidos (RTX 4060, EEVEE): una imagen fija a 1080x1920 tarda unos 20 segundos contando la apertura de Blender y del escenario.

## Lo que todavía no hace

Los personajes están quietos dentro de cada plano: no cambian de ojos ni de boca por fotograma. Eso es la actuación (ticket 19).
