# 13: Voz gratuita real

**What to build:** Un proveedor de voz local y gratuito conectado al enchufe de voz, con dos voces distintas en español (una para el Perro y otra para el Tutor), que genera un audio por frase con marcas de tiempo por palabra, propias o por alineación. También queda el proveedor "grabación", para usar audios grabados por el creador. El creador escucha las voces y decide.

**Dónde:** PC de casa (ADR 0005).

**Blocked by:** 02 (Preparar el PC), 04 (Voces de prueba y cronometraje)

**Status:** ready-for-agent

- [ ] Comparadas al menos dos opciones gratuitas en español, con muestras para que el creador elija.
- [ ] El proveedor elegido se conecta solo por configuración, sin más cambios.
- [ ] Cada frase del guion piloto tiene su audio y sus marcas de tiempo por palabra.
- [ ] El proveedor "grabación" recoge audios por frase dejados por el creador.
- [ ] El creador aprueba las voces, o queda anotada la alternativa elegida (grabar la voz del Tutor, o una voz de pago con compuerta humana).

## Comments

**2026-11-09, agente (desde el ticket 04).** Al conectar el primer proveedor real:

- Si no da marcas por palabra, alinear cada audio con su texto. Hoy `Audio.palabras` es obligatorio en `src/estudio/voces.py`.
- Comprobar el cambio real de proveedor cambiando una sola línea de `estudio.toml`.
- Decidir con el creador si se añade el aviso de la spec "CTA muy lejos de unos 150 fotogramas", y con qué margen.

**2026-11-10, agente (desde la nube).** HyperFrames 0.9.26 ya trae lo necesario, sin instalar otro motor:

- **Voz:** `npx hyperframes tts "texto" -o frase.wav --voice <voz>` genera en el PC con Kokoro. Voces en español: `ef_dora` (mujer), `em_alex` y `em_santa` (hombres). Kokoro no da marcas por palabra.
- **Marcas por palabra:** `npx hyperframes transcribe frase.wav --model small --language es` (whisper.cpp) da `[{text, start, end}]` en segundos. Pasar siempre `--model` y `--language es`: el modelo por defecto, `small.en`, traduce al inglés. Como el texto ya se conoce, lo seguro es tomar solo los tiempos y emparejarlos con las palabras del guion, y fallar si no salen las mismas.
- Para la comparación de "al menos dos opciones": Kokoro es una; la otra puede ser Piper, cuyas voces están en Hugging Face (bloqueado en la nube: en el PC). Kokoro sí se puede probar desde la nube, porque su modelo se baja de GitHub.
