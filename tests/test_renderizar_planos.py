"""Renderizar los planos con Blender: la cámara y la colocación de cada plano salen de tomas.toml.

Los tests usan un Blender falso (tests/programas/blender) que deja imágenes pequeñas y apunta lo que se le pide.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from ayudas import Estudio, cambiar, leer_composicion, montar, tramo

PROGRAMAS = Path(__file__).parent / "programas"
TAMANO_REAL = (1080, 1920)


@pytest.fixture
def blender(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Pone el Blender falso delante en el PATH; devuelve la carpeta donde apunta sus llamadas."""
    carpeta = tmp_path / "blender-falso"
    carpeta.mkdir()
    monkeypatch.setenv("BLENDER_FALSO", str(carpeta))
    monkeypatch.setenv("PATH", f"{PROGRAMAS}{os.pathsep}{os.environ['PATH']}")
    return carpeta


def llamadas(blender: Path) -> list[dict[str, Any]]:
    archivo = blender / "llamadas.jsonl"
    return [json.loads(linea) for linea in archivo.read_text(encoding="utf-8").splitlines()] if archivo.exists() else []


def planos_de(llamada: dict[str, Any]) -> list[dict[str, Any]]:
    planos: list[dict[str, Any]] = llamada["planos"]
    return planos


def sonda(video: Path) -> dict[str, str]:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-of", "json",
         "-show_entries", "stream=nb_read_frames,width,height,r_frame_rate", str(video)],
        capture_output=True, text=True, check=True,
    ).stdout
    flujo: dict[str, str] = json.loads(salida)["streams"][0]
    return flujo


def preparar(estudio: Estudio, episodio: Path) -> dict[str, dict[str, int]]:
    """Genera las voces y cronometra; devuelve inicio y final de cada plano."""
    assert estudio("generar-voces", episodio).codigo == 0
    assert estudio("cronometrar", episodio).codigo == 0
    linea = json.loads((episodio / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    return {plano["id"]: plano for plano in linea["planos"]}


def test_un_plano_de_camara_fija_deja_una_imagen_con_su_nombre(estudio: Estudio, episodio: Path, blender: Path) -> None:
    preparar(estudio, episodio)

    resultado = estudio("renderizar-planos", episodio, "--planos", "02")

    assert resultado.codigo == 0, resultado.salida
    assert (episodio / "planos" / "02.png").is_file()
    assert not (episodio / "planos" / "02.mp4").exists()
    (plano,) = planos_de(llamadas(blender)[0])
    assert plano["id"] == "02" and plano["fija"] is True
    assert (plano["ancho_px"], plano["alto_px"]) == TAMANO_REAL  # las imágenes fijas, siempre a tamaño real


def test_un_plano_con_movimiento_deja_un_video_de_1080x1920_con_un_fotograma_por_fotograma_de_la_linea_de_tiempo(
    estudio: Estudio, episodio: Path, blender: Path
) -> None:
    linea = preparar(estudio, episodio)

    resultado = estudio("renderizar-planos", episodio, "--planos", "01")

    assert resultado.codigo == 0, resultado.salida
    datos = sonda(episodio / "planos" / "01.mp4")
    duracion = linea["01"]["final"] - linea["01"]["inicio"]
    assert (int(datos["width"]), int(datos["height"])) == TAMANO_REAL
    assert datos["r_frame_rate"] == "30/1"
    assert int(datos["nb_read_frames"]) == duracion
    (plano,) = planos_de(llamadas(blender)[0])
    assert (plano["desde"], plano["hasta"]) == (0, duracion - 1)
    assert not (episodio / "planos" / "01.png").exists()


def test_la_toma_llega_a_blender_con_la_camara_el_destino_y_los_personajes_del_plano(
    estudio: Estudio, episodio: Path, blender: Path
) -> None:
    preparar(estudio, episodio)

    estudio("renderizar-planos", episodio, "--planos", "02,04")

    por_id = {plano["id"]: plano for plano in planos_de(llamadas(blender)[0])}
    assert por_id["02"]["escenario"] == "recibidor"
    toma = por_id["02"]["toma"]
    assert toma["mira"] == [0.0, 1.0, 1.2] and toma["ancho"] == 1.5 and toma["hasta"] is None
    assert toma["personajes"][0] == {
        "pieza": "tutor_sentado_frente", "en": [-0.3, 1.0, 0.0], "espejo": False, "ojos": "mirada_izq", "boca": "sonrisa",
    }
    assert toma["personajes"][1]["espejo"] is True
    assert por_id["04"]["toma"]["hasta"]["mira"] == [0.3, 1.0, 1.0]


def test_la_calidad_rapida_renderiza_a_media_resolucion_y_la_final_a_tamano_real(
    estudio: Estudio, episodio: Path, blender: Path
) -> None:
    preparar(estudio, episodio)

    estudio("renderizar-planos", episodio, "--planos", "01")
    estudio("renderizar-planos", episodio, "--planos", "01", "--calidad", "final")

    rapida, final = (planos_de(llamada)[0] for llamada in llamadas(blender))
    assert (rapida["ancho_px"], rapida["alto_px"]) == (540, 960) and rapida["muestras"] < final["muestras"]
    assert (final["ancho_px"], final["alto_px"]) == TAMANO_REAL


def test_se_pueden_elegir_varios_planos_por_su_numero_y_por_rangos(
    estudio: Estudio, episodio: Path, blender: Path
) -> None:
    preparar(estudio, episodio)

    estudio("renderizar-planos", episodio, "--planos", "01-02,04")

    assert [plano["id"] for plano in planos_de(llamadas(blender)[0])] == ["01", "02", "04"]


def test_volver_a_renderizar_un_rango_solo_toca_esos_fotogramas_y_recompone_el_video(
    estudio: Estudio, episodio: Path, blender: Path
) -> None:
    linea = preparar(estudio, episodio)
    estudio("renderizar-planos", episodio, "--planos", "01")
    fotogramas = episodio / "planos" / "_fotogramas" / "01"
    antes = {n: (fotogramas / f"{n:04d}.png").read_bytes() for n in range(20)}

    resultado = estudio("renderizar-planos", episodio, "--planos", "01", "--fotogramas", "5-8")

    assert resultado.codigo == 0, resultado.salida
    (plano,) = planos_de(llamadas(blender)[1])
    assert (plano["desde"], plano["hasta"]) == (5, 8)
    despues = {n: (fotogramas / f"{n:04d}.png").read_bytes() for n in range(20)}
    assert [n for n in antes if antes[n] != despues[n]] == [5, 6, 7, 8]
    duracion = linea["01"]["final"] - linea["01"]["inicio"]
    assert int(sonda(episodio / "planos" / "01.mp4")["nb_read_frames"]) == duracion


def test_un_rango_de_fotogramas_pide_un_solo_plano_que_ya_este_renderizado(
    estudio: Estudio, episodio: Path, blender: Path
) -> None:
    preparar(estudio, episodio)

    varios = estudio("renderizar-planos", episodio, "--planos", "01,04", "--fotogramas", "5-8")
    sin_render = estudio("renderizar-planos", episodio, "--planos", "01", "--fotogramas", "5-8")

    assert varios.codigo == 1 and any("un solo plano" in error for error in varios.errores)
    assert sin_render.codigo == 1 and any("entero" in error for error in sin_render.errores)
    assert llamadas(blender) == []


def test_la_composicion_usa_el_video_de_los_planos_con_movimiento_y_la_imagen_de_los_fijos(
    estudio: Estudio, episodio: Path, blender: Path
) -> None:
    preparar(estudio, episodio)
    estudio("renderizar-planos", episodio, "--planos", "01-02")

    composicion, linea = montar(estudio, episodio)

    por_id = {capa["id"]: capa for capa in composicion.planos}
    assert por_id["plano-01"]["src"] == "planos/01.mp4"
    assert "muted" in por_id["plano-01"]
    assert por_id["plano-02"]["src"] == "planos/02.png"
    assert por_id["plano-03"]["src"].startswith("assets/carteles/")
    plano = next(p for p in linea["planos"] if p["id"] == "01")
    assert tramo(por_id["plano-01"]) == (plano["inicio"], plano["final"])


def test_un_plano_que_pasa_de_movimiento_a_fijo_deja_solo_su_imagen(
    estudio: Estudio, episodio: Path, blender: Path
) -> None:
    preparar(estudio, episodio)
    estudio("renderizar-planos", episodio, "--planos", "01")
    cambiar(episodio / "planos.toml", 'camara = "acercamiento lento"\nmotivo = "la pregunta del gancho', 'camara = "fija"\nmotivo = "la pregunta del gancho')
    cambiar(episodio / "tomas.toml", 'hasta = { ancho = 0.8 }\n', "")

    resultado = estudio("renderizar-planos", episodio, "--planos", "01")

    assert resultado.codigo == 0, resultado.salida
    assert (episodio / "planos" / "01.png").is_file()
    assert not (episodio / "planos" / "01.mp4").exists()


@pytest.mark.parametrize(
    ("antes", "despues", "error"),
    [
        ('id = "02"\nmira', 'id = "99"\nmira', "99"),  # un plano que no existe
        ('ancho = 1.5\npersonajes = [\n', 'ancho = 1.5\nhasta = { ancho = 1.2 }\npersonajes = [\n', "fija"),
        ('hasta = { ancho = 0.8 }', 'hasta = { ancho = 0.3 }', "lento"),  # se acerca demasiado deprisa
        ('hasta = { ancho = 0.8 }', 'hasta = { ancho = 0.8, mira = [2.0, 1.0, 0.3] }', "lento"),  # el acercamiento se desvía
        ('hasta = { mira = [0.3, 1.0, 1.0], azimut = 5 }', 'hasta = { mira = [3.3, 1.0, 1.0], azimut = 5 }', "lento"),
        ('ancho = 1.0\n', 'ancho = -1.0\n', "ancho"),
        ('ancho = 1.0\n', 'ancho = 1.0\nlente = 85\n', "lente"),  # un campo que no existe
        ('{ pieza = "perro_de_pie_frente", en = [0.0, 1.0, 0.0] }', '{ pieza = "perro_de_pie_frente" }', "en"),
    ],
)
def test_una_toma_mal_escrita_no_se_renderiza_y_dice_por_que(
    estudio: Estudio, episodio: Path, blender: Path, antes: str, despues: str, error: str
) -> None:
    preparar(estudio, episodio)
    cambiar(episodio / "tomas.toml", antes, despues)

    resultado = estudio("renderizar-planos", episodio, "--planos", "01-02")

    assert resultado.codigo == 1
    assert any(error in linea for linea in resultado.errores), resultado.salida
    assert llamadas(blender) == []


def test_un_plano_sin_toma_no_se_renderiza_y_se_dice(estudio: Estudio, episodio: Path, blender: Path) -> None:
    preparar(estudio, episodio)

    resultado = estudio("renderizar-planos", episodio, "--planos", "03")

    assert resultado.codigo == 1 and any("03" in error and "tomas.toml" in error for error in resultado.errores)


def test_sin_tomas_toml_se_dice_donde_escribirlo(estudio: Estudio, episodio: Path, blender: Path) -> None:
    preparar(estudio, episodio)
    (episodio / "tomas.toml").unlink()

    resultado = estudio("renderizar-planos", episodio)

    assert resultado.codigo == 1 and any("tomas.toml" in error for error in resultado.errores)


def test_sin_blender_se_dice_como_indicarlo(
    estudio: Estudio, episodio: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    preparar(estudio, episodio)
    monkeypatch.setenv("PATH", str(tmp_path / "sin-programas"))
    monkeypatch.delenv("ESTUDIO_BLENDER", raising=False)

    resultado = estudio("renderizar-planos", episodio, "--planos", "02")

    assert resultado.codigo == 1 and any("Blender" in error and "estudio.toml" in error for error in resultado.errores)


def test_si_blender_falla_no_queda_la_imagen_de_la_vez_anterior(
    estudio: Estudio, episodio: Path, blender: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    preparar(estudio, episodio)
    estudio("renderizar-planos", episodio, "--planos", "02")
    monkeypatch.setenv("BLENDER_FALSO_FALLA", "1")

    resultado = estudio("renderizar-planos", episodio, "--planos", "02")

    assert resultado.codigo == 1 and any("Blender" in error for error in resultado.errores)
    assert not (episodio / "planos" / "02.png").exists()
