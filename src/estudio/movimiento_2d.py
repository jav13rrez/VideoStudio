"""Mover una pose 2D: las zonas blandas de los gestos, el párpado y la respiración.

Una zona blanda es una parte de la propia ilustración (una oreja, la cola) con un pivote y un peso por píxel: 0 en la
unión con el cuerpo, 1 en la punta, con una transición suave. La zona gira el ángulo del gesto multiplicado por ese peso,
así que no hay piezas pegadas ni cortes. Nada fuera de la caja de la zona cambia. La curva de los gestos es la de
actuacion.py; el formato de las zonas está en docs/dibujo-2d.md.
"""

import math

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageDraw

from estudio.actuacion import DURACION_DEL_PARPADEO
from estudio.poses import Caja, Pose, Zona

Premultiplicada = NDArray[np.float32]  # RGBA con el color ya multiplicado por la opacidad: así se mezcla sin halos
MARGEN = 12  # píxeles de la ilustración en los que el peso baja a 0 hacia el borde de la caja: no hay corte en su borde
RESPIRACION = 0.007  # lo que se estira la figura en vertical, como fracción de su alto, al respirar
SEGUNDOS_POR_RESPIRACION = 3
PARPADEO_MINIMO = 0.05  # por debajo de este cierre el ojo se deja como está
TINTA_DEL_PARPADEO = (22, 18, 20, 255)


def _suave(t: NDArray[np.float32]) -> NDArray[np.float32]:
    t = np.clip(t, 0, 1)
    return np.asarray(t * t * (3 - 2 * t), dtype=np.float32)


def premultiplicar(pose: Pose) -> Premultiplicada:
    pm = np.asarray(pose.ilustracion, dtype=np.float32) / 255
    pm[..., :3] *= pm[..., 3:4]
    return np.asarray(pm, dtype=np.float32)


def peso(zona: Zona, xs: NDArray[np.float32], ys: NDArray[np.float32]) -> NDArray[np.float32]:
    """0 en la unión y 1 en la punta, con transición suave, y 0 también en el borde de la caja."""
    (ux, uy), (px, py) = zona.union, zona.punta
    dx, dy = px - ux, py - uy
    a_lo_largo = ((xs - ux) * dx + (ys - uy) * dy) / (dx * dx + dy * dy)
    x0, y0, x1, y1 = zona.caja
    al_borde = np.minimum(np.minimum(xs - x0, x1 - 1 - xs), np.minimum(ys - y0, y1 - 1 - ys))
    return np.asarray(_suave(a_lo_largo.astype(np.float32)) * _suave((al_borde / MARGEN).astype(np.float32)), dtype=np.float32)


def _muestrear(pm: Premultiplicada, sx: NDArray[np.float32], sy: NDArray[np.float32]) -> Premultiplicada:
    """Los píxeles de `pm` en esas coordenadas, mezclando los cuatro vecinos (los bordes de la imagen se repiten)."""
    alto, ancho = pm.shape[:2]
    sx, sy = np.clip(sx, 0, ancho - 1), np.clip(sy, 0, alto - 1)
    x0, y0 = np.floor(sx).astype(np.intp), np.floor(sy).astype(np.intp)
    x1, y1 = np.minimum(x0 + 1, ancho - 1), np.minimum(y0 + 1, alto - 1)
    fx, fy = (sx - x0)[..., None], (sy - y0)[..., None]
    mezcla = pm[y0, x0] * (1 - fx) * (1 - fy) + pm[y0, x1] * fx * (1 - fy) + pm[y1, x0] * (1 - fx) * fy + pm[y1, x1] * fx * fy
    return np.asarray(mezcla, dtype=np.float32)


def _girar(pm: Premultiplicada, zona: Zona, grados: float) -> None:
    """Gira la zona dentro de `pm` (positivo: contra el reloj): cada píxel sale del que el giro contrario trae hasta él."""
    x0, y0, x1, y1 = zona.caja
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    t = np.radians(grados) * peso(zona, xs, ys)
    dx, dy = xs - zona.union[0], ys - zona.union[1]
    c, s = np.cos(t), np.sin(t)
    pm[y0:y1, x0:x1] = _muestrear(pm, zona.union[0] + dx * c - dy * s, zona.union[1] + dx * s + dy * c)


def _a_imagen(pm: Premultiplicada, original: NDArray[np.uint8], cajas: list[Caja]) -> Image.Image:
    """La ilustración original con solo el interior de las cajas de las zonas movidas puesto de nuevo (fuera, ni un píxel cambia)."""
    salida = original.copy()
    for x0, y0, x1, y1 in cajas:
        trozo = pm[y0:y1, x0:x1]
        alfa = trozo[..., 3:4]
        color = np.where(alfa > 1e-4, trozo[..., :3] / np.maximum(alfa, 1e-4), 0)
        salida[y0:y1, x0:x1] = (np.clip(np.concatenate([color, alfa], axis=2), 0, 1) * 255 + 0.5).astype(np.uint8)
    return Image.fromarray(salida, "RGBA")


def cierre_del_ojo(fotograma: int, parpadeos: tuple[int, ...]) -> float:
    """0 con el ojo abierto, 1 con el ojo cerrado del todo: cada parpadeo baja y sube en DURACION_DEL_PARPADEO fotogramas."""
    mitad = DURACION_DEL_PARPADEO / 2
    return max((1 - abs((fotograma - p - mitad) / mitad) for p in parpadeos if p <= fotograma <= p + DURACION_DEL_PARPADEO), default=0.0)


def _con_parpado(imagen: Image.Image, ojo: Caja, cierre: float) -> Image.Image:
    """El párpado baja sobre el ojo con el color del pelo de al lado y, cerrado, deja una línea."""
    x0, y0, x1, y1 = ojo
    mascara = Image.new("L", imagen.size, 0)
    ImageDraw.Draw(mascara).ellipse(ojo, fill=255)
    ImageDraw.Draw(mascara).rectangle((0, y0 + round((y1 - y0) * cierre), imagen.width, imagen.height), fill=0)
    movida = imagen.copy()
    pelo = imagen.getpixel((min(x1 + 8, imagen.width - 1), (y0 + y1) // 2))
    assert isinstance(pelo, tuple), "la ilustración es RGBA"
    movida.paste(pelo, mask=mascara)
    if cierre > 0.85:
        ImageDraw.Draw(movida).arc((x0 + 3, y0 + 4, x1 - 3, y1 - 6), 20, 160, fill=TINTA_DEL_PARPADEO, width=4)
    return movida


def pose_movida(pose: Pose, premultiplicada: Premultiplicada, angulos: dict[str, float], cierre: float) -> Image.Image:
    """La ilustración de la pose en un fotograma: cada zona girada por la suma de los gestos de su parte, y el párpado.

    `angulos` dice los grados de cada parte (orejas, cola). Sin ángulos ni cierre, es la ilustración de siempre.
    """
    pm = premultiplicada.copy() if any(angulos.get(z.parte) for z in pose.zonas) else premultiplicada
    movidas = []
    for zona in pose.zonas:
        grados = angulos.get(zona.parte, 0.0)
        if grados:
            _girar(pm, zona, grados)
            movidas.append(zona.caja)
    imagen = _a_imagen(pm, np.asarray(pose.ilustracion), movidas) if movidas else pose.ilustracion
    if pose.ojo is not None and cierre >= PARPADEO_MINIMO:
        imagen = _con_parpado(imagen, pose.ojo, cierre)
    return imagen


def estiramiento(fotograma: int, fase: float, fps: int) -> float:
    """El alto de la figura al respirar, como múltiplo de su alto en reposo: un estiramiento mínimo, sin pasarse del 1 %."""
    return 1 + RESPIRACION * math.sin(2 * math.pi * fotograma / (SEGUNDOS_POR_RESPIRACION * fps) + fase)
