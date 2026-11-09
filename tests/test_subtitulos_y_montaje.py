"""Subtítulos y montaje: la herramienta ejecutada sobre carpetas de episodio de ejemplo.

Las cuentas a mano salen de los mismos datos que en test_voces_y_cronometraje.py:
- el proveedor de voz falso habla a 3 palabras por segundo: cada palabra dura 10 fotogramas a 30 fps;
- la configuración de los tests pone 6 fotogramas de pausa entre frases.
"""

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pytest

from ayudas import Estudio, linea_de_tiempo

FPS = 30


def tarjetas_de_la_frase(linea: dict[str, Any], numero: int) -> list[tuple[str, int, int]]:
    """Las tarjetas de subtítulo que caen dentro de la frase número `numero` (desde 1)."""
    frase = linea["frases"][numero - 1]
    return [
        (tarjeta["texto"], tarjeta["inicio"], tarjeta["final"])
        for tarjeta in linea["subtitulos"]
        if frase["inicio"] <= tarjeta["inicio"] < frase["final"]
    ]


def test_cada_tarjeta_tiene_una_o_dos_palabras_y_empieza_en_el_fotograma_de_su_primera_palabra(
    estudio: Estudio, episodio: Path
) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    # Frase 1: «¿Sabes por qué te huelo los zapatos cuando vuelves a casa?», del fotograma 0 al 110.
    assert tarjetas_de_la_frase(linea, 1) == [
        ("¿Sabes por", 0, 20),
        ("qué te", 20, 40),
        ("huelo los", 40, 60),
        ("zapatos cuando", 60, 80),
        ("vuelves a", 80, 100),
        ("casa?", 100, 110),
    ]
    assert all(1 <= len(tarjeta["texto"].split()) <= 2 for tarjeta in linea["subtitulos"])
    # Entre todas las tarjetas salen todas las palabras del guion, en orden, sin perder ni repetir ninguna.
    assert " ".join(tarjeta["texto"] for tarjeta in linea["subtitulos"]).split() == [
        palabra["texto"] for frase in linea["frases"] for palabra in frase["palabras"]
    ]


def test_una_tarjeta_no_junta_palabras_de_los_dos_lados_de_un_signo_de_puntuacion(
    estudio: Estudio, episodio: Path
) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    # Frase 6: «Vale, me ganas por goleada.», del fotograma 480 al 530. La coma deja «Vale,» sola.
    assert tarjetas_de_la_frase(linea, 6) == [
        ("Vale,", 480, 490),
        ("me ganas", 490, 510),
        ("por goleada.", 510, 530),
    ]


def test_cada_tarjeta_acaba_donde_empieza_la_siguiente_o_donde_acaba_su_frase(
    estudio: Estudio, episodio: Path
) -> None:
    assert estudio("generar-voces", episodio).codigo == 0
    # Una voz real deja silencios: «por» acaba antes de que empiece «qué», y la frase sigue
    # sonando después de «casa?». Las marcas de tiempo se tocan sin cambiar con qué se generó el audio.
    marcas_de_la_frase_1 = episodio / "voces" / "frase-01.json"
    marcas = json.loads(marcas_de_la_frase_1.read_text(encoding="utf-8"))
    marcas["palabras"][1]["final"] = 0.5  # «por» acaba en el fotograma 15; «qué» sigue empezando en el 20
    marcas["duracion"] = 4.0  # la frase acaba en el fotograma 120; «casa?», en el 110
    marcas_de_la_frase_1.write_text(json.dumps(marcas, ensure_ascii=False), encoding="utf-8")

    assert estudio("cronometrar", episodio).codigo == 0

    linea = json.loads((episodio / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    assert tarjetas_de_la_frase(linea, 1) == [
        ("¿Sabes por", 0, 20),
        ("qué te", 20, 40),
        ("huelo los", 40, 60),
        ("zapatos cuando", 60, 80),
        ("vuelves a", 80, 100),
        ("casa?", 100, 120),
    ]


def test_cada_tarjeta_lleva_el_personaje_que_dice_su_frase(estudio: Estudio, episodio: Path) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    for tarjeta in linea["subtitulos"]:
        (frase,) = [f for f in linea["frases"] if f["inicio"] <= tarjeta["inicio"] < f["final"]]
        assert tarjeta["personaje"] == frase["personaje"]
    assert {tarjeta["personaje"] for tarjeta in linea["subtitulos"]} == {"Perro", "Tutor"}


def test_solo_se_animan_las_tarjetas_con_palabras_acentuadas(estudio: Estudio, episodio: Path) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    # Frase 5: «Tengo hasta *trescientos millones* de receptores de olor. Tú tienes unos *seis millones*.»
    frase = linea["frases"][4]
    animadas = [
        (tarjeta["texto"], tarjeta["animada"])
        for tarjeta in linea["subtitulos"]
        if frase["inicio"] <= tarjeta["inicio"] < frase["final"]
    ]
    assert animadas == [
        ("Tengo hasta", False),
        ("trescientos millones", True),
        ("de receptores", False),
        ("de olor.", False),
        ("Tú tienes", False),
        ("unos seis", True),
        ("millones.", True),
    ]
    # En todo el guion hay 3 tramos acentuados («trescientos millones», «seis millones» y «leyendo»).
    assert [tarjeta["texto"] for tarjeta in linea["subtitulos"] if tarjeta["animada"]] == [
        "trescientos millones",
        "unos seis",
        "millones.",
        "Estoy leyendo",
    ]


# --- La composición de HyperFrames ---


@dataclass
class Composicion:
    raiz: dict[str, str] = field(default_factory=dict)
    audios: list[dict[str, str]] = field(default_factory=list)
    tarjetas: list[tuple[dict[str, str], str]] = field(default_factory=list)  # atributos y texto
    estilo: str = ""


class _Lector(HTMLParser):
    """Lee de la composición la raíz, las capas de audio, las de subtítulos y la hoja de estilo."""

    def __init__(self) -> None:
        super().__init__()
        self.composicion = Composicion()
        self._dentro_de_la_tarjeta = 0  # profundidad de etiquetas dentro de una tarjeta
        self._en_el_estilo = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        atributos = {nombre: valor or "" for nombre, valor in attrs}
        if self._dentro_de_la_tarjeta:
            self._dentro_de_la_tarjeta += 1
        elif "data-composition-id" in atributos:
            self.composicion.raiz = atributos
        elif tag == "audio":
            self.composicion.audios.append(atributos)
        elif "tarjeta" in atributos.get("class", "").split():
            self.composicion.tarjetas.append((atributos, ""))
            self._dentro_de_la_tarjeta = 1
        self._en_el_estilo = tag == "style"

    def handle_endtag(self, tag: str) -> None:
        if self._dentro_de_la_tarjeta:
            self._dentro_de_la_tarjeta -= 1
        self._en_el_estilo = False

    def handle_data(self, data: str) -> None:
        if self._dentro_de_la_tarjeta:
            atributos, texto = self.composicion.tarjetas[-1]
            self.composicion.tarjetas[-1] = (atributos, texto + data)
        elif self._en_el_estilo:
            self.composicion.estilo += data


def montar(estudio: Estudio, carpeta: Path) -> tuple[Composicion, dict[str, Any]]:
    """Genera las voces, monta el episodio y devuelve la composición y la línea de tiempo que deja."""
    assert estudio("generar-voces", carpeta).codigo == 0
    resultado = estudio("montar", carpeta)
    assert resultado.codigo == 0, resultado.salida
    lector = _Lector()
    lector.feed((carpeta / "index.html").read_text(encoding="utf-8"))
    linea: dict[str, Any] = json.loads((carpeta / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    return lector.composicion, linea


def fotogramas(segundos: str) -> int:
    return round(float(segundos) * FPS)


def tramo(capa: dict[str, str]) -> tuple[int, int]:
    """El primer fotograma de una capa y el primero después de ella."""
    inicio = fotogramas(capa["data-start"])
    return inicio, inicio + fotogramas(capa["data-duration"])


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
    assert composicion.tarjetas[0][1].strip() == "¿Sabes por"
    assert tramo(composicion.tarjetas[0][0]) == (0, 20)


def reglas(estilo: str) -> list[tuple[str, str]]:
    """Las reglas de la hoja de estilo, como (selector, declaraciones), sin las de @keyframes."""
    sin_keyframes = re.sub(r"@keyframes[^{]*\{(?:[^{}]*\{[^}]*\})*\s*\}", "", estilo)
    sin_comentarios = re.sub(r"/\*.*?\*/", "", sin_keyframes, flags=re.S)
    return [(selector.strip(), cuerpo) for selector, cuerpo in re.findall(r"([^{}]+)\{([^}]*)\}", sin_comentarios)]


def test_cada_tarjeta_lleva_los_colores_de_su_personaje_y_solo_las_acentuadas_se_animan(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, linea = montar(estudio, episodio)

    for (capa, _), tarjeta in zip(composicion.tarjetas, linea["subtitulos"], strict=True):
        clases = capa["class"].split()
        assert tarjeta["personaje"] in clases
        assert ("animada" in clases) == tarjeta["animada"]
    colores = {selector: cuerpo.upper() for selector, cuerpo in reglas(composicion.estilo)}
    # Tutor: texto blanco con borde negro. Perro: texto lightcyan con borde maroon.
    assert "#FFFFFF" in colores[".Tutor"] and "#000000" in colores[".Tutor"]
    assert "#E0FFFF" in colores[".Perro"] and "#800000" in colores[".Perro"]
    animan = [selector for selector, cuerpo in reglas(composicion.estilo) if "animation" in cuerpo]
    assert animan and all(".animada" in selector for selector in animan)


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
