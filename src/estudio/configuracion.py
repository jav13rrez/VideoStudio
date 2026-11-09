"""Configuración del estudio: un estudio.toml en la carpeta del episodio o en alguna de encima.

La biblioteca es la carpeta biblioteca/ junto a ese estudio.toml.
El formato está en docs/voces-y-linea-de-tiempo.md; el de la App ([app]), en docs/montaje.md.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TypeGuard

ARCHIVO = "estudio.toml"
BIBLIOTECA = "biblioteca"
_EJEMPLO = {"nombre": "Nombre de la App", "logo": "app/logo.png"}  # para los mensajes de error


@dataclass(frozen=True)
class Voz:
    proveedor: str
    voz: str


@dataclass(frozen=True)
class App:
    """La App a la que invita el CTA; lo que falte, el cierre lo lleva con un marcador."""

    nombre: str | None
    logo: Path | None  # la imagen del logo; en estudio.toml, su ruta desde la carpeta de estudio.toml


@dataclass(frozen=True)
class Configuracion:
    fps: int
    pausa_entre_frases: int  # en fotogramas
    voces: dict[str, Voz]  # por personaje
    biblioteca: Path  # la carpeta de la biblioteca, junto a estudio.toml
    app: App


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
    app = datos.get("app", {})
    if not isinstance(app, dict):
        raise ErrorDeConfiguracion(f"{ARCHIVO}: la App va en su sección, [app], con su nombre y su logo.")
    for clave in ("nombre", "logo"):
        if clave in app and not (isinstance(app[clave], str) and app[clave].strip()):
            raise ErrorDeConfiguracion(
                f'{ARCHIVO}: en [app], el {clave} de la App es un texto entre comillas: {clave} = "{_EJEMPLO[clave]}".'
            )
    logo = archivo.parent / app["logo"] if "logo" in app else None
    return Configuracion(fps, pausa, leidas, archivo.parent / BIBLIOTECA, App(app.get("nombre"), logo))


def _es_entero(valor: object) -> TypeGuard[int]:
    return isinstance(valor, int) and not isinstance(valor, bool)
