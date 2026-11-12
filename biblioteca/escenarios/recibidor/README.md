# Escenario: recibidor

El recibidor del piloto (`001-mirada`): la puerta de casa abierta hacia el rellano (luz fría), una lámpara cálida de techo, un perchero con abrigo, un mueble con espejo y un felpudo. Archivo: `recibidor.blend` (Blender 5.2).

**Estado: provisional, pendiente de que el creador lo apruebe.** Es un primer bloqueo con luz y materiales con desgaste; no ha pasado por las tres pasadas del salón. No tiene hoja de vistas todavía.

## Qué tiene

- **Luz principal con motivo:** el rellano (`luz_principal_rellano`, fría) entrando por la puerta abierta. Luz cálida de ambiente: `luz_cenital_calida`, `ambiente_calido_frente`, `ambiente_pasillo`.
- **Colecciones:** `RECIBIDOR_geometria`, `RECIBIDOR_luces`, `RECIBIDOR_camaras` (`cam_frente`). El render de los planos añade su propia cámara.
- **Orientación:** la puerta está en la pared del fondo (y = 3 m), la habitación va de x = −1,2 a 1,2 y la pared del lado de la cámara (`pared_frente`) no se ve desde ella. El rellano continúa hasta y = 5 m.
- **Silueta:** la persona desconocida del plano 17 es una pieza aparte, `biblioteca/objetos/silueta`.

## Límites conocidos

- El rellano sale muy claro (casi quemado) en los planos 15 y 16.
- La silueta es un bloque simple, sin forma de persona creíble.
