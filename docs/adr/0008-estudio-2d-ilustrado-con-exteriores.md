# Imagen del estudio: 2D ilustrado plano, con paisajes exteriores y los dos personajes siempre juntos

El estudio deja de hacer la imagen con Blender (escenarios 3D con personajes recortados) y pasa a una imagen **2D ilustrada plana**: formas con contorno de grosor uniforme y color liso, tanto en los personajes como en los paisajes. El creador lo decidió el 2026-11-13 tras ver el piloto con Blender ("los personajes son ridículos, parecen recortes de papel sobre escenarios 3D") y un prototipo de un plano en 2D ("has dado con la clave").

## Qué se decide

- **Estilo:** ilustración plana con contorno uniforme y sombreado de dos tonos. Nada fotográfico ni con luz realista.
- **Escenarios:** siempre exteriores, parajes naturales de un día de un tutor y su perro (mar, bosque, lago, montaña, monte, prado). Se dibujan con código, como formas planas; no se generan con IA (Fal repitió el aspecto de render 3D en dos intentos).
- **Personajes:** el Tutor (Javier) y el Perro (Merlín) **siempre juntos, uno al lado del otro (side by side) y lo más cerca posible**, a la misma distancia de la cámara y sin que ninguno tape al otro. Se usan todas las poses de las hojas del creador: Tutor de pie y sentado, y Merlín sentado, de pie y tumbado ("esfinge"). Las ilustraciones se generan con Fal a partir de cada hoja, conservando el parecido, y se recortan.
- **Animación:** orejas, cola y demás partes que se mueven no son piezas pegadas, sino zonas de la propia ilustración que **se doblan con un peso que vale 0 en la unión con el cuerpo y 1 en la punta**, con una transición suave. Así no hay cortes ni huecos. El párpado se dibuja sobre el ojo.
- **Actuación:** se mantiene tal cual el [ticket 19](../../.scratch/estudio-de-episodios/issues/19-actuacion.md) ([`actuacion.toml`](../actuacion.md) y su curva de anticipación, acción, pausa y vuelta sin rebote).
- **Contacto con el suelo y con el asiento:** las reglas de [`docs/estilo-2d.md`](../estilo-2d.md) valen para todas las poses.
- **Montaje:** sigue siendo HyperFrames ([ADR 0007](0007-herramientas-blender-y-hyperframes.md)), que compone los planos ya dibujados.

## Qué reemplaza

Este ADR sustituye al [0007](0007-herramientas-blender-y-hyperframes.md) **solo en lo que dice de Blender** para escenarios, personajes y render. Quedan sin uso para los planos los tickets 14 (salón), 15 (personajes en Blender) y 18 (render de planos con Blender); el salón y el recibidor aprobados y los renders de `planos/` dejan de usarse. El código de Blender (`render_toma.py`, `tomas.py`, `renderizar_planos.py`) se queda hasta que el equivalente 2D lo sustituya, y no se borra todavía.

## Opciones consideradas

- **Personajes 3D reales** dentro del Blender actual: se integra mejor, pero cuesta mucho más y es difícil mantener el parecido del rostro del creador. Descartado.
- **Collage 2.5D intencionado** (los mismos recortes con luz y sombra): cambia poco la tubería, pero seguiría pareciendo papel. Descartado.
- **Dejar el 3D de Blender y pulir:** el problema es de estilo (personajes planos y sin sombreado sobre un entorno con luz y profundidad de campo), no de detalle. Descartado.

## Consecuencias

- Cada pose nueva necesita su ilustración (coste en Fal, a confirmar con el creador antes de gastarlo) y sus zonas blandas calibradas a mano; automatizarlo queda como mejora.
- Las ilustraciones del Tutor llevan el rostro del creador y siguen fuera de git, como las actuales.
- La cabeza y la mirada del Perro, y la boca del Tutor, siguen sin animar: para hablar hay que partir la cabeza en zonas blandas con el mismo método.
- El prototipo que lo validó está en `.scratch/prototipo-2d/` (scripts `generar.py`, `piezas.py` y `animar.py`) y es la base del código definitivo.
