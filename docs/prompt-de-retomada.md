# Prompt de retomada

Pega este texto como primer mensaje al abrir la sesión en la app de escritorio. Está escrito para el agente, no para el usuario. Se actualiza al cerrar cada sesión larga.

---

Retomas el proyecto VideoStudio (estudio de shorts verticales Perro–Tutor con CTA a la App K9 Architect). La sesión anterior se cortó varias veces de forma abrupta en Claude Code dentro de WSL. Todo el trabajo está commiteado y subido a `main` (2026-11-14: ticket 07 de estudio-2d y regeneración del piloto).

**Antes de nada:** lee `AGENTS.md` (única fuente de verdad), `PROGRESS.md` y `docs/dibujo-2d.md`. Abre con una frase sobre la fase y el siguiente paso, y ofrécete a darlo. Habla en español y en lenguaje llano: el creador no programa.

**Dónde estamos (Fase 3, Construir, spec `estudio-2d`):**
- Cambio de rumbo del 2026-11-13 ([ADR 0008](adr/0008-estudio-2d-ilustrado-con-exteriores.md)): la imagen pasa de Blender a 2D ilustrado plano, con exteriores y el Tutor y Merlín siempre juntos. Reglas en `docs/estilo-2d.md`.
- Hechos: tickets 01 (plano fijo), 02 (dos personajes), 03 (sentarse en una roca) y 07 (`generar-poses` con proveedor `falso`). Tests: 329 en verde (`uv run pytest`), tipos con `uv run mypy`.
- Pendientes, en `.scratch/estudio-2d/issues/`: 04 (gestos con zonas blandas), 05 (cámara), 06 (boca del Tutor), 08 (poses con Fal), 09 (las cinco poses reales), 10 a 12 (escenarios de mar, bosque y monte), 13 a 17.
- **Siguiente paso recomendado:** el ticket 04 (o el 05 o el 06; son independientes, solo código Python y tests). Un ticket por conversación nueva, con tests primero (`/implement`), y cierra con revisión y commit.

**Compuertas humanas que te esperan:**
- Tickets 08 y 09: la generación real con Fal gasta dinero (estimado de 0,5 a 1 € por las poses que faltan, sin verificar). Pide confirmación explícita antes de gastar, explicando el coste.
- No hagas `git push --force`, no borres ramas ni publiques nada sin confirmación.

**Entorno (importante):**
- El proyecto vive en `~/VideoStudio` dentro de WSL. Si la app de escritorio abre otra copia o una carpeta de Windows, para y dilo: no trabajes sobre una copia distinta.
- Las claves van en `.env` (git lo ignora; Fal usa `FAL_KEY`, ElevenLabs su clave). No las pidas en el chat.
- Las imágenes del Tutor llevan el rostro del creador y están fuera de git: solo existen en el PC de casa. Si faltan, los tests de poses pueden fallar; es esperable.
- Diagnóstico de las interrupciones (2026-11-14): no hubo OOM ni falta de memoria (Windows con 31,9 GB y WSL limitado a 16 GB). El registro de Windows muestra `wslhost.exe` colgándose, y había dos `.wslconfig` con una sección `[wsl2]` duplicada. Se quitó `networkingMode=mirrored` del `.wslconfig` del usuario `Usuario` (con copia de seguridad). Efecto secundario: los scripts de Blender conectaban desde WSL por la red `mirrored` (ver `DEBT_TECH.md`); con el 2D ya no hacen falta, pero revísalo antes de volver a usar Blender.
- Si la consola vuelve a cerrarse sola, no culpes al código: mira primero el registro de aplicación de Windows y `wsl --shutdown`.

**Al terminar cada ticket:** marca sus criterios, actualiza `PROGRESS.md` (una línea en el historial con fecha), documenta en `docs/dibujo-2d.md` y haz commit pequeño con mensaje claro. Acaba cada respuesta con **Siguiente paso:** y una acción concreta.
