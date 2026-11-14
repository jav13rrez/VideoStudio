"""Renderizar los planos con Blender, desde la línea de comandos y por rangos de fotogramas.

La cámara y la colocación de cada plano salen de tomas.toml. Un plano de cámara fija deja una imagen (planos/<id>.png);
uno con movimiento deja los fotogramas en planos/_fotogramas/<id>/ y un vídeo (planos/<id>.mp4). El formato y el
funcionamiento están en docs/tomas.md.
"""

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from estudio.actuacion import Linea, leer_actuacion
from estudio.actuacion_de_blender import Estados, estados_del_plano
from estudio.configuracion import Configuracion
from estudio.cronometraje import LineaDeTiempo, PlanoCronometrado
from estudio.planos import ESCENARIOS, Plano
from estudio.tomas import ARCHIVO as ARCHIVO_DE_TOMAS
from estudio.tomas import FIJA, Toma, camaras_de_los_planos, leer_tomas

CARPETA = "planos"
FOTOGRAMAS = "_fotogramas"
TRABAJO = "_trabajo.json"
ANCHO, ALTO = 1080, 1920
CALIDADES = {"rapida": (0.5, 32), "final": (1.0, 128)}  # escala de la resolución y muestras de EEVEE
GUION_DEL_PROGRAMA = Path(__file__).parent / "blender" / "render_toma.py"
_RANGO = re.compile(r"(\d+)-(\d+)")


@dataclass(frozen=True)
class Trabajo:
    plano: PlanoCronometrado
    escenario: str
    toma: Toma
    estados: Estados | None  # lo que hacen los personajes en cada fotograma; None si no hacen nada
    fija: bool  # una sola imagen: cámara fija y personajes quietos
    desde: int  # primer fotograma que se renderiza, contando desde el principio del plano
    hasta: int  # último, incluido


def renderizar_planos(
    carpeta: Path,
    linea: LineaDeTiempo,
    planos: list[Plano],
    configuracion: Configuracion,
    seleccion: str | None,
    fotogramas: str | None,
    calidad: str,
) -> list[str]:
    """Renderiza los planos elegidos (todos, si no se elige ninguno); devuelve los errores que lo impiden."""
    if not planos:
        return ["El episodio no tiene lista de planos (planos.toml): no hay nada que renderizar."]
    camaras = camaras_de_los_planos(carpeta)
    tomas, informe = leer_tomas(carpeta, camaras)
    if informe.errores:
        return informe.errores
    elegidos, errores = elegir(linea, seleccion)
    if errores:
        return errores
    escenarios = {plano.id: plano.escenario for plano in planos}
    lineas, errores = leer_actuacion(carpeta, set(escenarios), [plano.id for plano in elegidos if plano.id in tomas])
    if errores:
        return errores
    trabajos, errores = _trabajos(carpeta, linea, elegidos, escenarios, tomas, lineas, camaras, fotogramas)
    if errores:
        return errores
    programa = _programa_de_blender(configuracion)
    if isinstance(programa, list):
        return programa
    for trabajo in trabajos:
        _preparar_salida(carpeta, trabajo, parcial=fotogramas is not None)
    errores = _ejecutar_blender(programa, carpeta, configuracion, trabajos, linea.fps, calidad)
    if errores:
        return errores
    return [error for trabajo in trabajos if not trabajo.fija for error in componer_video(carpeta, trabajo.plano, linea.fps)]


def elegir(linea: LineaDeTiempo, seleccion: str | None) -> tuple[list[PlanoCronometrado], list[str]]:
    """Los planos de la selección «01-03,05» (o todos), en el orden de la línea de tiempo."""
    if seleccion is None:
        return list(linea.planos), []
    ids: set[str] = set()
    for trozo in (t.strip() for t in seleccion.split(",") if t.strip()):
        rango = _RANGO.fullmatch(trozo)
        if rango:
            desde, hasta = int(rango[1]), int(rango[2])
            ids |= {p.id for p in linea.planos if p.id.isdigit() and desde <= int(p.id) <= hasta}
        else:
            ids.add(trozo)
    desconocidos = sorted(ids - {p.id for p in linea.planos})
    if desconocidos or not ids:
        return [], [f"No hay plano «{id_}» en la lista de planos." for id_ in desconocidos] or ["La selección de planos está vacía."]
    return [p for p in linea.planos if p.id in ids], []


def _trabajos(
    carpeta: Path,
    linea: LineaDeTiempo,
    elegidos: list[PlanoCronometrado],
    escenarios: dict[str, str],
    tomas: dict[str, Toma],
    lineas: dict[str, Linea],
    camaras: dict[str, str],
    fotogramas: str | None,
) -> tuple[list[Trabajo], list[str]]:
    errores = [
        f"El plano «{plano.id}» no tiene toma en {ARCHIVO_DE_TOMAS}: falta su cámara y la colocación."
        for plano in elegidos
        if plano.id not in tomas
    ]
    if errores:
        return [], errores
    estados: dict[str, Estados | None] = {}
    for plano in elegidos:
        estados[plano.id], errores_del_plano = estados_del_plano(plano, linea, tomas[plano.id], lineas[plano.id])
        errores += errores_del_plano
    rango = None
    if fotogramas is not None and not errores:
        quietos = {id_ for id_, e in estados.items() if e is None and camaras[id_] == FIJA}
        rango, errores_del_rango = _leer_rango(carpeta, elegidos, quietos, fotogramas)
        errores += errores_del_rango
    if errores:
        return [], errores
    trabajos = []
    for plano in elegidos:
        duracion = plano.final - plano.inicio
        fija = camaras[plano.id] == FIJA and estados[plano.id] is None
        desde, hasta = rango if rango else (0, 0 if fija else duracion - 1)
        trabajos.append(Trabajo(plano, escenarios[plano.id], tomas[plano.id], estados[plano.id], fija, desde, hasta))
    return trabajos, []


def _leer_rango(
    carpeta: Path, elegidos: list[PlanoCronometrado], quietos: set[str], texto: str
) -> tuple[tuple[int, int] | None, list[str]]:
    if len(elegidos) != 1:
        return None, ["Un rango de fotogramas (--fotogramas) se pide para un solo plano: elígelo con --planos."]
    plano = elegidos[0]
    rango = _RANGO.fullmatch(texto.strip())
    duracion = plano.final - plano.inicio
    if not rango or not 0 <= int(rango[1]) <= int(rango[2]) < duracion:
        return None, [
            f"El rango de fotogramas se escribe como 5-8, contando desde el principio del plano «{plano.id}», "
            f"que tiene {duracion} fotogramas (del 0 al {duracion - 1})."
        ]
    if plano.id in quietos:
        return None, [f"El plano «{plano.id}» es de cámara fija y sus personajes no se mueven: se renderiza entero, en una sola imagen."]
    existentes = list((carpeta / CARPETA / FOTOGRAMAS / plano.id).glob("*.png"))
    if len(existentes) != duracion:
        return None, [
            f"Para renderizar solo un rango, el plano «{plano.id}» tiene que estar ya renderizado entero "
            "(le faltan fotogramas): renderízalo entero primero."
        ]
    return (int(rango[1]), int(rango[2])), []


def _programa_de_blender(configuracion: Configuracion) -> str | list[str]:
    """El ejecutable de Blender: ESTUDIO_BLENDER, `blender` de estudio.toml o el del PATH."""
    candidato = os.environ.get("ESTUDIO_BLENDER") or configuracion.blender or shutil.which("blender")
    if candidato and (Path(candidato).is_file() or shutil.which(candidato)):
        return candidato
    return [
        "No encuentro Blender. Pon su ruta en estudio.toml, como "
        'blender = "/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe", '
        "o en la variable ESTUDIO_BLENDER."
    ]


def _ruta(programa: str, ruta: Path) -> str:
    """La ruta tal como la entiende Blender: en formato de Windows si es un blender.exe corriendo desde WSL."""
    if programa.lower().endswith(".exe"):
        convertida = subprocess.run(["wslpath", "-w", str(ruta.resolve())], capture_output=True, text=True, check=True)
        return convertida.stdout.strip()
    return str(ruta.resolve())


def _preparar_salida(carpeta: Path, trabajo: Trabajo, parcial: bool) -> None:
    """Quita lo de la vez anterior que ya no vale, para que un fallo no deje imágenes viejas."""
    base = carpeta / CARPETA
    id_ = trabajo.plano.id
    base.mkdir(exist_ok=True)
    (base / f"{id_}.png").unlink(missing_ok=True)
    (base / f"{id_}.mp4").unlink(missing_ok=True)
    if not parcial:
        shutil.rmtree(base / FOTOGRAMAS / id_, ignore_errors=True)


def _ejecutar_blender(
    programa: str, carpeta: Path, configuracion: Configuracion, trabajos: list[Trabajo], fps: int, calidad: str
) -> list[str]:
    escala, muestras = CALIDADES[calidad]
    planos: list[dict[str, Any]] = []
    for trabajo in trabajos:
        id_ = trabajo.plano.id
        a_tamano_real = trabajo.fija or escala == 1.0
        ancho, alto = (ANCHO, ALTO) if a_tamano_real else (round(ANCHO * escala), round(ALTO * escala))
        escenario = configuracion.biblioteca / ESCENARIOS / trabajo.escenario / f"{trabajo.escenario}.blend"
        planos.append(
            {
                "id": id_,
                "escenario": trabajo.escenario,
                "blend": _ruta(programa, escenario),
                "toma": trabajo.toma.como_datos(),
                "actuacion": trabajo.estados,
                "fija": trabajo.fija,
                "desde": trabajo.desde,
                "hasta": trabajo.hasta,
                "duracion": trabajo.plano.final - trabajo.plano.inicio,
                "ancho_px": ancho,
                "alto_px": alto,
                "muestras": muestras,
                "imagen": _ruta(programa, carpeta / CARPETA / f"{id_}.png"),
                "fotogramas": _ruta(programa, carpeta / CARPETA / FOTOGRAMAS / id_),
            }
        )
    archivo = carpeta / CARPETA / TRABAJO
    datos = {"fps": fps, "biblioteca": _ruta(programa, configuracion.biblioteca), "planos": planos}
    archivo.write_text(json.dumps(datos, indent=1), encoding="utf-8")
    orden = [programa, "-b", "--python", _ruta(programa, GUION_DEL_PROGRAMA), "--", _ruta(programa, archivo)]
    proceso = subprocess.run(orden, capture_output=True, text=True, check=False)
    if proceso.returncode != 0:
        mensajes = [linea for linea in (proceso.stdout + proceso.stderr).splitlines() if linea.strip()]
        motivo = mensajes[-1].strip() if mensajes else "sin mensajes"
        return [f"Blender terminó con el código {proceso.returncode} ({motivo})."]
    return []


def componer_video(carpeta: Path, plano: PlanoCronometrado, fps: int) -> list[str]:
    """Junta los fotogramas del plano en planos/<id>.mp4, a 1080x1920."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return ["No encuentro ffmpeg, que hace falta para componer el vídeo de cada plano."]
    id_ = plano.id
    fotogramas = carpeta / CARPETA / FOTOGRAMAS / id_
    duracion = plano.final - plano.inicio
    faltan = [n for n in range(duracion) if not (fotogramas / f"{n:04d}.png").is_file()]
    if faltan:
        return [f"No están todos los fotogramas del plano «{id_}» (faltan {len(faltan)}, desde el {faltan[0]})."]
    salida = carpeta / CARPETA / f"{id_}.mp4"
    orden = [
        ffmpeg, "-y", "-loglevel", "error", "-framerate", str(fps), "-start_number", "0",
        "-i", str(fotogramas / "%04d.png"), "-vf", f"scale={ANCHO}:{ALTO}:flags=lanczos",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", "-r", str(fps), str(salida),
    ]
    proceso = subprocess.run(orden, capture_output=True, text=True, check=False)
    if proceso.returncode != 0 or not salida.is_file():
        return [f"ffmpeg no ha podido componer el vídeo del plano «{id_}»: {proceso.stderr.strip()[-200:]}"]
    return []
