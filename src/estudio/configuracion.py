"""Configuración del estudio: un estudio.toml en la carpeta del episodio o en alguna de encima.

La biblioteca es la carpeta biblioteca/ junto a ese estudio.toml, y la documentación de la App, la carpeta app/.
El formato está en docs/voces-y-linea-de-tiempo.md.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TypeGuard

from estudio import app

ARCHIVO = "estudio.toml"
BIBLIOTECA = "biblioteca"


@dataclass(frozen=True)
class Voz:
    proveedor: str
    voz: str


@dataclass(frozen=True)
class Configuracion:
    fps: int
    pausa_entre_frases: int  # en fotogramas
    voces: dict[str, Voz]  # por personaje
    biblioteca: Path  # la carpeta de la biblioteca, junto a estudio.toml
    app: Path  # la carpeta con la documentación de la App, junto a estudio.toml
    blender: str | None = None  # la ruta del ejecutable de Blender, si estudio.toml la dice


class ErrorDeConfiguracion(Exception):
    pass


def leer_configuracion(carpeta: Path) -> Configuracion:
    """La primera configuración que se encuentra subiendo desde la carpeta del episodio."""
    carpeta = carpeta.resolve()
    archivo = next((d / ARCHIVO for d in (carpeta, *carpeta.parents) if (d / ARCHIVO).is_file()), None)
    if archivo is None:
        raise ErrorDeConfiguracion(
            f"No encuentro la configuración del estudio: tiene que haber un {ARCHIVO} "
            "en la carpeta del episodio o en alguna de las de encima."
        )
    try:
        datos = tomllib.loads(archivo.read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as error:
        raise ErrorDeConfiguracion(f"{ARCHIVO}: no entiendo el archivo ({error}).") from error

    fps = datos.get("fps")
    if not _es_entero(fps) or fps < 1:
        raise ErrorDeConfiguracion(f"{ARCHIVO}: falta «fps» o no es un número entero, como fps = 30.")
    pausa = datos.get("pausa_entre_frases")
    if not _es_entero(pausa) or pausa < 0:
        raise ErrorDeConfiguracion(
            f"{ARCHIVO}: falta «pausa_entre_frases» o no es un número entero de fotogramas, "
            "como pausa_entre_frases = 9."
        )
    voces = datos.get("voces")
    if not isinstance(voces, dict):
        raise ErrorDeConfiguracion(f"{ARCHIVO}: falta la sección [voces] con la voz de cada personaje.")
    leidas = {}
    for personaje, voz in voces.items():
        if not (isinstance(voz, dict) and isinstance(voz.get("proveedor"), str) and isinstance(voz.get("voz"), str)):
            raise ErrorDeConfiguracion(
                f'{ARCHIVO}: la voz de «{personaje}» se escribe {personaje} = {{ proveedor = "falso", voz = "…" }}.'
            )
        leidas[personaje] = Voz(voz["proveedor"], voz["voz"])
    blender = datos.get("blender")
    if blender is not None and not isinstance(blender, str):
        raise ErrorDeConfiguracion(
            f'{ARCHIVO}: «blender» es la ruta del ejecutable de Blender, como blender = "/ruta/a/blender.exe".'
        )
    return Configuracion(fps, pausa, leidas, archivo.parent / BIBLIOTECA, archivo.parent / app.CARPETA, blender)


def _es_entero(valor: object) -> TypeGuard[int]:
    return isinstance(valor, int) and not isinstance(valor, bool)
