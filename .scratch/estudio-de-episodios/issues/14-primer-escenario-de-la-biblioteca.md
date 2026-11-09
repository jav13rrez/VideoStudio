# 14: Primer escenario de la biblioteca

**What to build:** El agente construye en Blender, a través del MCP, el primer escenario que pide el piloto, por pasadas (bloquear, iluminar, vestir) y con una hoja de vistas al final de cada pasada. Render siempre a 1080x1920, con cielo HDRI si es de naturaleza. El creador lo aprueba y queda en la biblioteca, listo para que los episodios lo enlacen.

**Dónde:** PC de casa (ADR 0005).

**Blocked by:** 01 (Aportaciones del creador), 02 (Preparar el PC)

**Status:** ready-for-agent

- [ ] Hay hojas de vistas de las tres pasadas.
- [ ] El escenario tiene una luz principal con motivo, luces cálidas de ambiente, materiales con desgaste y profundidad de campo.
- [ ] El tiempo de render por fotograma está medido y anotado.
- [ ] El creador lo ha aprobado y la aprobación está registrada.
- [ ] Está guardado en la biblioteca y un episodio puede enlazarlo.

## Comments

**2026-11-09, agente (desde el ticket 05).** La herramienta da por hecho que la biblioteca es la carpeta `biblioteca/` junto a `estudio.toml`, y que cada escenario es una carpeta `biblioteca/escenarios/<nombre>/` con el mismo nombre que usa la lista de planos. Lo que va dentro de esa carpeta lo decide este ticket.
