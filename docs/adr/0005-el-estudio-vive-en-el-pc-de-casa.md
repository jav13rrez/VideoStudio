# El estudio vive en el PC de casa, no en la nube

Los episodios se renderizan con Blender, y Blender necesita tarjeta gráfica para hacerlo en un tiempo razonable. El 2026-11-09 se midió en el servidor en la nube de las sesiones de Claude Code: Cycles en CPU tardó 14,9 s por fotograma 1080x1920 con una escena vacía (más de 8 horas para los 1.950 fotogramas de un episodio de 65 s), y EEVEE y Workbench no arrancan sin tarjeta gráfica. Además, la red de ese entorno bloquea la descarga oficial de Blender, Poly Haven y los modelos de Whisper. Por eso todo lo que renderiza o genera medios corre en el PC de casa. La nube queda para escribir (contenido, guion, lista de planos, specs) y para pruebas puntuales de un fotograma.

## Consecuencias

- Las instalaciones y las pruebas del estudio se hacen en el PC: ver `DEBT_TECH.md`.
- Si algún día se quiere renderizar en la nube, hará falta una máquina con tarjeta gráfica, y eso cuesta dinero (compuerta humana).
