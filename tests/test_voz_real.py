"""Voz real: Kokoro por HyperFrames y las grabaciones del creador, con las marcas por palabra de Whisper.

No se ejecutan Kokoro ni Whisper: tests/programas/npx hace de HyperFrames. Su voz habla a 0,4 s por palabra
y su transcripción escribe los números como Whisper («trescientos» sale «300»).
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from ayudas import Estudio, cambiar

PROGRAMAS = Path(__file__).parent / "programas"
PERRO = 'Perro = { proveedor = "falso", voz = "perro" }'
TUTOR = 'Tutor = { proveedor = "falso", voz = "tutor" }'


@pytest.fixture
def npx(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Pone el npx falso delante en el PATH; devuelve la carpeta donde apunta sus llamadas."""
    carpeta = tmp_path / "npx-falso"
    carpeta.mkdir()
    monkeypatch.setenv("NPX_FALSO", str(carpeta))
    monkeypatch.setenv("PATH", f"{PROGRAMAS}{os.pathsep}{os.environ['PATH']}")
    return carpeta


def llamadas(npx: Path, orden: str) -> list[list[str]]:
    archivo = npx / "llamadas.jsonl"
    if not archivo.exists():
        return []
    todas = [json.loads(linea) for linea in archivo.read_text(encoding="utf-8").splitlines()]
    return [llamada for llamada in todas if llamada[2] == orden]


def marcas(episodio: Path, numero: int) -> dict[str, Any]:
    datos: dict[str, Any] = json.loads((episodio / "voces" / f"frase-{numero:02d}.json").read_text(encoding="utf-8"))
    return datos


def con_kokoro(episodio: Path) -> None:
    configuracion = episodio.parent / "estudio.toml"
    cambiar(configuracion, PERRO, 'Perro = { proveedor = "kokoro", voz = "em_santa" }')
    cambiar(configuracion, TUTOR, 'Tutor = { proveedor = "kokoro", voz = "em_alex" }')


def test_con_kokoro_cada_frase_tiene_su_audio_con_la_voz_de_su_personaje(
    estudio: Estudio, episodio: Path, npx: Path
) -> None:
    con_kokoro(episodio)

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 0, resultado.salida
    voces = llamadas(npx, "tts")
    assert len(voces) == 17
    # Frase 1, del Perro; frase 2, del Tutor. Se dice el texto sin marcas.
    assert voces[0][3] == "¿Sabes por qué te huelo los zapatos cuando vuelves a casa?"
    assert voces[0][voces[0].index("--voice") + 1] == "em_santa"
    assert voces[1][voces[1].index("--voice") + 1] == "em_alex"
    assert len(list((episodio / "voces").glob("*.wav"))) == 17
    # Las marcas por palabra se piden a Whisper en español, con el modelo multilingüe.
    transcripciones = llamadas(npx, "transcribe")
    assert len(transcripciones) == 17
    assert all({"--model", "small", "--language", "es"} <= set(llamada) for llamada in transcripciones)
    assert all(llamada[1].startswith("hyperframes@") for llamada in voces + transcripciones)


def test_las_marcas_por_palabra_de_kokoro_son_las_del_guion_con_los_tiempos_de_whisper(
    estudio: Estudio, episodio: Path, npx: Path
) -> None:
    con_kokoro(episodio)

    assert estudio("generar-voces", episodio).codigo == 0

    frase = marcas(episodio, 1)
    assert frase["proveedor"] == "kokoro"
    assert frase["duracion"] == pytest.approx(11 * 0.4)
    assert frase["palabras"][0] == {"texto": "¿Sabes", "inicio": 0.0, "final": 0.4}
    assert frase["palabras"][-1] == {"texto": "casa?", "inicio": 4.0, "final": 4.4}


def test_las_palabras_que_whisper_escribe_distinto_toman_su_tiempo_igualmente(
    estudio: Estudio, episodio: Path, npx: Path
) -> None:
    con_kokoro(episodio)

    assert estudio("generar-voces", episodio).codigo == 0

    # Frase 5: «Tengo hasta *trescientos millones* … Tú tienes unos *seis millones*.»; Whisper da «300» y «6».
    palabras = marcas(episodio, 5)["palabras"]
    assert palabras[2] == {"texto": "trescientos", "inicio": 0.8, "final": 1.2}
    assert palabras[11] == {"texto": "seis", "inicio": 4.4, "final": 4.8}


def test_dos_palabras_que_whisper_junta_se_reparten_su_tiempo(estudio: Estudio, episodio: Path, npx: Path) -> None:
    con_kokoro(episodio)

    assert estudio("generar-voces", episodio).codigo == 0

    # Frase 10: «¿Y si te meto prisa?»; Whisper oye «Ysi» de 0 a 0,4 s, que se reparte por letras (1 y 2).
    palabras = marcas(episodio, 10)["palabras"]
    assert palabras[0] == {"texto": "¿Y", "inicio": 0.0, "final": 0.133}
    assert palabras[1] == {"texto": "si", "inicio": 0.133, "final": 0.4}
    assert palabras[2] == {"texto": "te", "inicio": 0.4, "final": 0.8}


def test_una_palabra_que_whisper_se_salta_toma_el_hueco_entre_sus_vecinas(
    estudio: Estudio, episodio: Path, npx: Path
) -> None:
    con_kokoro(episodio)

    assert estudio("generar-voces", episodio).codigo == 0

    # Frase 13: «Exacto. Y yo ni siquiera…»; Whisper no oye el «ni». Aquí sus vecinas se tocan (0,8 s y 0,8 s),
    # así que el «ni» queda en ese instante, sin desordenar las demás.
    palabras = marcas(episodio, 13)["palabras"]
    assert palabras[2] == {"texto": "yo", "inicio": 0.8, "final": 1.2}
    assert palabras[3] == {"texto": "ni", "inicio": 1.2, "final": 1.2}
    assert palabras[4] == {"texto": "siquiera", "inicio": 1.2, "final": 1.6}
    assert len(palabras) == 9


def test_con_kokoro_se_cronometra_igual_que_con_el_proveedor_falso(
    estudio: Estudio, episodio: Path, npx: Path
) -> None:
    con_kokoro(episodio)
    assert estudio("generar-voces", episodio).codigo == 0

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 0, resultado.salida
    linea = json.loads((episodio / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    # Frase 1: 11 palabras a 0,4 s = 4,4 s = 132 fotogramas.
    assert (linea["frases"][0]["inicio"], linea["frases"][0]["final"]) == (0, 132)


def test_error_y_no_un_fallo_si_hyperframes_no_puede_generar_la_voz(
    estudio: Estudio, episodio: Path, npx: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    con_kokoro(episodio)
    monkeypatch.setenv("NPX_FALSO_FALLA", "1")

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "línea 3" in resultado.errores[0]  # la de la frase 1 en guion.md
    assert "Kokoro" in resultado.errores[0]


def test_error_si_no_hay_npx_para_usar_kokoro(
    estudio: Estudio, episodio: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    con_kokoro(episodio)
    monkeypatch.setenv("PATH", str(tmp_path / "sin-programas"))

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert "npx" in resultado.errores[0]
    assert "Node.js" in resultado.errores[0]


# --- Grabaciones del creador ---

FRASES_DEL_TUTOR = {
    2: "¿Porque huelen fatal?",
    4: "¿Todo eso con la nariz?",
    6: "Vale, me ganas por goleada.",
    8: "Entonces, cuando en el paseo te paras en cada farola…",
    10: "¿Y si te meto prisa?",
    12: "Así que tirar de la correa es como quitarte el periódico de las manos.",
    14: "Pero algún día tendremos que volver a casa, ¿no?",
    16: "Pues a partir de hoy, tú marcas el ritmo y yo leo contigo.",
}


def grabar(archivo: Path, texto: str) -> None:
    """Deja una «grabación» que dice el texto (la hace la voz del npx falso, que recuerda lo que dice)."""
    archivo.parent.mkdir(exist_ok=True)
    subprocess.run([str(PROGRAMAS / "npx"), "--yes", "hyperframes", "tts", texto, "-o", str(archivo)], check=True)


def con_el_tutor_grabado(episodio: Path, *, menos: int = 0) -> None:
    cambiar(episodio.parent / "estudio.toml", TUTOR, 'Tutor = { proveedor = "grabacion", voz = "creador" }')
    for numero, texto in FRASES_DEL_TUTOR.items():
        if numero != menos:
            grabar(episodio / "grabaciones" / f"frase-{numero:02d}.wav", texto)


def test_las_frases_grabadas_por_el_creador_se_usan_con_sus_marcas_por_palabra(
    estudio: Estudio, episodio: Path, npx: Path
) -> None:
    con_el_tutor_grabado(episodio)

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 0, resultado.salida
    grabada = episodio / "grabaciones" / "frase-02.wav"
    assert (episodio / "voces" / "frase-02.wav").read_bytes() == grabada.read_bytes()
    frase = marcas(episodio, 2)
    assert frase["proveedor"] == "grabacion"
    assert frase["duracion"] == pytest.approx(3 * 0.4)
    assert frase["palabras"] == [
        {"texto": "¿Porque", "inicio": 0.0, "final": 0.4},
        {"texto": "huelen", "inicio": 0.4, "final": 0.8},
        {"texto": "fatal?", "inicio": 0.8, "final": 1.2},
    ]
    # El Perro sigue con su proveedor.
    assert marcas(episodio, 1)["proveedor"] == "falso"


def test_error_si_falta_la_grabacion_de_una_frase(estudio: Estudio, episodio: Path, npx: Path) -> None:
    con_el_tutor_grabado(episodio, menos=4)

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "grabaciones/frase-04.wav" in resultado.errores[0]
    assert "línea 6" in resultado.errores[0]


def test_error_si_una_grabacion_no_dice_su_frase(estudio: Estudio, episodio: Path, npx: Path) -> None:
    con_el_tutor_grabado(episodio)
    grabar(episodio / "grabaciones" / "frase-06.wav", "Hoy no me apetece nada salir a la calle.")

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert "grabaciones/frase-06.wav" in resultado.errores[0]
    assert "no dice" in resultado.errores[0]


def test_error_si_una_grabacion_no_es_un_wav(estudio: Estudio, episodio: Path, npx: Path) -> None:
    con_el_tutor_grabado(episodio)
    (episodio / "grabaciones" / "frase-02.wav").write_bytes(b"esto no es un audio")

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert "grabaciones/frase-02.wav" in resultado.errores[0]
    assert "WAV" in resultado.errores[0]
