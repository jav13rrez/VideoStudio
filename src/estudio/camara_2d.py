"""Cámara del dibujo 2D: acercamiento y desplazamiento como recortes suavizados de un lienzo más grande.

El tipo de cámara de cada plano sale de planos.toml (fija, acercamiento o desplazamiento) y los números, de `desde` y
`hasta` en reparto.toml. Una vista se dice en fracciones del escenario: `ancho` es la fracción de su ancho que cabe en la
imagen y `centro`, el punto al que mira, también como fracción del escenario (x, y). El ancho del acercamiento y la
variación de ancho del desplazamiento son los mismos de tomas.py (Blender); el desvío del centro, que allí es en metros,
aquí es en fracciones. El formato está en docs/dibujo-2d.md.
"""

from dataclasses import dataclass

from estudio.tomas import (
    ACERCAMIENTO,
    ACERCAMIENTO_MINIMO,
    DESPLAZAMIENTO,
    FIJA,
    VARIACION_DE_ANCHO_EN_DESPLAZAMIENTO,
)

LIENZO = 1.5  # el escenario y los personajes se dibujan a este múltiplo de 1080x1920 antes de recortar
ANCHO_MINIMO = 0.7  # la vista no baja de esta fracción del escenario: el recorte mide siempre más de 1080 píxeles y solo se reduce
DESVIO_DEL_ACERCAMIENTO = 0.02  # lo que puede moverse el centro en un acercamiento, como fracción del escenario
DESPLAZAMIENTO_MAXIMO = 0.1  # lo que puede moverse el centro en un desplazamiento, como fracción del escenario

TOLERANCIA = 1e-9  # los límites se escriben con decimales: 0.55 - 0.45 no es exactamente 0.1
Caja = tuple[float, float, float, float]


@dataclass(frozen=True)
class Vista:
    ancho: float = 1.0  # fracción del ancho del escenario que cabe en la imagen (la altura sigue la misma proporción)
    centro: tuple[float, float] = (0.5, 0.5)  # a dónde mira, como fracción del escenario


VISTA_ENTERA = Vista()


def comprobar(id_: str, tipo: str, desde: Vista | None, hasta: Vista | None) -> list[str]:
    """Los errores de la cámara de un plano: lo que se escribió tiene que concordar con su tipo y caer dentro de los límites."""
    nombre = f"Plano «{id_}»"
    if tipo == FIJA:
        if desde is None and hasta is None:
            return []
        return [f"{nombre}: la cámara del plano es fija en planos.toml, así que el reparto no puede llevar «desde» ni «hasta»."]
    if hasta is None:
        return [f"{nombre}: la cámara del plano se mueve ({tipo}) y el reparto no dice hasta dónde: falta «hasta»."]
    if tipo == DESPLAZAMIENTO and desde is None:
        return [
            f"{nombre}: un desplazamiento necesita «desde» con un ancho menor que 1: sobre el escenario entero "
            "la vista no tiene por dónde moverse (por ejemplo desde = { ancho = 0.8 })."
        ]
    inicio = desde or VISTA_ENTERA
    problemas = [*_fuera_del_escenario("desde", inicio), *_fuera_del_escenario("hasta", hasta)]
    if problemas:
        return [f"{nombre}: {'; '.join(problemas)}."]
    desvio = max(abs(a - b) for a, b in zip(inicio.centro, hasta.centro, strict=True))
    if tipo == ACERCAMIENTO:
        if not ACERCAMIENTO_MINIMO * inicio.ancho - TOLERANCIA <= hasta.ancho <= inicio.ancho + TOLERANCIA:
            problemas.append(
                f"el ancho va de {inicio.ancho:g} a {hasta.ancho:g} "
                f"(tiene que acabar entre {ACERCAMIENTO_MINIMO * inicio.ancho:.2f} y {inicio.ancho:g})"
            )
        if desvio > DESVIO_DEL_ACERCAMIENTO + TOLERANCIA:
            problemas.append(f"el centro se mueve {desvio:.3f} del escenario (como mucho {DESVIO_DEL_ACERCAMIENTO})")
    elif tipo == DESPLAZAMIENTO:
        if desvio > DESPLAZAMIENTO_MAXIMO + TOLERANCIA:
            problemas.append(f"el centro se mueve {desvio:.3f} del escenario (como mucho {DESPLAZAMIENTO_MAXIMO})")
        if abs(hasta.ancho - inicio.ancho) / inicio.ancho > VARIACION_DE_ANCHO_EN_DESPLAZAMIENTO + TOLERANCIA:
            problemas.append("el ancho cambia demasiado para un desplazamiento")
    return [f"{nombre}: el movimiento de cámara no es lento: {'; '.join(problemas)}."] if problemas else []


def _fuera_del_escenario(cual: str, vista: Vista) -> list[str]:
    """Que la vista quepa en el escenario y no sea tan pequeña que el recorte haya que ampliarlo (pierde nitidez)."""
    problemas = []
    if not ANCHO_MINIMO - TOLERANCIA <= vista.ancho <= 1 + TOLERANCIA:
        problemas.append(f"el ancho de «{cual}» ({vista.ancho:g}) tiene que estar entre {ANCHO_MINIMO:g} y 1 del escenario")
    mitad = vista.ancho / 2
    if any(not mitad - TOLERANCIA <= c <= 1 - mitad + TOLERANCIA for c in vista.centro):
        problemas.append(f"la vista «{cual}» se sale del escenario (con ancho {vista.ancho:g}, el centro va entre {mitad:g} y {1 - mitad:g})")
    return problemas


def _suave(t: float) -> float:
    return t * t * (3 - 2 * t)


def vista_en(desde: Vista, hasta: Vista, fotograma: int, duracion: int) -> Vista:
    """La vista en un fotograma: una línea recta de `desde` a `hasta`, suave al principio y al final."""
    t = _suave(fotograma / (duracion - 1)) if duracion > 1 else 0.0
    return Vista(
        desde.ancho + (hasta.ancho - desde.ancho) * t,
        (desde.centro[0] + (hasta.centro[0] - desde.centro[0]) * t, desde.centro[1] + (hasta.centro[1] - desde.centro[1]) * t),
    )


def recorte(vista: Vista, ancho_del_lienzo: int, alto_del_lienzo: int) -> Caja:
    """La caja del lienzo (izquierda, arriba, derecha, abajo, en píxeles) que se ve con esa vista."""
    mitad = vista.ancho / 2
    x, y = vista.centro
    # la tolerancia de `comprobar` admite vistas que se pasan por un redondeo: la caja nunca sale del lienzo
    return (
        max(0.0, (x - mitad) * ancho_del_lienzo),
        max(0.0, (y - mitad) * alto_del_lienzo),
        min(float(ancho_del_lienzo), (x + mitad) * ancho_del_lienzo),
        min(float(alto_del_lienzo), (y + mitad) * alto_del_lienzo),
    )
