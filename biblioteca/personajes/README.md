# Personajes: Tutor y Perro

Piezas recortadas de las hojas de personaje del creador, montadas en Blender 5.2 como planos sin sombreado (la luz del escenario no los toca), con contorno grueso y sombra de contacto. Cada personaje es un `.blend` con una colección (`PERSONAJE_tutor`, `PERSONAJE_perro`) que un episodio copia o enlaza.

**Estado:** aceptados con reservas por el creador (2026-11-12): le sorprende lo realista y duda de que este tipo de imagen funcione; dará su veredicto sobre el resultado final de un episodio. Si no le convence, cambiar de estilo es una decisión de producto.

| Personaje | Archivo | Hoja de vistas |
| --- | --- | --- |
| Tutor | `tutor/tutor.blend` | `tutor/hoja_vistas.png` |
| Perro | `perro/perro.blend` | `perro/hoja_vistas.png` |

`hoja_prueba_salon.png`: los dos sentados en el sofá del salón, desde `cam_frente` y `cam_tres_cuartos`.

**Fuera de git** (llevan el rostro del creador y el repositorio podría ser público): `_trabajo/`, `tutor/` y `hoja_prueba_salon.png`. Solo se versionan este README, `receta/` y `perro/`.

## Tutor (`tutor_sentado_frente`)

- Cuerpo sentado de frente (de la hoja sentada) y cabeza (del primer plano), que son planos distintos.
- **Ojos** (propiedad `ojos` de la raíz, 0 a 5): `neutros`, `cerrados`, `muy_abiertos`, `entornados`, `mirada_izq`, `mirada_der`.
- **Bocas** (propiedad `boca`, 0 a 5): `cerrada`, `abierta_pequena`, `abierta_grande`, `o`, `ceno`, `sonrisa`.
- Cambiar `ojos` o `boca` en la raíz cambia el parche visible (drivers). En la animación se cambian por fotograma.
- Las expresiones se generaron con Fal (`fal-ai/nano-banana/edit`) sobre el primer plano y se recortaron como parches alineados con la cabeza.
- `cuerpo_sentado_perfil.png` está en `tutor/piezas/` pero no se usa: las hojas no traen la cabeza de perfil.

## Perro (cuatro poses, cada una con su raíz)

`perro_sentado_frente`, `perro_sentado_perfil`, `perro_de_pie_frente`, `perro_de_pie_perfil`.

- Orejas (sentado de frente y de perfil) y cola (sentado de perfil): piezas aparte con el pivote en su base; se animan rotando en Y. Las de pie no las tienen.
- Parpadeo del sentado de frente: propiedad `ojos` de la raíz (0 abiertos, 1 cerrados).
- Sin bocas habladas (el Perro habla en voz en off).

## Cómo están hechas

- Escala: Tutor 1 px = 1,106 mm (cuerpo) y 0,311 mm (cabeza); Perro 0,8 mm por píxel.
- Origen de cada raíz: el punto de contacto con el asiento o el suelo. Se coloca la raíz sobre el asiento (en el salón, z = 0,42 m).
- Los planos miran a −Y (hacia las cámaras del salón) y se separan 2 a 4 mm en profundidad para ordenarse sin parpadeos.
- Los materiales son emisivos (color de la imagen, sin sombreado) con transparencia; no proyectan sombra.
- El contorno grueso (unos 5 mm) va incorporado en la imagen de las piezas principales (cuerpos y cabeza).
- Los recortes de fondo se hicieron con `fal-ai/birefnet/v2`; las imágenes del perro se limpiaron del borde blanco del recorte.
- La receta (scripts y prompts) está en `receta/`. Las rutas de algunos scripts apuntan a la carpeta temporal de la sesión.

## Límites conocidos

- Los personajes no se iluminan: en un escenario muy oscuro o de otro color pueden destacar. El material tiene un valor `Strength` para ajustar el brillo de cada pieza.
- Falta la cabeza del Tutor de perfil y de tres cuartos.
- Las expresiones `entornados` y `cerrados` del Tutor salen cercanas a un guiño.
