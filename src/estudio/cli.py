"""Punto de entrada de la herramienta del estudio."""

import argparse
from collections.abc import Callable
from pathlib import Path

from estudio import cronometraje
from estudio.configuracion import Configuracion, ErrorDeConfiguracion, leer_configuracion
from estudio.guion import Frase, Informe, comprobar_guion
from estudio.voces import CARPETA, generar_voces, leer_voces


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="estudio", description="Herramienta del estudio de episodios.")
    ordenes = parser.add_subparsers(dest="orden", required=True)
    for nombre, (ayuda, _) in ORDENES.items():
        orden = ordenes.add_parser(nombre, help=ayuda)
        orden.add_argument("carpeta", type=Path, help="Carpeta del episodio.")
    args = parser.parse_args(argv)
    _, ejecutar = ORDENES[args.orden]
    return ejecutar(args.carpeta)


def _comprobar_guion(carpeta: Path) -> int:
    _, informe = comprobar_guion(carpeta)
    print(f"Comprobación del guion de {carpeta.name}")
    _imprimir(informe, "impiden pasar a la parada 1")
    if informe.errores:
        print("Resultado: el guion no puede pasar a la parada 1 hasta que se corrijan los errores.")
    else:
        print("Resultado: el guion puede pasar a la parada 1.")
    return 1 if informe.errores else 0


def _generar_voces(carpeta: Path) -> int:
    frases, configuracion, informe = _leer_episodio(carpeta)
    if configuracion is not None and not informe.errores:
        informe.errores += generar_voces(carpeta, frases, configuracion)
    print(f"Voces de {carpeta.name}")
    _imprimir(informe, "hay que corregirlos para generar las voces")
    if informe.errores or configuracion is None:
        print("Resultado: no se han generado las voces.")
    else:
        for personaje in sorted({frase.personaje for frase in frases}):
            voz = configuracion.voces[personaje]
            print(f"{personaje}: proveedor «{voz.proveedor}», voz «{voz.voz}»")
        print(f"Resultado: {len(frases)} voces generadas en {CARPETA}/.")
    return 1 if informe.errores else 0


def _cronometrar(carpeta: Path) -> int:
    frases, configuracion, informe = _leer_episodio(carpeta)
    linea = None
    if configuracion is not None and not informe.errores:
        audios, errores = leer_voces(carpeta, frases, configuracion)
        informe.errores += errores
        if not errores:
            linea = cronometraje.cronometrar(carpeta, frases, audios, configuracion)
            informe.avisos += cronometraje.avisos(linea)
    print(f"Línea de tiempo de {carpeta.name}")
    _imprimir(informe, "hay que corregirlos para cronometrar")
    if linea is None:
        print("Resultado: no se ha cronometrado el episodio.")
    else:
        print(f"Total: {linea.total} fotogramas a {linea.fps} fps ({cronometraje.segundos(linea.total, linea.fps)}).")
        if linea.cta:
            print(f"CTA: del fotograma {linea.cta.inicio} al {linea.cta.final}.")
        print(f"Resultado: línea de tiempo guardada en {cronometraje.ARCHIVO}.")
    return 1 if informe.errores else 0


def _leer_episodio(carpeta: Path) -> tuple[list[Frase], Configuracion | None, Informe]:
    """El guion y la configuración del estudio, con los errores que impiden seguir."""
    frases, guion = comprobar_guion(carpeta)
    informe = Informe(errores=list(guion.errores))  # los avisos del guion son cosa de comprobar-guion
    try:
        return frases, leer_configuracion(carpeta), informe
    except ErrorDeConfiguracion as error:
        informe.errores.append(str(error))
        return frases, None, informe


def _imprimir(informe: Informe, que_hacen_los_errores: str) -> None:
    if informe.errores:
        print(f"\nErrores ({que_hacen_los_errores}):")
        for error in informe.errores:
            print(f"  - {error}")
    if informe.avisos:
        print("\nAvisos (no impiden pasar, pero revísalos):")
        for aviso in informe.avisos:
            print(f"  - {aviso}")
    print()


ORDENES: dict[str, tuple[str, Callable[[Path], int]]] = {
    "comprobar-guion": ("Dice si el guion de un episodio puede pasar a la parada 1.", _comprobar_guion),
    "generar-voces": ("Genera un audio por frase con la voz de cada personaje.", _generar_voces),
    "cronometrar": ("Calcula la línea de tiempo del episodio en fotogramas.", _cronometrar),
}
