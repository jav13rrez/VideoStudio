"""Ayudas compartidas por los tests: todos entran por la herramienta del estudio."""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

EPISODIOS = Path(__file__).parent / "episodios"
EJEMPLO = EPISODIOS / "001-olfato"
# La configuración del estudio para los tests, aparte de la del estudio real.
CONFIGURACION = EPISODIOS / "estudio.toml"
# La biblioteca de los tests, junto a su configuración, como la del estudio real.
BIBLIOTECA = EPISODIOS / "biblioteca"
FPS = 30  # los de la configuración de los tests


@dataclass
class Resultado:
    codigo: int
    salida: str
    errores: list[str]
    avisos: list[str]


# Ejecuta una orden de la herramienta sobre una carpeta de episodio: estudio("cronometrar", carpeta).
Estudio = Callable[[str, Path], Resultado]


def leer_salida(codigo: int, salida: str) -> Resultado:
    """Separa la salida de la herramienta en sus listas de errores y avisos."""
    errores: list[str] = []
    avisos: list[str] = []
    lista: list[str] | None = None
    for linea in salida.splitlines():
        if linea.startswith("Errores"):
            lista = errores
        elif linea.startswith("Avisos"):
            lista = avisos
        elif linea.startswith("  - ") and lista is not None:
            lista.append(linea[4:])
        elif not linea.strip():
            lista = None
    return Resultado(codigo, salida, errores, avisos)


def linea_de_tiempo(estudio: Estudio, carpeta: Path) -> dict[str, Any]:
    """Genera las voces, cronometra y devuelve la línea de tiempo que deja la herramienta."""
    assert estudio("generar-voces", carpeta).codigo == 0
    resultado = estudio("cronometrar", carpeta)
    assert resultado.codigo == 0, resultado.salida
    datos: dict[str, Any] = json.loads((carpeta / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    return datos


def cambiar(archivo: Path, antes: str, despues: str) -> None:
    texto = archivo.read_text(encoding="utf-8")
    assert texto.count(antes) == 1, f"«{antes}» tiene que aparecer una vez en {archivo.name}"
    archivo.write_text(texto.replace(antes, despues), encoding="utf-8")


# --- La composición de HyperFrames ---


@dataclass
class Composicion:
    raiz: dict[str, str] = field(default_factory=dict)
    audios: list[dict[str, str]] = field(default_factory=list)
    tarjetas: list[tuple[dict[str, str], str]] = field(default_factory=list)  # atributos y texto
    tarjetas_en_la_pista_de_subtitulos: int = 0
    planos: list[dict[str, str]] = field(default_factory=list)  # las capas de imagen de los planos
    cierre: dict[str, str] | None = None  # la capa del cierre del CTA
    logo: dict[str, str] | None = None  # la imagen que lleva el cierre
    texto_del_cierre: str = ""
    fuentes: list[str] = field(default_factory=list)  # todos los src: los archivos que usan las capas
    estilo: str = ""


class _Lector(HTMLParser):
    """Lee de la composición la raíz, sus capas y la hoja de estilo.

    Cuenta con que las etiquetas sin cierre (meta, img) se escriben acabadas en />, como hace la herramienta.
    """

    def __init__(self) -> None:
        super().__init__()
        self.composicion = Composicion()
        self._abiertas: list[dict[str, str]] = []  # las etiquetas dentro de las que está el lector
        self._en_el_estilo = False

    def _dentro(self, condicion: Callable[[dict[str, str]], bool]) -> bool:
        return any(condicion(atributos) for atributos in self._abiertas)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        composicion = self.composicion
        atributos = {nombre: valor or "" for nombre, valor in attrs}
        clases = atributos.get("class", "").split()
        if "src" in atributos:
            composicion.fuentes.append(atributos["src"])
        if "data-composition-id" in atributos:
            composicion.raiz = atributos
        elif tag == "audio":
            composicion.audios.append(atributos)
        elif "tarjeta" in clases:
            composicion.tarjetas.append((atributos, ""))
            en_la_pista = self._dentro(lambda abierta: abierta.get("data-track-kind") == "captions")
            composicion.tarjetas_en_la_pista_de_subtitulos += en_la_pista
        elif tag == "img" and "plano" in clases:
            composicion.planos.append(atributos)
        elif atributos.get("id") == "cierre-del-cta":
            composicion.cierre = atributos
        elif tag == "img" and self._dentro(lambda abierta: abierta.get("id") == "cierre-del-cta"):
            composicion.logo = atributos
        self._abiertas.append(atributos)
        self._en_el_estilo = tag == "style"

    def handle_endtag(self, tag: str) -> None:
        self._abiertas.pop()
        self._en_el_estilo = False

    def handle_data(self, data: str) -> None:
        composicion = self.composicion
        if self._dentro(lambda abierta: "tarjeta" in abierta.get("class", "").split()):
            atributos, texto = composicion.tarjetas[-1]
            composicion.tarjetas[-1] = (atributos, texto + data)
        elif self._dentro(lambda abierta: abierta.get("id") == "cierre-del-cta"):
            composicion.texto_del_cierre += data
        elif self._en_el_estilo:
            composicion.estilo += data


def leer_composicion(carpeta: Path) -> Composicion:
    lector = _Lector()
    lector.feed((carpeta / "index.html").read_text(encoding="utf-8"))
    return lector.composicion


def montar(estudio: Estudio, carpeta: Path) -> tuple[Composicion, dict[str, Any]]:
    """Genera las voces, monta el episodio y devuelve la composición y la línea de tiempo que deja."""
    assert estudio("generar-voces", carpeta).codigo == 0
    resultado = estudio("montar", carpeta)
    assert resultado.codigo == 0, resultado.salida
    linea: dict[str, Any] = json.loads((carpeta / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    return leer_composicion(carpeta), linea


def fotogramas(segundos: str) -> int:
    return round(float(segundos) * FPS)


def tramo(capa: dict[str, str]) -> tuple[int, int]:
    """El primer fotograma de una capa y el primero después de ella."""
    inicio = fotogramas(capa["data-start"])
    return inicio, inicio + fotogramas(capa["data-duration"])


def reglas(estilo: str) -> list[tuple[str, str]]:
    """Las reglas de la hoja de estilo, como (selector, declaraciones), sin las de @keyframes."""
    sin_keyframes = re.sub(r"@keyframes[^{]*\{(?:[^{}]*\{[^}]*\})*\s*\}", "", estilo)
    sin_comentarios = re.sub(r"/\*.*?\*/", "", sin_keyframes, flags=re.S)
    return [(selector.strip(), cuerpo) for selector, cuerpo in re.findall(r"([^{}]+)\{([^}]*)\}", sin_comentarios)]


def declaraciones(cuerpo: str) -> dict[str, str]:
    pares = (declaracion.split(":", 1) for declaracion in cuerpo.split(";") if declaracion.strip())
    return {nombre.strip(): valor.strip().upper() for nombre, valor in pares}
