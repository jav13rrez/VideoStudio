"""Punto de entrada de la herramienta del estudio."""

import argparse
from collections.abc import Callable
from pathlib import Path

from estudio import cronometraje, hyperframes, montaje, revision
from estudio.configuracion import Configuracion, ErrorDeConfiguracion, leer_configuracion
from estudio.cronometraje import LineaDeTiempo
from estudio.guion import Frase, Informe, comprobar_guion
from estudio.planos import ARCHIVO as ARCHIVO_DE_PLANOS
from estudio.planos import Plano, leer_planos
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
    linea, planos, _, informe = _linea_de_tiempo(carpeta)
    print(f"Línea de tiempo de {carpeta.name}")
    _imprimir(informe, "hay que corregirlos para cronometrar")
    if linea is None:
        print("Resultado: no se ha cronometrado el episodio.")
    else:
        _imprimir_total(linea)
        if linea.cta:
            print(f"CTA: del fotograma {linea.cta.inicio} al {linea.cta.final}.")
        if planos is None:
            print(f"Planos: no hay lista de planos ({ARCHIVO_DE_PLANOS}), así que la línea de tiempo sale sin planos.")
        else:
            escenarios = len({plano.escenario for plano in planos})
            print(f"Planos: {len(planos)}, en {escenarios} escenario{'' if escenarios == 1 else 's'}.")
        print(f"Resultado: línea de tiempo guardada en {cronometraje.ARCHIVO}.")
    return 1 if informe.errores else 0


def _montar(carpeta: Path) -> int:
    linea, planos, configuracion, informe = _linea_de_tiempo(carpeta)
    if linea is not None and configuracion is not None:
        del_montaje = montaje.montar(carpeta, linea, planos or [], configuracion.app)
        informe.errores += del_montaje.errores
        informe.avisos += del_montaje.avisos
    print(f"Montaje de {carpeta.name}")
    _imprimir(informe, "hay que corregirlos para montar")
    if linea is None or informe.errores:
        print("Resultado: no se ha montado el episodio.")
        return 1
    _imprimir_total(linea)
    if linea.planos:
        con_imagen = sum(montaje.imagen_del_plano(carpeta, plano.id) is not None for plano in linea.planos)
        con_cartel = len(linea.planos) - con_imagen
        imagenes = f"{len(linea.planos)} planos ({con_cartel} con cartel y {con_imagen} con su imagen)"
    else:
        imagenes = "ningún plano (un fondo liso, porque no hay lista de planos)"
    cierre = " y el cierre del CTA" if linea.cta else "; sin cierre del CTA, porque el guion no tiene CTA"
    print(f"Capas: {imagenes}, {len(linea.frases)} voces, {len(linea.subtitulos)} tarjetas de subtítulo{cierre}.")
    print(f"Resultado: composición guardada en {montaje.ARCHIVO} (y la línea de tiempo en {cronometraje.ARCHIVO}).")
    return 0


def _renderizar(carpeta: Path) -> int:
    if _montar(carpeta):
        return 1
    print(f"\nRender de {carpeta.name} con {hyperframes.HYPERFRAMES}")
    errores = montaje.renderizar(carpeta)
    _imprimir(Informe(errores=errores), "no se ha podido renderizar")
    if errores:
        print("Resultado: no se ha renderizado el episodio.")
        return 1
    print(f"Resultado: vídeo guardado en {montaje.VIDEO}.")
    return 0


def _revisar(carpeta: Path) -> int:
    hojas, errores = revision.revisar(carpeta)
    print(f"Revisión de {carpeta.name}")
    _imprimir(Informe(errores=errores), "no se han podido sacar las hojas")
    for hoja in hojas:
        print(f"Hoja guardada: {hoja}")
    if errores:
        print("Resultado: faltan hojas de revisión.")
        return 1
    print(f"Resultado: {len(hojas)} hojas en {revision.CARPETA}/.")
    return 0


def _comprobar_exportacion(carpeta: Path) -> int:
    errores = revision.comprobar_exportacion(carpeta)
    print(f"Comprobación de la exportación de {carpeta.name} ({revision.ruta_de_la_exportacion(carpeta)})")
    _imprimir(Informe(errores=errores), "no se puede subir así")
    if errores:
        print("Resultado: la exportación no se puede subir hasta que se corrijan los errores.")
        return 1
    print("Resultado: la exportación cuadra con la línea de tiempo y se puede subir.")
    return 0


def _linea_de_tiempo(
    carpeta: Path,
) -> tuple[LineaDeTiempo | None, list[Plano] | None, Configuracion | None, Informe]:
    """Cronometra el episodio si nada lo impide; los planos son None si no hay lista de planos."""
    frases, configuracion, informe = _leer_episodio(carpeta)
    if configuracion is None or informe.errores:
        return None, None, configuracion, informe
    audios, errores = leer_voces(carpeta, frases, configuracion)
    planos, de_los_planos = leer_planos(carpeta, frases, configuracion.biblioteca)
    informe.errores += errores + de_los_planos.errores
    informe.avisos += de_los_planos.avisos
    if informe.errores:
        return None, planos, configuracion, informe
    linea = cronometraje.cronometrar(carpeta, frases, audios, configuracion, planos or [])
    informe.avisos += cronometraje.avisos(linea)
    return linea, planos, configuracion, informe


def _leer_episodio(carpeta: Path) -> tuple[list[Frase], Configuracion | None, Informe]:
    """El guion y la configuración del estudio, con los errores que impiden seguir."""
    frases, guion = comprobar_guion(carpeta)
    informe = Informe(errores=list(guion.errores))  # los avisos del guion son cosa de comprobar-guion
    try:
        return frases, leer_configuracion(carpeta), informe
    except ErrorDeConfiguracion as error:
        informe.errores.append(str(error))
        return frases, None, informe


def _imprimir_total(linea: LineaDeTiempo) -> None:
    print(f"Total: {linea.total} fotogramas a {linea.fps} fps ({cronometraje.segundos(linea.total, linea.fps)}).")


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
    "montar": ("Genera la composición de HyperFrames: planos, voces, subtítulos y cierre del CTA.", _montar),
    "renderizar": (f"Monta el episodio y lo renderiza a {montaje.VIDEO} con HyperFrames.", _renderizar),
    "revisar": ("Saca la hoja de contactos y la prueba de móvil de cada versión del episodio.", _revisar),
    "comprobar-exportacion": (
        "Dice si la exportación mide 1080x1920, va a 30 fps y dura lo que la línea de tiempo.",
        _comprobar_exportacion,
    ),
}
