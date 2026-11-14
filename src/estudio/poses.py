"""Poses de los personajes: cada una es una ilustración con transparencia y su ficha, en la biblioteca.

La pose se llama <personaje>_<pose> (perro_de_pie) y vive en biblioteca/personajes/<personaje>/poses/, con su ficha
(<pose>.toml) y su ilustración (el PNG que dice la ficha). La silueta y la línea de suelo no se escriben: se miden de la
ilustración con lo opaco. La ficha solo dice lo que no se puede medir: qué partes no cuentan para apoyar en el suelo,
como la cola del Perro, y lo que se mueve (las zonas blandas y el ojo). El formato está en docs/dibujo-2d.md.
"""

import re
import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from estudio.actuacion import PARTES
from estudio.configuracion import BIBLIOTECA

PERSONAJES = "personajes"  # dentro de la biblioteca, una carpeta por personaje
POSES = "poses"  # dentro de la de cada personaje
OPACO = 128  # una transparencia mayor que esta cuenta como silueta; el borde casi transparente de un recorte no cuenta

_NOMBRE = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)+")  # <personaje>_<pose>
_CLAVES = ("ilustracion", "ignora", "asiento", "trasero", "ojo", "zona", "generacion")  # generacion la anota generar-poses
_CLAVES_DE_UNA_PARTE = ("parte", "caja")
_CLAVES_DE_UNA_ZONA = ("parte", "caja", "union", "punta")
Caja = tuple[int, int, int, int]


@dataclass(frozen=True)
class Zona:
    """Una parte blanda de la ilustración (una oreja, la cola): gira con un peso de 0 en la `union` con el cuerpo a 1 en la `punta`."""

    parte: str  # orejas o cola: qué gestos la mueven
    caja: Caja  # fuera de ella no se toca ningún píxel
    union: tuple[float, float]  # en píxeles de la ilustración; es también el pivote del giro
    punta: tuple[float, float]


@dataclass(frozen=True)
class Pose:
    nombre: str
    ilustracion: Image.Image  # RGBA; quien la use no la modifica
    silueta: Caja  # izquierda, arriba, derecha y abajo (el primero de fuera) de lo opaco, en píxeles de la ilustración
    suelo: int  # la fila (la primera de fuera) en la que apoya, sin contar las partes que la ficha manda ignorar
    asiento: float | None = None  # sentada: píxeles que sube el asiento sobre el suelo, en la ilustración
    trasero: float | None = None  # sentada: dónde cae el trasero, como fracción del ancho de la silueta desde la espalda
    zonas: tuple[Zona, ...] = ()  # lo que se puede mover con un gesto
    ojo: Caja | None = None  # la caja del ojo, para el párpado

    @property
    def es_sentada(self) -> bool:
        return self.asiento is not None and self.trasero is not None


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
        f"Pose «{nombre}»: la ficha no conoce «{clave}»; solo lleva {', '.join(_CLAVES)}." for clave in datos if clave not in _CLAVES
    ]
    ilustracion = _leer_ilustracion(nombre, ficha.parent, datos.get("ilustracion"), errores)
    cajas = _leer_partes_que_se_ignoran(nombre, datos.get("ignora", []), ilustracion, errores)
    zonas = _leer_zonas(nombre, datos.get("zona", []), ilustracion, errores)
    ojo = _leer_ojo(nombre, datos.get("ojo"), ilustracion, errores)
    if errores or ilustracion is None:
        return None, errores
    pose, errores = _medir(nombre, ilustracion, cajas)
    if pose is None:
        return None, errores
    asiento, trasero, errores = _leer_medidas_de_sentada(pose, datos)
    if errores:
        return None, errores
    return replace(pose, asiento=asiento, trasero=trasero, zonas=zonas, ojo=ojo), []


def _es_numero(valor: object) -> bool:
    return isinstance(valor, int | float) and not isinstance(valor, bool)


def _leer_medidas_de_sentada(pose: Pose, datos: dict[str, Any]) -> tuple[float | None, float | None, list[str]]:
    """El asiento y el trasero de una pose sentada. Van los dos o ninguno; sin ellos la pose apoya en el suelo."""
    nombre = pose.nombre
    asiento, trasero = datos.get("asiento"), datos.get("trasero")
    if asiento is None and trasero is None:
        return None, None, []
    errores = []
    if asiento is None:
        errores.append(f"Pose «{nombre}»: la ficha lleva «trasero» pero le falta «asiento», lo que sube el asiento sobre las suelas.")
    elif not _es_numero(asiento) or not 0 < asiento < pose.suelo - pose.silueta[1]:
        errores.append(
            f"Pose «{nombre}»: «asiento» son los píxeles que sube el asiento sobre las suelas: un número mayor que 0 "
            f"y menor que lo que mide la pose de alto sobre el suelo ({pose.suelo - pose.silueta[1]})."
        )
    if trasero is None:
        errores.append(f"Pose «{nombre}»: la ficha lleva «asiento» pero le falta «trasero», dónde cae el trasero.")
    elif not _es_numero(trasero) or not 0 < trasero < 1:
        errores.append(
            f"Pose «{nombre}»: «trasero» es la fracción del ancho de la silueta, contada desde la espalda, "
            "en la que cae el trasero: un número entre 0 y 1, sin llegar a ellos."
        )
    return (None, None, errores) if errores else (float(asiento), float(trasero), [])  # type: ignore[arg-type]


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
    parte = tabla.get("parte")
    if not isinstance(parte, str) or not parte.strip():
        errores.append(f'Pose «{nombre}»: falta la «parte» que se ignora, como parte = "cola".')
        return None
    return _leer_caja(nombre, f"de la parte «{parte}»", tabla.get("caja"), ilustracion, errores)


def _leer_caja(nombre: str, de_que: str, caja: object, ilustracion: Image.Image | None, errores: list[str]) -> Caja | None:
    """Una caja [x0, y0, x1, y1] en píxeles de la ilustración, que tiene que caer dentro de ella."""
    if not (
        isinstance(caja, list) and len(caja) == 4 and all(isinstance(v, int) and not isinstance(v, bool) for v in caja)
    ):
        errores.append(f"Pose «{nombre}»: la caja {de_que} son cuatro números enteros, como caja = [x0, y0, x1, y1].")
        return None
    x0, y0, x1, y1 = caja
    if ilustracion is not None and not (0 <= x0 < x1 <= ilustracion.width and 0 <= y0 < y1 <= ilustracion.height):
        errores.append(
            f"Pose «{nombre}»: la caja {de_que} tiene que caer dentro de la ilustración, "
            f"que mide {ilustracion.width}x{ilustracion.height}, y tener x0 < x1 e y0 < y1."
        )
        return None
    return x0, y0, x1, y1


def _leer_zonas(nombre: str, valor: object, ilustracion: Image.Image | None, errores: list[str]) -> tuple[Zona, ...]:
    if not isinstance(valor, list):
        errores.append(f"Pose «{nombre}»: «zona» es una lista de zonas blandas, cada una con [[zona]].")
        return ()
    zonas = [zona for tabla in valor if (zona := _leer_zona(nombre, tabla, ilustracion, errores)) is not None]
    return tuple(zonas)


def _leer_zona(nombre: str, tabla: object, ilustracion: Image.Image | None, errores: list[str]) -> Zona | None:
    if not isinstance(tabla, dict):
        errores.append(f"Pose «{nombre}»: cada zona blanda es una tabla con su parte, su caja, su unión y su punta, bajo [[zona]].")
        return None
    antes = len(errores)
    errores += [
        f"Pose «{nombre}»: una zona no tiene «{clave}»; solo {', '.join(_CLAVES_DE_UNA_ZONA)}."
        for clave in tabla
        if clave not in _CLAVES_DE_UNA_ZONA
    ]
    parte = tabla.get("parte")
    if parte == "boca":
        errores.append(f"Pose «{nombre}»: una zona no puede ser la boca: la boca del Perro no se mueve nunca.")
    elif parte not in PARTES:
        errores.append(f"Pose «{nombre}»: la zona «{parte}» no se mueve; solo se mueven {', '.join(PARTES)}.")
    caja = _leer_caja(nombre, f"de la zona «{parte}»", tabla.get("caja"), ilustracion, errores)
    puntos = [_leer_punto(nombre, parte, campo, tabla.get(campo), caja, errores) for campo in ("union", "punta")]
    union, punta = puntos
    if union is not None and punta is not None and union == punta:
        errores.append(f"Pose «{nombre}»: en la zona «{parte}» la «punta» no puede ser el mismo punto que la «union»: marcan hacia dónde crece el peso.")
    if len(errores) > antes or caja is None or union is None or punta is None or not isinstance(parte, str):
        return None
    return Zona(parte, caja, union, punta)


def _leer_punto(
    nombre: str, parte: object, campo: str, valor: object, caja: Caja | None, errores: list[str]
) -> tuple[float, float] | None:
    if valor is None:
        errores.append(f"Pose «{nombre}»: a la zona «{parte}» le falta la «{campo}», un punto como {campo} = [x, y].")
        return None
    if not (isinstance(valor, list) and len(valor) == 2 and all(_es_numero(v) for v in valor)):
        errores.append(f"Pose «{nombre}»: la «{campo}» de la zona «{parte}» son dos números, como {campo} = [x, y].")
        return None
    x, y = float(valor[0]), float(valor[1])
    if caja is not None and not (caja[0] <= x <= caja[2] and caja[1] <= y <= caja[3]):
        errores.append(f"Pose «{nombre}»: la «{campo}» de la zona «{parte}» tiene que caer dentro de la caja de la zona.")
        return None
    return x, y


def _leer_ojo(nombre: str, valor: object, ilustracion: Image.Image | None, errores: list[str]) -> Caja | None:
    """La caja del ojo, para el párpado; sin ella, la pose no parpadea."""
    return None if valor is None else _leer_caja(nombre, "del ojo (ojo)", valor, ilustracion, errores)


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
