# Voces y línea de tiempo

Después de aprobar el guion en la parada 1, la herramienta del estudio genera un audio por frase y calcula la línea de tiempo del episodio: cuándo empieza y acaba cada frase, cada palabra, cada plano, cada tarjeta de subtítulo y el CTA, en fotogramas. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Cronometraje" y "Voces (enchufe de voz)".

```bash
uv run estudio generar-voces ruta/a/la/carpeta-del-episodio
```

```bash
uv run estudio cronometrar ruta/a/la/carpeta-del-episodio
```

Las dos órdenes se niegan a seguir si el guion tiene errores (los de `comprobar-guion`) o si la configuración no cuadra, y entonces terminan con código de salida 1.

## Configuración del estudio: `estudio.toml`

Un único archivo con la configuración común a todos los episodios. La herramienta lo busca en la carpeta del episodio y, si no está, en las de encima, y usa el primero que encuentra. El del estudio está en la raíz del repositorio; los tests tienen el suyo en `tests/episodios/estudio.toml`.

```toml
fps = 30                 # fotogramas por segundo
pausa_entre_frases = 9   # silencio entre frases, en fotogramas (a 30 fps, 9 = 0,3 s)

[voces]
Perro = { proveedor = "elevenlabs", voz = "DLIf7HryZtanUtJkT4ps" }  # MerlinVoice1
Tutor = { proveedor = "elevenlabs", voz = "LxK6rS8QLud12eLvrTxc" }  # JaviVoice
```

- **`[voces]`**: una línea por personaje con su proveedor de voz y la voz concreta dentro de ese proveedor. Cambiar de proveedor o de voz es cambiar esa línea y volver a generar las voces.
- **Proveedores** que hay hoy:
  - `kokoro`: voz gratuita hecha en el propio PC con Kokoro, a través de HyperFrames (`npx hyperframes tts`). Voces en español: `em_santa` y `em_alex` (hombres) y `ef_dora` (mujer). El creador eligió el 2026-11-10 `em_santa` para el Perro y `em_alex` para el Tutor, tras comparar las tres con cuatro de Piper (ticket 13). Necesita el entorno de Python de Kokoro que se instaló en el ticket 02 (`~/.local/share/estudio/kokoro`, ver [DEBT_TECH.md](../DEBT_TECH.md)); la herramienta lo usa sola, salvo que `HYPERFRAMES_PYTHON` diga otro.
  - `elevenlabs`: voz de pago de ElevenLabs (elevenlabs.io), con el modelo multilingüe `eleven_multilingual_v2`. La voz es el ID de la voz en ElevenLabs (se ve en su biblioteca de voces). El creador tiene el plan Starter desde el 2026-11-11, con licencia comercial para el audio generado mientras esté suscrito: hay que generar las voces de lo que se publique con el plan activo. Cada carácter del guion gasta un crédito (el piloto, unos 1.000). La clave va en `ELEVENLABS_API_KEY`, en el archivo `.env` del estudio (git lo ignora; la lista de claves está en `.env.example`) o en el entorno. ElevenLabs devuelve el tiempo de cada letra, así que las marcas por palabra salen de ahí, sin Whisper; solo si no cuadran con las palabras del guion se pasa por Whisper como con `kokoro`. El audio llega en PCM de 24 kHz y se guarda como WAV.
  - `grabacion`: los audios que graba el creador. Por cada frase de ese personaje, un WAV en la carpeta `grabaciones/` del episodio con el mismo nombre que tendrá en `voces/`: `grabaciones/frase-02.wav` para la frase 2 del guion. La voz no cambia nada; sirve para apuntar quién graba (`voz = "creador"`). Si se vuelve a grabar una frase, hay que volver a generar las voces.
  - `falso`: silencio, para los tests. Habla a 3 palabras por segundo (cada palabra dura 10 fotogramas a 30 fps) e ignora la voz.
  - Uno nuevo (por ejemplo, un servicio de pago) se añade por el mismo enchufe: una clase en `src/estudio/voces.py` apuntada en `PROVEEDORES`.
- **Marcas por palabra** de `kokoro` y `grabacion`: ni Kokoro ni una grabación las traen, así que la herramienta pasa cada audio por Whisper (`npx hyperframes transcribe --engine whisper --model small --language es`) y empareja lo que oye con las palabras del guion. Whisper no siempre escribe igual que el guion (pone «300» por «trescientos» o junta «Ysi»), así que una palabra que no casa toma el tiempo de lo que Whisper oyó en su lugar, o el hueco entre sus vecinas. Si casan menos de la mitad de las palabras, la herramienta da error: el audio no dice la frase. Con Kokoro, el guion de ejemplo tarda unos 2 minutos en el PC.
- Junto a `estudio.toml` van la biblioteca (`biblioteca/`, ver [lista-de-planos.md](lista-de-planos.md)) y la documentación de la App (`app/`, ver "El cierre del CTA" en [montaje.md](montaje.md)).

## `generar-voces`

Deja en la carpeta `voces/` del episodio, por cada frase del guion, en orden:

- `frase-01.wav`: el audio de la frase.
- `frase-01.json`: con qué se generó (personaje, lo que se pronuncia, proveedor y voz), la duración del audio y el inicio y el final de cada palabra, en segundos desde el principio del audio. La línea de tiempo toma la duración de aquí.

Son archivos generados: no se editan a mano. Si cambia lo que se pronuncia en una frase o la línea de su personaje en `estudio.toml`, su audio deja de valer y `cronometrar` pide volver a generar las voces. Cambiar solo las marcas de fuente o los asteriscos de acento no obliga a generarlas otra vez.

## `cronometrar`

Lee el guion, `estudio.toml`, las voces y la lista de planos, y deja `linea-de-tiempo.json` en la carpeta del episodio. Escribe en pantalla el total, los fotogramas del CTA y cuántos planos y escenarios hay. La lista de planos se comprueba aquí mismo: ver [lista-de-planos.md](lista-de-planos.md).

- La primera frase empieza en el fotograma 0. Cada frase dura lo que su audio, y la siguiente empieza tras la pausa entre frases.
- Los tiempos de los audios (en segundos) se pasan a fotogramas redondeando al más cercano.
- **`inicio`** es el primer fotograma de una frase o palabra; **`final`**, el primero después de ella. Así, la duración es `final - inicio`.
- El total del episodio es el `final` de la última frase.
- Cada plano empieza en el fotograma en que empieza su palabra (el primero, en el 0) y acaba donde empieza el siguiente; el último, en el total.
- Cada tarjeta de subtítulo, de hasta tres palabras, empieza en el fotograma de su primera palabra y acaba donde empieza la siguiente de su frase; la última, donde acaba la frase. Las reglas y el estilo están en [montaje.md](montaje.md).
- El mismo guion con los mismos audios da siempre el mismo archivo.

```json
{
  "fps": 30,
  "total": 1904,
  "cta": { "inicio": 1784, "final": 1904 },
  "planos": [
    { "id": "01", "inicio": 0, "final": 70 },
    …
  ],
  "subtitulos": [
    { "texto": "¿Sabes por qué", "personaje": "Perro", "animada": false, "inicio": 0, "final": 30 },
    …
  ],
  "frases": [
    {
      "numero": 1,
      "linea": 3,
      "personaje": "Perro",
      "audio": "voces/frase-01.wav",
      "inicio": 0,
      "final": 110,
      "palabras": [
        { "texto": "¿Sabes", "acentuada": false, "inicio": 0, "final": 10 },
        …
      ]
    },
    …
  ]
}
```

- `linea`: la línea de la frase en `guion.md`.
- `cta`: del principio de la primera frase del CTA al final de la última; `null` si el guion no tiene CTA.
- `planos`: los de `planos.toml`, en orden; vacía si el episodio no tiene lista de planos.
- `subtitulos`: las tarjetas de subtítulo, en orden; `animada` dice si la tarjeta empieza por una palabra acentuada, que son las únicas que entran con animación.
- `palabras`: las del guion, con su puntuación, sin asteriscos y sin marcas de fuente; `acentuada` dice si iba entre asteriscos.

**Avisos** (no impiden seguir): el total se sale de 1.650-2.100 fotogramas, es decir, de 55-70 segundos a 30 fps; el CTA dura menos de 3 s o más de 7 s (90-210 fotogramas a 30 fps; acordado con el creador el 2026-11-10). Los avisos y errores de la lista de planos están en [lista-de-planos.md](lista-de-planos.md).
