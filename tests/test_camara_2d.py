"""Cámara en el dibujo 2D (ticket 05 de estudio-2d): acercamiento y desplazamiento como recortes de un lienzo más grande.

El tipo de cámara sale de planos.toml (plano 01: acercamiento lento; plano 12: desplazamiento) y los números van en
reparto.toml como `desde` y `hasta`, con `ancho` y `centro` en fracciones del escenario. Los tests miden, en los fotogramas
inicial, medio y final, el tamaño y la posición del cuerpo de una pose sintética (un rectángulo rojo de 200x200 en su
ilustración, a escala 0,66) y de la línea de suelo del lago. Formato en docs/dibujo-2d.md.
"""

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image

from ayudas import Estudio, Resultado, cambiar
from test_dibujar_planos import CUERPO, crear_pose, donde_hay
from test_renderizar_planos import preparar, sonda
from test_sentarse_en_roca import PIERNAS, UNA, crear_sentada, donde_esta_la_roca

Imagen = NDArray[np.int_]
TINTA = (38, 26, 32)
ESCALA = 0.66
CUERPO_ANCHO = 200 * ESCALA  # el ancho del cuerpo en la imagen con la vista entera
SUELO = 1590  # la línea de suelo del lago, en píxeles de imagen con la vista entera
LINEA_DE_SUELO = 1560  # el contorno del prado, 30 píxeles por encima de donde apoyan los personajes
MITAD = 540.0  # la columna central de la imagen
PERRO = 'personajes = [{ pose = "perro_de_pie" }]\n'


def reparto(id_: str, camara: str, personajes: str = PERRO) -> str:
    return f'[[plano]]\nid = "{id_}"\n{personajes}{camara}\n'


def preparar_planos_de_camara(estudio: Estudio, episodio: Path) -> dict[str, dict[str, int]]:
    """Los planos 01 (acercamiento) y 12 (desplazamiento) pasan al lago y se cronometra el episodio."""
    crear_pose(episodio)
    cambiar(episodio / "planos.toml", 'empieza = "¿Sabes por qué"\nescenario = "recibidor"', 'empieza = "¿Sabes por qué"\nescenario = "lago"')
    cambiar(episodio / "planos.toml", 'empieza = "Entonces, cuando"\nescenario = "calle"', 'empieza = "Entonces, cuando"\nescenario = "lago"')
    return preparar(estudio, episodio)


def dibujar(estudio: Estudio, episodio: Path, id_: str, camara: str, personajes: str = PERRO) -> Resultado:
    (episodio / "reparto.toml").write_text(reparto(id_, camara, personajes), encoding="utf-8")
    return estudio("renderizar-planos", episodio, "--planos", id_)


def leer(episodio: Path, id_: str, numero: int) -> Imagen:
    with Image.open(episodio / "planos" / "_fotogramas" / id_ / f"{numero:04d}.png") as imagen:
        return np.asarray(imagen.convert("RGB")).astype(np.int_)


def cuerpo(imagen: Imagen) -> tuple[float, float, int]:
    """Ancho del cuerpo, columna de su centro y fila de su base."""
    izquierda, derecha, _, abajo = donde_hay(imagen, CUERPO)
    return derecha - izquierda + 1.0, (izquierda + derecha + 1) / 2, abajo + 1


def fila_de_la_linea_de_suelo(imagen: Imagen) -> int:
    """La fila más baja que es casi toda de tinta en unas columnas libres de personajes: el contorno del prado."""
    oscuro = np.abs(imagen[:, 100:200] - np.array(TINTA)).max(axis=2) <= 30
    return int(np.where(oscuro.mean(axis=1) > 0.8)[0].max())


def en_tres_momentos(estudio: Estudio, episodio: Path, id_: str, camara: str, duracion: int) -> list[Imagen]:
    assert dibujar(estudio, episodio, id_, camara).codigo == 0
    return [leer(episodio, id_, n) for n in (0, (duracion - 1) // 2, duracion - 1)]


# --- Acercamiento ---


def test_un_acercamiento_agranda_el_encuadre_con_el_centro_quieto_y_la_base_sobre_el_suelo(
    estudio: Estudio, episodio: Path
) -> None:
    duracion = (lineas := preparar_planos_de_camara(estudio, episodio))["01"]["final"] - lineas["01"]["inicio"]

    inicial, medio, final = en_tres_momentos(estudio, episodio, "01", "hasta = { ancho = 0.8 }", duracion)

    for imagen, ancho in ((inicial, 1.0), (medio, 0.9), (final, 0.8)):
        tamano, centro, base = cuerpo(imagen)
        assert tamano == pytest.approx(CUERPO_ANCHO / ancho, rel=0.03)  # el ancho de vista manda el tamaño
        assert centro == pytest.approx(MITAD, abs=3)  # el centro casi quieto: el cuerpo no se desplaza de lado
        assert base == pytest.approx(630 / ancho + 960, abs=2)  # la base sigue la línea de suelo del escenario


def test_personajes_y_escenario_se_mueven_juntos_y_la_union_con_el_suelo_no_se_separa(
    estudio: Estudio, episodio: Path
) -> None:
    duracion = (lineas := preparar_planos_de_camara(estudio, episodio))["01"]["final"] - lineas["01"]["inicio"]

    cuadros = en_tres_momentos(estudio, episodio, "01", "hasta = { ancho = 0.75 }", duracion)

    for imagen, ancho in zip(cuadros, (1.0, 0.875, 0.75), strict=True):
        _, _, base = cuerpo(imagen)
        distancia = (base - fila_de_la_linea_de_suelo(imagen)) * ancho  # los 30 píxeles de siempre, escalados por la vista
        assert distancia == pytest.approx(SUELO - LINEA_DE_SUELO, abs=3)


def test_el_acercamiento_no_pierde_nitidez_ni_en_el_limite_del_70_por_ciento(estudio: Estudio, episodio: Path) -> None:
    duracion = (lineas := preparar_planos_de_camara(estudio, episodio))["01"]["final"] - lineas["01"]["inicio"]
    assert dibujar(estudio, episodio, "01", "hasta = { ancho = 0.7 }").codigo == 0

    final = leer(episodio, "01", duracion - 1)
    izquierda, _, arriba, abajo = donde_hay(final, CUERPO)
    fila = final[(arriba + abajo) // 2, izquierda - 8 : izquierda + 8]
    de_cuerpo = np.abs(fila - np.array(CUERPO)).max(axis=1) <= 30
    de_prado = np.abs(fila - np.array((124, 194, 98))).max(axis=1) <= 30
    assert int((~de_cuerpo & ~de_prado).sum()) <= 3  # el borde del cuerpo pasa de un color al otro en pocos píxeles


def test_la_roca_de_una_pose_sentada_se_mueve_con_la_camara_y_su_base_sigue_en_el_suelo(
    estudio: Estudio, episodio: Path
) -> None:
    duracion = (lineas := preparar_planos_de_camara(estudio, episodio))["01"]["final"] - lineas["01"]["inicio"]
    crear_sentada(episodio, UNA)
    sentado_y_perro = 'personajes = [{ pose = "tutor_sentado" }, { pose = "perro_de_pie" }]\n'

    assert dibujar(estudio, episodio, "01", "hasta = { ancho = 0.8 }", sentado_y_perro).codigo == 0

    for numero in (0, duracion - 1):
        imagen = leer(episodio, "01", numero)
        _, _, _, base_de_la_roca = donde_esta_la_roca(imagen)
        suelas = donde_hay(imagen, PIERNAS)[3]
        # el relleno de la roca acaba donde empieza su contorno de abajo (unos 6 píxeles por encima de la base, más con zoom):
        # que no pase de las suelas ni quede lejos de ellas es que la roca y las suelas siguen en la misma línea de suelo
        assert 0 <= suelas - base_de_la_roca <= 14


# --- Desplazamiento ---

DESPLAZAMIENTO = "desde = { ancho = 0.8, centro = [0.45, 0.5] }\nhasta = { centro = [0.55, 0.5] }"


def test_un_desplazamiento_mueve_el_centro_en_linea_recta_sin_cambiar_el_tamano(estudio: Estudio, episodio: Path) -> None:
    duracion = (lineas := preparar_planos_de_camara(estudio, episodio))["12"]["final"] - lineas["12"]["inicio"]

    inicial, medio, final = en_tres_momentos(estudio, episodio, "12", DESPLAZAMIENTO, duracion)

    columnas = [cuerpo(imagen)[1] for imagen in (inicial, medio, final)]
    assert columnas == pytest.approx([607.5, 540.0, 472.5], abs=3)  # el cuerpo se va hacia la izquierda al mirar a la derecha
    assert columnas[1] == pytest.approx((columnas[0] + columnas[2]) / 2, abs=2)  # y a mitad de camino está a mitad de camino
    for imagen in (inicial, medio, final):
        tamano, _, base = cuerpo(imagen)
        assert tamano == pytest.approx(CUERPO_ANCHO / 0.8, rel=0.03)
        assert base == pytest.approx(630 / 0.8 + 960, abs=2)  # en línea recta: ni sube ni baja


def test_el_movimiento_se_suaviza_al_principio_y_al_final(estudio: Estudio, episodio: Path) -> None:
    duracion = (lineas := preparar_planos_de_camara(estudio, episodio))["12"]["final"] - lineas["12"]["inicio"]
    assert dibujar(estudio, episodio, "12", DESPLAZAMIENTO).codigo == 0

    columnas = [cuerpo(leer(episodio, "12", n))[1] for n in range(duracion)]
    pasos = [abs(b - a) for a, b in zip(columnas, columnas[1:], strict=False)]
    assert max(pasos[:2]) < 0.25 * max(pasos)  # arranca despacio
    assert max(pasos[-2:]) < 0.25 * max(pasos)  # y frena despacio
    assert all(a >= b - 1 for a, b in zip(columnas, columnas[1:], strict=False))  # siempre hacia el mismo lado


def test_un_plano_con_la_camara_en_movimiento_deja_un_video_de_1080x1920_con_un_fotograma_por_fotograma(
    estudio: Estudio, episodio: Path
) -> None:
    duracion = (lineas := preparar_planos_de_camara(estudio, episodio))["12"]["final"] - lineas["12"]["inicio"]

    resultado = dibujar(estudio, episodio, "12", DESPLAZAMIENTO)

    assert resultado.codigo == 0, resultado.salida
    datos = sonda(episodio / "planos" / "12.mp4")
    assert (int(datos["width"]), int(datos["height"])) == (1080, 1920) and datos["r_frame_rate"] == "30/1"
    assert int(datos["nb_read_frames"]) == duracion
    assert not (episodio / "planos" / "12.png").exists()


def test_un_plano_fijo_sigue_siendo_una_imagen_con_la_vista_entera(estudio: Estudio, episodio: Path) -> None:
    preparar_planos_de_camara(estudio, episodio)
    cambiar(episodio / "planos.toml", 'empieza = "Porque me cuentan"\nescenario = "recibidor"', 'empieza = "Porque me cuentan"\nescenario = "lago"')
    preparar(estudio, episodio)

    assert dibujar(estudio, episodio, "03", "").codigo == 0

    with Image.open(episodio / "planos" / "03.png") as imagen:
        assert imagen.size == (1080, 1920)
    assert not (episodio / "planos" / "03.mp4").exists()


# --- Lo que se rechaza ---


@pytest.mark.parametrize(
    ("id_", "camara", "dice"),
    [
        pytest.param("01", "", "falta «hasta»", id="acercamiento-sin-hasta"),
        pytest.param("01", "hasta = { ancho = 0.5 }", "ancho", id="acercamiento-que-acerca-demasiado"),
        pytest.param("01", "hasta = { ancho = 0.8, centro = [0.6, 0.5] }", "centro", id="acercamiento-que-mueve-el-centro"),
        pytest.param("01", "hasta = { ancho = 1.2 }", "ancho", id="acercamiento-que-aleja"),
        pytest.param("12", "", "falta «hasta»", id="desplazamiento-sin-hasta"),
        pytest.param("12", "hasta = { centro = [0.55, 0.5] }", "desde", id="desplazamiento-sin-desde"),
        pytest.param("12", "desde = { ancho = 0.8 }\nhasta = { centro = [0.8, 0.5] }", "centro", id="desplazamiento-demasiado-largo"),
        pytest.param("12", "desde = { ancho = 0.75 }\nhasta = { ancho = 0.9 }", "ancho", id="desplazamiento-que-cambia-el-ancho"),
        pytest.param("12", "desde = { ancho = 0.8, centro = [0.95, 0.5] }\nhasta = { centro = [0.96, 0.5] }", "se sale", id="vista-fuera-del-escenario"),
        pytest.param("12", "desde = { ancho = 0.5 }\nhasta = { centro = [0.52, 0.5] }", "0.7", id="vista-demasiado-pequena"),
        pytest.param("03", "hasta = { ancho = 0.8 }", "fija", id="plano-fijo-con-hasta"),
        pytest.param("03", "desde = { ancho = 0.8 }", "fija", id="plano-fijo-con-desde"),
        pytest.param("01", "hasta = { ancho = 0.8, color = 3 }", "color", id="campo-desconocido"),
        pytest.param("01", "hasta = { centro = [0.5] }", "centro", id="centro-mal-escrito"),
        pytest.param("01", "hasta = { ancho = 0 }", "ancho", id="ancho-no-valido"),
        pytest.param("01", 'hasta = "cerca"', "hasta", id="hasta-no-es-una-tabla"),
    ],
)
def test_un_movimiento_fuera_de_limites_o_que_no_concuerda_con_la_camara_se_rechaza_y_no_se_dibuja_nada(
    estudio: Estudio, episodio: Path, id_: str, camara: str, dice: str
) -> None:
    preparar_planos_de_camara(estudio, episodio)
    cambiar(episodio / "planos.toml", 'empieza = "Porque me cuentan"\nescenario = "recibidor"', 'empieza = "Porque me cuentan"\nescenario = "lago"')
    preparar(estudio, episodio)

    resultado = dibujar(estudio, episodio, id_, camara)

    assert resultado.codigo == 1 and any(id_ in error and dice in error for error in resultado.errores), resultado.salida
    assert not (episodio / "planos" / f"{id_}.png").exists() and not (episodio / "planos" / f"{id_}.mp4").exists()
    assert not (episodio / "planos" / "_fotogramas" / id_).exists()
