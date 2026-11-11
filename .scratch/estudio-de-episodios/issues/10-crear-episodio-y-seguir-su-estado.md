# 10: Crear un episodio y seguir su estado

**What to build:** La herramienta crea la carpeta de un episodio nuevo, con número consecutivo, nombre corto y su estructura vacía. Guarda y muestra el estado del episodio: en qué paso está, qué paradas están aprobadas y cuándo, y qué escenarios o personajes nuevos esperan aprobación. Lleva también el registro de horas por etapa, con su suma.

**Blocked by:** 03 (Comprobar un guion)

**Status:** done

- [x] Crear un episodio deja la carpeta con su estructura y su estado inicial, con numeración consecutiva.
- [x] Registrar la aprobación de una parada la deja anotada con su fecha.
- [x] Mostrar el estado dice en lenguaje llano en qué paso está el episodio y qué está esperando.
- [x] El registro de horas da las horas por etapa y el total.
- [x] Probado a través de la herramienta sobre carpetas de episodio de ejemplo.

## Comments

**2026-11-09, agente (desde el ticket 05).** Los escenarios nuevos que esperan aprobación ya están apuntados en `escenarios_nuevos` de `planos.toml` (ver `docs/lista-de-planos.md`). El estado del episodio puede leerlos de ahí en lugar de repetirlos.
