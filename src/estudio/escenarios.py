"""Escenarios 2D: recetas que dibujan un paisaje exterior con formas planas y contorno de grosor uniforme.

Cada receta devuelve el fondo de un plano y su línea de suelo, la fila en la que apoyan los personajes. Se dibujan con
código, sin imágenes generadas, y salen siempre iguales (los elementos al azar usan una semilla fija). El formato y
las reglas están en docs/dibujo-2d.md y docs/estilo-2d.md.
"""

import random
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache

from PIL import Image, ImageDraw

ANCHO, ALTO = 1080, 1920
_SUPER = 2  # se dibuja al doble y se reduce, para que los bordes salgan suaves
_TINTA = (38, 26, 32)
Color = tuple[int, int, int]
Punto = tuple[float, float]

# El lago: dónde empieza el agua, dónde el prado y en qué fila apoyan los personajes.
_HORIZONTE = 905
_ORILLA = 1190
_SUELO_DEL_LAGO = 1590


@dataclass(frozen=True)
class Escenario:
    nombre: str
    suelo_y: int  # la fila de la línea de suelo: lo más bajo que apoya de cada personaje cae en ella
    fondo: Image.Image  # RGBA, de ANCHO x ALTO; quien lo use tiene que copiarlo antes de dibujar encima


def _punto(x: float, y: float) -> Punto:
    return (x * _SUPER, y * _SUPER)


def _rectangulo(d: ImageDraw.ImageDraw, caja: tuple[int, int, int, int], relleno: Color, radio: int = 0) -> None:
    x0, y0, x1, y1 = (v * _SUPER for v in caja)
    d.rounded_rectangle((x0, y0, x1, y1), radius=radio * _SUPER, fill=relleno, outline=_TINTA, width=6 * _SUPER)


def _poligono(d: ImageDraw.ImageDraw, puntos: tuple[Punto, ...], relleno: Color) -> None:
    d.polygon([_punto(x, y) for x, y in puntos], fill=relleno)
    d.line([_punto(x, y) for x, y in (*puntos, puntos[0])], fill=_TINTA, width=6 * _SUPER, joint="curve")


def _nube(d: ImageDraw.ImageDraw, x: int, y: int, escala: float) -> None:
    bolas = ((0, 0, 62), (70, -22, 74), (150, 0, 60), (75, 18, 70))
    for borde, color in ((6, _TINTA), (0, (250, 250, 252))):
        for dx, dy, radio in bolas:
            caja = (x + (dx - radio - borde) * escala, y + (dy - radio - borde) * escala,
                    x + (dx + radio + borde) * escala, y + (dy + radio + borde) * escala)
            d.ellipse([v * _SUPER for v in caja], fill=color)


def _pino(d: ImageDraw.ImageDraw, x: int, base: int, alto: int) -> None:
    _rectangulo(d, (x - alto // 20, base - alto // 5, x + alto // 20, base), (112, 74, 50))
    for i, color in enumerate(((46, 112, 78), (56, 130, 90), (68, 150, 102))):
        arriba = base - alto + i * alto // 5
        mitad = int(alto * 0.55 * (0.45 + 0.2 * i))
        _poligono(d, ((x, arriba), (x + mitad, arriba + alto // 2), (x - mitad, arriba + alto // 2)), color)


@cache
def _fondo_del_lago() -> Image.Image:
    """Un día junto a un lago: cielo, montañas con nieve, lago, prado con flores y pinos, todo plano y con contorno."""
    imagen = Image.new("RGBA", (ANCHO * _SUPER, ALTO * _SUPER), (150, 205, 235, 255))
    d = ImageDraw.Draw(imagen)
    d.rectangle((0, 520 * _SUPER, ANCHO * _SUPER, _HORIZONTE * _SUPER), fill=(196, 228, 242))
    d.rectangle((0, 760 * _SUPER, ANCHO * _SUPER, _HORIZONTE * _SUPER), fill=(226, 240, 242))
    d.ellipse([v * _SUPER for v in (700, 250, 900, 450)], fill=(255, 226, 140), outline=_TINTA, width=6 * _SUPER)
    _nube(d, 130, 250, 1.0)
    _nube(d, 560, 140, 0.8)
    cumbres = ((-10, _HORIZONTE + 10), (-10, 770), (160, 640), (300, 780), (470, 600), (650, 800), (820, 690), (1090, 830),
               (1090, _HORIZONTE + 10))
    _poligono(d, cumbres, (128, 156, 190))
    for nieve in (((160, 640), (112, 700), (208, 700)), ((470, 600), (415, 672), (528, 672)), ((820, 690), (780, 740), (862, 740))):
        _poligono(d, nieve, (248, 250, 252))
    orilla_lejana = ((-10, _HORIZONTE + 10), (-10, 850), (250, 884), (600, 858), (900, 892), (1090, 860), (1090, _HORIZONTE + 10))
    _poligono(d, orilla_lejana, (62, 132, 94))
    _rectangulo(d, (-10, _HORIZONTE, ANCHO + 10, _ORILLA), (92, 174, 204))
    for y, x0, x1 in ((970, 80, 360), (1010, 560, 900), (1075, 200, 520), (1130, 640, 980), (1160, 60, 280)):
        d.line([v * _SUPER for v in (x0, y, x1, y)], fill=(160, 220, 238), width=7 * _SUPER)
    _rectangulo(d, (-10, _ORILLA, ANCHO + 10, ALTO + 10), (124, 194, 98))
    d.rectangle((0, 1560 * _SUPER, ANCHO * _SUPER, ALTO * _SUPER), fill=(108, 178, 86))
    d.line([v * _SUPER for v in (0, 1560, ANCHO, 1560)], fill=_TINTA, width=5 * _SUPER)
    _pino(d, 960, _ORILLA + 30, 520)
    _pino(d, 1055, _ORILLA + 12, 400)
    _pino(d, 40, _ORILLA + 18, 360)
    azar = random.Random(7)  # las flores salen siempre en los mismos sitios
    for _ in range(46):
        x, y = azar.randint(10, ANCHO - 10), azar.randint(_ORILLA + 60, ALTO - 30)
        flor: Color = azar.choice(((252, 250, 240), (250, 214, 92), (240, 130, 150)))
        d.ellipse([v * _SUPER for v in (x - 9, y - 9, x + 9, y + 9)], fill=flor, outline=_TINTA, width=3 * _SUPER)
    return imagen.resize((ANCHO, ALTO), Image.Resampling.LANCZOS)


def _lago() -> Escenario:
    return Escenario("lago", _SUELO_DEL_LAGO, _fondo_del_lago().copy())


RECETAS: dict[str, Callable[[], Escenario]] = {"lago": _lago}
NOMBRES = frozenset(RECETAS)


def dibujar_escenario(nombre: str) -> Escenario | None:
    """El escenario con ese nombre, o None si no tiene receta 2D."""
    receta = RECETAS.get(nombre)
    return receta() if receta else None
