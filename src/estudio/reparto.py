"""Reparto: qué poses lleva cada plano, en reparto.toml junto a planos.toml.

Si el episodio tiene este archivo, sus planos se dibujan en 2D; si no, se renderizan con Blender desde tomas.toml.
El formato está en docs/dibujo-2d.md.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

ARCHIVO = "reparto.toml"
_CAMPOS_DEL_PLANO = ("id", "personajes")
_CAMPOS_DEL_PERSONAJE = ("pose",)


@dataclass(frozen=True)
class Reparto:
    id: str
    poses: tuple[str, ...]  # una por personaje, en el orden en que se dibujan


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
        f"{nombre}: no conozco «{clave}»; un plano tiene {' y '.join(_CAMPOS_DEL_PLANO)}."
        for clave in tabla
        if clave not in _CAMPOS_DEL_PLANO
    ]
    personajes = tabla.get("personajes", [])
    if not isinstance(personajes, list):
        errores.append(f'{nombre}: «personajes» es una lista, como personajes = [{{ pose = "perro_de_pie" }}].')
        return None
    poses = [pose for personaje in personajes if (pose := _leer_personaje(nombre, personaje, errores)) is not None]
    return Reparto(id_, tuple(poses)) if len(errores) == antes else None


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
