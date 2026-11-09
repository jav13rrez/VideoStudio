"""Ayudas compartidas por los tests: todos entran por la herramienta del estudio."""

from dataclasses import dataclass
from pathlib import Path

EPISODIOS = Path(__file__).parent / "episodios"
EJEMPLO = EPISODIOS / "001-olfato"
# La configuración del estudio para los tests, aparte de la del estudio real.
CONFIGURACION = EPISODIOS / "estudio.toml"


@dataclass
class Resultado:
    codigo: int
    salida: str
    errores: list[str]
    avisos: list[str]


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


def cambiar(archivo: Path, antes: str, despues: str) -> None:
    texto = archivo.read_text(encoding="utf-8")
    assert texto.count(antes) == 1, f"«{antes}» tiene que aparecer una vez en {archivo.name}"
    archivo.write_text(texto.replace(antes, despues), encoding="utf-8")
