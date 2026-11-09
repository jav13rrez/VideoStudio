"""Subtítulos y montaje: la herramienta ejecutada sobre carpetas de episodio de ejemplo.

Las cuentas a mano salen de los mismos datos que en test_voces_y_cronometraje.py:
- el proveedor de voz falso habla a 3 palabras por segundo: cada palabra dura 10 fotogramas a 30 fps;
- la configuración de los tests pone 6 fotogramas de pausa entre frases.
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest

from ayudas import Estudio, declaraciones, linea_de_tiempo, montar, reglas, tramo


def tarjetas_de_la_frase(linea: dict[str, Any], numero: int) -> list[dict[str, Any]]:
    """Las tarjetas de subtítulo que caen dentro de la frase número `numero` (desde 1)."""
    frase = linea["frases"][numero - 1]
    return [tarjeta for tarjeta in linea["subtitulos"] if frase["inicio"] <= tarjeta["inicio"] < frase["final"]]


def tramos_de_la_frase(linea: dict[str, Any], numero: int) -> list[tuple[str, int, int]]:
    return [(tarjeta["texto"], tarjeta["inicio"], tarjeta["final"]) for tarjeta in tarjetas_de_la_frase(linea, numero)]


def test_cada_tarjeta_tiene_hasta_tres_palabras_y_empieza_en_el_fotograma_de_su_primera_palabra(
    estudio: Estudio, episodio: Path
) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    # Frase 1: «¿Sabes por qué te huelo los zapatos cuando vuelves a casa?», del fotograma 0 al 110.
    assert tramos_de_la_frase(linea, 1) == [
        ("¿Sabes por qué", 0, 30),
        ("te huelo los", 30, 60),
        ("zapatos cuando vuelves", 60, 90),
        ("a casa?", 90, 110),
    ]
    assert all(1 <= len(tarjeta["texto"].split()) <= 3 for tarjeta in linea["subtitulos"])
    # Entre todas las tarjetas salen todas las palabras del guion, en orden, sin perder ni repetir ninguna.
    assert " ".join(tarjeta["texto"] for tarjeta in linea["subtitulos"]).split() == [
        palabra["texto"] for frase in linea["frases"] for palabra in frase["palabras"]
    ]


def test_una_tarjeta_acaba_al_final_de_cada_oracion_pero_no_en_una_coma(estudio: Estudio, episodio: Path) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    # Frase 13: «Exacto. Y yo ni siquiera tengo manos para recuperarlo.», del fotograma 1282 al 1372.
    assert tramos_de_la_frase(linea, 13) == [
        ("Exacto.", 1282, 1292),
        ("Y yo ni", 1292, 1322),
        ("siquiera tengo manos", 1322, 1352),
        ("para recuperarlo.", 1352, 1372),
    ]
    # Frase 6: «Vale, me ganas por goleada.», del fotograma 480 al 530. La coma no corta: con una voz real,
    # si hay pausa la corta la regla de las pausas.
    assert tramos_de_la_frase(linea, 6) == [("Vale, me ganas", 480, 510), ("por goleada.", 510, 530)]


@pytest.mark.parametrize(
    ("final_de_por", "tarjetas"),
    [
        # «por» acaba en el fotograma 14 y «qué» empieza en el 20: 6 fotogramas, 0,2 s de pausa, corta.
        (0.45, [("¿Sabes por", 0, 20), ("qué te huelo", 20, 50), ("los zapatos cuando", 50, 80)]),
        # «por» acaba en el fotograma 17: 3 fotogramas, 0,1 s de pausa, no llega a 0,15 s y no corta.
        (0.5667, [("¿Sabes por qué", 0, 30), ("te huelo los", 30, 60), ("zapatos cuando vuelves", 60, 90)]),
    ],
)
def test_una_pausa_de_150_ms_corta_la_tarjeta_y_cada_tarjeta_acaba_donde_empieza_la_siguiente(
    estudio: Estudio, episodio: Path, final_de_por: float, tarjetas: list[tuple[str, int, int]]
) -> None:
    assert estudio("generar-voces", episodio).codigo == 0
    # Una voz real deja silencios: «por» acaba antes de que empiece «qué», y la frase sigue sonando
    # después de «casa?». Las marcas de tiempo se tocan sin cambiar con qué se generó el audio.
    marcas_de_la_frase_1 = episodio / "voces" / "frase-01.json"
    marcas = json.loads(marcas_de_la_frase_1.read_text(encoding="utf-8"))
    marcas["palabras"][1]["final"] = final_de_por  # «qué» sigue empezando en el fotograma 20
    marcas["duracion"] = 4.0  # la frase acaba en el fotograma 120; «casa?», en el 110
    marcas_de_la_frase_1.write_text(json.dumps(marcas, ensure_ascii=False), encoding="utf-8")

    assert estudio("cronometrar", episodio).codigo == 0

    linea = json.loads((episodio / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    # Cada tarjeta dura hasta que empieza la siguiente, aunque su última palabra acabe antes,
    # y la última de la frase, hasta que acaba la frase.
    assert tramos_de_la_frase(linea, 1)[:3] == tarjetas
    assert tramos_de_la_frase(linea, 1)[-1][2] == 120


def test_cada_tarjeta_lleva_el_personaje_que_dice_su_frase(estudio: Estudio, episodio: Path) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    for numero, frase in enumerate(linea["frases"], start=1):
        assert {tarjeta["personaje"] for tarjeta in tarjetas_de_la_frase(linea, numero)} == {frase["personaje"]}
    assert {tarjeta["personaje"] for tarjeta in linea["subtitulos"]} == {"Perro", "Tutor"}


def test_una_palabra_acentuada_abre_su_tarjeta_y_solo_esas_tarjetas_se_animan(
    estudio: Estudio, episodio: Path
) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    # Frase 5, desde el fotograma 344:
    # «Tengo hasta *trescientos millones* de receptores de olor. Tú tienes unos *seis millones*.»
    # «Tengo hasta» se queda en dos palabras para que la tarjeta animada empiece justo en «trescientos».
    assert [
        (tarjeta["texto"], tarjeta["animada"], tarjeta["inicio"], tarjeta["final"])
        for tarjeta in tarjetas_de_la_frase(linea, 5)
    ] == [
        ("Tengo hasta", False, 344, 364),
        ("trescientos millones de", True, 364, 394),
        ("receptores de olor.", False, 394, 424),
        ("Tú tienes unos", False, 424, 454),
        ("seis millones.", True, 454, 474),
    ]
    # En todo el guion hay 3 tramos acentuados: una animación por tramo.
    # Frase 9: «No estoy perdiendo el tiempo. Estoy *leyendo* las noticias del barrio.»
    assert [tarjeta["texto"] for tarjeta in linea["subtitulos"] if tarjeta["animada"]] == [
        "trescientos millones de",
        "seis millones.",
        "leyendo las noticias",
    ]


# --- La composición de HyperFrames ---


def test_montar_deja_una_composicion_vertical_de_1080x1920_a_30_fps_que_dura_lo_que_el_episodio(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, linea = montar(estudio, episodio)

    raiz = composicion.raiz
    assert (raiz["data-width"], raiz["data-height"], raiz["data-fps"]) == ("1080", "1920", "30")
    assert tramo(raiz) == (0, linea["total"]) == (0, 1856)


def test_la_composicion_tiene_una_capa_de_audio_por_frase_con_los_tiempos_de_la_linea_de_tiempo(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, linea = montar(estudio, episodio)

    assert [(audio["src"], *tramo(audio)) for audio in composicion.audios] == [
        (frase["audio"], frase["inicio"], frase["final"]) for frase in linea["frases"]
    ]
    assert len(composicion.audios) == 17
    assert all((episodio / audio["src"]).is_file() for audio in composicion.audios)
    # HyperFrames deja fuera de la mezcla los audios sin id.
    assert len({audio.get("id") for audio in composicion.audios} - {None, ""}) == 17


def test_la_composicion_tiene_una_capa_por_tarjeta_con_su_texto_y_sus_tiempos(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, linea = montar(estudio, episodio)

    assert [(texto.strip(), *tramo(capa)) for capa, texto in composicion.tarjetas] == [
        (tarjeta["texto"], tarjeta["inicio"], tarjeta["final"]) for tarjeta in linea["subtitulos"]
    ]
    assert composicion.tarjetas[0][1].strip() == "¿Sabes por qué"
    assert tramo(composicion.tarjetas[0][0]) == (0, 30)
    # Todas en la pista de subtítulos: HyperFrames las trata como subtítulos que siguen a la voz.
    assert composicion.tarjetas_en_la_pista_de_subtitulos == len(composicion.tarjetas)


def test_cada_tarjeta_lleva_los_colores_de_su_personaje_y_solo_las_acentuadas_se_animan(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, linea = montar(estudio, episodio)

    for (capa, _), tarjeta in zip(composicion.tarjetas, linea["subtitulos"], strict=True):
        clases = capa["class"].split()
        assert tarjeta["personaje"] in clases
        assert ("animada" in clases) == tarjeta["animada"]
    colores = {selector: declaraciones(cuerpo) for selector, cuerpo in reglas(composicion.estilo)}
    # Tutor: texto blanco con borde negro. Perro: texto lightcyan con borde maroon.
    assert colores[".Tutor"] == {"--relleno": "#FFFFFF", "--borde": "#000000"}
    assert colores[".Perro"] == {"--relleno": "#E0FFFF", "--borde": "#800000"}
    animan = [selector for selector, cuerpo in reglas(composicion.estilo) if "animation" in cuerpo]
    assert animan and all(".animada" in selector for selector in animan)


def test_la_composicion_solo_usa_archivos_de_la_carpeta_del_episodio(estudio: Estudio, episodio: Path) -> None:
    composicion, _ = montar(estudio, episodio)

    html = (episodio / "index.html").read_text(encoding="utf-8")
    # Nada de internet: el render no puede depender de la red.
    assert "http:" not in html and "https:" not in html
    usados = composicion.fuentes + re.findall(r'url\("([^"]+)"\)', composicion.estilo)
    assert len(usados) == 48  # 17 voces, 29 carteles, el marcador del logo de la App y la letra de los subtítulos
    assert all((episodio / usado).is_file() for usado in usados)


def test_montar_se_niega_si_faltan_las_voces_y_no_deja_composicion(estudio: Estudio, episodio: Path) -> None:
    resultado = estudio("montar", episodio)

    assert resultado.codigo == 1
    assert any("generar-voces" in error for error in resultado.errores)
    assert not (episodio / "index.html").exists()


def test_renderizar_sin_node_dice_que_hay_que_instalarlo(
    estudio: Estudio, episodio: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert estudio("generar-voces", episodio).codigo == 0
    monkeypatch.setenv("PATH", str(tmp_path / "sin-programas"))

    resultado = estudio("renderizar", episodio)

    assert resultado.codigo == 1
    assert any("Node.js" in error for error in resultado.errores)
    assert not (episodio / "versiones" / "previa.mp4").exists()
