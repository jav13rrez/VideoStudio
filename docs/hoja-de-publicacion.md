# Hoja de publicación

Cuando el episodio está exportado, la herramienta deja la hoja de publicación: lo que el creador copia al subir el vídeo a cada plataforma. La herramienta no publica nada; sube el creador, a mano. Ver [spec](../.scratch/estudio-de-episodios/spec.md), "Publicación".

```
uv run estudio hoja-de-publicacion <carpeta del episodio>
```

Escribe `publicacion.md` en la carpeta del episodio. Es un archivo generado: no se edita a mano, se vuelve a generar.

## Qué lleva

- **Enlaces con seguimiento**: uno por plataforma, el enlace a la App con tres etiquetas (UTM, las que leen las herramientas de analítica para saber de dónde llega cada visita):
  - `utm_source`: `youtube`, `tiktok` o `instagram`;
  - `utm_medium`: `social` (el medio que las analíticas agrupan como redes sociales);
  - `utm_campaign`: la carpeta del episodio, por ejemplo `001-olfato`.

  Si el enlace base ya lleva otras etiquetas o un ancla (`#…`), se conservan; las `utm_` que tuviera se sustituyen.
- **Descripción** de cada plataforma: el CTA del guion (sin marcas de fuente ni asteriscos) y debajo el enlace de esa plataforma.
- **Recordatorios de subida**: subir a mano `exportacion/<carpeta>.mp4` tras comprobarlo con `comprobar-exportacion` ([revision.md](revision.md)); marcar el aviso de marca propia donde la plataforma lo pida; no marcar la etiqueta de IA (decisión por defecto del estudio); usar en cada plataforma su enlace, y en TikTok e Instagram ponerlo en la bio, porque en la descripción no se puede pulsar.

## De dónde sale el enlace

De `enlace` en `app/app.toml`, la documentación de la App junto a `estudio.toml` (ver [montaje.md](montaje.md), "El cierre del CTA"):

```toml
enlace = "https://…"   # una dirección web completa, con http:// o https://
```

Los tests tienen su App de ejemplo en `tests/episodios/app/`, con `enlace = "https://huellas.example/app"`.

## Cuándo no hay hoja

La orden termina con código de salida 1, sin escribir `publicacion.md`, si:

- el guion tiene errores (los de `comprobar-guion`) o no tiene CTA;
- falta `enlace` en `app/app.toml`, no es una dirección web completa o el archivo no se entiende;
- falta o no se entiende `estudio.toml`.
