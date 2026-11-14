"""Reparto: qué poses lleva cada plano y cómo se mueve su cámara, en reparto.toml junto a planos.toml.

Si el episodio tiene este archivo, sus planos se dibujan en 2D; si no, se renderizan con Blender desde tomas.toml.
El formato está en docs/dibujo-2d.md.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from estudio.camara_2d import VISTA_ENTERA, Vista

ARCHIVO = "reparto.toml"
_CAMPOS_DEL_PLANO = ("id", "personajes", "desde", "hasta")
_CAMPOS_DEL_PERSONAJE = ("pose",)
_CAMPOS_DE_LA_VISTA = ("ancho", "centro")


@dataclass(frozen=True)
class Reparto:
    id: str
    poses: tuple[str, ...]  # una por personaje, en el orden en que se dibujan
    desde: Vista | None = None  # la vista al empezar el plano; sin ella, el escenario entero
    hasta: Vista | None = None  # la vista al acabar: solo en planos con cámara en movimiento


def hay_reparto(carpeta: Path) -> bool:
    return (carpeta / ARCHIVO).is_file()


def leer_reparto(carpeta: Path, ids_de_planos: set[str]) -> tuple[dict[str, Reparto], list[str]]:
    """El reparto de cada plano por su id, y los errores. Que las poses existan lo comprueba quien las dibuja."""
    try:
        datos = tomllib.loads((carpeta / ARCHIVO).read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as error:
        return {}, [f"{ARCHIVO}: no entiendo el archivo ({error})."]
    errores = [
        f"{ARCHIVO}: no conozco «{clave}»; solo puede haber planos, cada uno con [[plano]]." for clave in datos if clave != "plano"
    ]
    tablas = datos.get("plano", [])
    if not isinstance(tablas, list):
        return {}, [f"{ARCHIVO}: cada plano empieza con [[plano]], con dos corchetes."]
    repartos: dict[str, Reparto] = {}
    for tabla in tablas:
        reparto = _leer_plano(tabla, ids_de_planos, repartos, errores)
        if reparto is not None:
            repartos[reparto.id] = reparto
    return repartos, errores


def _leer_plano(tabla: object, ids_de_planos: set[str], leidos: dict[str, Reparto], errores: list[str]) -> Reparto | None:
    if not isinstance(tabla, dict) or not isinstance(tabla.get("id"), str):
        errores.append(f"{ARCHIVO}: cada [[plano]] tiene su «id», el del plano al que corresponde.")
        return None
    id_ = tabla["id"]
    nombre = f"{ARCHIVO}, plano «{id_}»"
    antes = len(errores)
    if id_ not in ids_de_planos:
        errores.append(f"{ARCHIVO}: el plano «{id_}» no está en planos.toml.")
    elif id_ in leidos:
        errores.append(f"{nombre}: aparece dos veces; cada plano tiene un solo reparto.")
    errores += [
        f"{nombre}: no conozco «{clave}»; un plano tiene {', '.join(_CAMPOS_DEL_PLANO)}."
        for clave in tabla
        if clave not in _CAMPOS_DEL_PLANO
    ]
    personajes = tabla.get("personajes", [])
    if not isinstance(personajes, list):
        errores.append(f'{nombre}: «personajes» es una lista, como personajes = [{{ pose = "perro_de_pie" }}].')
        return None
    poses = [pose for personaje in personajes if (pose := _leer_personaje(nombre, personaje, errores)) is not None]
    desde = _leer_vista(nombre, "desde", tabla, None, errores)
    hasta = _leer_vista(nombre, "hasta", tabla, desde or VISTA_ENTERA, errores)
    return Reparto(id_, tuple(poses), desde, hasta) if len(errores) == antes else None


def _leer_vista(nombre: str, clave: str, tabla: dict[str, Any], base: Vista | None, errores: list[str]) -> Vista | None:
    """La vista de `desde` o `hasta`; lo que no se escribe sale de `base` (la vista entera, o la de `desde`)."""
    if clave not in tabla:
        return None
    vista = tabla[clave]
    if not isinstance(vista, dict):
        errores.append(f"{nombre}: «{clave}» es una tabla, como {clave} = {{ ancho = 0.8, centro = [0.5, 0.5] }}.")
        return None
    antes = len(errores)
    errores += [
        f"{nombre}: «{clave}» no tiene «{campo}»; solo {' y '.join(_CAMPOS_DE_LA_VISTA)}." for campo in vista if campo not in _CAMPOS_DE_LA_VISTA
    ]
    base = base or VISTA_ENTERA
    ancho, centro = vista.get("ancho", base.ancho), vista.get("centro", list(base.centro))
    if not _es_numero(ancho) or ancho <= 0:
        errores.append(f"{nombre}: el «ancho» de «{clave}» es una fracción del escenario mayor que 0, como ancho = 0.8.")
    if not (isinstance(centro, list) and len(centro) == 2 and all(_es_numero(c) for c in centro)):
        errores.append(f"{nombre}: el «centro» de «{clave}» son dos números, x e y como fracción del escenario, como centro = [0.5, 0.5].")
    if len(errores) > antes:
        return None
    return Vista(float(ancho), (float(centro[0]), float(centro[1])))


def _es_numero(valor: object) -> bool:
    return isinstance(valor, int | float) and not isinstance(valor, bool)


def _leer_personaje(nombre: str, personaje: object, errores: list[str]) -> str | None:
    if not isinstance(personaje, dict):
        errores.append(f'{nombre}: cada personaje es una tabla con su pose, como {{ pose = "perro_de_pie" }}.')
        return None
    errores += [
        f"{nombre}: un personaje no tiene «{clave}»; solo lleva {' y '.join(_CAMPOS_DEL_PERSONAJE)}."
        for clave in personaje
        if clave not in _CAMPOS_DEL_PERSONAJE
    ]
    pose = personaje.get("pose")
    if not isinstance(pose, str) or not pose.strip():
        errores.append(f'{nombre}: a un personaje le falta su «pose», como {{ pose = "perro_de_pie" }}.')
        return None
    return pose
