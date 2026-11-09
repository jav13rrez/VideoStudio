# 03: Comprobar un guion

**What to build:** Primera versión de la herramienta del estudio. Dada una carpeta de episodio con un guion en el formato canónico y sus fuentes, la herramienta dice si el guion puede pasar a la parada 1 y da sus errores y avisos en lenguaje llano. Este ticket define el formato canónico del guion y de las fuentes, crea una carpeta de episodio de ejemplo para los tests y deja montado el proyecto en Python (uv y pytest) con la única costura de pruebas: la herramienta ejecutada sobre carpetas de episodio de ejemplo.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] El formato canónico del guion está documentado: frases con su personaje, gancho, remate, CTA aparte, palabras acentuadas y marcas de fuente.
- [x] Error si habla un personaje que no es el Perro ni el Tutor.
- [x] Error si el CTA no va al final o lo dice el Tutor.
- [x] Error si una marca apunta a una fuente que no existe.
- [x] Aviso si la conversación (sin el CTA) se sale de 150-170 palabras, o si el CTA pasa de unas 15 palabras.
- [x] Aviso si falta la marca de gancho o la de remate.
- [x] Aviso por fuentes que ninguna frase usa y por fuentes que el creador no ha revisado.
- [x] Un guion correcto pasa sin errores.
- [x] Todo probado ejecutando la herramienta sobre carpetas de episodio de ejemplo.

## Comments

**2026-11-09, agente.** Hecho.

- La herramienta se usa así: `uv run estudio comprobar-guion <carpeta del episodio>`.
- El formato está en [docs/formato-del-guion.md](../../../docs/formato-del-guion.md).
- La carpeta de ejemplo es [tests/episodios/001-olfato](../../../tests/episodios/001-olfato/).
- Hay 29 tests en `tests/test_comprobar_guion.py`, todos a través de la herramienta.

Decidido por el agente, además de lo que pedía el ticket:

- **Errores de lectura**, para que nada se ignore en silencio:
  - falta `guion.md`, o no tiene frases;
  - una línea no sigue el formato;
  - una marca está mal escrita (`[Fuente: x]`, `[fuente x]`, `[gancho]` dentro del texto…);
  - una fuente no dice nada después de su id.
- **Aviso si el guion no tiene CTA**, porque el CTA cierra todos los episodios y el ticket 04 lo necesita para cronometrar.
- **Se toleran** los archivos guardados con BOM (el carácter invisible que añaden algunos editores de Windows).
- **No se comprueba** que el CTA tenga 1 o 2 frases: el aviso de unas 15 palabras ya cubre su duración.
- **Comprobación de tipos** con mypy (`uv run mypy`).
