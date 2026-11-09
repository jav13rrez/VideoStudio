# Lista de planos

La lista de planos divide el guion en planos, uno por idea, y decide la imagen de cada uno antes de construirla. Es el archivo `planos.toml` de la carpeta del episodio. La escribe el agente con el guion aprobado, y el creador la puede leer tal cual. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Lista de planos".

Hay un ejemplo completo en [`tests/episodios/001-olfato/planos.toml`](../tests/episodios/001-olfato/planos.toml).

## `planos.toml`

```toml
# Escenarios que todavía no están en la biblioteca.
escenarios_nuevos = ["parque"]

[[plano]]
id = "01"
empieza = "¿Sabes por qué"
escenario = "recibidor"
encuadre = "plano detalle de los zapatos del Tutor junto a la puerta"
camara = "acercamiento lento"
motivo = "la pregunta del gancho señala los zapatos"
personajes = { Perro = "asoma el hocico por el borde del encuadre y olfatea" }
objeto = "zapatos del Tutor"
sonido = "olfateo"

[[plano]]
id = "02"
empieza = "cuando vuelves"
…
```

Cada plano empieza con `[[plano]]`, con dos corchetes, y van en el orden del guion. Las líneas que empiezan por `#` son comentarios.

| Campo | ¿Obligatorio? | Qué es |
| --- | --- | --- |
| `id` | sí | El nombre del plano, distinto en cada uno: letras, números, guiones o guiones bajos, sin espacios. Por ejemplo `"01"`. |
| `empieza` | sí | Las primeras palabras del plano, copiadas de una frase del guion. Bastan las necesarias para que aparezcan una sola vez en el guion. No cuentan las mayúsculas, la puntuación, los asteriscos ni las marcas de fuente. |
| `escenario` | sí | El nombre del escenario, igual que su carpeta en la biblioteca: letras, números, guiones o guiones bajos, sin espacios. |
| `encuadre` | sí | Qué se ve y a qué distancia: plano general, plano medio, primer plano, plano detalle… |
| `camara` | sí | El movimiento de cámara: fija, acercamiento lento o desplazamiento. Se escribe sin tilde, `camara`, porque así lo pide el formato del archivo. |
| `motivo` | sí | Por qué la cámara hace eso. La cámara nunca se mueve sin motivo. |
| `personajes` | no | El gesto de cada personaje que sale, como `{ Perro = "ladea la cabeza", Tutor = "deja las llaves" }`. Si no sale ninguno, no se pone. |
| `objeto` | no | El objeto protagonista, si sale en el plano. |
| `sonido` | no | El sonido físico del plano, si lo hay (un golpe, una correa que se tensa). Nunca un "whoosh" en el corte. |

`escenarios_nuevos`, fuera de los planos, es la lista de escenarios que el episodio usa y que todavía no están en la biblioteca. El creador los aprueba la primera vez que se construyen. Si no hay ninguno, se puede omitir.

## La duración no se escribe

Un plano empieza en el fotograma en que empieza su palabra y dura hasta que empieza el siguiente. El último dura hasta el final del episodio. Así, cada corte cae justo sobre la palabra a la que pertenece. Para cambiar cuánto dura un plano, se cambia la palabra en la que empieza el siguiente.

El primer plano empieza siempre en el fotograma 0, aunque la voz tarde un poco en arrancar. Así no queda imagen sin plano.

## La biblioteca

La biblioteca es la carpeta `biblioteca/` que está junto a `estudio.toml`. Un escenario está en la biblioteca si existe la carpeta `biblioteca/escenarios/<nombre>/`, con el nombre que usa la lista de planos. Lo que va dentro de cada carpeta (el archivo de Blender, sus texturas, sus hojas de vistas) lo decide el primer escenario que se construya. Los tests tienen su propia biblioteca de mentira en `tests/episodios/biblioteca/`.

## Comprobarla

La lista de planos se comprueba al cronometrar, porque sus duraciones salen de la línea de tiempo:

```bash
uv run estudio cronometrar ruta/a/la/carpeta-del-episodio
```

Si la lista está bien, sus planos entran en `linea-de-tiempo.json` con su inicio y su final en fotogramas ([voces-y-linea-de-tiempo.md](voces-y-linea-de-tiempo.md)). Si el episodio no tiene `planos.toml`, la línea de tiempo sale sin planos y la orden lo dice.

**Errores**: con cualquiera de ellos no se cronometra, y la orden termina con código de salida 1.

- El principio del guion queda sin cubrir: el primer plano no empieza en la primera palabra. Dice qué frases quedan sin plano.
- Un plano va fuera de orden (empieza antes que el anterior) o empieza en la misma palabra que el anterior.
- Un escenario no está en la biblioteca y no está en `escenarios_nuevos`.
- El archivo no sigue el formato: falta un campo obligatorio, hay un campo que no existe (por ejemplo `camera`), dos planos tienen el mismo `id`, o el texto de `empieza` no está en el guion o aparece más de una vez.

Los errores de formato se dan primero. Las comprobaciones entre planos (orden, principio del guion, biblioteca) llegan cuando el formato está bien, para no dar errores encadenados que confundan.

**Avisos**: no impiden cronometrar, pero hay que revisarlos.

- Un plano dura menos de 45 o más de 90 fotogramas, es decir, de 1,5 a 3 segundos a 30 fps. Solo el último plano puede pasar de 90, y solo si empieza dentro del CTA: acompaña al CTA con el nombre y el logo de la App, y dura como mucho lo que el CTA, unos 5 segundos (`comprobar-guion` avisa si el CTA es más largo).
- El episodio usa más de 5 escenarios.
- El último plano no empieza en la primera palabra del CTA. Es el plano que muestra el nombre y el logo de la App mientras el Perro dice el CTA ([montaje.md](montaje.md), "El cierre del CTA"), así que empieza con él.

Con voces reales los tiempos cambian, así que los avisos de duración se vuelven a mirar cada vez que se generan las voces.
