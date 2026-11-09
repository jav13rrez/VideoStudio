# 06: Primer montaje: subtítulos

**What to build:** La herramienta genera las tarjetas de subtítulo (1-2 palabras) a partir de las marcas de tiempo, y una composición de HyperFrames que las muestra sobre un fondo liso junto con las voces. Se renderiza a un MP4 vertical: es el primer vídeo que produce el estudio.

**Blocked by:** 04 (Voces de prueba y cronometraje)

**Status:** ready-for-agent

- [ ] Tarjetas de 1-2 palabras; cada una empieza en el fotograma de su primera palabra y acaba donde empieza la siguiente o donde termina la frase.
- [ ] Tutor: texto blanco con borde negro. Perro: texto lightcyan (`#E0FFFF`) con borde maroon (`#800000`). Los dos en negrita, con borde grueso alrededor de cada letra, abajo en el centro y dentro de la zona segura del 9:16.
- [ ] Solo las tarjetas con palabras acentuadas tienen animación de entrada.
- [ ] La composición generada tiene las capas de audio y de subtítulos con los tiempos de la línea de tiempo (probado sin renderizar).
- [ ] Hay un MP4 1080x1920 a 30 fps renderizado con HyperFrames y revisado por el agente en fotogramas sueltos. Si en la nube no se puede renderizar, se comprueba en el PC.
- [ ] La versión de HyperFrames queda fijada.
