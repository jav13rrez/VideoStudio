"""Música y efectos: sonido.toml de la carpeta del episodio, con la licencia de cada uno.

La música suena baja, por debajo de las voces, y se coloca para que su final caiga en el último fotograma del
episodio. Cada efecto acompaña al plano que lo pide en la lista de planos (su campo «sonido») y se coloca para que
su golpe, la muestra más fuerte del archivo, caiga en el primer fotograma de ese plano. Los audios son WAV de
16 bits dentro de la carpeta del episodio. El formato está en docs/musica-y-efectos.md.

Es el enchufe de la música y los efectos: hoy se eligen de bibliotecas gratuitas y se anotan aquí a mano. Un
proveedor futuro (música generada o de pago) solo tendría que dejar sus archivos y sus líneas en sonido.toml.
"""

import math
import operator
import sys
import tomllib
import wave
from array import array
from dataclasses import dataclass
from pathlib import Path

from estudio.cronometraje import LineaDeTiempo
from estudio.guion import Informe
from estudio.planos import Plano

ARCHIVO = "sonido.toml"
DEBAJO_DE_LAS_VOCES = 18  # dB: lo que la música queda por debajo del nivel medio de las voces
# El nivel medio (dBFS) que se supone a las voces si son silencio, como las del proveedor falso de los tests.
# Las de Kokoro rondan los -20 (DEBT_TECH.md, medido con earshot).
NIVEL_DE_LAS_VOCES_EN_SILENCIO = -20.0
PISTA_DE_LA_MUSICA, PISTA_DE_LOS_EFECTOS = 4, 5  # en la composición; las voces van en la 0
_MAXIMO = 32768  # la escala de una muestra de 16 bits
_CAMPOS = ("archivo", "licencia", "fuente")
_COMO_CONVERTIR = "ffmpeg -i original -c:a pcm_s16le archivo.wav"
_QUE_ES = {
    "sonido": "el sonido de la lista de planos al que acompaña, escrito igual",
    "archivo": 'el audio WAV, desde la carpeta del episodio, como "sonido/olfateo.wav"',
    "licencia": 'la licencia con la que se puede usar, como "CC0 1.0" o "CC BY 4.0, de Autor"',
    "fuente": "de dónde sale: la dirección de la página de la que se descargó",
}


@dataclass(frozen=True)
class Pista:
    """Una capa de audio de música o de efecto, colocada en la línea de tiempo."""

    id: str
    pista: int  # la pista de HyperFrames: PISTA_DE_LA_MUSICA o PISTA_DE_LOS_EFECTOS
    archivo: str  # desde la carpeta del episodio
    inicio: int  # fotograma en que empieza a sonar
    final: int  # primer fotograma en que ya no suena
    recorte: float  # segundos del principio del archivo que no suenan (data-media-start)
    volumen: float  # 1 = tal como está el archivo


@dataclass(frozen=True)
class _Entrada:
    """Una música o un efecto de sonido.toml."""

    nombre: str  # para los mensajes: «la música» o «el efecto «olfateo»»
    archivo: str  # la licencia y la fuente se comprueban al leer, pero la herramienta no las usa


@dataclass(frozen=True)
class _Audio:
    duracion: float  # segundos
    nivel: float  # dBFS de media (-inf si es silencio)
    golpe: float  # segundo de la muestra más fuerte


class _ErrorDeAudio(Exception):
    pass


def colocar_sonido(carpeta: Path, linea: LineaDeTiempo, planos: list[Plano]) -> tuple[list[Pista], Informe]:
    """La música y los efectos del episodio, colocados; con lo que falta (avisos) y lo que impide montar (errores)."""
    informe = Informe()
    if not (carpeta / ARCHIVO).is_file():
        informe.avisos.append(
            f"El episodio no tiene música ni efectos: falta {ARCHIVO} en su carpeta "
            "(formato en docs/musica-y-efectos.md)."
        )
        return [], informe
    musica, efectos = _leer(carpeta / ARCHIVO, informe)
    if informe.errores:
        return [], informe
    if musica is None:
        informe.avisos.append(f"{ARCHIVO}: el episodio no tiene música ([musica]).")
    usados = _efectos_de_los_planos(planos, efectos, informe)
    entradas = ([musica] if musica else []) + list(dict.fromkeys(entrada for _, entrada in usados))
    audios = {entrada: audio for entrada in entradas if (audio := _leer_audio(carpeta, entrada, informe))}
    if informe.errores:
        return [], informe

    pistas = []
    if musica is not None:
        pista = _colocar_la_musica(musica.archivo, audios[musica], _nivel_de_las_voces(carpeta, linea, informe), linea)
        pistas.append(pista)
        if pista.inicio > 0:
            informe.avisos.append(
                f"{ARCHIVO}: la música dura menos que el episodio, así que entra en el fotograma {pista.inicio} "
                "para acabar en el último."
            )
    inicios = {plano.id: plano.inicio for plano in linea.planos}
    for numero, (plano, entrada) in enumerate(usados, start=1):
        evento = inicios[plano.id]
        pistas.append(_colocar_el_efecto(f"efecto-{numero:02d}", entrada.archivo, audios[entrada], evento, linea))
    return pistas, informe


def _leer(archivo: Path, informe: Informe) -> tuple[_Entrada | None, dict[str, _Entrada]]:
    """La música y los efectos (por su sonido, sin mayúsculas) que anota sonido.toml."""
    try:
        datos = tomllib.loads(archivo.read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as error:
        informe.errores.append(f"{ARCHIVO}: no entiendo el archivo ({error}).")
        return None, {}
    for clave in datos:
        if clave not in ("musica", "efecto"):
            informe.errores.append(f"{ARCHIVO}: no conozco «{clave}»; solo pueden ir [musica] y [[efecto]].")
    musica = _entrada(datos["musica"], "la música", (), informe) if "musica" in datos else None
    tablas = datos.get("efecto", [])
    if not isinstance(tablas, list):
        informe.errores.append(f"{ARCHIVO}: cada efecto empieza con [[efecto]], con dos corchetes.")
        tablas = []
    efectos: dict[str, _Entrada] = {}
    for numero, tabla in enumerate(tablas, start=1):
        sonido = tabla.get("sonido") if isinstance(tabla, dict) else None
        nombre = f"el efecto «{sonido}»" if isinstance(sonido, str) else f"el efecto número {numero}"
        entrada = _entrada(tabla, nombre, ("sonido",), informe)
        if entrada is None or not isinstance(sonido, str):
            continue
        if _clave(sonido) in efectos:
            informe.errores.append(f"{ARCHIVO}: hay dos efectos para el sonido «{sonido}»; cada sonido lleva uno.")
        efectos[_clave(sonido)] = entrada
    return musica, efectos


def _entrada(tabla: object, nombre: str, otros: tuple[str, ...], informe: Informe) -> _Entrada | None:
    """Una música o un efecto con sus campos, o None si no sigue el formato (los errores van al informe)."""
    if not isinstance(tabla, dict):
        informe.errores.append(f"{ARCHIVO}, {nombre}: no sigue el formato de docs/musica-y-efectos.md.")
        return None
    campos = otros + _CAMPOS
    errores = [
        f"no conozco el campo «{clave}»; los que lleva son {', '.join(campos)}." for clave in tabla if clave not in campos
    ]
    errores += [
        f"falta «{clave}» o está vacío: es {_QUE_ES[clave]}. Sin su licencia y su fuente no se puede usar."
        for clave in campos
        if not (isinstance(tabla.get(clave), str) and tabla[clave].strip())
    ]
    informe.errores += [f"{ARCHIVO}, {nombre}: {error}" for error in errores]
    if errores:
        return None
    return _Entrada(nombre, tabla["archivo"])


def _clave(sonido: str) -> str:
    return " ".join(sonido.casefold().split())


def _efectos_de_los_planos(
    planos: list[Plano], efectos: dict[str, _Entrada], informe: Informe
) -> list[tuple[Plano, _Entrada]]:
    """El efecto de cada plano que pide un sonido; avisa de los sonidos que no tienen efecto."""
    usados = []
    for plano in planos:
        if plano.sonido is None:
            continue
        entrada = efectos.get(_clave(plano.sonido))
        if entrada is None:
            informe.avisos.append(
                f"El plano «{plano.id}» pide el sonido «{plano.sonido}», que no tiene efecto en {ARCHIVO}: va sin él."
            )
        else:
            usados.append((plano, entrada))
    return usados


def _leer_audio(carpeta: Path, entrada: _Entrada, informe: Informe) -> _Audio | None:
    """El audio de la entrada, si está en la carpeta del episodio y se puede leer."""
    donde = f"{ARCHIVO}, {entrada.nombre}"
    archivo = (carpeta / entrada.archivo).resolve()
    if not archivo.is_relative_to(carpeta.resolve()):
        informe.errores.append(f"{donde}: «{entrada.archivo}» tiene que estar dentro de la carpeta del episodio.")
        return None
    if not archivo.is_file():
        informe.errores.append(f"{donde}: «{entrada.archivo}» no está en la carpeta del episodio.")
        return None
    try:
        return _analizar(archivo)
    except _ErrorDeAudio as error:
        informe.errores.append(f"{donde}: «{entrada.archivo}» {error}")
        return None


def _analizar(archivo: Path) -> _Audio:
    muestras, canales, por_segundo = _leer_wav(archivo)
    if not muestras:
        raise _ErrorDeAudio("está vacío.")
    alta, baja = max(muestras), min(muestras)
    golpe = (muestras.index(alta) if alta >= -baja else muestras.index(baja)) // canales
    return _Audio(len(muestras) / canales / por_segundo, _nivel([muestras]), golpe / por_segundo)


def _leer_wav(archivo: Path) -> tuple["array[int]", int, int]:
    """Las muestras (intercaladas por canal), los canales y las muestras por segundo de un WAV de 16 bits."""
    try:
        with wave.open(str(archivo), "rb") as audio:
            if audio.getsampwidth() != 2:
                raise _ErrorDeAudio(f"no es un WAV de 16 bits; conviértelo con «{_COMO_CONVERTIR}».")
            datos = audio.readframes(audio.getnframes())
            canales, por_segundo = audio.getnchannels(), audio.getframerate()
    except OSError as error:
        raise _ErrorDeAudio("no se puede abrir.") from error
    except (wave.Error, EOFError) as error:
        raise _ErrorDeAudio(f"no es un WAV que se pueda leer; conviértelo con «{_COMO_CONVERTIR}».") from error
    muestras = array("h", datos[: len(datos) - len(datos) % 2])
    if sys.byteorder == "big":
        muestras.byteswap()  # un WAV guarda las muestras con el byte bajo primero
    return muestras, canales, por_segundo


def _nivel(audios: list["array[int]"]) -> float:
    """El nivel medio (RMS) de los audios juntos, en dBFS; -inf si son silencio."""
    cuadrados = sum(sum(map(operator.mul, muestras, muestras)) for muestras in audios)
    if not cuadrados:
        return -math.inf
    cuantas = sum(len(muestras) for muestras in audios)
    return 20 * math.log10(math.sqrt(cuadrados / cuantas) / _MAXIMO)


def _nivel_de_las_voces(carpeta: Path, linea: LineaDeTiempo, informe: Informe) -> float:
    """El nivel medio de todas las voces; si son silencio o no se pueden leer, el de las de Kokoro."""
    try:
        nivel = _nivel([_leer_wav(carpeta / frase.audio)[0] for frase in linea.frases])
    except _ErrorDeAudio as error:
        informe.avisos.append(
            f"No he podido medir el nivel de las voces (una {error}); la música se baja como si fueran de Kokoro, "
            f"a {NIVEL_DE_LAS_VOCES_EN_SILENCIO:g} dBFS. Escúchala por si tapa a alguna voz."
        )
        return NIVEL_DE_LAS_VOCES_EN_SILENCIO
    return nivel if nivel > -math.inf else NIVEL_DE_LAS_VOCES_EN_SILENCIO


def _colocar_la_musica(archivo: str, audio: _Audio, voces: float, linea: LineaDeTiempo) -> Pista:
    """Su final, en el último fotograma; si es más larga que el episodio, se recorta por el principio."""
    fps, total = linea.fps, linea.total
    volumen = 1.0
    if audio.nivel > -math.inf:
        volumen = min(1.0, 10 ** ((voces - DEBAJO_DE_LAS_VOCES - audio.nivel) / 20))
    if audio.duracion * fps >= total:
        return Pista("musica", PISTA_DE_LA_MUSICA, archivo, 0, total, audio.duracion - total / fps, volumen)
    # Entra en el fotograma que la hace acabar dentro del último (como mucho, justo en su final).
    inicio = math.floor(total - audio.duracion * fps + 1e-9)
    return Pista("musica", PISTA_DE_LA_MUSICA, archivo, inicio, total, 0.0, volumen)


def _colocar_el_efecto(id_: str, archivo: str, audio: _Audio, evento: int, linea: LineaDeTiempo) -> Pista:
    """Su golpe, en mitad del fotograma del evento.

    HyperFrames ajusta al fotograma el inicio de cada capa, así que la capa empieza en un fotograma entero y el
    ajuste fino se hace recortando el principio del archivo. Si el golpe está en el primer medio fotograma del
    archivo, la capa empieza en el fotograma del evento sin recorte, y el golpe cae en su primera mitad.
    """
    fps = linea.fps
    golpe = (evento + 0.5) / fps
    inicio = min(evento, max(0, math.ceil((golpe - audio.golpe) * fps - 1e-9)))
    recorte = max(0.0, inicio / fps + audio.golpe - golpe)
    final = min(linea.total, inicio + math.ceil((audio.duracion - recorte) * fps))
    return Pista(id_, PISTA_DE_LOS_EFECTOS, archivo, inicio, final, recorte, 1.0)
