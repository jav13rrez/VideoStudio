# 04: Voces de prueba y cronometraje

**What to build:** La herramienta genera un audio por frase con el proveedor de voz falso y construye la línea de tiempo del episodio en fotogramas globales a 30 fps. Queda definido el enchufe de voz (proveedor y voz por personaje en la configuración del estudio), con el proveedor falso como primer proveedor.

**Blocked by:** 03 (Comprobar un guion)

**Status:** ready-for-agent

- [ ] Hay una configuración del estudio con proveedor y voz por personaje, fps y pausa entre frases.
- [ ] El proveedor falso deja un audio por frase, de duración proporcional a sus palabras, con marcas de tiempo por palabra.
- [ ] La línea de tiempo da el inicio y el final de cada frase, de cada palabra y del CTA, y la duración total.
- [ ] Aviso si el total queda fuera de 1.650-2.100 fotogramas (55-70 s).
- [ ] El mismo guion con los mismos audios da siempre la misma línea de tiempo.
- [ ] Cambiar el proveedor de un personaje es cambiar una línea de la configuración.
- [ ] Probado a través de la herramienta sobre carpetas de episodio de ejemplo.
