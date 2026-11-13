"""Dibujar los planos en 2D: renderizar-planos con un reparto.toml dibuja el plano sin pasar por Blender.

Los tests usan poses sintéticas (un rectángulo rojo de cuerpo y, a veces, uno azul que hace de cola) con una silueta y
una línea de suelo conocidas, y miran solo la imagen que sale. Nunca entran ilustraciones reales: llevan el rostro del
creador. Formato en docs/dibujo-2d.md.
"""

from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image, ImageDraw

from ayudas import Estudio, Resultado, cambiar
from test_renderizar_planos import preparar

TAMANO = (1080, 1920)
CUERPO = (251, 3, 7)
COLA = (3, 7, 251)
ILUSTRACION = (400, 300)  # ancho y alto de las ilustraciones sintéticas
CAJA_DEL_CUERPO = (100, 40, 300, 240)
CAJA_DE_LA_COLA = (300, 200, 360, 290)  # cuelga por debajo del cuerpo
UN_PERRO = '[[plano]]\nid = "03"\npersonajes = [{ pose = "perro_de_pie" }]\n'
SIN_PERSONAJES = '[[plano]]\nid = "03"\npersonajes = []\n'
FICHA = 'ilustracion = "perro_de_pie.png"\n'


def crear_pose(
    episodio: Path,
    nombre: str = "perro_de_pie",
    cuerpo: tuple[int, int, int, int] | None = CAJA_DEL_CUERPO,
    cola: bool = False,
    halo: int = 0,
    ficha: str | None = None,
    tamano: tuple[int, int] = ILUSTRACION,
) -> None:
    """Escribe en la biblioteca una pose sintética: su ilustración y su ficha."""
    carpeta = episodio.parent / "biblioteca" / "personajes" / nombre.split("_")[0] / "poses"
    carpeta.mkdir(parents=True, exist_ok=True)
    imagen = Image.new("RGBA", tamano, (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    texto = f'ilustracion = "{nombre}.png"\n'
    if cuerpo is not None:
        dibujo.rectangle(_inclusiva(cuerpo), fill=(*CUERPO, 255))
        if halo:  # un borde casi transparente por debajo del cuerpo, como el que deja un recorte
            dibujo.rectangle(_inclusiva((cuerpo[0], cuerpo[3], cuerpo[2], cuerpo[3] + halo)), fill=(*CUERPO, 10))
    if cola:
        dibujo.rectangle(_inclusiva(CAJA_DE_LA_COLA), fill=(*COLA, 255))
        texto += f'\n[[ignora]]\nparte = "cola"\ncaja = {list(CAJA_DE_LA_COLA)}\n'
    imagen.save(carpeta / f"{nombre}.png")
    (carpeta / f"{nombre}.toml").write_text(texto if ficha is None else ficha, encoding="utf-8")


def _inclusiva(caja: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Pillow dibuja los rectángulos con el último píxel incluido; las cajas de aquí acaban en el primero de fuera."""
    return caja[0], caja[1], caja[2] - 1, caja[3] - 1


def preparar_el_lago(estudio: Estudio, episodio: Path) -> None:
    """El plano 03 pasa al escenario lago (el único que tiene receta 2D) y se cronometra el episodio."""
    cambiar(
        episodio / "planos.toml",
        'empieza = "Porque me cuentan"\nescenario = "recibidor"',
        'empieza = "Porque me cuentan"\nescenario = "lago"',
    )
    preparar(estudio, episodio)


def dibujar(estudio: Estudio, episodio: Path, reparto: str, *argumentos: str) -> Resultado:
    (episodio / "reparto.toml").write_text(reparto, encoding="utf-8")
    return estudio("renderizar-planos", episodio, *(argumentos or ("--planos", "03")))


def imagen_del_plano(episodio: Path, id_: str = "03") -> NDArray[np.int_]:
    with Image.open(episodio / "planos" / f"{id_}.png") as imagen:
        return np.asarray(imagen.convert("RGB")).astype(np.int_)


def donde_hay(imagen: NDArray[np.int_], color: tuple[int, int, int]) -> tuple[int, int, int, int]:
    """Columna mínima, columna máxima, fila mínima y fila máxima de los píxeles de ese color."""
    cerca = np.abs(imagen - np.array(color)).max(axis=2) <= 30
    assert cerca.any(), f"no hay píxeles de color {color} en la imagen"
    filas, columnas = np.where(cerca)
    return int(columnas.min()), int(columnas.max()), int(filas.min()), int(filas.max())


def claridad(imagen: NDArray[np.int_], columna: int, fila: int) -> float:
    return float(imagen[fila, columna].mean())


def test_un_plano_fijo_en_2d_deja_una_imagen_de_1080x1920_sin_pasar_por_blender(
    estudio: Estudio, episodio: Path
) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_PERRO)

    assert resultado.codigo == 0, resultado.salida
    with Image.open(episodio / "planos" / "03.png") as imagen:
        assert imagen.size == TAMANO
    assert not (episodio / "planos" / "03.mp4").exists()
    assert not (episodio / "planos" / "_fotogramas").exists()
    assert "Blender" not in resultado.salida


def test_el_escenario_lago_dibuja_cielo_lago_y_prado(estudio: Estudio, episodio: Path) -> None:
    preparar_el_lago(estudio, episodio)

    assert dibujar(estudio, episodio, SIN_PERSONAJES).codigo == 0
    imagen = imagen_del_plano(episodio)

    cielo, lago, prado = (imagen[fila - 10 : fila + 10, 500:580].reshape(-1, 3).mean(axis=0) for fila in (100, 950, 1750))
    assert cielo[2] > cielo[0] + 20  # el cielo es azul
    assert lago[2] > lago[0] + 30 and lago[1] > lago[0]  # el lago es azul verdoso
    assert prado[1] > prado[0] + 20 and prado[1] > prado[2] + 20  # el prado es verde


def test_toda_pose_apoya_en_la_misma_linea_de_suelo_y_queda_en_el_centro(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio, "perro_de_pie")
    crear_pose(episodio, "perro_sentado", cuerpo=(80, 20, 320, 280))
    preparar_el_lago(estudio, episodio)

    assert dibujar(estudio, episodio, UN_PERRO).codigo == 0
    de_pie = donde_hay(imagen_del_plano(episodio), CUERPO)
    assert dibujar(estudio, episodio, UN_PERRO.replace("perro_de_pie", "perro_sentado")).codigo == 0
    sentado = donde_hay(imagen_del_plano(episodio), CUERPO)

    assert abs(de_pie[3] - sentado[3]) <= 2  # lo más bajo de las dos cae en la misma fila
    assert sentado[2] < de_pie[2]  # y la más alta sobresale más: no están todas a la misma altura
    for columnas in (de_pie, sentado):
        assert abs((columnas[0] + columnas[1]) / 2 - TAMANO[0] / 2) <= 3  # centrada en la imagen


def test_las_partes_que_la_ficha_manda_ignorar_no_cuentan_para_apoyar(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio, "perro_de_pie")
    crear_pose(episodio, "perro_con_cola", cola=True)
    preparar_el_lago(estudio, episodio)

    assert dibujar(estudio, episodio, UN_PERRO).codigo == 0
    sin_cola = donde_hay(imagen_del_plano(episodio), CUERPO)
    assert dibujar(estudio, episodio, UN_PERRO.replace("perro_de_pie", "perro_con_cola")).codigo == 0
    imagen = imagen_del_plano(episodio)
    con_cola = donde_hay(imagen, CUERPO)

    assert abs(con_cola[3] - sin_cola[3]) <= 2  # el cuerpo apoya igual
    assert donde_hay(imagen, COLA)[3] > con_cola[3] + 10  # y la cola, que sí se dibuja, cuelga por debajo del suelo


def test_la_silueta_se_mide_con_lo_opaco_y_no_con_la_caja_del_recorte(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio, "perro_de_pie")
    crear_pose(episodio, "perro_con_halo", halo=40)
    preparar_el_lago(estudio, episodio)

    assert dibujar(estudio, episodio, UN_PERRO).codigo == 0
    limpia = donde_hay(imagen_del_plano(episodio), CUERPO)
    assert dibujar(estudio, episodio, UN_PERRO.replace("perro_de_pie", "perro_con_halo")).codigo == 0
    con_halo = donde_hay(imagen_del_plano(episodio), CUERPO)

    assert abs(con_halo[3] - limpia[3]) <= 2  # el borde translúcido no levanta a la pose del suelo


def test_hay_una_sombra_de_contacto_bajo_la_pose(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)

    assert dibujar(estudio, episodio, UN_PERRO).codigo == 0
    con_pose = imagen_del_plano(episodio)
    fila = donde_hay(con_pose, CUERPO)[3] + 8
    assert dibujar(estudio, episodio, SIN_PERSONAJES).codigo == 0
    sin_pose = imagen_del_plano(episodio)

    assert claridad(con_pose, TAMANO[0] // 2, fila) < claridad(sin_pose, TAMANO[0] // 2, fila) - 10


def test_dos_renders_del_mismo_plano_salen_identicos(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)

    assert dibujar(estudio, episodio, UN_PERRO).codigo == 0
    primero = (episodio / "planos" / "03.png").read_bytes()
    assert dibujar(estudio, episodio, UN_PERRO).codigo == 0

    assert (episodio / "planos" / "03.png").read_bytes() == primero


def test_si_falta_la_pose_la_orden_lo_dice_y_no_dibuja_a_medias(estudio: Estudio, episodio: Path) -> None:
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_PERRO)

    assert resultado.codigo == 1
    assert any("perro_de_pie" in error and "03" in error for error in resultado.errores), resultado.salida
    assert not (episodio / "planos" / "03.png").exists()


def test_una_pose_mas_ancha_que_el_plano_se_rechaza_en_vez_de_dibujarla_recortada(
    estudio: Estudio, episodio: Path
) -> None:
    crear_pose(episodio, cuerpo=(0, 40, 1900, 240), tamano=(2000, 300))
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_PERRO)

    assert resultado.codigo == 1
    assert any("perro_de_pie" in error and "no cabe" in error for error in resultado.errores), resultado.salida
    assert not (episodio / "planos" / "03.png").exists()


def test_una_ilustracion_sin_nada_opaco_se_rechaza(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio, cuerpo=None)
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_PERRO)

    assert resultado.codigo == 1
    assert any("perro_de_pie" in error and "opaco" in error for error in resultado.errores), resultado.salida
    assert not (episodio / "planos" / "03.png").exists()


@pytest.mark.parametrize(
    ("ficha", "dice"),
    [
        pytest.param("", "ilustracion", id="sin-ilustracion"),
        pytest.param('ilustracion = "no-existe.png"\n', "no-existe.png", id="ilustracion-que-no-existe"),
        pytest.param(FICHA + '[[ignora]]\nparte = "cola"\ncaja = [1, 2, 3]\n', "caja", id="caja-con-tres-numeros"),
        pytest.param(FICHA + '[[ignora]]\nparte = "cola"\ncaja = [0, 0, 999, 999]\n', "caja", id="caja-fuera-de-la-imagen"),
        pytest.param(FICHA + "suelo = 5\n", "suelo", id="clave-desconocida"),
    ],
)
def test_una_ficha_mal_escrita_dice_que_falla_y_no_dibuja_nada(
    estudio: Estudio, episodio: Path, ficha: str, dice: str
) -> None:
    crear_pose(episodio, ficha=ficha)
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_PERRO)

    assert resultado.codigo == 1
    assert any("perro_de_pie" in error and dice in error for error in resultado.errores), resultado.salida
    assert not (episodio / "planos" / "03.png").exists()


def test_un_plano_elegido_sin_reparto_se_rechaza(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, '[[plano]]\nid = "05"\npersonajes = []\n')

    assert resultado.codigo == 1
    assert any("03" in error and "reparto.toml" in error for error in resultado.errores), resultado.salida


def test_solo_hace_falta_el_reparto_de_los_planos_elegidos(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)
    otro_plano = '\n[[plano]]\nid = "05"\npersonajes = [{ pose = "perro_que_no_existe" }]\n'

    resultado = dibujar(estudio, episodio, UN_PERRO + otro_plano)

    assert resultado.codigo == 0, resultado.salida
    assert (episodio / "planos" / "03.png").is_file()


def test_un_plano_de_camara_en_movimiento_se_rechaza_por_ahora(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    cambiar(
        episodio / "planos.toml",
        'empieza = "¿Sabes por qué"\nescenario = "recibidor"',
        'empieza = "¿Sabes por qué"\nescenario = "lago"',
    )
    preparar(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_PERRO.replace('"03"', '"01"'), "--planos", "01")

    assert resultado.codigo == 1
    assert any("01" in error and "cámara fija" in error for error in resultado.errores), resultado.salida
    assert not (episodio / "planos" / "01.png").exists()


def test_un_escenario_sin_receta_2d_se_rechaza_y_dice_cuales_hay(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    preparar(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_PERRO.replace('"03"', '"17"'), "--planos", "17")

    assert resultado.codigo == 1
    assert any("parque" in error and "lago" in error for error in resultado.errores), resultado.salida


def test_dos_personajes_en_un_plano_se_rechazan_por_ahora(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(
        estudio, episodio, '[[plano]]\nid = "03"\npersonajes = [{ pose = "perro_de_pie" }, { pose = "perro_de_pie" }]\n'
    )

    assert resultado.codigo == 1
    assert any("03" in error and "un solo personaje" in error for error in resultado.errores), resultado.salida


def test_un_rango_de_fotogramas_no_vale_en_un_plano_fijo_de_una_sola_imagen(estudio: Estudio, episodio: Path) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, UN_PERRO, "--planos", "03", "--fotogramas", "0-1")

    assert resultado.codigo == 1
    assert any("fotogramas" in error and "03" in error for error in resultado.errores), resultado.salida


@pytest.mark.parametrize(
    ("reparto", "dice"),
    [
        pytest.param('[[plano]]\nid = "99"\npersonajes = []\n', "99", id="plano-que-no-esta-en-la-lista"),
        pytest.param(
            '[[plano]]\nid = "03"\npersonajes = [{ pose = "perro_de_pie", soporte = "roca" }]\n', "soporte", id="clave-desconocida"
        ),
        pytest.param('[[plano]]\nid = "03"\npersonajes = [{ nombre = "perro_de_pie" }]\n', "pose", id="falta-la-pose"),
        pytest.param('[[plano]]\nid = "03"\nfondo = "lago"\npersonajes = []\n', "fondo", id="campo-desconocido-en-el-plano"),
    ],
)
def test_un_reparto_mal_escrito_dice_que_falla(estudio: Estudio, episodio: Path, reparto: str, dice: str) -> None:
    crear_pose(episodio)
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, reparto)

    assert resultado.codigo == 1
    assert any("reparto.toml" in error and dice in error for error in resultado.errores), resultado.salida
    assert not (episodio / "planos" / "03.png").exists()
