# 16: Música y efectos

**What to build:** Los enchufes de música y efectos. Una pista gratuita y libre de derechos elegida por episodio, baja por debajo de las voces y ajustada para que resuelva en el último fotograma. Efectos solo para los sonidos físicos de la lista de planos, con su golpe en el fotograma del evento. Las licencias quedan anotadas en la carpeta del episodio y la composición lo incluye todo.

**Blocked by:** 07 (Versión previa de cartón)

**Status:** done

- [x] La composición incluye la música y los efectos con los tiempos correctos (probado sin renderizar).
- [x] La música termina de resolver en el último fotograma.
- [x] El pico de cada efecto cae en el fotograma de su evento.
- [x] Error si una música o un efecto usado no tiene su licencia anotada.
- [x] Las voces quedan siempre por encima de la música en la mezcla.

## Comments

**2026-11-11, agente (hecho en el PC).**

- **Formato.** Cada episodio anota su música y sus efectos en `sonido.toml`, con `archivo`, `licencia` y `fuente`. Cada efecto se une al plano por su `sonido`. Está en [docs/musica-y-efectos.md](../../../docs/musica-y-efectos.md). El código está en `src/estudio/sonido.py`, y `montar` lo mete en la composición (pistas 4 y 5).
- **Comprobado en un render** de una copia del ejemplo con audios sintéticos: los cinco golpes caen en el fotograma de su plano (0, 70, 536, 954 y 1534) y la última muestra de la música, en la última del vídeo.
- **Decisiones técnicas:**
  - Además de la licencia, se exige la fuente (la página de donde se descargó), para poder demostrar el permiso.
  - Solo se aceptan WAV de 16 bits; lo demás se convierte con ffmpeg.
  - La música queda 18 dB por debajo del nivel medio de las voces.
  - Sin `sonido.toml`, se monta igual, con un aviso, para la versión previa.
- **No se ha hecho:** el proveedor de música en `estudio.toml` que menciona la spec ("proveedores de música y efectos"). Hoy solo hay una forma de traer música, elegirla a mano, y no hay nada que cambiar. Se añadirá con el primer proveedor de música generada o de pago (compuerta humana).
- **Pendiente para otros tickets** (también en "Límites conocidos" de la doc):
  - El golpe cae en el primer fotograma del plano, sin poder retrasarse dentro del plano. Encaja con el ticket 19.
  - El volumen de la música se calcula con el nivel medio de todo el archivo.
  - Falta elegir la música y los efectos reales del piloto, con licencia, para el ticket 20.
