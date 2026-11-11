"""Revisión de un episodio: hojas de cada versión y comprobación de la exportación (docs/revision.md).

Usa ffmpeg y ffprobe como programas externos.
"""

import json
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from estudio import cronometraje
from estudio.montaje import ALTO, ANCHO

VERSIONES = "versiones"
CARPETA = "revision"
EXPORTACION = "exportacion"  # la exportación es exportacion/<nombre de la carpeta del episodio>.mp4
VELOCIDAD = "30/1"  # fotogramas por segundo de la exportación, como los da ffprobe
MARGEN = 1  # fotogramas que la exportación puede apartarse de la línea de tiempo


@dataclass(frozen=True)
class Hoja:
    """Una imagen en rejilla con fotogramas del vídeo: uno cada `cada` segundos, `columnas` por fila."""

    sufijo: str
    cada: int  # segundos
    ancho: int  # px de cada fotograma; el alto sale de la proporción vertical
    columnas: int


CONTACTOS = Hoja("contactos", cada=1, ancho=216, columnas=8)  # 8 x 216 = 1728 px de ancho
MOVIL = Hoja("movil", cada=3, ancho=360, columnas=6)  # el episodio a 360 px de ancho, como en un móvil
HOJAS = (CONTACTOS, MOVIL)


@dataclass(frozen=True)
class Medidas:
    ancho: int
    alto: int
    velocidad: str  # como la da ffprobe: "30/1"
    segundos: float


class ErrorDeFfmpeg(Exception):
    pass


def ruta_de_la_exportacion(carpeta: Path) -> str:
    return f"{EXPORTACION}/{carpeta.name}.mp4"


def revisar(carpeta: Path) -> tuple[list[str], list[str]]:
    """Saca las hojas de cada versión; devuelve las hojas guardadas (rutas relativas) y los errores."""
    versiones = sorted((carpeta / VERSIONES).glob("*.mp4"))
    if not versiones:
        return [], [f"No hay ninguna versión en {VERSIONES}/: hay que renderizar el episodio antes de revisarlo."]
    (carpeta / CARPETA).mkdir(exist_ok=True)
    guardadas: list[str] = []
    try:
        for version in versiones:
            segundos = medir(version).segundos
            for hoja in HOJAS:
                destino = f"{CARPETA}/{version.stem}-{hoja.sufijo}.png"
                _sacar_hoja(version, carpeta / destino, hoja, segundos)
                guardadas.append(destino)
    except ErrorDeFfmpeg as error:
        return guardadas, [str(error)]
    return guardadas, []


def comprobar_exportacion(carpeta: Path) -> list[str]:
    """Los motivos por los que la exportación no se puede subir; ninguno si cuadra con la línea de tiempo."""
    ruta = ruta_de_la_exportacion(carpeta)
    if not (carpeta / ruta).is_file():
        return [f"No encuentro la exportación: tiene que estar en {ruta}."]
    try:
        datos = json.loads((carpeta / cronometraje.ARCHIVO).read_text(encoding="utf-8"))
        total, fps = int(datos["total"]), int(datos["fps"])
    except (OSError, ValueError, KeyError, TypeError):
        return [f"No hay una línea de tiempo válida ({cronometraje.ARCHIVO}): hay que cronometrar el episodio antes."]
    try:
        medidas = medir(carpeta / ruta)
    except ErrorDeFfmpeg as error:
        return [str(error)]
    errores = []
    if (medidas.ancho, medidas.alto) != (ANCHO, ALTO):
        errores.append(f"La exportación mide {medidas.ancho}x{medidas.alto} y tiene que medir {ANCHO}x{ALTO}.")
    if medidas.velocidad != VELOCIDAD:
        errores.append(f"La exportación va a {medidas.velocidad} fotogramas por segundo y tiene que ir a {VELOCIDAD}.")
    # En segundos pasados a fotogramas de la línea de tiempo, para comparar aunque la velocidad no cuadre.
    dura = round(medidas.segundos * fps)
    if abs(dura - total) > MARGEN:
        errores.append(
            f"La exportación dura {dura} fotogramas (a {fps} por segundo) y la línea de tiempo {total}: "
            f"se admite {MARGEN} de diferencia."
        )
    return errores


def medir(video: Path) -> Medidas:
    salida = _ejecutar(
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration", "-of", "json", str(video),
    )
    try:
        flujo = json.loads(salida)["streams"][0]
        return Medidas(int(flujo["width"]), int(flujo["height"]), flujo["r_frame_rate"], float(flujo["duration"]))
    except (ValueError, KeyError, IndexError, TypeError):
        motivo = f"ffprobe no da el tamaño, la velocidad y la duración de {video.name}: ¿es un vídeo?"
        raise ErrorDeFfmpeg(motivo) from None


def _sacar_hoja(video: Path, destino: Path, hoja: Hoja, segundos: float) -> None:
    cuantos = max(1, math.ceil(segundos / hoja.cada))
    filas = math.ceil(cuantos / hoja.columnas)
    alto = hoja.ancho * ALTO // ANCHO
    # eof_action=pass: sin él, un vídeo más corto que `cada` segundos no da ningún fotograma.
    filtro = f"fps=1/{hoja.cada}:eof_action=pass,scale={hoja.ancho}:{alto},tile={hoja.columnas}x{filas}"
    destino.unlink(missing_ok=True)  # que no quede la hoja de la vez anterior si esta falla
    # -frames:v 1: una sola imagen aunque ffmpeg saque un fotograma de más al final.
    _ejecutar("ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", filtro, "-frames:v", "1", str(destino))
    if not destino.is_file():  # ffmpeg puede terminar bien sin haber escrito nada
        raise ErrorDeFfmpeg(f"ffmpeg no ha sacado ningún fotograma de {video.name} para {destino.name}.")


def _ejecutar(programa: str, *argumentos: str) -> str:
    ruta = shutil.which(programa)
    if ruta is None:
        raise ErrorDeFfmpeg(
            f"No encuentro {programa}, que viene con ffmpeg: hace falta instalarlo "
            "(en WSL, `sudo apt install ffmpeg`) y volver a intentarlo."
        )
    proceso = subprocess.run([ruta, *argumentos], capture_output=True, text=True, check=False)
    if proceso.returncode != 0:
        mensajes = [linea for linea in proceso.stderr.splitlines() if linea.strip()]
        motivo = mensajes[-1].strip() if mensajes else "sin mensajes"
        raise ErrorDeFfmpeg(f"{programa} terminó con el código {proceso.returncode} ({motivo}).")
    return proceso.stdout
