# 04: Voces de prueba y cronometraje

**What to build:** La herramienta genera un audio por frase con el proveedor de voz falso y construye la línea de tiempo del episodio en fotogramas globales a 30 fps. Queda definido el enchufe de voz (proveedor y voz por personaje en la configuración del estudio), con el proveedor falso como primer proveedor.

**Blocked by:** 03 (Comprobar un guion)

**Status:** done

- [x] Hay una configuración del estudio con proveedor y voz por personaje, fps y pausa entre frases.
- [x] El proveedor falso deja un audio por frase, de duración proporcional a sus palabras, con marcas de tiempo por palabra.
- [x] La línea de tiempo da el inicio y el final de cada frase, de cada palabra y del CTA, y la duración total.
- [x] Aviso si el total queda fuera de 1.650-2.100 fotogramas (55-70 s).
- [x] El mismo guion con los mismos audios da siempre la misma línea de tiempo.
- [x] Cambiar el proveedor de un personaje es cambiar una línea de la configuración.
- [x] Probado a través de la herramienta sobre carpetas de episodio de ejemplo.

## Comments

**2026-11-09, agente.** Hecho.

- Órdenes nuevas: `uv run estudio generar-voces <carpeta>` y `uv run estudio cronometrar <carpeta>`.
- Configuración del estudio en `estudio.toml` (raíz del repositorio); la de los tests, en `tests/episodios/estudio.toml`.
- Formato de la configuración, de las voces y de `linea-de-tiempo.json`: [docs/voces-y-linea-de-tiempo.md](../../../docs/voces-y-linea-de-tiempo.md).
- 29 casos de test nuevos en `tests/test_voces_y_cronometraje.py` y uno en `tests/test_comprobar_guion.py`, todos a través de la herramienta.
- Con la configuración real (pausa de 9 fotogramas), el episodio de ejemplo dura 1.904 fotogramas (63,47 s), y el CTA va del fotograma 1.784 al 1.904.

Decidido por el agente, además de lo que pedía el ticket:

- **Dos órdenes separadas**: generar las voces y cronometrar. Con voces reales, generar es lento o cuesta dinero; cronometrar se repite a menudo, por ejemplo al cambiar la pausa.
- **`cronometrar` se niega a usar voces que faltan o están desactualizadas**, y dice qué líneas regenerar. Una voz está desactualizada si ha cambiado lo que se pronuncia en su frase o la línea de su personaje en `estudio.toml`. Cambiar solo marcas de fuente o asteriscos no la invalida.
- **Error en `comprobar-guion` si un asterisco de acento no tiene pareja.** Sin él, todas las palabras siguientes saldrían marcadas como acentuadas sin aviso.
- **`estudio.toml` se busca** desde la carpeta del episodio hacia arriba.
- **El proveedor falso** escribe WAV de silencio a 24 kHz.

Pendiente, con su motivo:

- **Hoy las marcas por palabra son obligatorias.** La spec las admite opcionales ("si las sabe dar"). Un proveedor sin marcas necesita alinearlas con Whisper (ticket 13).
- **Cambiar de proveedor solo se ha probado cambiando la voz**, porque de momento solo existe el proveedor `falso`. El cambio real de proveedor se comprueba en el ticket 13.
- **La spec pide también el aviso "CTA muy lejos de unos 150 fotogramas"**, que ningún ticket recoge. No se ha hecho porque la spec no dice cuánto es "lejos", y mientras tanto el aviso de más de 15 palabras de `comprobar-guion` lo cubre. Tiene más sentido con voces reales (ticket 13).
- **La duración de cada audio se toma de su `.json`, no del archivo de audio.** Así vale para cualquier formato de audio; los archivos generados no se editan a mano.
