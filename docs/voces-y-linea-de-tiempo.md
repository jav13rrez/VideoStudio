# Voces y línea de tiempo

Después de aprobar el guion en la parada 1, la herramienta del estudio genera un audio por frase y calcula la línea de tiempo del episodio: cuándo empieza y acaba cada frase, cada palabra y el CTA, en fotogramas. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Cronometraje" y "Voces (enchufe de voz)".

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
Perro = { proveedor = "falso", voz = "perro" }
Tutor = { proveedor = "falso", voz = "tutor" }
```

- **`[voces]`**: una línea por personaje con su proveedor de voz y la voz concreta dentro de ese proveedor. Cambiar de proveedor o de voz es cambiar esa línea y volver a generar las voces.
- **Proveedores** que hay hoy:
  - `falso`: silencio, para los tests. Habla a 3 palabras por segundo (cada palabra dura 10 fotogramas a 30 fps) e ignora la voz.
  - Los demás (voz gratuita en el PC, grabación del creador, servicio de pago) llegan en otros tickets por el mismo enchufe: una clase en `src/estudio/voces.py` apuntada en `PROVEEDORES`.

## `generar-voces`

Deja en la carpeta `voces/` del episodio, por cada frase del guion, en orden:

- `frase-01.wav`: el audio de la frase.
- `frase-01.json`: con qué se generó (personaje, lo que se pronuncia, proveedor y voz), la duración del audio y el inicio y el final de cada palabra, en segundos desde el principio del audio. La línea de tiempo toma la duración de aquí.

Son archivos generados: no se editan a mano. Si cambia lo que se pronuncia en una frase o la línea de su personaje en `estudio.toml`, su audio deja de valer y `cronometrar` pide volver a generar las voces. Cambiar solo las marcas de fuente o los asteriscos de acento no obliga a generarlas otra vez.

## `cronometrar`

Lee el guion, `estudio.toml` y las voces, y deja `linea-de-tiempo.json` en la carpeta del episodio. Escribe en pantalla el total y los fotogramas del CTA.

- La primera frase empieza en el fotograma 0. Cada frase dura lo que su audio, y la siguiente empieza tras la pausa entre frases.
- Los tiempos de los audios (en segundos) se pasan a fotogramas redondeando al más cercano.
- **`inicio`** es el primer fotograma de una frase o palabra; **`final`**, el primero después de ella. Así, la duración es `final - inicio`.
- El total del episodio es el `final` de la última frase.
- El mismo guion con los mismos audios da siempre el mismo archivo.

```json
{
  "fps": 30,
  "total": 1904,
  "cta": { "inicio": 1784, "final": 1904 },
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
- `palabras`: las del guion, con su puntuación, sin asteriscos y sin marcas de fuente; `acentuada` dice si iba entre asteriscos.

**Aviso** (no impide seguir): el total se sale de 1.650-2.100 fotogramas, es decir, de 55-70 segundos a 30 fps.
