"""Punto de entrada de la herramienta del estudio."""

import argparse
from collections.abc import Callable
from datetime import date
from pathlib import Path

from estudio import cronometraje, dibujar_planos, episodio, hyperframes, montaje, publicacion, renderizar_planos, reparto, revision
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
        orden.add_argument("carpeta", type=Path, help=_AYUDA_DE_LA_CARPETA.get(nombre, "Carpeta del episodio."))
    for nombre, (ayuda, argumentos, _) in ORDENES_CON_ARGUMENTOS.items():
        orden = ordenes.add_parser(nombre, help=ayuda)
        orden.add_argument("carpeta", type=Path, help="Carpeta del episodio.")
        for argumento, ayuda_del_argumento in argumentos:
            orden.add_argument(argumento, help=ayuda_del_argumento)
    orden_de_planos = ordenes.add_parser(
        "renderizar-planos", help="Renderiza los planos con Blender, con la cámara y la colocación de tomas.toml."
    )
    orden_de_planos.add_argument("carpeta", type=Path, help="Carpeta del episodio.")
    orden_de_planos.add_argument("--planos", help="Los planos que se renderizan, como 01-03,05 (por defecto, todos).")
    orden_de_planos.add_argument("--fotogramas", help="Solo este rango de fotogramas de un plano, como 5-8.")
    orden_de_planos.add_argument(
        "--calidad", choices=list(renderizar_planos.CALIDADES), default="rapida", help="rapida (por defecto) o final."
    )
    args = parser.parse_args(argv)
    if args.orden == "renderizar-planos":
        return _renderizar_planos(args.carpeta, args.planos, args.fotogramas, args.calidad)
    if args.orden in ORDENES:
        _, ejecutar = ORDENES[args.orden]
        return ejecutar(args.carpeta)
    _, argumentos, ejecutar_con_argumentos = ORDENES_CON_ARGUMENTOS[args.orden]
    return ejecutar_con_argumentos(args.carpeta, *(getattr(args, argumento) for argumento, _ in argumentos))


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


def _renderizar_planos(carpeta: Path, planos: str | None, fotogramas: str | None, calidad: str) -> int:
    linea, lista, configuracion, informe = _linea_de_tiempo(carpeta)
    en_2d = reparto.hay_reparto(carpeta)  # con reparto.toml se dibuja en 2D; sin él, se renderiza con Blender
    print(f"Render de los planos de {carpeta.name} " + ("en 2D" if en_2d else f"con Blender (calidad {calidad})"))
    if linea is None or configuracion is None or informe.errores:
        _imprimir(informe, "hay que corregirlos para renderizar")
        print("Resultado: no se han renderizado los planos.")
        return 1
    if en_2d:
        errores = dibujar_planos.dibujar_planos(carpeta, linea, lista or [], configuracion, planos, fotogramas)
    else:
        errores = renderizar_planos.renderizar_planos(carpeta, linea, lista or [], configuracion, planos, fotogramas, calidad)
    informe.errores += errores
    _imprimir(informe, "no se han podido renderizar los planos")
    if informe.errores:
        print("Resultado: no se han renderizado los planos.")
        return 1
    print(f"Resultado: planos renderizados en {renderizar_planos.CARPETA}/. Para verlos en el episodio, monta de nuevo.")
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


def _hoja_de_publicacion(carpeta: Path) -> int:
    errores = publicacion.generar_hoja(carpeta)
    print(f"Hoja de publicación de {carpeta.name}")
    _imprimir(Informe(errores=errores), "hay que corregirlos para sacar la hoja")
    if errores:
        print("Resultado: no se ha generado la hoja de publicación.")
        return 1
    print(f"Resultado: hoja de publicación guardada en {publicacion.ARCHIVO}.")
    return 0


def _crear_episodio(ruta: Path) -> int:
    carpeta, errores = episodio.crear_episodio(ruta)
    print(f"Episodio nuevo «{ruta.name}»")
    _imprimir(Informe(errores=errores), "no se ha creado la carpeta")
    if carpeta is None:
        print("Resultado: no se ha creado el episodio.")
        return 1
    print(f"Resultado: episodio creado en {carpeta}. Deja el contenido en contenido.md.")
    return 0


def _estado(carpeta: Path) -> int:
    try:
        estado = episodio.leer_estado(carpeta)
        nuevos = episodio.nuevos_del_episodio(carpeta)
    except (episodio.ErrorDeEstado, ErrorDeConfiguracion) as error:
        print(f"Estado de {carpeta.resolve().name}")
        _imprimir(Informe(errores=[str(error)]), "no se puede leer el estado")
        return 1
    escenarios = nuevos.por_aprobar("escenario", estado)
    personajes = nuevos.por_aprobar("personaje", estado)
    paso, espera = estado.paso
    if escenarios or personajes:
        espera += "; y, en cuanto estén hechos, que apruebes los escenarios y personajes nuevos de abajo"
    print(f"Estado de {carpeta.resolve().name}\n")
    print(f"Paso: {paso}.")
    print(f"Esperando: {espera}.")
    print(f"Paradas aprobadas: {_aprobados(estado.aprobaciones['parada'], 'parada ', 'ninguna todavía')}.")
    print(f"Escenarios nuevos por aprobar: {', '.join(escenarios) or 'ninguno'}.")
    print(f"Personajes nuevos por aprobar: {', '.join(personajes) or 'ninguno'}.")
    print(f"Escenarios aprobados: {_aprobados(estado.aprobaciones['escenario'], '', 'ninguno')}.")
    print(f"Personajes aprobados: {_aprobados(estado.aprobaciones['personaje'], '', 'ninguno')}.\n")
    _imprimir_horas(estado.horas)
    return 0


def _aprobados(aprobados: dict[str, date], delante: str, si_no_hay: str) -> str:
    return ", ".join(f"{delante}{nombre} el {cuando.isoformat()}" for nombre, cuando in aprobados.items()) or si_no_hay


def _imprimir_horas(horas: dict[str, float]) -> None:
    print("Horas por etapa:" if horas else "Horas por etapa: ninguna registrada.")
    for etapa in episodio.ETAPAS:
        if etapa in horas:
            print(f"  {etapa}: {episodio.horas_en_texto(horas[etapa])}")
    print(f"Total: {episodio.horas_en_texto(sum(horas.values()))}")


def _aprobar(carpeta: Path, que: str, nombre: str) -> int:
    try:
        errores, avisos = episodio.aprobar(carpeta, que, nombre)
    except (episodio.ErrorDeEstado, ErrorDeConfiguracion) as error:
        errores, avisos = [str(error)], []
    print(f"Aprobación en {carpeta.resolve().name}: {que} {nombre}")
    _imprimir(Informe(errores=errores, avisos=avisos), "no se ha anotado la aprobación")
    if errores:
        print("Resultado: no se ha anotado la aprobación.")
        return 1
    print(f"Resultado: aprobación anotada en {episodio.ARCHIVO}." if not avisos else "Resultado: nada que cambiar.")
    return 0


def _registrar_horas(carpeta: Path, etapa: str, horas: str) -> int:
    try:
        errores = episodio.registrar_horas(carpeta, etapa, horas)
    except episodio.ErrorDeEstado as error:
        errores = [str(error)]
    print(f"Horas de {carpeta.resolve().name}")
    _imprimir(Informe(errores=errores), "no se han anotado las horas")
    if errores:
        print("Resultado: no se han anotado las horas.")
        return 1
    _imprimir_horas(episodio.leer_estado(carpeta).horas)
    print(f"Resultado: horas anotadas en {episodio.ARCHIVO}.")
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
    "hoja-de-publicacion": (
        "Deja la descripción, un enlace con seguimiento por plataforma y los recordatorios de subida.",
        _hoja_de_publicacion,
    ),
    "crear-episodio": (
        "Crea la carpeta de un episodio nuevo con el número siguiente: crear-episodio episodios/olfato.",
        _crear_episodio,
    ),
    "estado": ("Dice en qué paso está el episodio, qué espera y cuántas horas lleva.", _estado),
}
_AYUDA_DE_LA_CARPETA = {
    "crear-episodio": "La carpeta de los episodios y el nombre corto del nuevo, como episodios/olfato.",
}
# Órdenes que, además de la carpeta del episodio, piden más argumentos: (ayuda, argumentos, ejecutar).
ORDENES_CON_ARGUMENTOS: dict[str, tuple[str, list[tuple[str, str]], Callable[..., int]]] = {
    "aprobar": (
        "Anota con la fecha de hoy que el creador aprueba una parada, un escenario o un personaje.",
        [("que", "parada, escenario o personaje."), ("nombre", "El número de la parada o el nombre.")],
        _aprobar,
    ),
    "registrar-horas": (
        "Suma horas a una etapa del episodio.",
        [("etapa", f"Una de: {', '.join(episodio.ETAPAS)}."), ("horas", "Las horas, como 1,5.")],
        _registrar_horas,
    ),
}
