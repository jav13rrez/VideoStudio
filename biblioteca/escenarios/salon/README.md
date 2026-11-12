# Escenario: salon

El salón del piloto (`001-mirada`): sofá azul contra la pared de fondo, de noche, con la lámpara de pie encendida. Archivo: `salon.blend` (Blender 5.2).

## Qué tiene

- **Luz principal con motivo:** la lámpara de pie (`luz_principal_lampara` y `luz_lampara_cono`, cálidas, 2700 K aprox.), a la izquierda del sofá.
- **Luces cálidas de ambiente:** `ambiente_rebote_techo`, `ambiente_calido_frente`, `ambiente_estanteria`. Contraluz frío tenue por la ventana: `luz_ventana_fria`.
- **Materiales con desgaste:** tela del sofá, pared, madera del suelo, alfombra, manta y cortinas (ruido procedural en color, rugosidad y relieve).
- **Profundidad de campo:** activada en todas las cámaras (f/2.8), enfocada en el sofá. Al usarla en un plano, ajustar `focus_distance` a donde está el personaje.
- **Cámaras (1080x1920):** `cam_frente`, `cam_tres_cuartos`, `cam_lateral`, `cam_cenital`. El episodio añade las suyas.
- **Colecciones:** `SALON_geometria`, `SALON_camaras`, `SALON_luces`. Los personajes se colocan sobre el sofá (asiento a z = 0,42 m).

## Cómo se enlaza

Un episodio enlaza la colección `SALON_geometria` (y `SALON_luces`) con `bpy.ops.wm.link`, no la copia. Cuidado: el techo (`techo`) tapa la cámara cenital; el render de la `cam_cenital` pone `techo.visible_camera = False`.

## Tiempo de render

EEVEE, 1080x1920, 128 muestras, RTX 4060 (Blender 5.2 en Windows): **2,4 s por fotograma** (medido en 5 fotogramas de `cam_frente`; el cenital, 2,7 s). Un episodio de 1.950 fotogramas, unos 78 min. A 64 muestras, 1,4 s.

## Hojas de vistas

`hoja_p1_bloqueo.png`, `hoja_p2_luz.png`, `hoja_p3_vestir.png`: un render desde cada cámara (cenital, frente, lateral, tres cuartos, en ese orden).

## Aprobación

Aprobado por el creador el 2026-11-12 (primera versión; se puede pulir).
