# 09: Hoja de publicación

**What to build:** La herramienta genera la hoja de publicación de un episodio: el texto de la descripción con el CTA y el enlace; un enlace a la App con etiquetas de seguimiento distintas para YouTube, TikTok e Instagram, con el episodio como campaña; y los recordatorios de subida (marcar el aviso de marca propia donde se pida, sin etiqueta de IA por defecto, subida manual por el creador).

**Blocked by:** 03 (Comprobar un guion)

**Status:** done

- [x] Tres enlaces, uno por plataforma, con las etiquetas de fuente, medio y campaña correctas.
- [x] El enlace base se lee de la documentación de la App (en los tests, una documentación de ejemplo).
- [x] La descripción incluye el CTA del guion.
- [x] Los recordatorios de subida están presentes.
- [x] Probado a través de la herramienta sobre carpetas de episodio de ejemplo.

## Comments

**2026-11-09, agente (desde el ticket 07).** La documentación de la App es la carpeta `app/` junto a `estudio.toml`. La herramienta la lee con `leer_app` (`src/estudio/app.py`), de `app/app.toml`, que hoy tiene `nombre` y `logo`. El enlace base va en ese mismo archivo (por ejemplo, `enlace = "https://…"`). Los tests tienen su App de ejemplo en `tests/episodios/app/`.

**2026-11-11, agente.** Hecho: `uv run estudio hoja-de-publicacion <carpeta>` deja `publicacion.md` en la carpeta del episodio ([docs/hoja-de-publicacion.md](../../../docs/hoja-de-publicacion.md)). El enlace base es `enlace` en `app/app.toml`; las etiquetas son `utm_source` (youtube, tiktok, instagram), `utm_medium=social` y `utm_campaign=<carpeta del episodio>`. Sin enlace, sin CTA o con errores en el guion, no hay hoja. Falta el enlace real de la App, que llegará con su documentación (ticket 01).
