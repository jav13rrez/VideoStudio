"""Enchufe de voz: cada personaje habla con el proveedor y la voz que le asigna la configuración del estudio.

Un proveedor recibe una frase y una voz, deja el audio de la frase y da su duración y las marcas de
tiempo de cada palabra. Para añadir un proveedor, se escribe su clase y se apunta en PROVEEDORES.
"""

import json
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from estudio.configuracion import ARCHIVO, Configuracion, Voz
from estudio.guion import Frase

CARPETA = "voces"


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


PROVEEDORES: dict[str, ProveedorDeVoz] = {"falso": ProveedorFalso()}


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
                f'{ARCHIVO} no dice con qué voz habla «{personaje}»: añade en [voces] la línea '
                f'{personaje} = {{ proveedor = "falso", voz = "…" }}.'
            )
        elif voz.proveedor not in PROVEEDORES:
            errores.append(
                f"{ARCHIVO}: «{personaje}» usa el proveedor de voz «{voz.proveedor}», que no existe; "
                f"los que hay son: {', '.join(PROVEEDORES)}."
            )
    if errores:
        return errores
    (carpeta / CARPETA).mkdir(exist_ok=True)
    for numero, frase in enumerate(frases, start=1):
        voz = configuracion.voces[frase.personaje]
        audio = PROVEEDORES[voz.proveedor].generar(frase, voz.voz, carpeta / ruta_del_audio(numero))
        marcas = {**_receta(frase, voz), **asdict(audio)}
        (carpeta / _ruta_de_las_marcas(numero)).write_text(
            json.dumps(marcas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return []


def leer_voces(carpeta: Path, frases: list[Frase], configuracion: Configuracion) -> tuple[list[Audio], list[str]]:
    """La duración y las marcas de tiempo del audio de cada frase, o el error si faltan o están desactualizadas."""
    audios = []
    desfasadas = []
    for numero, frase in enumerate(frases, start=1):
        try:
            marcas = json.loads((carpeta / _ruta_de_las_marcas(numero)).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            marcas = {}
        receta = _receta(frase, configuracion.voces.get(frase.personaje))
        if {clave: marcas.get(clave) for clave in receta} != receta:
            desfasadas.append(frase.linea)
            continue
        audios.append(Audio(marcas["duracion"], [MarcaDePalabra(**palabra) for palabra in marcas["palabras"]]))
    if not desfasadas:
        return audios, []
    if len(desfasadas) == len(frases):
        cuales = "Faltan o están desactualizadas las voces de todas las frases"
    elif len(desfasadas) == 1:
        cuales = f"Falta o está desactualizada la voz de la frase de la línea {desfasadas[0]}"
    else:
        lineas = ", ".join(map(str, desfasadas[:-1])) + f" y {desfasadas[-1]}"
        cuales = f"Faltan o están desactualizadas las voces de las frases de las líneas {lineas}"
    return [], [
        f"{cuales}. Genéralas con «uv run estudio generar-voces {carpeta}»; hay que volver a hacerlo "
        f"cada vez que cambia una frase o la voz de su personaje en {ARCHIVO}."
    ]


def _receta(frase: Frase, voz: Voz | None) -> dict[str, str | None]:
    """Lo que decide cómo suena una frase: si algo de esto cambia, su audio ya no vale."""
    return {
        "personaje": frase.personaje,
        "texto": frase.texto,
        "proveedor": voz.proveedor if voz else None,
        "voz": voz.voz if voz else None,
    }
