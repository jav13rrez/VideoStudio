"""Cronometraje: la línea de tiempo del episodio en fotogramas globales.

Cada frase empieza donde acaba la anterior más la pausa entre frases. Los tiempos de los audios
(en segundos) se redondean al fotograma más cercano. El formato está en docs/voces-y-linea-de-tiempo.md.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from estudio.configuracion import Configuracion
from estudio.guion import Frase
from estudio.voces import Audio, ruta_del_audio

ARCHIVO = "linea-de-tiempo.json"
DURACION = (55, 70)  # segundos que debe durar un episodio


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
class LineaDeTiempo:
    fps: int
    total: int  # fotogramas del episodio
    cta: Tramo | None  # del principio de la primera frase del CTA al final de la última
    frases: list[FraseCronometrada]


def cronometrar(carpeta: Path, frases: list[Frase], audios: list[Audio], configuracion: Configuracion) -> LineaDeTiempo:
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
    linea = LineaDeTiempo(
        fps, cronometradas[-1].final, Tramo(cta[0].inicio, cta[-1].final) if cta else None, cronometradas
    )
    (carpeta / ARCHIVO).write_text(json.dumps(asdict(linea), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return linea


def avisos(linea: LineaDeTiempo) -> list[str]:
    minimo, maximo = (segundos * linea.fps for segundos in DURACION)
    if minimo <= linea.total <= maximo:
        return []
    return [
        f"El episodio dura {linea.total} fotogramas ({segundos(linea.total, linea.fps)}); debería durar "
        f"entre {minimo} y {maximo} fotogramas ({DURACION[0]}-{DURACION[1]} s)."
    ]


def segundos(fotogramas: int, fps: int) -> str:
    """Los fotogramas en segundos, escritos a la española: 1904 a 30 fps son «63,47 s»."""
    return f"{fotogramas / fps:.2f} s".replace(".", ",")
