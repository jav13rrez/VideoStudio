"""Ayudas compartidas por los tests: todos entran por la herramienta del estudio."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EPISODIOS = Path(__file__).parent / "episodios"
EJEMPLO = EPISODIOS / "001-olfato"
# La configuración del estudio para los tests, aparte de la del estudio real.
CONFIGURACION = EPISODIOS / "estudio.toml"
# La biblioteca de los tests, junto a su configuración, como la del estudio real.
BIBLIOTECA = EPISODIOS / "biblioteca"


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
