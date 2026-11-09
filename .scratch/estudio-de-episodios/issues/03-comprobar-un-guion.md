# 03: Comprobar un guion

**What to build:** Primera versión de la herramienta del estudio. Dada una carpeta de episodio con un guion en el formato canónico y sus fuentes, la herramienta dice si el guion puede pasar a la parada 1 y da sus errores y avisos en lenguaje llano. Este ticket define el formato canónico del guion y de las fuentes, crea una carpeta de episodio de ejemplo para los tests y deja montado el proyecto en Python (uv y pytest) con la única costura de pruebas: la herramienta ejecutada sobre carpetas de episodio de ejemplo.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] El formato canónico del guion está documentado: frases con su personaje, gancho, remate, CTA aparte, palabras acentuadas y marcas de fuente.
- [ ] Error si habla un personaje que no es el Perro ni el Tutor.
- [ ] Error si el CTA no va al final o lo dice el Tutor.
- [ ] Error si una marca apunta a una fuente que no existe.
- [ ] Aviso si la conversación (sin el CTA) se sale de 150-170 palabras, o si el CTA pasa de unas 15 palabras.
- [ ] Aviso si falta la marca de gancho o la de remate.
- [ ] Aviso por fuentes que ninguna frase usa y por fuentes que el creador no ha revisado.
- [ ] Un guion correcto pasa sin errores.
- [ ] Todo probado ejecutando la herramienta sobre carpetas de episodio de ejemplo.
