"""Voz de ElevenLabs: cada frase se pide a su servicio de texto a voz, con las marcas de tiempo por letra.

No se llama a ElevenLabs: un servidor local hace de él (ELEVENLABS_URL apunta a ese servidor). Su voz da
0,05 s por letra y devuelve el audio en PCM de 24 kHz, como lo pide la herramienta.
"""

import base64
import json
import threading
import wave
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from ayudas import Estudio, cambiar

PERRO = 'Perro = { proveedor = "falso", voz = "perro" }'
TUTOR = 'Tutor = { proveedor = "falso", voz = "tutor" }'
SEGUNDOS_POR_LETRA = 0.05
MUESTRAS_POR_SEGUNDO = 24_000


@dataclass
class ElevenLabsFalso:
    url: str
    peticiones: list[dict[str, Any]] = field(default_factory=list)
    estado: int = 200


def _respuesta(texto: str) -> dict[str, Any]:
    letras = list(texto)
    inicios = [i * SEGUNDOS_POR_LETRA for i in range(len(letras))]
    muestras = int(len(letras) * SEGUNDOS_POR_LETRA * MUESTRAS_POR_SEGUNDO)
    return {
        "audio_base64": base64.b64encode(bytes(2 * muestras)).decode(),
        "alignment": {
            "characters": letras,
            "character_start_times_seconds": inicios,
            "character_end_times_seconds": [inicio + SEGUNDOS_POR_LETRA for inicio in inicios],
        },
    }


@pytest.fixture
def elevenlabs(monkeypatch: pytest.MonkeyPatch) -> Iterator[ElevenLabsFalso]:
    falso = ElevenLabsFalso(url="")

    class Atiende(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            falso.peticiones.append({"ruta": self.path, "clave": self.headers.get("xi-api-key"), "cuerpo": cuerpo})
            datos = json.dumps(_respuesta(cuerpo["text"]) if falso.estado == 200 else {"detail": "mal"}).encode()
            self.send_response(falso.estado)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)

        def log_message(self, *argumentos: Any) -> None:
            pass

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), Atiende)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    falso.url = f"http://127.0.0.1:{servidor.server_address[1]}"
    monkeypatch.setenv("ELEVENLABS_URL", falso.url)
    monkeypatch.setenv("ELEVENLABS_API_KEY", "clave-de-prueba")
    yield falso
    servidor.shutdown()


def con_elevenlabs(episodio: Path) -> None:
    configuracion = episodio.parent / "estudio.toml"
    cambiar(configuracion, PERRO, 'Perro = { proveedor = "elevenlabs", voz = "voz-del-perro" }')
    cambiar(configuracion, TUTOR, 'Tutor = { proveedor = "elevenlabs", voz = "voz-del-tutor" }')


def marcas(episodio: Path, numero: int) -> dict[str, Any]:
    datos: dict[str, Any] = json.loads((episodio / "voces" / f"frase-{numero:02d}.json").read_text(encoding="utf-8"))
    return datos


def test_con_elevenlabs_cada_frase_se_pide_con_la_voz_de_su_personaje_y_la_clave(
    estudio: Estudio, episodio: Path, elevenlabs: ElevenLabsFalso
) -> None:
    con_elevenlabs(episodio)

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 0, resultado.salida
    assert len(elevenlabs.peticiones) == 17
    primera, segunda = elevenlabs.peticiones[:2]
    assert primera["ruta"].startswith("/v1/text-to-speech/voz-del-perro/with-timestamps")
    assert "output_format=pcm_24000" in primera["ruta"]
    assert segunda["ruta"].startswith("/v1/text-to-speech/voz-del-tutor/with-timestamps")
    assert primera["clave"] == "clave-de-prueba"
    assert primera["cuerpo"]["text"] == "¿Sabes por qué te huelo los zapatos cuando vuelves a casa?"
    assert primera["cuerpo"]["model_id"] == "eleven_multilingual_v2"


def test_el_audio_de_elevenlabs_queda_en_wav_con_las_marcas_de_sus_letras(
    estudio: Estudio, episodio: Path, elevenlabs: ElevenLabsFalso
) -> None:
    con_elevenlabs(episodio)

    assert estudio("generar-voces", episodio).codigo == 0

    texto = "¿Sabes por qué te huelo los zapatos cuando vuelves a casa?"
    with wave.open(str(episodio / "voces" / "frase-01.wav")) as audio:
        assert audio.getframerate() == MUESTRAS_POR_SEGUNDO
        assert audio.getnchannels() == 1
        assert audio.getsampwidth() == 2
    frase = marcas(episodio, 1)
    assert frase["proveedor"] == "elevenlabs"
    assert frase["duracion"] == pytest.approx(len(texto) * SEGUNDOS_POR_LETRA)
    palabras = frase["palabras"]
    assert [palabra["texto"] for palabra in palabras][:3] == ["¿Sabes", "por", "qué"]
    # «¿Sabes» son las letras 0-5; «por», las 7-9 (la 6 es el espacio).
    assert palabras[0]["inicio"] == pytest.approx(0)
    assert palabras[0]["final"] == pytest.approx(6 * SEGUNDOS_POR_LETRA)
    assert palabras[1]["inicio"] == pytest.approx(7 * SEGUNDOS_POR_LETRA)
    assert palabras[1]["final"] == pytest.approx(10 * SEGUNDOS_POR_LETRA)
    assert estudio("cronometrar", episodio).codigo == 0


def test_la_clave_se_lee_del_archivo_env_del_estudio(
    estudio: Estudio, episodio: Path, elevenlabs: ElevenLabsFalso, monkeypatch: pytest.MonkeyPatch
) -> None:
    con_elevenlabs(episodio)
    monkeypatch.delenv("ELEVENLABS_API_KEY")
    (episodio.parent / ".env").write_text("# claves\nELEVENLABS_API_KEY=clave-del-env\n", encoding="utf-8")

    assert estudio("generar-voces", episodio).codigo == 0

    assert elevenlabs.peticiones[0]["clave"] == "clave-del-env"


def test_error_si_no_hay_clave_de_elevenlabs(
    estudio: Estudio, episodio: Path, elevenlabs: ElevenLabsFalso, monkeypatch: pytest.MonkeyPatch
) -> None:
    con_elevenlabs(episodio)
    monkeypatch.delenv("ELEVENLABS_API_KEY")

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert "ELEVENLABS_API_KEY" in resultado.salida
    assert ".env" in resultado.salida
    assert elevenlabs.peticiones == []


def test_error_claro_si_elevenlabs_rechaza_la_clave(
    estudio: Estudio, episodio: Path, elevenlabs: ElevenLabsFalso
) -> None:
    con_elevenlabs(episodio)
    elevenlabs.estado = 401

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert "401" in resultado.salida
    assert "clave" in resultado.salida
