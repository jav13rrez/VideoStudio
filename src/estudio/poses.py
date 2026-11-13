"""Poses de los personajes: cada una es una ilustración con transparencia y su ficha, en la biblioteca.

La pose se llama <personaje>_<pose> (perro_de_pie) y vive en biblioteca/personajes/<personaje>/poses/, con su ficha
(<pose>.toml) y su ilustración (el PNG que dice la ficha). La silueta y la línea de suelo no se escriben: se miden de la
ilustración con lo opaco. La ficha solo dice lo que no se puede medir: qué partes no cuentan para apoyar en el suelo,
como la cola del Perro. El formato está en docs/dibujo-2d.md.
"""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from estudio.configuracion import BIBLIOTECA

PERSONAJES = "personajes"  # dentro de la biblioteca, una carpeta por personaje
POSES = "poses"  # dentro de la de cada personaje
OPACO = 128  # una transparencia mayor que esta cuenta como silueta; el borde casi transparente de un recorte no cuenta

_NOMBRE = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)+")  # <personaje>_<pose>
_CLAVES = ("ilustracion", "ignora")
_CLAVES_DE_UNA_PARTE = ("parte", "caja")
Caja = tuple[int, int, int, int]


@dataclass(frozen=True)
class Pose:
    nombre: str
    ilustracion: Image.Image  # RGBA; quien la use no la modifica
    silueta: Caja  # izquierda, arriba, derecha y abajo (el primero de fuera) de lo opaco, en píxeles de la ilustración
    suelo: int  # la fila (la primera de fuera) en la que apoya, sin contar las partes que la ficha manda ignorar


def cargar_pose(biblioteca: Path, nombre: str) -> tuple[Pose | None, list[str]]:
    """La pose de la biblioteca con ese nombre, o los errores que impiden usarla."""
    if not _NOMBRE.fullmatch(nombre):
        return None, [
            f"«{nombre}» no es un nombre de pose: va como <personaje>_<pose>, con minúsculas, números y guiones bajos, "
            "como perro_de_pie."
        ]
    personaje = nombre.split("_")[0]
    ficha = biblioteca / PERSONAJES / personaje / POSES / f"{nombre}.toml"
    if not ficha.is_file():
        return None, [
            f"Pose «{nombre}»: no encuentro su ficha, {BIBLIOTECA}/{PERSONAJES}/{personaje}/{POSES}/{nombre}.toml, "
            "con su ilustración y las partes que no cuentan al apoyar."
        ]
    try:
        datos: dict[str, Any] = tomllib.loads(ficha.read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as error:
        return None, [f"Pose «{nombre}»: no entiendo su ficha ({error})."]
    errores = [
        f"Pose «{nombre}»: la ficha no conoce «{clave}»; solo lleva ilustracion e ignora." for clave in datos if clave not in _CLAVES
    ]
    ilustracion = _leer_ilustracion(nombre, ficha.parent, datos.get("ilustracion"), errores)
    cajas = _leer_partes_que_se_ignoran(nombre, datos.get("ignora", []), ilustracion, errores)
    if errores or ilustracion is None:
        return None, errores
    return _medir(nombre, ilustracion, cajas)


def _leer_ilustracion(nombre: str, carpeta: Path, valor: object, errores: list[str]) -> Image.Image | None:
    if not isinstance(valor, str) or not valor.strip():
        errores.append(
            f'Pose «{nombre}»: falta «ilustracion», el PNG que va junto a la ficha, como ilustracion = "{nombre}.png".'
        )
        return None
    if Path(valor).name != valor:
        errores.append(f"Pose «{nombre}»: «ilustracion» es el nombre de un PNG junto a la ficha, sin carpetas.")
        return None
    archivo = carpeta / valor
    if not archivo.is_file():
        errores.append(f"Pose «{nombre}»: no encuentro la ilustración «{valor}» junto a su ficha.")
        return None
    try:
        with Image.open(archivo) as abierta:
            return abierta.convert("RGBA")
    except OSError:
        errores.append(f"Pose «{nombre}»: no puedo leer la ilustración «{valor}»; tiene que ser un PNG con transparencia.")
        return None


def _leer_partes_que_se_ignoran(nombre: str, valor: object, ilustracion: Image.Image | None, errores: list[str]) -> list[Caja]:
    if not isinstance(valor, list):
        errores.append(f"Pose «{nombre}»: «ignora» es una lista de partes, cada una con su parte y su caja.")
        return []
    cajas = []
    for tabla in valor:
        caja = _leer_parte(nombre, tabla, ilustracion, errores)
        if caja is not None:
            cajas.append(caja)
    return cajas


def _leer_parte(nombre: str, tabla: object, ilustracion: Image.Image | None, errores: list[str]) -> Caja | None:
    if not isinstance(tabla, dict):
        errores.append(f"Pose «{nombre}»: cada parte que se ignora es una tabla con su parte y su caja, bajo [[ignora]].")
        return None
    for clave in [clave for clave in tabla if clave not in _CLAVES_DE_UNA_PARTE]:
        errores.append(f"Pose «{nombre}»: una parte que se ignora no tiene «{clave}»; solo parte y caja.")
    parte, caja = tabla.get("parte"), tabla.get("caja")
    if not isinstance(parte, str) or not parte.strip():
        errores.append(f'Pose «{nombre}»: falta la «parte» que se ignora, como parte = "cola".')
        return None
    if not (
        isinstance(caja, list) and len(caja) == 4 and all(isinstance(v, int) and not isinstance(v, bool) for v in caja)
    ):
        errores.append(f"Pose «{nombre}»: la caja de la parte «{parte}» son cuatro números enteros, como caja = [x0, y0, x1, y1].")
        return None
    x0, y0, x1, y1 = caja
    if ilustracion is not None and not (0 <= x0 < x1 <= ilustracion.width and 0 <= y0 < y1 <= ilustracion.height):
        errores.append(
            f"Pose «{nombre}»: la caja de la parte «{parte}» tiene que caer dentro de la ilustración, "
            f"que mide {ilustracion.width}x{ilustracion.height}, y tener x0 < x1 e y0 < y1."
        )
        return None
    return x0, y0, x1, y1


def _medir(nombre: str, ilustracion: Image.Image, ignoradas: list[Caja]) -> tuple[Pose | None, list[str]]:
    """La silueta y la fila de apoyo de la ilustración, con lo opaco."""
    opaco = np.asarray(ilustracion.getchannel("A")) > OPACO
    if not opaco.any():
        return None, [f"Pose «{nombre}»: la ilustración no tiene nada opaco (transparencia mayor que {OPACO} de 255): no hay silueta."]
    filas, columnas = np.where(opaco)
    silueta = (int(columnas.min()), int(filas.min()), int(columnas.max()) + 1, int(filas.max()) + 1)
    apoya = opaco.copy()
    for x0, y0, x1, y1 in ignoradas:
        apoya[y0:y1, x0:x1] = False
    if not apoya.any():
        return None, [f"Pose «{nombre}»: todo lo opaco está dentro de partes que se ignoran, así que nada apoya en el suelo."]
    return Pose(nombre, ilustracion, silueta, int(np.where(apoya)[0].max()) + 1), []
