"""Prototipo 2D de un plano: el Tutor y el Perro juntos en un prado junto a un lago, todo ilustrado en plano.

El paisaje se dibuja aquí con formas planas y contorno. El Perro es su ilustración original entera: las orejas y la cola
se doblan con una deformación blanda (cada zona gira con un peso que vale 0 en la unión con el cuerpo y 1 en la punta,
con una transición suave), así que no hay piezas pegadas ni cortes. El Tutor es una sola pieza que respira y se sienta
en una roca. Los gestos usan la misma curva de la actuación del estudio (estudio.actuacion.angulo_en): anticipación,
acción, se mantiene y vuelve sin rebote.
Salida: prototipo.mp4 (1080x1920, 30 fps), hoja.jpg con fotogramas clave y detalle.jpg con la cabeza y la cola en pleno gesto.

Uso (desde la raíz del repo):
  PYTHONPATH=src uv run --with pillow --with numpy --with scipy python .scratch/prototipo-2d/animar.py
"""

import math
import random
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates

from estudio.actuacion import Gesto, angulo_en

AQUI = Path(__file__).parent
PIEZAS = AQUI / "piezas"
ANCHO, ALTO, FPS, FOTOGRAMAS = 1080, 1920, 30, 150
SUPER = 2  # lo que se dibuja con código va al doble y se reduce, para bordes suaves
TINTA = (38, 26, 32)
HORIZONTE = 905  # donde empieza el lago
ORILLA = 1190  # donde empieza el prado

# Los dos personajes van uno al lado del otro: misma escala y misma línea de suelo (ninguno va adelantado ni tapa al otro).
ESCALA = 0.66
SUELO_Y = 1590
SEPARACION = 14  # entre la cola de Merlín y los zapatos del Tutor
PERRO_X = 14  # donde queda el borde izquierdo de Merlín
# El Perro (la ilustración mide 1152x896): dónde apoyan las patas (la cola cuelga más abajo y no cuenta) y los bordes
# izquierdo y derecho de su silueta, en la ilustración original.
PATAS_Y, IZQUIERDA_X, DERECHA_X = 778, 169, 1042
OJO_CAJA = (252, 158, 292, 188)  # el ojo del Perro en la ilustración, para el párpado
# El Tutor (864x1184), en píxeles de su ilustración: cuánto sube su asiento sobre las suelas y cuánto sobresale la roca
# por delante y por detrás de su trasero.
ASIENTO_TUTOR = 157
ROCA_DELANTE, ROCA_DETRAS = 200, 215

# La actuación: dos gestos de oreja y dos de cola (inicio en fotogramas desde el principio del plano) y dos parpadeos.
GESTOS = [
    Gesto("perro", "orejas", 40, 14.0),
    Gesto("perro", "orejas", 104, 10.0),
    Gesto("perro", "cola", 64, 10.0),
    Gesto("perro", "cola", 104, 8.0),
]
PARPADEOS = (24, 120)
DURACION_PARPADEO = 6


def suave(t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


class Zona(NamedTuple):
    """Una parte blanda del Perro: gira alrededor de `pivote` con un peso por píxel (0 = quieto, 1 = gira entero)."""

    parte: str  # orejas o cola: qué gestos la mueven
    pivote: tuple[float, float]  # en píxeles de la ilustración original
    caja: tuple[int, int, int, int]  # x0, y0, x1, y1: fuera de ella no se toca nada (el peso vale 0 en su borde)
    peso: Callable[[np.ndarray, np.ndarray], np.ndarray]


ZONAS = (
    # oreja cercana: el peso baja a 0 hacia la base (y = 140) y en los lados, donde se funde con la cabeza y el cuello
    Zona("orejas", (340, 135), (290, 20, 400, 160),
         lambda x, y: suave((140 - y) / 55) * suave((x - 296) / 14) * (1 - suave((x - 382) / 14))),
    # oreja lejana
    Zona("orejas", (288, 100), (240, 20, 330, 125),
         lambda x, y: suave((102 - y) / 45) * suave((x - 250) / 12) * (1 - suave((x - 306) / 12))),
    # cola: el peso crece desde la grupa (x = 830) hasta la punta (x = 940)
    Zona("cola", (850, 745), (780, 600, 1100, 896), lambda x, y: suave((x - 830) / 110)),
)


def deformar(pm: np.ndarray, zona: Zona, grados: float) -> np.ndarray:
    """La imagen (RGBA premultiplicado) con la zona girada `grados` (positivo: contra el reloj) y fundida con el resto."""
    if not grados:
        return pm
    x0, y0, x1, y1 = zona.caja
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    t = np.radians(grados) * zona.peso(xs, ys)
    px, py = zona.pivote
    dx, dy = xs - px, ys - py
    c, s = np.cos(t), np.sin(t)
    origen = [py + dx * s + dy * c, px + dx * c - dy * s]  # de dónde sale cada píxel: el giro contrario
    salida = pm.copy()
    for canal in range(4):
        salida[y0:y1, x0:x1, canal] = map_coordinates(pm[..., canal], origen, order=1, mode="nearest")
    return salida


def a_imagen(pm: np.ndarray) -> Image.Image:
    alfa = pm[..., 3:4]
    rgb = np.where(alfa > 1e-4, pm[..., :3] / np.maximum(alfa, 1e-4), 0)
    return Image.fromarray((np.clip(np.dstack([rgb, alfa[..., 0]]), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")


def premultiplicada(imagen: Image.Image) -> np.ndarray:
    pm = np.asarray(imagen, dtype=np.float32) / 255
    pm[..., :3] *= pm[..., 3:4]
    return pm


def cierre_del_ojo(fotograma: int) -> float:
    """0 con el ojo abierto, 1 con el ojo cerrado del todo; el parpadeo baja y sube en DURACION_PARPADEO fotogramas."""
    mitad = DURACION_PARPADEO / 2
    return max((1 - abs((fotograma - p - mitad) / mitad) for p in PARPADEOS if p <= fotograma <= p + DURACION_PARPADEO), default=0.0)


def con_parpado(perro: Image.Image, cierre: float) -> Image.Image:
    """El párpado baja sobre el ojo con el color del pelo de al lado y, cerrado, deja una línea."""
    if cierre < 0.05:
        return perro
    x0, y0, x1, y1 = OJO_CAJA
    mascara = Image.new("L", perro.size, 0)
    ImageDraw.Draw(mascara).ellipse(OJO_CAJA, fill=255)
    ImageDraw.Draw(mascara).rectangle((0, y0 + round((y1 - y0) * cierre), perro.width, perro.height), fill=0)
    imagen = perro.copy()
    imagen.paste(perro.getpixel((x1 + 8, (y0 + y1) // 2)), mask=mascara)
    if cierre > 0.85:
        ImageDraw.Draw(imagen).arc((x0 + 3, y0 + 4, x1 - 3, y1 - 6), 20, 160, fill=(22, 18, 20, 255), width=4)
    return imagen


def punto(x: float, y: float) -> tuple[float, float]:
    return (x * SUPER, y * SUPER)


def rectangulo(d: ImageDraw.ImageDraw, caja: tuple[int, int, int, int], relleno: tuple, radio: int = 0) -> None:
    x0, y0, x1, y1 = (v * SUPER for v in caja)
    d.rounded_rectangle((x0, y0, x1, y1), radius=radio * SUPER, fill=relleno, outline=TINTA, width=6 * SUPER)


def poligono(d: ImageDraw.ImageDraw, puntos: tuple[tuple[float, float], ...], relleno: tuple, contorno: bool = True,
             grosor: int = 6) -> None:
    d.polygon([punto(x, y) for x, y in puntos], fill=relleno)
    if contorno:
        d.line([punto(x, y) for x, y in (*puntos, puntos[0])], fill=TINTA, width=grosor * SUPER, joint="curve")


def caja_firme(figura: Image.Image) -> tuple[int, int, int, int]:
    """La caja de la silueta contando solo lo opaco (el borde translúcido del recorte no se ve y falsea el suelo)."""
    return Image.fromarray(((np.asarray(figura.getchannel("A")) > 128) * 255).astype(np.uint8)).getbbox() or (0, 0, 0, 0)


def nube(d: ImageDraw.ImageDraw, x: int, y: int, k: float) -> None:
    bolas = ((0, 0, 62), (70, -22, 74), (150, 0, 60), (75, 18, 70))
    for borde, color in ((6, TINTA), (0, (250, 250, 252))):
        for dx, dy, r in bolas:
            d.ellipse(((x + (dx - r - borde) * k) * SUPER, (y + (dy - r - borde) * k) * SUPER,
                       (x + (dx + r + borde) * k) * SUPER, (y + (dy + r + borde) * k) * SUPER), fill=color)


def pino(d: ImageDraw.ImageDraw, x: int, base: int, alto: int) -> None:
    rectangulo(d, (x - alto // 20, base - alto // 5, x + alto // 20, base), (112, 74, 50))
    for i, color in enumerate(((46, 112, 78), (56, 130, 90), (68, 150, 102))):
        arriba = base - alto + i * alto // 5
        mitad = int(alto * 0.55 * (0.45 + 0.2 * i))
        poligono(d, ((x, arriba), (x + mitad, arriba + alto // 2), (x - mitad, arriba + alto // 2)), color)


def paisaje() -> Image.Image:
    """Un día junto a un lago: cielo, montañas con nieve, lago, prado con flores y pinos, todo plano y con contorno."""
    imagen = Image.new("RGBA", (ANCHO * SUPER, ALTO * SUPER), (150, 205, 235, 255))
    d = ImageDraw.Draw(imagen)
    d.rectangle((0, 520 * SUPER, ANCHO * SUPER, HORIZONTE * SUPER), fill=(196, 228, 242))
    d.rectangle((0, 760 * SUPER, ANCHO * SUPER, HORIZONTE * SUPER), fill=(226, 240, 242))
    d.ellipse((700 * SUPER, 250 * SUPER, 900 * SUPER, 450 * SUPER), fill=(255, 226, 140), outline=TINTA, width=6 * SUPER)
    nube(d, 130, 250, 1.0)
    nube(d, 560, 140, 0.8)
    poligono(d, ((-10, HORIZONTE + 10), (-10, 770), (160, 640), (300, 780), (470, 600), (650, 800), (820, 690), (1090, 830),
                 (1090, HORIZONTE + 10)), (128, 156, 190))
    for cima in (((160, 640), (112, 700), (208, 700)), ((470, 600), (415, 672), (528, 672)), ((820, 690), (780, 740), (862, 740))):
        poligono(d, cima, (248, 250, 252))
    poligono(d, ((-10, HORIZONTE + 10), (-10, 850), (250, 884), (600, 858), (900, 892), (1090, 860), (1090, HORIZONTE + 10)),
             (62, 132, 94))
    rectangulo(d, (-10, HORIZONTE, ANCHO + 10, ORILLA), (92, 174, 204))
    for y, x0, x1 in ((970, 80, 360), (1010, 560, 900), (1075, 200, 520), (1130, 640, 980), (1160, 60, 280)):
        d.line((x0 * SUPER, y * SUPER, x1 * SUPER, y * SUPER), fill=(160, 220, 238), width=7 * SUPER)
    rectangulo(d, (-10, ORILLA, ANCHO + 10, ALTO + 10), (124, 194, 98))
    d.rectangle((0, 1560 * SUPER, ANCHO * SUPER, ALTO * SUPER), fill=(108, 178, 86))
    d.line((0, 1560 * SUPER, ANCHO * SUPER, 1560 * SUPER), fill=TINTA, width=5 * SUPER)
    pino(d, 960, ORILLA + 30, 520)
    pino(d, 1055, ORILLA + 12, 400)
    pino(d, 40, ORILLA + 18, 360)
    azar = random.Random(7)
    for _ in range(46):
        x, y = azar.randint(10, ANCHO - 10), azar.randint(ORILLA + 60, ALTO - 30)
        color = azar.choice(((252, 250, 240), (250, 214, 92), (240, 130, 150)))
        d.ellipse(((x - 9) * SUPER, (y - 9) * SUPER, (x + 9) * SUPER, (y + 9) * SUPER), fill=color, outline=TINTA, width=3 * SUPER)
    return imagen.resize((ANCHO, ALTO), Image.LANCZOS)


def roca(x0: int, y0: int, x1: int, y1: int) -> Image.Image:
    """Una roca plana con contorno, en una capa del tamaño de la imagen: su techo es y0 y su base y1."""
    capa = Image.new("RGBA", (ANCHO * SUPER, ALTO * SUPER), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    w, h = x1 - x0, y1 - y0

    def p(fx: float, fy: float) -> tuple[float, float]:
        return (x0 + fx * w, y0 + fy * h)

    cuerpo = ((0.0, 0.86), (0.03, 0.4), (0.14, 0.1), (0.4, 0.0), (0.72, 0.03), (0.93, 0.2), (1.0, 0.6), (0.97, 1.0), (0.06, 1.0))
    poligono(d, tuple(p(*q) for q in cuerpo), (152, 154, 162))
    poligono(d, tuple(p(*q) for q in ((0.14, 0.1), (0.4, 0.0), (0.72, 0.03), (0.62, 0.2), (0.3, 0.24))), (186, 188, 196), False)
    poligono(d, tuple(p(*q) for q in ((0.72, 0.03), (0.93, 0.2), (1.0, 0.6), (0.97, 1.0), (0.72, 1.0), (0.8, 0.5))), (116, 118, 130), False)
    for a, b in (((0.3, 0.55), (0.42, 0.78)), ((0.55, 0.4), (0.6, 0.62))):
        d.line([punto(*p(*a)), punto(*p(*b))], fill=TINTA, width=4 * SUPER)
    d.line([punto(*p(*q)) for q in (*cuerpo, cuerpo[0])], fill=TINTA, width=6 * SUPER, joint="curve")
    return capa.resize((ANCHO, ALTO), Image.LANCZOS)


def sombra(imagen: Image.Image, centro: int, suelo: int, mitad: int, oscuridad: int = 90) -> Image.Image:
    capa = Image.new("RGBA", imagen.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).ellipse((centro - mitad, suelo - 16, centro + mitad, suelo + 26), fill=(20, 60, 20, oscuridad))
    return Image.alpha_composite(imagen, capa)


def planta_del_pie(figura: Image.Image, filas: int = 60) -> tuple[int, int]:
    """Entre qué columnas de la figura está lo más bajo de su silueta (los zapatos)."""
    abajo = caja_firme(figura)[3]
    columnas = np.where((np.asarray(figura.getchannel("A"))[abajo - filas:abajo] > 128).any(axis=0))[0]
    return int(columnas.min()), int(columnas.max())


def respirar(figura: Image.Image, escala: float, fase: float, numero: int) -> Image.Image:
    """La figura a su escala, con la respiración: se estira un poco en vertical sobre la línea del suelo."""
    estiramiento = 1 + 0.007 * math.sin(2 * math.pi * numero / (3 * FPS) + fase)
    return figura.resize((round(figura.width * escala), round(figura.height * escala * estiramiento)), Image.LANCZOS)


def perro_en(numero: int, base: np.ndarray) -> Image.Image:
    """El Perro de este fotograma: cada zona blanda girada por la suma de sus gestos, y el párpado."""
    pm = base
    for zona in ZONAS:
        pm = deformar(pm, zona, sum(angulo_en(g, numero) for g in GESTOS if g.parte == zona.parte))
    return con_parpado(a_imagen(pm), cierre_del_ojo(numero))


class Escenario(NamedTuple):
    """Lo que se dibuja una vez y se repite en cada fotograma."""

    fondo: Image.Image
    roca: Image.Image
    pie: tuple[int, int]  # centro y semiancho de sus zapatos en la imagen, para la sombra de contacto
    tutor_derecha: int  # dónde queda el borde derecho de la silueta del Tutor


def fotograma(numero: int, escenario: Escenario, perro_base: np.ndarray, tutor_img: Image.Image) -> Image.Image:
    tutor = respirar(tutor_img, ESCALA, 1.3, numero)
    caja = caja_firme(tutor)
    perro = respirar(perro_en(numero, perro_base), ESCALA, 0.0, numero)
    alto_perro = perro.height * PATAS_Y / 896  # la línea de las patas, ya a escala y con la respiración
    imagen = sombra(escenario.fondo, escenario.pie[0], SUELO_Y, escenario.pie[1], 120)
    imagen.alpha_composite(escenario.roca)
    imagen.alpha_composite(tutor, (escenario.tutor_derecha - caja[2], SUELO_Y - caja[3]))
    mitad_perro = round((DERECHA_X - IZQUIERDA_X) * ESCALA / 2)
    imagen = sombra(imagen, PERRO_X + mitad_perro, SUELO_Y, mitad_perro + 20)
    imagen.alpha_composite(perro, (round(PERRO_X - IZQUIERDA_X * ESCALA), round(SUELO_Y - alto_perro)))
    return imagen.convert("RGB")


def en_escena(x: float, y: float) -> tuple[int, int]:
    """Una coordenada de la ilustración original del Perro, en la imagen final."""
    return (round(PERRO_X + (x - IZQUIERDA_X) * ESCALA), round(SUELO_Y + (y - PATAS_Y) * ESCALA))


def main() -> None:
    perro_base = premultiplicada(Image.open(PIEZAS / "perro.png").convert("RGBA"))
    tutor_img = Image.open(PIEZAS / "tutor.png").convert("RGBA")
    fondo = paisaje()
    fondo.convert("RGB").save(AQUI / "paisaje_plano.png")
    tutor0 = respirar(tutor_img, ESCALA, 1.3, 0)
    izquierda, _, derecha, _ = caja_firme(tutor0)
    # El Tutor va justo a la derecha de Merlín, a su lado y en la misma línea de suelo.
    tutor_izquierda = PERRO_X + round((DERECHA_X - IZQUIERDA_X) * ESCALA) + SEPARACION
    tutor_derecha = tutor_izquierda + (derecha - izquierda)
    origen_x = tutor_derecha - derecha  # dónde queda la imagen del Tutor
    # La roca está centrada bajo el trasero del Tutor (algo adelantada, con el muslo sobresaliendo por el borde exterior y
    # roca visible también detrás de la espalda). Su techo está a la altura del asiento y su base en la misma línea de
    # suelo que las suelas: el Tutor y la roca apoyan en el mismo suelo, sin hierba que lo suba.
    trasero_x = tutor_derecha - round(0.17 * (derecha - izquierda))
    suelo_roca = SUELO_Y + 2
    capa_roca = roca(trasero_x - round(ROCA_DELANTE * ESCALA), SUELO_Y - round(ASIENTO_TUTOR * ESCALA) - 10,
                     trasero_x + round(ROCA_DETRAS * ESCALA), suelo_roca)
    fondo = sombra(fondo, trasero_x - 10, suelo_roca, round((ROCA_DELANTE + ROCA_DETRAS) * ESCALA / 2) + 20, 100)
    pie_izquierdo, pie_derecho = (origen_x + c for c in planta_del_pie(tutor0))
    escenario = Escenario(fondo, capa_roca, ((pie_izquierdo + pie_derecho) // 2, (pie_derecho - pie_izquierdo) // 2 + 30),
                          tutor_derecha)
    carpeta = Path(tempfile.mkdtemp(prefix="prototipo-2d-"))
    try:
        for numero in range(FOTOGRAMAS):
            fotograma(numero, escenario, perro_base, tutor_img).save(carpeta / f"{numero:04d}.png")
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(carpeta / "%04d.png"),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", str(AQUI / "prototipo.mp4")],
            check=True,
        )
        clave = (0, 34, 46, 60, 76, 88)  # reposo, anticipación y acción de la oreja, vuelta, cola, cola
        hoja = Image.new("RGB", (len(clave) * 360, 640), (255, 255, 255))
        for i, n in enumerate(clave):
            hoja.paste(Image.open(carpeta / f"{n:04d}.png").resize((360, 640), Image.LANCZOS), (i * 360, 0))
        hoja.save(AQUI / "hoja.jpg", quality=90)
        detalle = Image.new("RGB", (1440, 720), (255, 255, 255))
        for fila, (centro, numeros) in enumerate(((en_escena(340, 120), (34, 46, 58)), (en_escena(950, 760), (67, 80, 94)))):
            marco = (centro[0] - 240, centro[1] - 180, centro[0] + 240, centro[1] + 180)
            for i, n in enumerate(numeros):
                detalle.paste(Image.open(carpeta / f"{n:04d}.png").crop(marco), (i * 480, fila * 360))
        detalle.save(AQUI / "detalle.jpg", quality=92)
        asiento = Image.open(carpeta / "0010.png").crop((tutor_izquierda - 40, SUELO_Y - 260, ANCHO, SUELO_Y + 60))
        asiento.resize((asiento.width * 2, asiento.height * 2), Image.LANCZOS).save(AQUI / "detalle_tutor.jpg", quality=92)
    finally:
        shutil.rmtree(carpeta, ignore_errors=True)
    print("hecho: prototipo.mp4, hoja.jpg, detalle.jpg y paisaje_plano.png")


main()
