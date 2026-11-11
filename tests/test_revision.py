"""Revisión: hoja de contactos, prueba de móvil y comprobación de la exportación, con la herramienta.

Los vídeos son minúsculos y los genera ffmpeg dentro de cada test: un color liso, sin audio.
"""

import json
import subprocess
from pathlib import Path

import pytest

from ayudas import Estudio, linea_de_tiempo


def video(archivo: Path, fotogramas: int, ancho: int = 108, alto: int = 192, fps: int = 30) -> Path:
    """Un vídeo de color liso con ese tamaño, esa velocidad y ese número de fotogramas."""
    archivo.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=gray:s={ancho}x{alto}:r={fps}",
         "-frames:v", str(fotogramas), "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(archivo)],
        check=True,
    )
    return archivo


def tamano(imagen: Path) -> tuple[int, int]:
    proceso = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "json", str(imagen)],
        capture_output=True, text=True, check=True,
    )
    flujo = json.loads(proceso.stdout)["streams"][0]
    return flujo["width"], flujo["height"]


def exportacion(carpeta: Path) -> Path:
    return carpeta / "exportacion" / f"{carpeta.name}.mp4"


# --- Hoja de contactos y prueba de móvil ---


def test_la_hoja_de_contactos_pone_un_fotograma_por_segundo_en_filas_de_ocho(
    estudio: Estudio, episodio: Path
) -> None:
    video(episodio / "versiones" / "previa.mp4", fotogramas=10 * 30)  # 10 s: 10 fotogramas, 2 filas

    resultado = estudio("revisar", episodio)

    assert resultado.codigo == 0, resultado.salida
    assert tamano(episodio / "revision" / "previa-contactos.png") == (8 * 216, 2 * 384)


def test_la_prueba_de_movil_ve_el_episodio_a_360_px_de_ancho(estudio: Estudio, episodio: Path) -> None:
    video(episodio / "versiones" / "previa.mp4", fotogramas=10 * 30)  # 10 s: un fotograma cada 3 s, 4 en una fila

    resultado = estudio("revisar", episodio)

    assert resultado.codigo == 0, resultado.salida
    assert tamano(episodio / "revision" / "previa-movil.png") == (6 * 360, 640)
    assert "revision/previa-movil.png" in resultado.salida


def test_revisar_saca_las_hojas_de_cada_version(estudio: Estudio, episodio: Path) -> None:
    video(episodio / "versiones" / "previa.mp4", fotogramas=30)
    video(episodio / "versiones" / "final.mp4", fotogramas=30)

    resultado = estudio("revisar", episodio)

    assert resultado.codigo == 0, resultado.salida
    hojas = sorted(archivo.name for archivo in (episodio / "revision").iterdir())
    assert hojas == ["final-contactos.png", "final-movil.png", "previa-contactos.png", "previa-movil.png"]


def test_revisar_sin_versiones_dice_que_hay_que_renderizar(estudio: Estudio, episodio: Path) -> None:
    resultado = estudio("revisar", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1 and "renderizar" in resultado.errores[0]


def test_revisar_sin_ffmpeg_explica_que_hay_que_instalarlo(
    estudio: Estudio, episodio: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    video(episodio / "versiones" / "previa.mp4", fotogramas=30)
    monkeypatch.setenv("PATH", str(tmp_path / "sin-programas"))

    resultado = estudio("revisar", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1 and "ffmpeg" in resultado.errores[0]


# --- Comprobación de la exportación ---


@pytest.fixture
def total(estudio: Estudio, episodio: Path) -> int:
    """Los fotogramas que dura el episodio según su línea de tiempo."""
    fotogramas: int = linea_de_tiempo(estudio, episodio)["total"]
    return fotogramas


@pytest.mark.parametrize("de_mas", [0, 1, -1])
def test_la_exportacion_pasa_si_cuadran_el_tamano_la_velocidad_y_la_duracion_con_un_fotograma_de_margen(
    estudio: Estudio, episodio: Path, total: int, de_mas: int
) -> None:
    video(exportacion(episodio), total + de_mas, 1080, 1920)

    resultado = estudio("comprobar-exportacion", episodio)

    assert resultado.codigo == 0, resultado.salida
    assert resultado.errores == []


def test_la_exportacion_falla_si_no_mide_1080x1920(estudio: Estudio, episodio: Path, total: int) -> None:
    video(exportacion(episodio), total, 540, 960)

    resultado = estudio("comprobar-exportacion", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "540x960" in resultado.errores[0] and "1080x1920" in resultado.errores[0]


def test_la_exportacion_falla_si_no_va_a_30_fotogramas_por_segundo(
    estudio: Estudio, episodio: Path, total: int
) -> None:
    # Dura lo mismo en segundos, pero a 25 fotogramas por segundo.
    video(exportacion(episodio), round(total * 25 / 30), 1080, 1920, fps=25)

    resultado = estudio("comprobar-exportacion", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "25/1" in resultado.errores[0] and "30/1" in resultado.errores[0]


@pytest.mark.parametrize("de_mas", [2, -2])
def test_la_exportacion_falla_si_su_duracion_se_aparta_mas_de_un_fotograma(
    estudio: Estudio, episodio: Path, total: int, de_mas: int
) -> None:
    video(exportacion(episodio), total + de_mas, 1080, 1920)

    resultado = estudio("comprobar-exportacion", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert str(total + de_mas) in resultado.errores[0] and str(total) in resultado.errores[0]


def test_sin_exportacion_dice_donde_tiene_que_estar(estudio: Estudio, episodio: Path, total: int) -> None:
    resultado = estudio("comprobar-exportacion", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1 and f"exportacion/{episodio.name}.mp4" in resultado.errores[0]


def test_la_exportacion_falla_por_la_velocidad_y_por_la_duracion_si_no_cuadra_ninguna(
    estudio: Estudio, episodio: Path, total: int
) -> None:
    video(exportacion(episodio), total, 1080, 1920, fps=25)  # a 25 fps, los mismos fotogramas duran más

    resultado = estudio("comprobar-exportacion", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 2, resultado.salida


def test_una_linea_de_tiempo_rota_da_un_mensaje_claro(estudio: Estudio, episodio: Path) -> None:
    video(exportacion(episodio), 30, 1080, 1920)
    (episodio / "linea-de-tiempo.json").write_text("{ esto no es json", encoding="utf-8")

    resultado = estudio("comprobar-exportacion", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1 and "cronometrar" in resultado.errores[0]


def test_sin_linea_de_tiempo_dice_que_hay_que_cronometrar(estudio: Estudio, episodio: Path) -> None:
    video(exportacion(episodio), 30, 1080, 1920)

    resultado = estudio("comprobar-exportacion", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1 and "cronometrar" in resultado.errores[0]
