"""Marcas por palabra de un audio cuyo texto ya se conoce: Whisper (por HyperFrames) da los tiempos y se emparejan
con las palabras del guion.

Whisper no siempre escribe lo mismo que el guion («300» por «trescientos», «Ysi» por «Y si»), así que no se exige
que coincidan todas: las palabras que no casan toman el tiempo del trozo que Whisper oyó en su lugar, o el hueco
entre sus vecinas. Si casan menos de la mitad, el audio no dice la frase.
"""

import json
import shutil
import tempfile
import unicodedata
import wave
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from estudio import hyperframes

# Whisper multilingüe y en español: el modelo por defecto de HyperFrames, small.en, traduce al inglés.
TRANSCRIBIR = ["--engine", "whisper", "--model", "small", "--language", "es", "--json"]
MINIMO_QUE_CASA = 0.5  # parte de las palabras del guion que tiene que reconocer Whisper
DECIMALES = 3

class ErrorDeAlineacion(Exception):
    pass


@dataclass(frozen=True)
class Oida:
    """Una palabra tal como la oyó Whisper."""

    texto: str
    inicio: float  # segundos
    final: float


@dataclass(frozen=True)
class Tramo:
    """Unas palabras seguidas del guion, de la `desde` a la anterior a `hasta`, con el tiempo que Whisper les da;
    sin tiempo si Whisper no oyó nada en su lugar."""

    desde: int
    hasta: int
    inicio: float | None
    final: float | None


def duracion(audio: Path) -> float:
    """Los segundos que dura un WAV."""
    try:
        with wave.open(str(audio), "rb") as archivo:
            return archivo.getnframes() / archivo.getframerate()
    except (wave.Error, EOFError) as error:
        raise ErrorDeAlineacion("no es un archivo WAV que se pueda leer (PCM, como los que graba Audacity).") from error


def marcas(palabras: list[str], audio: Path) -> list[tuple[float, float]]:
    """El inicio y el final de cada palabra del guion en el audio, en segundos."""
    return emparejar(palabras, transcribir(audio), duracion(audio))


def transcribir(audio: Path) -> list[Oida]:
    """Las palabras que oye Whisper en el audio, con sus tiempos."""
    with tempfile.TemporaryDirectory() as temporal:
        carpeta = Path(temporal)
        shutil.copy(audio, carpeta / "frase.wav")
        try:
            hyperframes.ejecutar(["transcribe", "frase.wav", *TRANSCRIBIR], carpeta)
        except hyperframes.ErrorDeHyperFrames as error:
            raise ErrorDeAlineacion(f"Whisper no ha podido sacar los tiempos de las palabras: {error}") from error
        try:
            datos = json.loads((carpeta / "transcript.json").read_text(encoding="utf-8"))
            return [Oida(str(oida["text"]), float(oida["start"]), float(oida["end"])) for oida in datos]
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise ErrorDeAlineacion("Whisper no ha dejado una transcripción que se pueda leer.") from error


def emparejar(palabras: list[str], oidas: list[Oida], segundos: float) -> list[tuple[float, float]]:
    """Reparte los tiempos de lo que oyó Whisper entre las palabras del guion; `segundos`, lo que dura el audio."""
    con_letras = [oida for oida in oidas if _normalizar(oida.texto)]
    guion = [_normalizar(palabra) for palabra in palabras]
    tramos: list[Tramo] = []
    casan = 0
    emparejador = SequenceMatcher(None, guion, [_normalizar(oida.texto) for oida in con_letras], autojunk=False)
    for operacion, i1, i2, j1, j2 in emparejador.get_opcodes():
        if operacion == "equal":
            casan += i2 - i1
            tramos += [Tramo(i1 + k, i1 + k + 1, con_letras[j1 + k].inicio, con_letras[j1 + k].final) for k in range(i2 - i1)]
        elif operacion == "replace":
            tramos.append(Tramo(i1, i2, con_letras[j1].inicio, con_letras[j2 - 1].final))
        elif operacion == "delete":
            tramos.append(Tramo(i1, i2, None, None))
        # "insert": Whisper oyó palabras que no están en el guion; se ignoran.
    if casan < MINIMO_QUE_CASA * len(palabras):
        oido = " ".join(oida.texto for oida in con_letras)
        raise ErrorDeAlineacion(f"el audio no dice la frase: Whisper oye «{oido}».")
    return _repartir_tramos(palabras, tramos, segundos)


def _repartir_tramos(palabras: list[str], tramos: list[Tramo], segundos: float) -> list[tuple[float, float]]:
    """Da a cada tramo su tiempo; el que no tiene, toma el hueco entre sus vecinos."""
    resultado: list[tuple[float, float]] = []
    for n, tramo in enumerate(tramos):
        anterior = resultado[-1][1] if resultado else 0.0
        siguiente = next((otro.inicio for otro in tramos[n + 1 :] if otro.inicio is not None), segundos)
        empieza = max(anterior, anterior if tramo.inicio is None else tramo.inicio)
        acaba = max(empieza, siguiente if tramo.final is None else tramo.final)
        resultado += _repartir(palabras[tramo.desde : tramo.hasta], empieza, acaba)
    return resultado


def _repartir(palabras: list[str], inicio: float, final: float) -> list[tuple[float, float]]:
    """Reparte un tramo de tiempo entre sus palabras, según cuántas letras tienen (sin contar los signos)."""
    letras = [len(_normalizar(palabra)) for palabra in palabras]
    total = sum(letras)
    hasta_ahora = [sum(letras[:n]) for n in range(len(letras) + 1)]  # letras antes de cada palabra
    momentos = [round(inicio + (final - inicio) * cuenta / total, DECIMALES) for cuenta in hasta_ahora]
    return list(zip(momentos, momentos[1:]))


def _normalizar(palabra: str) -> str:
    """La palabra en minúsculas, sin tildes ni puntuación, para comparar."""
    sin_tildes = unicodedata.normalize("NFD", palabra.lower())
    return "".join(caracter for caracter in sin_tildes if caracter.isalnum())
