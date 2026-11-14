"""Lo de la actuación que es solo de Blender: el estado de cada pieza recortada en cada fotograma de un plano.

La curva de los gestos y la lectura de actuacion.toml no dependen de Blender y están en actuacion.py; el dibujo 2D las
usa tal cual (movimiento_2d.py). Aquí quedan las piezas de la biblioteca de Blender y la boca del Tutor, que es una pieza
que se cambia por otra. El formato está en docs/actuacion.md.
"""

from typing import Any

from estudio.actuacion import DURACION_DEL_GESTO, PERSONAJE_CON_BOCA, Linea, angulo_en
from estudio.boca_del_tutor import Palabras, apertura, palabras_acentuadas
from estudio.cronometraje import LineaDeTiempo, PlanoCronometrado
from estudio.tomas import Toma

# Qué partes tiene cada pieza del Perro en la biblioteca de Blender (las poses de pie no tienen ninguna).
PARTES_DE_LA_PIEZA = {"perro_sentado_frente": ("orejas",), "perro_sentado_perfil": ("orejas", "cola")}

BOCAS_ABIERTAS = ("abierta_grande", "abierta_pequena")  # se alternan dentro de una palabra acentuada
BOCA_EN_REPOSO = "cerrada"

Estados = list[dict[str, dict[str, Any]]]


def estados_del_plano(
    plano: PlanoCronometrado, linea: LineaDeTiempo, toma: Toma, actuacion: Linea
) -> tuple[Estados | None, list[str]]:
    """El estado de cada pieza en cada fotograma del plano; None si no cambia nada (el plano es una sola imagen)."""
    duracion = plano.final - plano.inicio
    piezas = {c.pieza: c for c in toma.personajes}
    errores = []
    if actuacion.parpadeos:
        errores.append(f"Plano «{plano.id}»: el parpadeo solo existe en el dibujo 2D (con reparto.toml); Blender no lo anima.")
    for gesto in actuacion.gestos:
        if gesto.pieza not in piezas:
            errores.append(f"Plano «{plano.id}»: el gesto es de «{gesto.pieza}», que no está en su toma.")
        elif gesto.parte not in PARTES_DE_LA_PIEZA.get(gesto.pieza, ()):
            errores.append(f"Plano «{plano.id}»: «{gesto.pieza}» no tiene {gesto.parte} que mover.")
        elif gesto.inicio + DURACION_DEL_GESTO > duracion:
            errores.append(
                f"Plano «{plano.id}»: el gesto de «{gesto.parte}» de «{gesto.pieza}» empieza en {gesto.inicio} y acaba en "
                f"{gesto.inicio + DURACION_DEL_GESTO}, y el plano tiene {duracion} fotogramas."
            )
    if errores:
        return None, errores
    palabras = palabras_acentuadas(linea)
    estados: Estados = []
    for numero in range(duracion):
        absoluto = plano.inicio + numero
        estado: dict[str, dict[str, Any]] = {}
        for pieza, colocacion in piezas.items():
            if pieza.startswith(PERSONAJE_CON_BOCA):
                estado[pieza] = {"boca": _boca(absoluto, palabras, colocacion.boca or BOCA_EN_REPOSO)}
            else:
                estado[pieza] = {}
        for gesto in actuacion.gestos:
            estado[gesto.pieza][gesto.parte] = angulo_en(gesto, numero)
        estados.append(estado)
    cambia = any(e != estados[0] for e in estados[1:])
    return (estados if cambia else None), []


def _boca(fotograma: int, palabras: Palabras, en_reposo: str) -> str:
    abierta = apertura(fotograma, palabras)
    return en_reposo if abierta is None else BOCAS_ABIERTAS[abierta]
