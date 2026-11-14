"""Sentarse en una roca: una pose con `asiento` y `trasero` en su ficha se coloca sola sobre una roca dibujada.

Las poses sintéticas son un torso (rojo), unos muslos (morado) y unas piernas (azul) con medidas conocidas. Los tests
miran solo la imagen que sale, por píxeles. Reglas en docs/estilo-2d.md y formato en docs/dibujo-2d.md.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image, ImageDraw

from ayudas import Estudio
from test_dibujar_planos import (
    CUERPO,
    SIN_PERSONAJES,
    TUTOR,
    claridad,
    crear_pose,
    dibujar,
    donde_hay,
    imagen_del_plano,
    preparar_el_lago,
)

TORSO = CUERPO
MUSLOS = TUTOR
PIERNAS = (3, 7, 251)
ROCA = (176, 150, 120)  # el relleno de la roca
ROCA_OSCURA = (150, 126, 100)  # la banda de abajo, de su segundo tono
TINTA = (38, 26, 32)  # su contorno
VERDE = (10, 240, 10)  # el cuerpo del perro sintético
UN_TUTOR_SENTADO = '[[plano]]\nid = "03"\npersonajes = [{ pose = "tutor_sentado" }]\n'
SENTADO_Y_PERRO = '[[plano]]\nid = "03"\npersonajes = [{ pose = "tutor_sentado" }, { pose = "perro_de_pie" }]\n'
UN_PERRO = '[[plano]]\nid = "03"\npersonajes = [{ pose = "perro_de_pie" }]\n'


@dataclass(frozen=True)
class Sentada:
    """Una pose sentada sintética, con las cajas en píxeles de la ilustración (x0, y0, x1, y1; x1 e y1, el primero de fuera)."""

    torso: tuple[int, int, int, int]
    muslos: tuple[int, int, int, int]  # a la altura del asiento, hacia delante
    piernas: tuple[int, int, int, int]  # cuelgan hasta el suelo
    asiento: float  # lo que sube la parte de abajo de los muslos sobre las suelas
    trasero: float  # dónde cae el trasero, como fracción del ancho de la silueta desde la espalda


UNA = Sentada((100, 40, 200, 240), (200, 200, 340, 240), (300, 240, 340, 300), asiento=60, trasero=0.2)
OTRA = Sentada((60, 20, 180, 220), (180, 170, 380, 220), (330, 220, 380, 290), asiento=70, trasero=0.25)
DOS_SENTADAS = [pytest.param(UNA, id="una"), pytest.param(OTRA, id="otra-con-solo-sus-dos-medidas")]


def crear_sentada(episodio: Path, sentada: Sentada, nombre: str = "tutor_sentado", ficha: str | None = None) -> None:
    carpeta = episodio.parent / "biblioteca" / "personajes" / nombre.split("_")[0] / "poses"
    carpeta.mkdir(parents=True, exist_ok=True)
    imagen = Image.new("RGBA", (400, 300), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    for caja, color in ((sentada.torso, TORSO), (sentada.muslos, MUSLOS), (sentada.piernas, PIERNAS)):
        dibujo.rectangle((caja[0], caja[1], caja[2] - 1, caja[3] - 1), fill=(*color, 255))
    imagen.save(carpeta / f"{nombre}.png")
    medidas = f"asiento = {sentada.asiento}\ntrasero = {sentada.trasero}\n"
    (carpeta / f"{nombre}.toml").write_text(
        f'ilustracion = "{nombre}.png"\n{medidas}' if ficha is None else ficha, encoding="utf-8"
    )


def _de_la_roca(imagen: NDArray[np.int_]) -> NDArray[np.bool_]:
    """Los píxeles con exactamente el color de la roca: los bordes suavizados del escenario no se le parecen."""
    return np.any([np.abs(imagen - np.array(color)).max(axis=2) <= 4 for color in (ROCA, ROCA_OSCURA)], axis=0)


def donde_esta_la_roca(imagen: NDArray[np.int_]) -> tuple[int, int, int, int]:
    """Columna mínima, columna máxima, fila mínima y fila máxima de la roca."""
    filas, columnas = np.where(_de_la_roca(imagen))
    assert len(filas), "no hay roca en la imagen"
    return int(columnas.min()), int(columnas.max()), int(filas.min()), int(filas.max())


def dibuja_sentada(estudio: Estudio, episodio: Path, sentada: Sentada) -> NDArray[np.int_]:
    crear_sentada(episodio, sentada)
    preparar_el_lago(estudio, episodio)
    assert dibujar(estudio, episodio, UN_TUTOR_SENTADO).codigo == 0
    return imagen_del_plano(episodio)


@pytest.mark.parametrize("sentada", DOS_SENTADAS)
def test_detras_de_la_espalda_se_ve_roca_y_el_cuerpo_queda_algo_hundido_en_ella(
    estudio: Estudio, episodio: Path, sentada: Sentada
) -> None:
    imagen = dibuja_sentada(estudio, episodio, sentada)

    roca = donde_esta_la_roca(imagen)
    torso, muslos = donde_hay(imagen, TORSO), donde_hay(imagen, MUSLOS)
    assert roca[0] <= torso[0] - 30  # sobresale por detrás de la espalda: se ve roca
    assert roca[1] < muslos[1]  # y no por delante de los muslos
    trasero = torso[0] + sentada.trasero * (muslos[1] + 1 - torso[0])
    assert abs((roca[0] + roca[1]) / 2 - trasero) <= 12  # centrada en el trasero
    assert muslos[2] < roca[2] < muslos[3]  # el techo queda bajo lo alto de los muslos y algo por encima del asiento


@pytest.mark.parametrize("sentada", DOS_SENTADAS)
def test_el_techo_de_la_roca_queda_tapado_por_el_cuerpo_y_no_asoma_sobre_el_asiento(
    estudio: Estudio, episodio: Path, sentada: Sentada
) -> None:
    imagen = dibuja_sentada(estudio, episodio, sentada)

    roca = donde_esta_la_roca(imagen)
    torso, muslos = donde_hay(imagen, TORSO), donde_hay(imagen, MUSLOS)
    fila_del_techo = roca[2] - 3  # dentro de la línea de contorno del techo
    detras = imagen[fila_del_techo, roca[0] + 8 : torso[0] - 2]
    bajo_el_cuerpo = imagen[fila_del_techo, torso[0] : roca[1] - 8]
    assert len(detras) and len(bajo_el_cuerpo)
    assert (np.abs(detras - np.array(TINTA)).max(axis=1) <= 40).all()  # detrás de la espalda el techo se ve
    for pixel in bajo_el_cuerpo:  # donde está el cuerpo, el techo no se ve: el trasero va encima
        assert min(np.abs(pixel - np.array(color)).max() for color in (TINTA, ROCA, ROCA_OSCURA)) > 40
    assert roca[2] > muslos[2]  # y la roca no sube por encima de los muslos


@pytest.mark.parametrize("sentada", DOS_SENTADAS)
def test_las_suelas_y_la_base_de_la_roca_comparten_linea_de_suelo_y_llevan_sombra(
    estudio: Estudio, episodio: Path, sentada: Sentada
) -> None:
    con_roca = dibuja_sentada(estudio, episodio, sentada)
    assert dibujar(estudio, episodio, SIN_PERSONAJES).codigo == 0
    vacio = imagen_del_plano(episodio)

    roca, suelas = donde_esta_la_roca(con_roca), donde_hay(con_roca, PIERNAS)
    assert abs(roca[3] - suelas[3]) <= 8  # la base de la roca (menos su contorno) cae en la línea de las suelas
    fila = suelas[3] + 10
    for columna in (roca[0] + 12, suelas[0]):  # bajo la roca y bajo las suelas
        assert claridad(con_roca, columna, fila) < claridad(vacio, columna, fila) - 10


@pytest.mark.parametrize("sentada", DOS_SENTADAS)
def test_sentarse_baja_al_personaje_y_no_sube_el_terreno_con_nada_mas(
    estudio: Estudio, episodio: Path, sentada: Sentada
) -> None:
    crear_sentada(episodio, sentada, "tutor_sin_roca", ficha='ilustracion = "tutor_sin_roca.png"\n')
    preparar_el_lago(estudio, episodio)
    assert dibujar(estudio, episodio, UN_TUTOR_SENTADO.replace("tutor_sentado", "tutor_sin_roca")).codigo == 0
    en_el_suelo = imagen_del_plano(episodio)
    assert dibujar(estudio, episodio, SIN_PERSONAJES).codigo == 0
    vacio = imagen_del_plano(episodio)
    crear_sentada(episodio, sentada)
    assert dibujar(estudio, episodio, UN_TUTOR_SENTADO).codigo == 0
    con_roca = imagen_del_plano(episodio)

    assert donde_hay(con_roca, PIERNAS)[3] == donde_hay(en_el_suelo, PIERNAS)[3]  # las suelas no suben por tener roca
    assert donde_hay(con_roca, TORSO)[2] == donde_hay(en_el_suelo, TORSO)[2]  # ni el cuerpo
    cambiado = np.where(np.abs(con_roca - vacio).max(axis=2) > 0)
    roca = donde_esta_la_roca(con_roca)
    assert cambiado[0].min() >= donde_hay(con_roca, TORSO)[2] - 6  # nada sube más arriba que la cabeza (menos el suavizado del borde)
    assert cambiado[1].min() >= roca[0] - 30  # ni a la izquierda de la roca y su sombra
    assert cambiado[1].max() <= donde_hay(con_roca, MUSLOS)[1] + 30  # ni a la derecha del cuerpo y su sombra


def test_una_pose_sentada_comparte_escena_con_otro_personaje_en_fila(estudio: Estudio, episodio: Path) -> None:
    crear_sentada(episodio, UNA)
    crear_pose(episodio, "perro_de_pie", color=VERDE)
    preparar_el_lago(estudio, episodio)

    assert dibujar(estudio, episodio, SENTADO_Y_PERRO).codigo == 0
    imagen = imagen_del_plano(episodio)

    perro = donde_hay(imagen, VERDE)
    assert donde_hay(imagen, PIERNAS)[3] == perro[3]  # los dos apoyan en la misma línea de suelo
    assert perro[0] > donde_hay(imagen, MUSLOS)[1]  # el perro va a la derecha


def test_dos_renders_de_un_plano_con_roca_salen_identicos(estudio: Estudio, episodio: Path) -> None:
    dibuja_sentada(estudio, episodio, UNA)
    primero = (episodio / "planos" / "03.png").read_bytes()

    assert dibujar(estudio, episodio, UN_TUTOR_SENTADO).codigo == 0

    assert (episodio / "planos" / "03.png").read_bytes() == primero


def a_la_ficha(medidas: str) -> str:
    return f'ilustracion = "tutor_sentado.png"\n{medidas}'


@pytest.mark.parametrize(
    ("ficha", "dice"),
    [
        pytest.param(a_la_ficha("asiento = 60\n"), "trasero", id="falta-el-trasero"),
        pytest.param(a_la_ficha("trasero = 0.2\n"), "asiento", id="falta-el-asiento"),
        pytest.param(a_la_ficha("asiento = 0\ntrasero = 0.2\n"), "asiento", id="asiento-cero"),
        pytest.param(a_la_ficha('asiento = "alto"\ntrasero = 0.2\n'), "asiento", id="asiento-que-no-es-un-numero"),
        pytest.param(a_la_ficha("asiento = 260\ntrasero = 0.2\n"), "asiento", id="asiento-mas-alto-que-la-pose"),
        pytest.param(a_la_ficha("asiento = 60\ntrasero = 0\n"), "trasero", id="trasero-en-la-espalda"),
        pytest.param(a_la_ficha("asiento = 60\ntrasero = 1\n"), "trasero", id="trasero-en-la-punta"),
        pytest.param(a_la_ficha('asiento = 60\ntrasero = "medio"\n'), "trasero", id="trasero-que-no-es-un-numero"),
    ],
)
def test_una_pose_sentada_con_medidas_que_faltan_o_no_valen_lo_dice_y_no_dibuja(
    estudio: Estudio, episodio: Path, ficha: str, dice: str
) -> None:
    crear_sentada(episodio, UNA, ficha=ficha)
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_TUTOR_SENTADO)

    assert resultado.codigo == 1
    assert any("tutor_sentado" in error and dice in error for error in resultado.errores), resultado.salida
    assert not (episodio / "planos" / "03.png").exists()


def test_una_pose_sin_asiento_ni_trasero_apoya_en_el_suelo_sin_roca(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)

    assert dibujar(estudio, episodio, UN_PERRO).codigo == 0

    assert not _de_la_roca(imagen_del_plano(episodio)).any()
