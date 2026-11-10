# Progreso

El agente lee este archivo al empezar cada sesión y lo actualiza al cerrar cada fase. Aquí no se copia el contenido de specs, tickets ni ADRs: se enlazan.

## Estado actual

- **Fase:** 3. Construir
- **Siguiente paso:** el ticket [13](.scratch/estudio-de-episodios/issues/13-voz-gratuita-real.md) (voces): muestras de Kokoro para que el creador elija las del Perro y el Tutor. Va en el PC de casa, con `/mattpocock-skills:implement` en una conversación nueva. Después, el [16](.scratch/estudio-de-episodios/issues/16-musica-y-efectos.md) (música y efectos). Los del 14 y 15 esperan las aportaciones del creador del [01](.scratch/estudio-de-episodios/issues/01-aportaciones-del-creador.md). El creador sigue desde la app de escritorio (2026-11-10). Ojo: el 13, el 16 y los de Blender necesitan las herramientas del PC (Blender en Windows por el MCP, la tarjeta, Kokoro, whisper.cpp y earshot en WSL; ver [DEBT_TECH.md](DEBT_TECH.md)), así que solo se pueden hacer si la sesión corre en el PC, en `~/VideoStudio` de WSL. Desde una sesión en la nube, solo el 08, el 09 y el 10.
- **Trabajo en curso:** ticket [02](.scratch/estudio-de-episodios/issues/02-preparar-el-pc.md) hecho el 2026-11-10: el PC de casa tiene el estudio instalado y probado (Blender 5.2 en Windows, conectado desde WSL por la red `mirrored`; detalle en [DEBT_TECH.md](DEBT_TECH.md)). Tickets [03](.scratch/estudio-de-episodios/issues/03-comprobar-un-guion.md) a [07](.scratch/estudio-de-episodios/issues/07-version-previa-de-carton.md) hechos y en `main`. La herramienta del estudio comprueba un guion, genera voces de prueba, comprueba la lista de planos y calcula la línea de tiempo en fotogramas. También monta la versión previa de cartón (un cartel por plano, las voces, los subtítulos y el cierre del CTA con el nombre y el logo de la App) y la renderiza con HyperFrames a un MP4 vertical (`uv run estudio --help`). El creador vio la del ejemplo en una hoja de contactos y le vale (2026-11-09). Tickets en [.scratch/estudio-de-episodios/issues/](.scratch/estudio-de-episodios/issues/); lo pendiente del PC está en [DEBT_TECH.md](DEBT_TECH.md).
- **Para enseñar resultados al creador:** su aplicación no reproduce vídeos MP4, pero sí muestra imágenes. Enséñale cada versión como hoja de contactos (un fotograma por segundo en una sola imagen) o como imagen animada (GIF).
- **Pendiente del creador:** la documentación de la App, con sus funcionalidades. Al recibirla, revisar si la carpeta `app/` (decidida en el ticket 07) sigue siendo el mejor sitio, y adaptar `app/app.toml`.

## Historial

<!-- Una línea por fase cerrada, la más reciente arriba. Formato: AAAA-MM-DD · Fase N · qué se hizo · enlace -->
- 2026-11-09 · Fase 2 · Spec y 20 tickets con sus dependencias (del 03 al 10 se pueden hacer en la nube; el 02 y del 13 al 20, en el PC) · [spec](.scratch/estudio-de-episodios/spec.md)
- 2026-11-09 · Fase 1 · Entrevista cerrada: episodios de diálogo Perro–Tutor con CTA a la App; vocabulario y decisiones apuntados · [GLOSSARY.md](GLOSSARY.md), [ADR 0005-0007](docs/adr/)
- 2026-11-09 · Fase 0 · Idea recibida (estudio de shorts 2.5D) y entorno revisado; lo pendiente está en DEBT_TECH.md · [docs/PlanBase.md](docs/PlanBase.md)
