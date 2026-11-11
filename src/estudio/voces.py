"""Enchufe de voz: cada personaje habla con el proveedor y la voz que le asigna la configuración del estudio.

Un proveedor recibe una frase y una voz, deja el audio de la frase y da su duración y las marcas de
tiempo de cada palabra. Para añadir un proveedor, se escribe su clase y se apunta en PROVEEDORES.
"""

import base64
import json
import os
import shutil
import urllib.error
import urllib.parse
import urllib.request
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from estudio import alineacion, hyperframes
from estudio.configuracion import ARCHIVO as ARCHIVO_DE_CONFIGURACION
from estudio.configuracion import Configuracion, Voz
from estudio.guion import Frase

CARPETA = "voces"
GRABACIONES = "grabaciones"  # donde deja el creador sus audios, uno por frase, junto a voces/
# El entorno de Python con kokoro-onnx y soundfile que usa HyperFrames para Kokoro (ver DEBT_TECH.md).
PYTHON_DE_KOKORO = Path.home() / ".local/share/estudio/kokoro/bin/python"


class ErrorDeVoz(Exception):
    pass


@dataclass(frozen=True)
class MarcaDePalabra:
    texto: str
    inicio: float  # segundos desde el principio del audio
    final: float


@dataclass(frozen=True)
class Audio:
    duracion: float  # segundos
    palabras: list[MarcaDePalabra]  # una por palabra de la frase, en orden


class ProveedorDeVoz(Protocol):
    def generar(self, frase: Frase, voz: str, destino: Path) -> Audio:
        """Deja en destino el audio de la frase dicha con esa voz."""
        ...


class ProveedorFalso:
    """Para los tests: silencio a 3 palabras por segundo, con una marca de tiempo por palabra."""

    PALABRAS_POR_SEGUNDO = 3
    MUESTRAS_POR_SEGUNDO = 24_000

    def generar(self, frase: Frase, voz: str, destino: Path) -> Audio:
        palabras = frase.palabras
        muestras = len(palabras) * self.MUESTRAS_POR_SEGUNDO // self.PALABRAS_POR_SEGUNDO
        with wave.open(str(destino), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)  # 16 bits
            audio.setframerate(self.MUESTRAS_POR_SEGUNDO)
            audio.writeframes(bytes(2 * muestras))
        return Audio(
            duracion=len(palabras) / self.PALABRAS_POR_SEGUNDO,
            palabras=[
                MarcaDePalabra(palabra.texto, i / self.PALABRAS_POR_SEGUNDO, (i + 1) / self.PALABRAS_POR_SEGUNDO)
                for i, palabra in enumerate(palabras)
            ],
        )


def _alinear(frase: Frase, audio: Path) -> Audio:
    """La duración del audio y las marcas de sus palabras, sacadas con Whisper."""
    palabras = [palabra.texto for palabra in frase.palabras]
    tiempos = alineacion.marcas(palabras, audio)
    return Audio(
        duracion=alineacion.duracion(audio),
        palabras=[MarcaDePalabra(texto, inicio, final) for texto, (inicio, final) in zip(palabras, tiempos)],
    )


class ProveedorKokoro:
    """Voz gratuita generada en el propio PC con Kokoro, por HyperFrames. Voces en español: em_santa, em_alex y
    ef_dora. Kokoro no da marcas por palabra: las saca Whisper."""

    def generar(self, frase: Frase, voz: str, destino: Path) -> Audio:
        entorno = dict(os.environ)
        if "HYPERFRAMES_PYTHON" not in entorno and PYTHON_DE_KOKORO.is_file():
            entorno["HYPERFRAMES_PYTHON"] = str(PYTHON_DE_KOKORO)
        try:
            hyperframes.ejecutar(["tts", frase.dicho, "-o", destino.name, "--voice", voz], destino.parent, entorno)
            return _alinear(frase, destino)
        except (hyperframes.ErrorDeHyperFrames, alineacion.ErrorDeAlineacion) as error:
            raise ErrorDeVoz(f"Kokoro no ha podido hacer la voz «{voz}»: {error}") from error


class ProveedorGrabacion:
    """Los audios que graba el creador: grabaciones/frase-01.wav para la frase 1, y así, en la carpeta del
    episodio. La voz no cambia nada: dice quién graba. Las marcas por palabra las saca Whisper."""

    def generar(self, frase: Frase, voz: str, destino: Path) -> Audio:
        origen = destino.parent.parent / GRABACIONES / destino.name
        nombre = f"{GRABACIONES}/{destino.name}"
        if not origen.is_file():
            raise ErrorDeVoz(f"falta la grabación {nombre}: graba la frase «{frase.dicho}» y déjala con ese nombre.")
        try:
            alineacion.duracion(origen)
            shutil.copy(origen, destino)
            return _alinear(frase, destino)
        except alineacion.ErrorDeAlineacion as error:
            raise ErrorDeVoz(f"la grabación {nombre}: {error}") from error


class ProveedorElevenLabs:
    """Voz de pago de ElevenLabs (elevenlabs.io). La voz es el ID de la voz en ElevenLabs. La clave va en
    ELEVENLABS_API_KEY, en el entorno o en el archivo .env del estudio. ElevenLabs da el tiempo de cada letra,
    y de ahí salen las marcas por palabra; si no cuadran con el guion, las saca Whisper."""

    MODELO = "eleven_multilingual_v2"
    MUESTRAS_POR_SEGUNDO = 24_000  # audio PCM de 16 bits y un canal
    VARIABLE_DE_LA_CLAVE = "ELEVENLABS_API_KEY"
    SEGUNDOS_DE_ESPERA = 120

    def generar(self, frase: Frase, voz: str, destino: Path) -> Audio:
        clave = _clave(self.VARIABLE_DE_LA_CLAVE, destino)
        if not clave:
            raise ErrorDeVoz(
                f"falta la clave de ElevenLabs: pégala en el archivo .env del estudio, en la línea "
                f"{self.VARIABLE_DE_LA_CLAVE}=… (la lista está en .env.example)."
            )
        respuesta = self._pedir(frase.dicho, voz, clave)
        try:
            pcm = base64.b64decode(respuesta["audio_base64"])
            alineacion_de_letras = respuesta.get("alignment") or {}
        except (KeyError, TypeError, ValueError) as error:
            raise ErrorDeVoz(f"ElevenLabs ha devuelto una respuesta que no se entiende ({error}).") from error
        with wave.open(str(destino), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(self.MUESTRAS_POR_SEGUNDO)
            audio.writeframes(pcm)
        marcas = _marcas_por_letras(alineacion_de_letras)
        if len(marcas) != len(frase.palabras):
            return _alinear(frase, destino)
        return Audio(
            duracion=len(pcm) / 2 / self.MUESTRAS_POR_SEGUNDO,
            palabras=[MarcaDePalabra(p.texto, inicio, final) for p, (inicio, final) in zip(frase.palabras, marcas)],
        )

    def _pedir(self, texto: str, voz: str, clave: str) -> dict[str, Any]:
        base = os.environ.get("ELEVENLABS_URL", "https://api.elevenlabs.io")
        url = (
            f"{base}/v1/text-to-speech/{urllib.parse.quote(voz)}/with-timestamps"
            f"?output_format=pcm_{self.MUESTRAS_POR_SEGUNDO}"
        )
        peticion = urllib.request.Request(
            url,
            data=json.dumps({"text": texto, "model_id": self.MODELO}).encode(),
            headers={"xi-api-key": clave, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(peticion, timeout=self.SEGUNDOS_DE_ESPERA) as respuesta:
                datos: dict[str, Any] = json.loads(respuesta.read())
                return datos
        except urllib.error.HTTPError as error:
            pista = " Revisa la clave de .env y que tu plan siga activo." if error.code in (401, 403) else ""
            raise ErrorDeVoz(f"ElevenLabs ha rechazado la voz «{voz}» (código {error.code}).{pista}") from error
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            raise ErrorDeVoz(f"no se ha podido hablar con ElevenLabs ({error}). ¿Hay conexión?") from error


def _clave(variable: str, desde: Path) -> str:
    """La clave del entorno o, si no está, del primer .env que haya subiendo desde `desde`."""
    if os.environ.get(variable):
        return os.environ[variable].strip()
    for carpeta in desde.resolve().parents:
        archivo = carpeta / ".env"
        if archivo.is_file():
            for linea in archivo.read_text(encoding="utf-8").splitlines():
                nombre, igual, valor = linea.partition("=")
                if igual and nombre.strip() == variable:
                    return valor.strip().strip("'\"")
            return ""
    return ""


def _marcas_por_letras(alineacion_de_letras: dict[str, Any]) -> list[tuple[float, float]]:
    """El inicio y el final de cada palabra (lo que va entre espacios), a partir del tiempo de cada letra."""
    letras = alineacion_de_letras.get("characters") or []
    inicios = alineacion_de_letras.get("character_start_times_seconds") or []
    finales = alineacion_de_letras.get("character_end_times_seconds") or []
    marcas: list[tuple[float, float]] = []
    en_palabra = False
    for letra, inicio, final in zip(letras, inicios, finales):
        if letra.isspace():
            en_palabra = False
        elif en_palabra:
            marcas[-1] = (marcas[-1][0], float(final))
        else:
            marcas.append((float(inicio), float(final)))
            en_palabra = True
    return marcas


PROVEEDORES: dict[str, ProveedorDeVoz] = {
    "falso": ProveedorFalso(),
    "kokoro": ProveedorKokoro(),
    "grabacion": ProveedorGrabacion(),
    "elevenlabs": ProveedorElevenLabs(),
}


def ruta_del_audio(numero: int) -> str:
    """Dónde queda el audio de la frase número `numero`, dentro de la carpeta del episodio."""
    return f"{CARPETA}/frase-{numero:02d}.wav"


def _ruta_de_las_marcas(numero: int) -> str:
    return f"{CARPETA}/frase-{numero:02d}.json"


def generar_voces(carpeta: Path, frases: list[Frase], configuracion: Configuracion) -> list[str]:
    """Genera el audio de cada frase y sus marcas de tiempo; devuelve los errores que lo impiden."""
    errores = []
    for personaje in sorted({frase.personaje for frase in frases}):
        voz = configuracion.voces.get(personaje)
        if voz is None:
            errores.append(
                f'{ARCHIVO_DE_CONFIGURACION} no dice con qué voz habla «{personaje}»: añade en [voces] la línea '
                f'{personaje} = {{ proveedor = "falso", voz = "…" }}.'
            )
        elif voz.proveedor not in PROVEEDORES:
            errores.append(
                f"{ARCHIVO_DE_CONFIGURACION}: «{personaje}» usa el proveedor de voz «{voz.proveedor}», que no existe; "
                f"los que hay son: {', '.join(PROVEEDORES)}."
            )
    if errores:
        return errores
    (carpeta / CARPETA).mkdir(exist_ok=True)
    for numero, frase in enumerate(frases, start=1):
        voz = configuracion.voces[frase.personaje]
        try:
            audio = PROVEEDORES[voz.proveedor].generar(frase, voz.voz, carpeta / ruta_del_audio(numero))
        except ErrorDeVoz as error:
            return [f"guion.md, línea {frase.linea} (frase {numero}, {frase.personaje}): {error}"]
        marcas = {**_con_que_se_genero(frase, voz), **asdict(audio)}
        (carpeta / _ruta_de_las_marcas(numero)).write_text(
            json.dumps(marcas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return []


def leer_voces(carpeta: Path, frases: list[Frase], configuracion: Configuracion) -> tuple[list[Audio], list[str]]:
    """La duración y las marcas de tiempo del audio de cada frase, o el error si faltan o están desactualizadas."""
    audios = []
    desfasadas = []
    for numero, frase in enumerate(frases, start=1):
        audio = _leer_audio(carpeta, numero, frase, configuracion.voces.get(frase.personaje))
        if audio is None:
            desfasadas.append(frase.linea)
        else:
            audios.append(audio)
    if not desfasadas:
        return audios, []
    return [], [
        "Faltan o están desactualizadas las voces de las frases de estas líneas de guion.md: "
        f"{', '.join(map(str, desfasadas))}. Genéralas con «uv run estudio generar-voces {carpeta}»; "
        "hay que volver a hacerlo cada vez que cambia una frase o la voz de su personaje en "
        f"{ARCHIVO_DE_CONFIGURACION}."
    ]


def _leer_audio(carpeta: Path, numero: int, frase: Frase, voz: Voz | None) -> Audio | None:
    """El audio de la frase, si existe y se generó para esta frase con esta voz."""
    try:
        marcas = json.loads((carpeta / _ruta_de_las_marcas(numero)).read_text(encoding="utf-8"))
        origen = _con_que_se_genero(frase, voz)
        if {clave: marcas.get(clave) for clave in origen} != origen:
            return None
        audio = Audio(marcas["duracion"], [MarcaDePalabra(**palabra) for palabra in marcas["palabras"]])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None  # no está, o no es lo que dejó generar-voces
    if len(audio.palabras) != len(frase.palabras) or not (carpeta / ruta_del_audio(numero)).is_file():
        return None
    return audio


def _con_que_se_genero(frase: Frase, voz: Voz | None) -> dict[str, str | None]:
    """Lo que decide cómo suena una frase: si algo de esto cambia, su audio ya no vale."""
    return {
        "personaje": frase.personaje,
        "texto": frase.dicho,
        "proveedor": voz.proveedor if voz else None,
        "voz": voz.voz if voz else None,
    }
