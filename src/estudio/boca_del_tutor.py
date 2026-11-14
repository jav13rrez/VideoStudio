"""La boca del Tutor: cuándo está abierta y cuánto, según las palabras acentuadas de la línea de tiempo.

Solo se abre en las palabras acentuadas (`*así*` en el guion) que dice el Tutor, y alterna abierta grande y abierta pequeña
cada pocos fotogramas; fuera de ellas está cerrada. Es común a los dos motores: Blender cambia la pieza de la boca
(actuacion_de_blender.py) y el dibujo 2D abre la zona blanda de la mandíbula de la pose (dibujar_planos.py). El formato
está en docs/actuacion.md y docs/dibujo-2d.md.
"""

from estudio.actuacion import PERSONAJE_CON_BOCA
from estudio.cronometraje import LineaDeTiempo

FOTOGRAMAS_POR_BOCA = 3  # lo que dura cada apertura antes de alternar con la otra
ANGULOS_DE_LA_BOCA = (16.0, 8.0)  # grados que abre la mandíbula en 2D: abierta grande y abierta pequeña

Palabras = list[tuple[int, int]]


def palabras_acentuadas(linea: LineaDeTiempo) -> Palabras:
    """El principio y el final, en fotogramas de la línea de tiempo, de cada palabra acentuada que dice el Tutor."""
    return [
        (palabra.inicio, palabra.final)
        for frase in linea.frases
        if frase.personaje.lower() == PERSONAJE_CON_BOCA
        for palabra in frase.palabras
        if palabra.acentuada
    ]


def apertura(fotograma: int, palabras: Palabras) -> int | None:
    """0 (abierta grande) o 1 (abierta pequeña) si el fotograma cae en una palabra acentuada; None, boca cerrada."""
    for inicio, final in palabras:
        if inicio <= fotograma < final:
            return ((fotograma - inicio) // FOTOGRAMAS_POR_BOCA) % len(ANGULOS_DE_LA_BOCA)
    return None


def angulo_de_la_boca(fotograma: int, palabras: Palabras) -> float:
    """Los grados que abre la mandíbula en ese fotograma (0 con la boca cerrada)."""
    abierta = apertura(fotograma, palabras)
    return 0.0 if abierta is None else ANGULOS_DE_LA_BOCA[abierta]
