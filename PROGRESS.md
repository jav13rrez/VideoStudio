# Progreso

El agente lee este archivo al empezar cada sesión y lo actualiza al cerrar cada fase. Aquí no se copia el contenido de specs, tickets ni ADRs: se enlazan.

## Estado actual

- **Fase:** 3. Construir
- **Siguiente paso:** renderizar con HyperFrames la versión previa de cartón del ejemplo y revisarla en fotogramas, para cerrar el ticket [07](.scratch/estudio-de-episodios/issues/07-version-previa-de-carton.md); en esta sesión el sistema de permisos bloqueó la descarga de HyperFrames. Después, en conversaciones nuevas, `/mattpocock-skills:implement` con el [08](.scratch/estudio-de-episodios/issues/08-revision.md) (revisión), el [09](.scratch/estudio-de-episodios/issues/09-hoja-de-publicacion.md) (hoja de publicación) o el [10](.scratch/estudio-de-episodios/issues/10-crear-episodio-y-seguir-su-estado.md) (crear un episodio y seguir su estado). En el PC de casa sigue pendiente el [02](.scratch/estudio-de-episodios/issues/02-preparar-el-pc.md), y el creador aporta lo del [01](.scratch/estudio-de-episodios/issues/01-aportaciones-del-creador.md), con la documentación de la App en una carpeta `app/`.
- **Trabajo en curso:** tickets [03](.scratch/estudio-de-episodios/issues/03-comprobar-un-guion.md) a [06](.scratch/estudio-de-episodios/issues/06-primer-montaje-subtitulos.md) hechos, y el [07](.scratch/estudio-de-episodios/issues/07-version-previa-de-carton.md) a falta del MP4. La herramienta del estudio comprueba un guion, genera voces de prueba, comprueba la lista de planos y calcula la línea de tiempo en fotogramas. También monta la versión previa de cartón: un cartel por plano, las voces, los subtítulos y el cierre del CTA con el nombre y el logo de la App. Y la renderiza con HyperFrames a un MP4 vertical (`uv run estudio --help`). Tickets en [.scratch/estudio-de-episodios/issues/](.scratch/estudio-de-episodios/issues/); lo pendiente del PC está en [DEBT_TECH.md](DEBT_TECH.md).

## Historial

<!-- Una línea por fase cerrada, la más reciente arriba. Formato: AAAA-MM-DD · Fase N · qué se hizo · enlace -->
- 2026-11-09 · Fase 2 · Spec y 20 tickets con sus dependencias (del 03 al 10 se pueden hacer en la nube; el 02 y del 13 al 20, en el PC) · [spec](.scratch/estudio-de-episodios/spec.md)
- 2026-11-09 · Fase 1 · Entrevista cerrada: episodios de diálogo Perro–Tutor con CTA a la App; vocabulario y decisiones apuntados · [GLOSSARY.md](GLOSSARY.md), [ADR 0005-0007](docs/adr/)
- 2026-11-09 · Fase 0 · Idea recibida (estudio de shorts 2.5D) y entorno revisado; lo pendiente está en DEBT_TECH.md · [docs/PlanBase.md](docs/PlanBase.md)
