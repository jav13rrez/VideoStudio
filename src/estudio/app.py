"""La documentación de la App: la carpeta app/ junto a estudio.toml, igual que la biblioteca.

En app/app.toml va lo que lee la herramienta: el nombre y el logo de la App, que salen en el cierre del CTA,
y el enlace a la App, del que salen los enlaces con seguimiento de la hoja de publicación.
El resto de la documentación de la App, para el agente, va en esa misma carpeta. El formato está en
docs/montaje.md, "El cierre del CTA", y en docs/hoja-de-publicacion.md.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from estudio.guion import Informe

CARPETA = "app"
ARCHIVO = "app.toml"
NOMBRE_PROVISIONAL = "Nombre de la App"
_EJEMPLOS = {"nombre": NOMBRE_PROVISIONAL, "logo": "logo.png", "enlace": "https://…"}


@dataclass(frozen=True)
class App:
    nombre: str  # NOMBRE_PROVISIONAL mientras falte
    logo: Path | None  # la imagen del logo; None mientras falte, y el cierre lleva un marcador
    enlace: str | None  # el enlace base a la App; sin él no hay hoja de publicación


def leer_app(carpeta: Path) -> tuple[App, Informe]:
    """La App que describe la carpeta app/, con lo que le falta (avisos) y lo que no se entiende (errores)."""
    informe = Informe()
    donde = f"{CARPETA}/{ARCHIVO}"
    archivo = carpeta / ARCHIVO
    datos: dict[str, Any] = {}
    if archivo.is_file():
        try:
            datos = tomllib.loads(archivo.read_text(encoding="utf-8-sig"))
        except tomllib.TOMLDecodeError as error:
            informe.errores.append(f"{donde}: no entiendo el archivo ({error}).")
    for clave, ejemplo in _EJEMPLOS.items():
        if clave in datos and not (isinstance(datos[clave], str) and datos[clave].strip()):
            informe.errores.append(f'{donde}: «{clave}» es un texto entre comillas, como {clave} = "{ejemplo}".')
    if informe.errores:
        return App(NOMBRE_PROVISIONAL, None, None), informe

    nombre = datos.get("nombre", NOMBRE_PROVISIONAL)
    if "nombre" not in datos:
        informe.avisos.append(
            f"Falta el nombre de la App (nombre, en {donde} junto a estudio.toml); "
            f"el cierre del CTA lleva «{NOMBRE_PROVISIONAL}» en su lugar."
        )
    logo = carpeta / datos["logo"] if "logo" in datos else None
    if logo is None:
        informe.avisos.append(
            f"Falta el logo de la App (logo, en {donde} junto a estudio.toml); "
            "el cierre del CTA lleva un marcador en su lugar."
        )
    elif not logo.is_file():
        informe.avisos.append(
            f"{donde}: el logo de la App, «{datos['logo']}», no está en la carpeta {CARPETA}/; "
            "el cierre del CTA lleva un marcador en su lugar."
        )
        logo = None
    return App(nombre, logo, datos.get("enlace")), informe
