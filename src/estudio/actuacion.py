"""Actuación: una línea por plano y los gestos de los personajes, fotograma a fotograma.

El archivo es actuacion.toml, junto a planos.toml. Cada plano lleva su línea (pensamiento, anticipación, acción y pausa)
y, si hace falta, los gestos del Perro. La boca del Tutor no se escribe: sale de la línea de tiempo (solo se abre en las
palabras acentuadas). El formato está en docs/actuacion.md.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from estudio.cronometraje import LineaDeTiempo, PlanoCronometrado
from estudio.guion import Informe
from estudio.tomas import Toma

ARCHIVO = "actuacion.toml"

# Un gesto: tira un poco hacia el otro lado (anticipación), actúa, se mantiene y vuelve al reposo sin pasarse (sin rebote).
ANTICIPACION = 6  # fotogramas
ACCION = 8
MANTIENE = 10
VUELTA = 12
RETROCESO = 0.25  # fracción del ángulo que se tira hacia atrás en la anticipación
ANGULO_MAXIMO = 30.0  # grados
DURACION_DEL_GESTO = ANTICIPACION + ACCION + MANTIENE + VUELTA
PARTES = ("orejas", "cola")
# Qué partes tiene cada pieza del Perro en la biblioteca (las poses de pie no tienen ninguna).
PARTES_DE_LA_PIEZA = {"perro_sentado_frente": ("orejas",), "perro_sentado_perfil": ("orejas", "cola")}

BOCAS_ABIERTAS = ("abierta_grande", "abierta_pequena")  # se alternan dentro de una palabra acentuada
FOTOGRAMAS_POR_BOCA = 3
BOCA_EN_REPOSO = "cerrada"
PERSONAJE_CON_BOCA = "tutor"
PERSONAJE_SIN_BOCA = "perro"

_CAMPOS_DE_TEXTO = ("pensamiento", "anticipacion", "accion", "pausa")
_CAMPOS_DEL_PLANO = ("id", *_CAMPOS_DE_TEXTO, "gestos")
_CAMPOS_DEL_GESTO = ("pieza", "parte", "inicio", "angulo")

Estados = list[dict[str, dict[str, Any]]]


@dataclass(frozen=True)
class Gesto:
    pieza: str
    parte: str  # orejas o cola
    inicio: int  # fotograma en que empieza, contado desde el principio del plano
    angulo: float  # grados a los que llega


@dataclass(frozen=True)
class Linea:
    id: str
    pensamiento: str
    anticipacion: str
    accion: str
    pausa: str
    gestos: tuple[Gesto, ...]


def leer_actuacion(carpeta: Path, ids_de_planos: set[str], elegidos: list[str]) -> tuple[dict[str, Linea], list[str]]:
    """Las líneas de actuación por id del plano, y los errores. Cada plano de `elegidos` tiene que tener la suya."""
    archivo = carpeta / ARCHIVO
    if not archivo.is_file():
        return {}, [
            f"No encuentro {ARCHIVO} en la carpeta del episodio: ahí va la línea de actuación de cada plano "
            "(formato en docs/actuacion.md)."
        ]
    try:
        datos = tomllib.loads(archivo.read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as error:
        return {}, [f"{ARCHIVO}: no entiendo el archivo ({error})."]
    informe = Informe()
    for clave in [clave for clave in datos if clave != "plano"]:
        informe.errores.append(f"{ARCHIVO}: no conozco «{clave}»; solo puede haber planos, cada uno con [[plano]].")
    tablas = datos.get("plano", [])
    if not isinstance(tablas, list):
        return {}, [f"{ARCHIVO}: cada plano empieza con [[plano]], con dos corchetes."]
    lineas: dict[str, Linea] = {}
    for tabla in tablas:
        linea = _leer_linea(tabla, ids_de_planos, informe)
        if linea is not None:
            lineas[linea.id] = linea
    informe.errores += [
        f"El plano «{id_}» no tiene línea de actuación en {ARCHIVO}: "
        "faltan su pensamiento, su anticipación, su acción y su pausa."
        for id_ in elegidos
        if id_ not in lineas
    ]
    return lineas, informe.errores


def _leer_linea(tabla: object, ids_de_planos: set[str], informe: Informe) -> Linea | None:
    if not isinstance(tabla, dict) or not isinstance(tabla.get("id"), str):
        informe.errores.append(f"{ARCHIVO}: cada [[plano]] tiene su «id», el del plano al que corresponde.")
        return None
    id_ = tabla["id"]
    nombre = f"{ARCHIVO}, plano «{id_}»"
    errores = len(informe.errores)
    if id_ not in ids_de_planos:
        informe.errores.append(f"{nombre}: no hay ningún plano «{id_}» en planos.toml.")
    for clave in [clave for clave in tabla if clave not in _CAMPOS_DEL_PLANO]:
        informe.errores.append(f"{nombre}: no conozco «{clave}».")
    textos = []
    for campo in _CAMPOS_DE_TEXTO:
        texto = tabla.get(campo)
        if not isinstance(texto, str) or not texto.strip():
            informe.errores.append(f"{nombre}: falta «{campo}», una frase que lo cuente.")
        textos.append(texto)
    gestos = _leer_gestos(tabla.get("gestos", []), nombre, informe)
    if len(informe.errores) > errores:
        return None
    return Linea(id_, str(textos[0]), str(textos[1]), str(textos[2]), str(textos[3]), gestos)


def _leer_gestos(lista: object, nombre: str, informe: Informe) -> tuple[Gesto, ...]:
    if not isinstance(lista, list):
        informe.errores.append(f"{nombre}: «gestos» es una lista de tablas con «pieza», «parte», «inicio» y «angulo».")
        return ()
    gestos: list[Gesto] = []
    for tabla in lista:
        gesto = _leer_gesto(tabla, nombre, informe)
        if gesto is None:
            continue
        pisado = next(
            (
                g
                for g in gestos
                if (g.pieza, g.parte) == (gesto.pieza, gesto.parte) and abs(g.inicio - gesto.inicio) < DURACION_DEL_GESTO
            ),
            None,
        )
        if pisado is not None:
            informe.errores.append(
                f"{nombre}: dos gestos de «{gesto.parte}» de «{gesto.pieza}» se pisan "
                f"(empiezan en {pisado.inicio} y en {gesto.inicio}; un gesto dura {DURACION_DEL_GESTO} fotogramas)."
            )
        gestos.append(gesto)
    return tuple(gestos)


def _leer_gesto(tabla: object, nombre: str, informe: Informe) -> Gesto | None:
    if not isinstance(tabla, dict):
        informe.errores.append(f"{nombre}: cada gesto es una tabla con «pieza», «parte», «inicio» y «angulo».")
        return None
    for clave in [clave for clave in tabla if clave not in _CAMPOS_DEL_GESTO]:
        informe.errores.append(f"{nombre}: un gesto no tiene «{clave}»; solo {', '.join(_CAMPOS_DEL_GESTO)}.")
    pieza, parte, inicio, angulo = (tabla.get(c) for c in _CAMPOS_DEL_GESTO)
    if not isinstance(pieza, str) or not pieza.startswith(PERSONAJE_SIN_BOCA):
        informe.errores.append(f"{nombre}: un gesto es de una pieza del Perro, como pieza = \"perro_sentado_frente\".")
        return None
    if parte not in PARTES:
        informe.errores.append(
            f"{nombre}: el gesto de «{pieza}» mueve «{parte}», y solo se mueven {', '.join(PARTES)} (la boca del Perro, nunca)."
        )
        return None
    if not isinstance(inicio, int) or isinstance(inicio, bool) or inicio < 0:
        informe.errores.append(f"{nombre}: el «inicio» del gesto es un fotograma del plano, un entero desde 0.")
        return None
    if isinstance(angulo, bool) or not isinstance(angulo, (int, float)) or angulo == 0 or abs(angulo) > ANGULO_MAXIMO:
        informe.errores.append(f"{nombre}: el «angulo» del gesto son grados distintos de 0 y de hasta {ANGULO_MAXIMO:.0f}.")
        return None
    return Gesto(pieza, parte, inicio, float(angulo))


def _suave(t: float) -> float:
    return t * t * (3 - 2 * t)


def angulo_en(gesto: Gesto, fotograma: int) -> float:
    """El ángulo del gesto en un fotograma del plano: anticipa, actúa, se mantiene y vuelve a 0 sin pasarse."""
    t = fotograma - gesto.inicio
    atras = -RETROCESO * gesto.angulo
    if t < 0:
        return 0.0
    if t < ANTICIPACION:
        return atras * _suave(t / ANTICIPACION)
    t -= ANTICIPACION
    if t < ACCION:
        return atras + (gesto.angulo - atras) * _suave(t / ACCION)
    t -= ACCION
    if t < MANTIENE:
        return gesto.angulo
    t -= MANTIENE
    if t < VUELTA:
        return gesto.angulo * (1 - _suave(t / VUELTA))
    return 0.0


def estados_del_plano(
    plano: PlanoCronometrado, linea: LineaDeTiempo, toma: Toma, actuacion: Linea
) -> tuple[Estados | None, list[str]]:
    """El estado de cada pieza en cada fotograma del plano; None si no cambia nada (el plano es una sola imagen)."""
    duracion = plano.final - plano.inicio
    piezas = {c.pieza: c for c in toma.personajes}
    errores = []
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
    palabras = [
        (p.inicio, p.final)
        for f in linea.frases
        if f.personaje.lower() == PERSONAJE_CON_BOCA
        for p in f.palabras
        if p.acentuada
    ]
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


def _boca(fotograma: int, palabras: list[tuple[int, int]], en_reposo: str) -> str:
    for inicio, final in palabras:
        if inicio <= fotograma < final:
            return BOCAS_ABIERTAS[((fotograma - inicio) // FOTOGRAMAS_POR_BOCA) % len(BOCAS_ABIERTAS)]
    return en_reposo
