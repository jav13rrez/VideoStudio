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

**2026-11-10, agente.** Las hojas de vistas se hacen así: un render EEVEE de un fotograma desde cada cámara de la escena (con `bpy.ops.render.render` a través del MCP), unidos en una sola imagen con ffmpeg (filtro `tile`). Probado en el ticket 02 con cuatro cámaras (frente, tres cuartos, lateral y cenital), unos 0,7 s por render. Por ejemplo:

```bash
ffmpeg -pattern_type glob -i 'cam_*.png' -vf "scale=360:640,tile=4x1:padding=8:color=white" -frames:v 1 hoja_de_vistas.png
```

Avisos del ticket 02 en `DEBT_TECH.md`: la herramienta `render_viewport_to_path` del MCP no renderiza la sesión abierta, y la pantalla de bienvenida de Blender tapa las capturas hasta que se hace clic.
