"""Voces de prueba y cronometraje: la herramienta ejecutada sobre carpetas de episodio de ejemplo.

Las cuentas a mano salen de dos datos:
- el proveedor de voz falso habla a 3 palabras por segundo: cada palabra dura 10 fotogramas a 30 fps;
- la configuración de los tests (tests/episodios/estudio.toml) pone 6 fotogramas de pausa entre frases.
"""

import json
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import pytest

from ayudas import CONFIGURACION, Estudio, cambiar, linea_de_tiempo


def duracion_del_audio(archivo: Path) -> float:
    with wave.open(str(archivo), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def test_el_proveedor_falso_deja_un_audio_por_frase_que_dura_lo_que_sus_palabras(
    estudio: Estudio, episodio: Path
) -> None:
    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 0
    assert resultado.errores == []
    audios = sorted((episodio / "voces").glob("*.wav"))
    assert len(audios) == 17  # 17 frases en el guion de ejemplo
    # Frase 1: «¿Sabes por qué te huelo los zapatos cuando vuelves a casa?», 11 palabras.
    assert duracion_del_audio(episodio / "voces" / "frase-01.wav") == pytest.approx(11 / 3)
    # Frase 17, el CTA: «Pídele a la App un plan de paseos hecho para tu perro.», 12 palabras.
    assert duracion_del_audio(episodio / "voces" / "frase-17.wav") == pytest.approx(12 / 3)


def test_la_linea_de_tiempo_coloca_cada_frase_en_fotogramas_con_la_pausa_entre_frases(
    estudio: Estudio, episodio: Path
) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    tramos = [(frase["inicio"], frase["final"]) for frase in linea["frases"]]
    assert len(tramos) == 17
    # Frase 1: 11 palabras → 110 fotogramas. Frase 2 («¿Porque huelen fatal?»): 3 palabras, 6 de pausa antes.
    # Frase 3: 13 palabras. Frase 4 («¿Todo eso con la nariz?»): 5 palabras.
    assert tramos[:4] == [(0, 110), (116, 146), (152, 282), (288, 338)]
    assert linea["frases"][0]["personaje"] == "Perro"
    assert linea["frases"][1]["personaje"] == "Tutor"
    assert linea["frases"][0]["audio"] == "voces/frase-01.wav"
    # 176 palabras (164 de conversación y 12 de CTA) y 16 pausas entre 17 frases: 1760 + 96.
    assert linea["total"] == 1856
    assert linea["fps"] == 30


def test_la_linea_de_tiempo_da_cada_palabra_con_sus_fotogramas_y_su_acento(
    estudio: Estudio, episodio: Path
) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    # Frase 5, que empieza en el fotograma 344 (la frase 4 acaba en el 338, más 6 de pausa):
    # «Tengo hasta *trescientos millones* de receptores de olor. Tú tienes unos *seis millones*. [fuente: nova]»
    frase = linea["frases"][4]
    assert (frase["inicio"], frase["final"]) == (344, 474)
    palabras = frase["palabras"]
    assert [palabra["texto"] for palabra in palabras] == [
        "Tengo", "hasta", "trescientos", "millones", "de", "receptores", "de", "olor.",
        "Tú", "tienes", "unos", "seis", "millones.",
    ]
    acentuadas = [palabra["texto"] for palabra in palabras if palabra["acentuada"]]
    assert acentuadas == ["trescientos", "millones", "seis", "millones."]
    assert palabras[0] == {"texto": "Tengo", "acentuada": False, "inicio": 344, "final": 354}
    assert palabras[2] == {"texto": "trescientos", "acentuada": True, "inicio": 364, "final": 374}
    assert palabras[-1] == {"texto": "millones.", "acentuada": True, "inicio": 464, "final": 474}


CTA = "[cta] Perro: Pídele a la App un plan de paseos hecho para tu perro.\n"


def test_la_linea_de_tiempo_da_el_inicio_y_el_final_del_cta(estudio: Estudio, episodio: Path) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    # El CTA es la última frase, de 12 palabras: los últimos 120 fotogramas.
    assert linea["cta"] == {"inicio": 1736, "final": 1856}


def test_un_cta_de_dos_frases_va_del_principio_de_la_primera_al_final_de_la_segunda(
    estudio: Estudio, episodio: Path
) -> None:
    cambiar(episodio / "guion.md", CTA, CTA + "[cta] Perro: Búscala hoy mismo.\n")

    linea = linea_de_tiempo(estudio, episodio)

    # La segunda frase del CTA, de 3 palabras, empieza 6 fotogramas después de la primera.
    assert linea["cta"] == {"inicio": 1736, "final": 1892}
    assert linea["total"] == 1892


def test_sin_cta_la_linea_de_tiempo_no_tiene_cta(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio / "guion.md", CTA, "")
    (episodio / "planos.toml").unlink()  # su último plano empieza en el CTA, que ya no está

    linea = linea_de_tiempo(estudio, episodio)

    assert linea["cta"] is None
    assert linea["total"] == 1856 - 6 - 120


def escribir_episodio(raiz: Path, palabras: int, pausa: int) -> Path:
    """Un episodio de dos frases con ese total de palabras, bajo un estudio con esa pausa entre frases."""
    shutil.copy(CONFIGURACION, raiz / "estudio.toml")
    cambiar(raiz / "estudio.toml", "pausa_entre_frases = 6", f"pausa_entre_frases = {pausa}")
    carpeta = raiz / "ep"
    carpeta.mkdir()
    guau = " ".join(["guau"] * (palabras - 1))
    (carpeta / "guion.md").write_text(f"[gancho] Perro: {guau}\n[remate] Tutor: Vale.\n", encoding="utf-8")
    return carpeta


@pytest.mark.parametrize(
    ("palabras", "pausa", "total", "aviso"),
    [
        (164, 9, 1649, True),  # 1640 fotogramas de voz y una pausa de 9
        (164, 10, 1650, False),
        (210, 0, 2100, False),
        (210, 1, 2101, True),
    ],
)
def test_aviso_si_el_episodio_dura_menos_de_1650_o_mas_de_2100_fotogramas(
    estudio: Estudio, tmp_path: Path, palabras: int, pausa: int, total: int, aviso: bool
) -> None:
    carpeta = escribir_episodio(tmp_path, palabras, pausa)
    estudio("generar-voces", carpeta)

    resultado = estudio("cronometrar", carpeta)

    assert resultado.codigo == 0
    assert json.loads((carpeta / "linea-de-tiempo.json").read_text(encoding="utf-8"))["total"] == total
    if aviso:
        assert len(resultado.avisos) == 1
        assert str(total) in resultado.avisos[0]
        assert "1650" in resultado.avisos[0] and "2100" in resultado.avisos[0]
    else:
        assert resultado.avisos == []


@pytest.mark.parametrize(
    ("palabras", "aviso"),
    [(8, True), (9, False), (21, False), (22, True)],  # a 10 fotogramas por palabra: 80, 90, 210 y 220
)
def test_aviso_si_el_cta_dura_menos_de_90_o_mas_de_210_fotogramas(
    estudio: Estudio, episodio: Path, palabras: int, aviso: bool
) -> None:
    guaus = " ".join(["guau"] * (palabras - 3))
    cambiar(episodio / "guion.md", "Pídele a la App un plan de paseos hecho para tu perro.", f"Pídele la App. {guaus}")
    (episodio / "planos.toml").unlink()  # sus planos no vienen al caso
    assert estudio("generar-voces", episodio).codigo == 0

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 0, resultado.salida
    del_cta = [aviso for aviso in resultado.avisos if aviso.startswith("El CTA dura")]
    if aviso:
        assert len(del_cta) == 1
        assert f"{palabras * 10} fotogramas" in del_cta[0]
        assert "entre 90 y 210 fotogramas (3-7 s)" in del_cta[0]
    else:
        assert del_cta == []


def test_error_si_se_cronometra_sin_haber_generado_las_voces(estudio: Estudio, episodio: Path) -> None:
    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "generar-voces" in resultado.errores[0]
    assert not (episodio / "linea-de-tiempo.json").exists()


def test_error_si_una_frase_cambio_despues_de_generar_su_voz(estudio: Estudio, episodio: Path) -> None:
    estudio("generar-voces", episodio)
    cambiar(episodio / "guion.md", "Tutor: ¿Porque huelen fatal?", "Tutor: ¿Porque te huelen fatal?")

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "líneas de guion.md: 4." in resultado.errores[0]
    assert "generar-voces" in resultado.errores[0]


def test_error_si_la_voz_de_un_personaje_cambio_despues_de_generar_sus_frases(
    estudio: Estudio, episodio: Path
) -> None:
    estudio("generar-voces", episodio)
    cambiar(episodio.parent / "estudio.toml", 'voz = "tutor"', 'voz = "tutor-grave"')

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    # Las frases del Tutor en el guion de ejemplo.
    assert "líneas de guion.md: 4, 6, 8, 10, 12, 14, 16, 18." in resultado.errores[0]



def test_error_si_falta_el_audio_de_una_frase(estudio: Estudio, episodio: Path) -> None:
    estudio("generar-voces", episodio)
    (episodio / "voces" / "frase-03.wav").unlink()

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "líneas de guion.md: 5." in resultado.errores[0]  # la frase 3 está en la línea 5


def test_error_y_no_un_fallo_si_las_marcas_de_una_voz_no_cuadran_con_su_frase(
    estudio: Estudio, episodio: Path
) -> None:
    estudio("generar-voces", episodio)
    marcas = episodio / "voces" / "frase-02.json"
    datos = json.loads(marcas.read_text(encoding="utf-8"))
    datos["palabras"].pop()
    marcas.write_text(json.dumps(datos), encoding="utf-8")

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "líneas de guion.md: 4." in resultado.errores[0]


def test_cambiar_solo_una_marca_de_fuente_no_obliga_a_generar_las_voces_otra_vez(
    estudio: Estudio, episodio: Path
) -> None:
    estudio("generar-voces", episodio)
    cambiar(episodio / "guion.md", " [fuente: craven]", "")

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 0, resultado.salida

TUTOR = 'Tutor = { proveedor = "falso", voz = "tutor" }'


@pytest.mark.parametrize(
    ("antes", "despues", "se_menciona"),
    [
        (TUTOR, 'Tutor = { proveedor = "doblaje", voz = "tutor" }', ["Tutor", "doblaje", "falso", "kokoro"]),
        (TUTOR + "\n", "", ["Tutor", "[voces]"]),
        ('Perro = { proveedor = "falso", voz = "perro" }', 'Perro = "falso"', ["Perro"]),
        ("[voces]", "[vocez]", ["[voces]"]),
        ("fps = 30", "fps = 0", ["fps"]),
        ("pausa_entre_frases = 6", "pausa_entre_frases = -1", ["pausa_entre_frases"]),
        ("fps = 30", "fps = treinta", ["estudio.toml"]),
    ],
)
def test_error_si_la_configuracion_del_estudio_no_cuadra(
    estudio: Estudio, episodio: Path, antes: str, despues: str, se_menciona: list[str]
) -> None:
    cambiar(episodio.parent / "estudio.toml", antes, despues)

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    for texto in se_menciona:
        assert texto in resultado.errores[0]
    assert not (episodio / "voces").exists()


def test_error_si_no_hay_configuracion_del_estudio(estudio: Estudio, episodio: Path) -> None:
    (episodio.parent / "estudio.toml").unlink()

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "estudio.toml" in resultado.errores[0]


def test_no_se_generan_voces_si_el_guion_tiene_errores(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio / "guion.md", "Tutor: ¿Porque huelen fatal?", "Gato: ¿Porque huelen fatal?")

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "Gato" in resultado.errores[0]
    assert not (episodio / "voces").exists()


def test_cambiar_la_voz_de_un_personaje_es_cambiar_su_linea_de_la_configuracion(
    estudio: Estudio, episodio: Path
) -> None:
    estudio("generar-voces", episodio)
    cambiar(episodio.parent / "estudio.toml", TUTOR, 'Tutor = { proveedor = "falso", voz = "tutor-grave" }')

    resultado = estudio("generar-voces", episodio)

    assert resultado.codigo == 0
    assert "Tutor: proveedor «falso», voz «tutor-grave»" in resultado.salida
    assert "Perro: proveedor «falso», voz «perro»" in resultado.salida
    assert estudio("cronometrar", episodio).codigo == 0


def test_los_fotogramas_por_segundo_salen_de_la_configuracion(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio.parent / "estudio.toml", "fps = 30", "fps = 60")

    linea = linea_de_tiempo(estudio, episodio)

    # A 60 fps cada palabra del proveedor falso dura 20 fotogramas; la pausa sigue siendo de 6.
    assert linea["fps"] == 60
    assert (linea["frases"][0]["inicio"], linea["frases"][0]["final"]) == (0, 220)
    assert linea["total"] == 176 * 20 + 16 * 6


def test_el_mismo_guion_con_los_mismos_audios_da_siempre_la_misma_linea_de_tiempo(
    estudio: Estudio, episodio: Path
) -> None:
    estudio("generar-voces", episodio)
    lineas = []
    # En procesos separados y con semillas distintas: Python cambia el orden de los conjuntos de un proceso a otro.
    for semilla in ("1", "2"):
        subprocess.run(
            [sys.executable, "-c", "import sys; from estudio.cli import main; sys.exit(main(sys.argv[1:]))",
             "cronometrar", str(episodio)],
            env={**os.environ, "PYTHONHASHSEED": semilla},
            check=True,
            capture_output=True,
        )
        lineas.append((episodio / "linea-de-tiempo.json").read_bytes())

    assert lineas[0] == lineas[1]


def test_la_salida_resume_el_total_y_el_cta(estudio: Estudio, episodio: Path) -> None:
    estudio("generar-voces", episodio)

    resultado = estudio("cronometrar", episodio)

    assert "Total: 1856 fotogramas a 30 fps (61,87 s)." in resultado.salida
    assert "CTA: del fotograma 1736 al 1856." in resultado.salida
    assert "linea-de-tiempo.json" in resultado.salida
