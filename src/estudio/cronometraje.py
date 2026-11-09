"""Cronometraje: la línea de tiempo del episodio en fotogramas globales.

Cada frase empieza donde acaba la anterior más la pausa entre frases. Los tiempos de los audios
(en segundos) se redondean al fotograma más cercano. Cada plano empieza en el fotograma de su palabra
y acaba donde empieza el siguiente. El formato está en docs/voces-y-linea-de-tiempo.md.
"""

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from estudio.configuracion import Configuracion
from estudio.guion import Frase
from estudio.planos import Plano
from estudio.voces import Audio, ruta_del_audio

ARCHIVO = "linea-de-tiempo.json"
DURACION = (55, 70)  # segundos que debe durar un episodio
DURACION_DEL_PLANO = (1.5, 3)  # segundos que debe durar un plano


@dataclass(frozen=True)
class PalabraCronometrada:
    texto: str
    acentuada: bool
    inicio: int
    final: int


@dataclass(frozen=True)
class FraseCronometrada:
    numero: int
    linea: int  # en guion.md
    personaje: str
    audio: str
    inicio: int  # primer fotograma de la frase
    final: int  # primer fotograma después de la frase
    palabras: list[PalabraCronometrada]


@dataclass(frozen=True)
class Tramo:
    inicio: int
    final: int


@dataclass(frozen=True)
class PlanoCronometrado:
    id: str
    inicio: int  # el fotograma en que empieza su palabra; el primero, en el 0
    final: int  # donde empieza el plano siguiente; el último, donde acaba el episodio


@dataclass(frozen=True)
class LineaDeTiempo:
    fps: int
    total: int  # fotogramas del episodio
    cta: Tramo | None  # del principio de la primera frase del CTA al final de la última
    planos: list[PlanoCronometrado]
    frases: list[FraseCronometrada]


def cronometrar(
    carpeta: Path, frases: list[Frase], audios: list[Audio], configuracion: Configuracion, planos: list[Plano]
) -> LineaDeTiempo:
    """Calcula la línea de tiempo y la deja en la carpeta del episodio."""
    fps = configuracion.fps
    cronometradas = []
    inicio = 0
    for numero, (frase, audio) in enumerate(zip(frases, audios, strict=True), start=1):
        final = inicio + round(audio.duracion * fps)
        palabras = [
            PalabraCronometrada(
                palabra.texto, palabra.acentuada, inicio + round(marca.inicio * fps), inicio + round(marca.final * fps)
            )
            for palabra, marca in zip(frase.palabras, audio.palabras, strict=True)
        ]
        cronometradas.append(
            FraseCronometrada(numero, frase.linea, frase.personaje, ruta_del_audio(numero), inicio, final, palabras)
        )
        inicio = final + configuracion.pausa_entre_frases
    cta = [cronometrada for frase, cronometrada in zip(frases, cronometradas) if frase.es_cta]
    total = cronometradas[-1].final
    # El primer plano empieza en el 0 aunque la voz tarde en arrancar, para que no quede imagen sin plano.
    inicios = [0] + [cronometradas[plano.frase].palabras[plano.palabra].inicio for plano in planos[1:]]
    linea = LineaDeTiempo(
        fps,
        total,
        Tramo(cta[0].inicio, cta[-1].final) if cta else None,
        [
            PlanoCronometrado(plano.id, inicio, final)
            for plano, inicio, final in zip(planos, inicios, inicios[1:] + [total])
        ],
        cronometradas,
    )
    (carpeta / ARCHIVO).write_text(json.dumps(asdict(linea), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return linea


def avisos(linea: LineaDeTiempo) -> list[str]:
    avisos = []
    minimo, maximo = (segundos * linea.fps for segundos in DURACION)
    if not minimo <= linea.total <= maximo:
        avisos.append(
            f"El episodio dura {linea.total} fotogramas ({segundos(linea.total, linea.fps)}); debería durar "
            f"entre {minimo} y {maximo} fotogramas ({DURACION[0]}-{DURACION[1]} s)."
        )
    corto, largo = DURACION_DEL_PLANO
    minimo, maximo = math.ceil(corto * linea.fps), math.floor(largo * linea.fps)
    entre = f"{corto:g}-{largo:g} s".replace(".", ",")  # «1,5-3 s»
    for plano in linea.planos:
        dura = plano.final - plano.inicio
        # El último plano, si empieza dentro del CTA, lo acompaña con el nombre y el logo de la App y puede pasar
        # de 3 s: dura como mucho lo que el CTA (unos 5 s), que comprobar-guion ya vigila.
        acompana_el_cta = plano is linea.planos[-1] and linea.cta is not None and plano.inicio >= linea.cta.inicio
        if dura < minimo or (dura > maximo and not acompana_el_cta):
            avisos.append(
                f"El plano «{plano.id}» dura {dura} fotogramas ({segundos(dura, linea.fps)}); "
                f"debería durar entre {minimo} y {maximo} fotogramas ({entre})."
            )
    return avisos


def segundos(fotogramas: int, fps: int) -> str:
    """Los fotogramas en segundos, escritos a la española: 1904 a 30 fps son «63,47 s»."""
    return f"{fotogramas / fps:.2f} s".replace(".", ",")
