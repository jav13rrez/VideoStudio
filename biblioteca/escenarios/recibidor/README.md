# Escenario: recibidor

El recibidor del piloto (`001-mirada`): la puerta de casa abierta hacia el rellano (luz fría), una lámpara cálida de techo, un perchero con abrigo, un mueble con espejo y un felpudo. Archivo: `recibidor.blend` (Blender 5.2).

**Estado: aceptado tal cual por el creador el 2026-11-12** ("lo probamos tal cual"), a la espera de verlo en el episodio. Es un primer bloqueo con luz y materiales con desgaste; no ha pasado por las tres pasadas del salón, y se puede pulir. Hoja de vistas: `hoja_vistas.png` (frente a la altura del Perro, frente desde arriba, tres cuartos y lateral).

## Qué tiene

- **Luz principal con motivo:** el rellano (`luz_principal_rellano`, fría) entrando por la puerta abierta. Luz cálida de ambiente: `luz_cenital_calida`, `ambiente_calido_frente`, `ambiente_pasillo`.
- **Colecciones:** `RECIBIDOR_geometria`, `RECIBIDOR_luces`, `RECIBIDOR_camaras` (`cam_frente`). El render de los planos añade su propia cámara.
- **Orientación:** la puerta está en la pared del fondo (y = 3 m), la habitación va de x = −1,2 a 1,2 y la pared del lado de la cámara (`pared_frente`) no se ve desde ella. El rellano continúa hasta y = 5 m.
- **Silueta:** la persona desconocida del plano 17 es una pieza aparte, `biblioteca/objetos/silueta`.

## Límites conocidos

- El rellano sale muy claro (casi quemado) en los planos 15 y 16.
- La silueta es un bloque simple, sin forma de persona creíble.
