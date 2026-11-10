# 13: Voz gratuita real

**What to build:** Un proveedor de voz local y gratuito conectado al enchufe de voz, con dos voces distintas en español (una para el Perro y otra para el Tutor), que genera un audio por frase con marcas de tiempo por palabra, propias o por alineación. También queda el proveedor "grabación", para usar audios grabados por el creador. El creador escucha las voces y decide.

**Dónde:** PC de casa (ADR 0005).

**Blocked by:** 02 (Preparar el PC), 04 (Voces de prueba y cronometraje)

**Status:** done

- [x] Comparadas al menos dos opciones gratuitas en español, con muestras para que el creador elija.
- [x] El proveedor elegido se conecta solo por configuración, sin más cambios.
- [x] Cada frase del guion piloto tiene su audio y sus marcas de tiempo por palabra.
- [x] El proveedor "grabación" recoge audios por frase dejados por el creador.
- [x] El creador aprueba las voces, o queda anotada la alternativa elegida (grabar la voz del Tutor, o una voz de pago con compuerta humana).

## Comments

**2026-11-09, agente (desde el ticket 04).** Al conectar el primer proveedor real:

- Si no da marcas por palabra, alinear cada audio con su texto. Hoy `Audio.palabras` es obligatorio en `src/estudio/voces.py`.
- Comprobar el cambio real de proveedor cambiando una sola línea de `estudio.toml`.
- Decidir con el creador si se añade el aviso de la spec "CTA muy lejos de unos 150 fotogramas", y con qué margen.

**2026-11-10, agente (desde la nube).** HyperFrames 0.9.26 ya trae lo necesario, sin instalar otro motor:

- **Voz:** `npx hyperframes tts "texto" -o frase.wav --voice <voz>` genera en el PC con Kokoro. Voces en español: `ef_dora` (mujer), `em_alex` y `em_santa` (hombres). Kokoro no da marcas por palabra.
- **Marcas por palabra:** `npx hyperframes transcribe frase.wav --model small --language es` (whisper.cpp) da `[{text, start, end}]` en segundos. Pasar siempre `--model` y `--language es`: el modelo por defecto, `small.en`, traduce al inglés. Como el texto ya se conoce, lo seguro es tomar solo los tiempos y emparejarlos con las palabras del guion, y fallar si no salen las mismas.
- Para la comparación de "al menos dos opciones": Kokoro es una; la otra puede ser Piper, cuyas voces están en Hugging Face (bloqueado en la nube: en el PC). Kokoro sí se puede probar desde la nube, porque su modelo se baja de GitHub.

**2026-11-10, agente (hecho en el PC).**

- **Comparativa.** Se hicieron muestras de 3 voces de Kokoro (`ef_dora`, `em_alex`, `em_santa`) y de 4 de Piper (`davefx`, `sharvard` hombre y mujer, `claude` mexicano). Una quinta voz de Piper, `ald`, no arrancó. El creador eligió Kokoro: `em_santa` para el Perro y `em_alex` para el Tutor. Después aprobó el episodio de ejemplo entero con esas voces. Piper no se conectó, porque no hace falta.
- **Proveedores** `kokoro` y `grabacion`, en `src/estudio/voces.py`. Se cambia de proveedor cambiando la línea del personaje en `estudio.toml`; se probó con el guion piloto real: 17 audios en unos 2 minutos.
- **Marcas por palabra.** Las saca Whisper, en `src/estudio/alineacion.py`. No se exige que Whisper escriba lo mismo que el guion, al contrario de lo que proponía el comentario anterior: se comprobó que escribe «300» por «trescientos» y junta «Ysi». Las palabras que no casan toman el tiempo de lo que Whisper oyó en su lugar, y solo se da error si casan menos de la mitad.
- **Aviso del CTA.** Acordado con el creador: salta si el CTA dura menos de 3 s o más de 7 s.
- **Pendiente para otro ticket.**
  - Con Kokoro, tres planos del ejemplo (21, 23 y 27) duran menos de 1,5 s; se ajusta en la lista de planos.
  - No se avisa de las palabras que Whisper no reconoce.
  - Si se vuelve a grabar una frase, la herramienta no lo nota: hay que volver a generar las voces.
