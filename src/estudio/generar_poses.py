"""generar-poses: genera la ilustración de una pose a partir de la hoja de su personaje.

La pose se llama <personaje>_<postura> (tutor_sentado). La hoja con la vista de perfil que necesita está en
biblioteca/personajes/_trabajo/hojas/<pose>_perfil_izq.png. La orden construye el texto con una plantilla fija del estilo
de la casa, enseña cuántas imágenes va a generar y cuánto costarían, y solo genera con una confirmación explícita.
Deja la ilustración y su ficha, y anota en la ficha, en [generacion], el modelo, el texto y la fecha.
El formato está en docs/dibujo-2d.md.
"""

import json
import os
import re
import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

from PIL import Image, ImageDraw

from estudio.configuracion import Configuracion
from estudio.poses import PERSONAJES, POSES
from estudio.voces import leer_clave

HOJAS = Path(PERSONAJES) / "_trabajo" / "hojas"  # dentro de la biblioteca
VISTA = "perfil_izq"  # la vista de la hoja que necesita toda pose: hoy todas son de perfil
IMAGENES_POR_POSE = 1
VARIABLE_DE_LA_CLAVE_DE_FAL = "FAL_KEY"

# La plantilla del texto: el estilo es el mismo para todos; cambian el sujeto, la postura y un detalle del personaje.
_ESTILO = (
    "Style: clean flat vector illustration, bold dark outline of uniform thickness, simple cel shading with two tones, "
    "no photographic fur or skin texture, big readable shapes. Plain flat light-gray background, full body visible."
)
_SUJETOS = {
    "tutor": "man (same face, same hair, same clothes and colors, same proportions)",
    "perro": "dog (same breed, same black-and-white markings and mottled face, same proportions)",
}
_DETALLES = {"tutor": "", "perro": ", with the tail and both ears clearly visible and distinct"}
_POSTURAS = {
    "de_pie": "a standing profile pose",
    "sentado": "a sitting profile pose",
    "tumbado": "a lying down sphinx profile pose, front paws stretched forward, head up",
}
_PROVEEDORES = ("falso", "fal")


class ErrorDeGeneracion(Exception):
    pass


class ProveedorDeIlustracion(Protocol):
    modelo: str
    coste_por_imagen: float  # en euros

    def generar(self, texto: str, hojas: tuple[Path, ...], destino: Path) -> None:
        """Escribe en `destino` un PNG con transparencia: la pose, sin fondo."""
        ...


class ProveedorFalso:
    """Ilustración de prueba: una elipse sobre fondo transparente. No gasta ni pide clave."""

    modelo = "falso"
    coste_por_imagen = 0.0

    def generar(self, texto: str, hojas: tuple[Path, ...], destino: Path) -> None:
        imagen = Image.new("RGBA", (400, 300), (0, 0, 0, 0))
        ImageDraw.Draw(imagen).ellipse((80, 60, 320, 270), fill=(120, 150, 200, 255), outline=(38, 26, 32, 255), width=6)
        imagen.save(destino, format="PNG")


@dataclass(frozen=True)
class Plan:
    """Lo que la orden va a hacer, ya comprobado."""

    pose: str
    texto: str
    hojas: tuple[Path, ...]
    ilustracion: Path
    ficha: Path
    proveedor: ProveedorDeIlustracion

    @property
    def imagenes(self) -> int:
        return IMAGENES_POR_POSE

    @property
    def coste(self) -> float:
        return self.imagenes * self.proveedor.coste_por_imagen


def texto_de_la_pose(personaje: str, postura: str) -> str:
    """El texto que se manda al proveedor: la plantilla fija del estilo de la casa."""
    return (
        f"Redraw this exact {_SUJETOS[personaje]} as a 2D cartoon character for an animated series, "
        f"in {_POSTURAS[postura]}, facing left{_DETALLES[personaje]}. No furniture. {_ESTILO}"
    )


def preparar(
    carpeta: Path, configuracion: Configuracion, pose: str, proveedor: str, reemplazar: bool
) -> tuple[Plan | None, list[str]]:
    """Comprueba la pose, su hoja, el proveedor y lo que ya hay, sin escribir nada."""
    personaje, _, postura = pose.partition("_")
    errores = _errores_de_la_pose(pose, personaje, postura)
    if errores:
        return None, errores
    hoja = configuracion.biblioteca / HOJAS / f"{pose}_{VISTA}.png"
    if not hoja.is_file():
        errores.append(
            f"A la hoja de «{personaje}» le falta la vista de perfil de «{pose}»: "
            f"pon {hoja.relative_to(configuracion.biblioteca.parent)} (un PNG con la pose de perfil, mirando a la izquierda)."
        )
    elegido, errores_del_proveedor = _elegir_proveedor(proveedor, carpeta)
    errores += errores_del_proveedor
    carpeta_de_poses = configuracion.biblioteca / PERSONAJES / personaje / POSES
    ficha = carpeta_de_poses / f"{pose}.toml"
    ilustracion, errores_de_la_ficha = _ilustracion_de(ficha, carpeta_de_poses, pose)
    errores += errores_de_la_ficha
    if not errores_de_la_ficha and ilustracion.exists() and not reemplazar:
        errores.append(
            f"La pose «{pose}» ya tiene ilustración ({ilustracion.name}) y puede que el creador la haya aprobado. "
            "Si quieres volver a generarla, repite la orden con --reemplazar."
        )
    if errores or elegido is None:
        return None, errores
    return Plan(pose, texto_de_la_pose(personaje, postura), (hoja,), ilustracion, ficha, elegido), []


def generar(plan: Plan, hoy: date | None = None) -> list[str]:
    """Genera la ilustración y anota en su ficha el modelo, el texto y la fecha."""
    plan.ilustracion.parent.mkdir(parents=True, exist_ok=True)
    nueva = plan.ilustracion.with_name(plan.ilustracion.name + ".nueva")
    try:
        plan.proveedor.generar(plan.texto, plan.hojas, nueva)
        os.replace(nueva, plan.ilustracion)  # una generación que falla no estropea la ilustración anterior
    except (ErrorDeGeneracion, OSError) as error:
        nueva.unlink(missing_ok=True)
        return [f"No se ha podido generar «{plan.pose}»: {error}"]
    actual = plan.ficha.read_text(encoding="utf-8-sig") if plan.ficha.is_file() else f'ilustracion = "{plan.ilustracion.name}"\n'
    fecha = (hoy or date.today()).isoformat()
    plan.ficha.write_text(_ficha_con_generacion(actual, plan.proveedor.modelo, plan.texto, fecha), encoding="utf-8")
    return []


def _errores_de_la_pose(pose: str, personaje: str, postura: str) -> list[str]:
    if not postura:
        return [f"«{pose}» no es una pose: va como <personaje>_<postura>, como tutor_sentado."]
    if personaje not in _SUJETOS:
        return [f"No conozco al personaje «{personaje}»: los que hay son {', '.join(_SUJETOS)}."]
    if postura not in _POSTURAS:
        return [f"No conozco la postura «{postura}»: las que hay son {', '.join(_POSTURAS)}."]
    return []


def _elegir_proveedor(nombre: str, desde: Path) -> tuple[ProveedorDeIlustracion | None, list[str]]:
    if nombre == "falso":
        return ProveedorFalso(), []
    if nombre != "fal":
        return None, [f"No conozco el proveedor «{nombre}»: los que hay son {', '.join(_PROVEEDORES)}."]
    if not leer_clave(VARIABLE_DE_LA_CLAVE_DE_FAL, desde):
        return None, [
            f"Falta la clave de Fal: pégala en el archivo .env del estudio, en la línea "
            f"{VARIABLE_DE_LA_CLAVE_DE_FAL}=… (la lista está en .env.example)."
        ]
    return None, ["El proveedor «fal» todavía no genera: se conecta con Fal en el ticket 08 de estudio-2d. Usa «falso»."]


def _ilustracion_de(ficha: Path, carpeta_de_poses: Path, pose: str) -> tuple[Path, list[str]]:
    """La ilustración que dice la ficha, si ya hay ficha, o <pose>.png."""
    if not ficha.is_file():
        return carpeta_de_poses / f"{pose}.png", []
    try:
        nombre = tomllib.loads(ficha.read_text(encoding="utf-8-sig")).get("ilustracion")
    except tomllib.TOMLDecodeError as error:
        return carpeta_de_poses / f"{pose}.png", [f"Pose «{pose}»: no entiendo su ficha ({error})."]
    if not isinstance(nombre, str) or Path(nombre).name != nombre:
        return carpeta_de_poses / f"{pose}.png", [
            f"Pose «{pose}»: su ficha tiene que decir en «ilustracion» el nombre de un PNG junto a ella, sin carpetas."
        ]
    return carpeta_de_poses / nombre, []


def _cadena(valor: str) -> str:
    """Una cadena de TOML se escribe igual que una de JSON."""
    return json.dumps(valor, ensure_ascii=False)


def _ficha_con_generacion(actual: str, modelo: str, texto: str, fecha: str) -> str:
    """La ficha con su tabla [generacion] al final y todo lo demás como estaba."""
    conservadas: list[str] = []
    en_la_tabla = False
    for linea in actual.splitlines():
        if re.fullmatch(r"\s*\[generacion\]\s*", linea):
            en_la_tabla = True
        elif en_la_tabla and linea.lstrip().startswith("["):
            en_la_tabla = False
        if not en_la_tabla:
            conservadas.append(linea)
    return (
        "\n".join(conservadas).rstrip()
        + f"\n\n[generacion]\nmodelo = {_cadena(modelo)}\ntexto = {_cadena(texto)}\nfecha = {_cadena(fecha)}\n"
    )
