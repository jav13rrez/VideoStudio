"""Punto de entrada de la herramienta del estudio."""

import argparse
from pathlib import Path

from estudio.guion import Informe, comprobar_guion


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="estudio", description="Herramienta del estudio de episodios.")
    ordenes = parser.add_subparsers(dest="orden", required=True)
    orden = ordenes.add_parser(
        "comprobar-guion",
        help="Dice si el guion de un episodio puede pasar a la parada 1.",
    )
    orden.add_argument("carpeta", type=Path, help="Carpeta del episodio.")
    args = parser.parse_args(argv)

    informe = comprobar_guion(args.carpeta)
    _imprimir(args.carpeta, informe)
    return 1 if informe.errores else 0


def _imprimir(carpeta: Path, informe: Informe) -> None:
    print(f"Comprobación del guion de {carpeta.name}")
    if informe.errores:
        print("\nErrores (impiden pasar a la parada 1):")
        for error in informe.errores:
            print(f"  - {error}")
    if informe.avisos:
        print("\nAvisos (no impiden pasar, pero revísalos):")
        for aviso in informe.avisos:
            print(f"  - {aviso}")
    print()
    if informe.errores:
        print("Resultado: el guion no puede pasar a la parada 1 hasta que se corrijan los errores.")
    else:
        print("Resultado: el guion puede pasar a la parada 1.")
