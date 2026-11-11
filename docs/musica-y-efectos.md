# Música y efectos

Cada episodio lleva una música gratuita y libre de derechos y los efectos de los sonidos físicos que pide su lista de planos. Se anotan, con su licencia, en el archivo `sonido.toml` de la carpeta del episodio, y `montar` los mete en la composición. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Música y efectos (enchufes)".

## `sonido.toml`

```toml
# La música del episodio: una sola.
[musica]
archivo = "sonido/musica.wav"
licencia = "CC0 1.0"
fuente = "https://freesound.org/s/123456/"

# Un efecto por cada sonido de la lista de planos.
[[efecto]]
sonido = "olfateo"
archivo = "sonido/olfateo.wav"
licencia = "CC BY 4.0, de NombreDelAutor"
fuente = "https://freesound.org/s/654321/"
```

| Campo | Qué es |
| --- | --- |
| `sonido` | Solo en los efectos: el sonido de la lista de planos al que acompaña, escrito igual que en el campo `sonido` del plano (no cuentan las mayúsculas). Un mismo efecto sirve para todos los planos que piden ese sonido. |
| `archivo` | El audio, dentro de la carpeta del episodio (lo normal, en `sonido/`). Tiene que ser WAV de 16 bits. Si se descarga en otro formato (MP3, OGG, WAV de 24 bits), se convierte con `ffmpeg -i original.mp3 -c:a pcm_s16le sonido/olfateo.wav`. |
| `licencia` | La licencia con la que se puede usar: `CC0 1.0`, `CC BY 4.0, de Autor`… Si pide atribución, se escribe aquí a quién, para ponerlo en la descripción del vídeo. |
| `fuente` | De dónde sale: la dirección de la página de la que se descargó. |

Los tres campos son obligatorios: sirven para poder demostrar que se puede usar cada audio.

## Cómo se colocan

- **La música** se coloca para que su final caiga en el último fotograma del episodio, y así el final suene cerrado. Si es más larga que el episodio, se recorta por el principio. Si es más corta, entra más tarde (`montar` avisa del fotograma en que entra).
- **Volumen de la música**: queda 18 dB por debajo del nivel medio de las voces (`DEBAJO_DE_LAS_VOCES`, en `src/estudio/sonido.py`). Para eso, `montar` mide el nivel de las voces del episodio y el de la música y le baja el volumen lo que haga falta. Nunca la sube. Si las voces son silencio, como las del proveedor de pruebas, supone el nivel de las de Kokoro (unos -20 dBFS).
- **Cada efecto** acompaña a su plano: su golpe, que es el momento más fuerte del audio, cae en el primer fotograma del plano. Si el golpe está más cerca del principio del archivo de lo que deja el plano (por ejemplo, en el plano 01, que empieza en el fotograma 0), se recorta el principio del archivo. Los efectos suenan a su volumen, sin cambiarlo.
- En la composición, la música es la capa `musica` (pista 4) y los efectos son `efecto-01`, `efecto-02`… (pista 5), en el orden de los planos. HyperFrames ajusta al fotograma el inicio de cada capa, así que el ajuste fino va en `data-media-start`, que es el trozo del principio del archivo que no suena.
- Comprobado en un render del ejemplo (2026-11-11): los golpes de los cinco efectos caen en el fotograma de su plano y la última muestra de la música, en la última del vídeo.

## Errores y avisos

**Errores** (no se monta):

- A una música o un efecto que se usa le falta la licencia o la fuente.
- Su archivo no está, está fuera de la carpeta del episodio o no es un WAV de 16 bits.
- `sonido.toml` no sigue el formato: un campo que no existe, dos efectos para el mismo sonido…

**Avisos** (se monta igual):

- El episodio no tiene `sonido.toml`, o no tiene `[musica]`. Así se puede montar la versión previa antes de elegir la música.
- Un plano pide un sonido que no tiene efecto en `sonido.toml`: ese plano va sin efecto.
- La música dura menos que el episodio.

## Límites conocidos

- El golpe de un efecto cae en el primer fotograma de su plano. Si el sonido pasa a mitad del plano (una correa que se tensa un segundo después del corte), hoy no se puede indicar; lo resolverá el ticket de actuación (19), cuando cada plano tenga sus tiempos.
- El volumen de la música sale del nivel medio de todo el archivo, aunque solo suene su final, y es el mismo durante todo el episodio (no baja más cuando habla alguien). Con 18 dB de margen basta para músicas de fondo de nivel parejo; con una que crezca mucho al final, hay que escucharla.
- "Resolver en el último fotograma" es que la última muestra del archivo cae en el último fotograma. Si la pista acaba con un silencio largo, se oye acabar antes: se recorta el silencio del archivo con ffmpeg antes de anotarlo.

Los efectos que están en `sonido.toml` pero no pide ningún plano no se usan, y de ellos no se comprueban ni la licencia ni el archivo.

## De dónde sacar música y efectos

De bibliotecas gratuitas en las que cada audio dice su licencia, como Freesound (filtrando por CC0 o CC BY) o la Biblioteca de audio de YouTube. Este es el enchufe de música y efectos: hoy se eligen a mano y se anotan en `sonido.toml`. Si más adelante hay música generada o de pago (con su compuerta humana), ese proveedor solo tendrá que dejar sus archivos y sus líneas en `sonido.toml`.

Los efectos son solo para los sonidos físicos que pide la lista de planos: nunca un "whoosh" en cada corte.
