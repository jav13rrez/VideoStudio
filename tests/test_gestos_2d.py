"""Gestos con zonas blandas en un plano 2D (ticket 04 de estudio-2d): orejas, cola, párpado y respiración.

El Perro sintético es un cuerpo rojo con una oreja verde que sube desde el lomo, una cola azul que sale por detrás y un ojo
negro, con una silueta y unas zonas conocidas. Los tests miran solo los fotogramas que deja la herramienta. Nunca entran
ilustraciones reales. Formato en docs/dibujo-2d.md y docs/actuacion.md.
"""

import hashlib
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image, ImageDraw

from ayudas import Estudio, Resultado
from estudio.actuacion import ACCION, ANTICIPACION, DURACION_DEL_GESTO, MANTIENE
from test_dibujar_planos import CUERPO, TUTOR, crear_pose, donde_hay, preparar_el_lago
from test_renderizar_planos import sonda

Imagen = NDArray[np.int_]
Caja = tuple[int, int, int, int]

OREJA = (10, 200, 10)
COLA = (3, 7, 251)
NEGRO = 40  # un píxel con todos los canales por debajo de esto es del ojo
ESCALA = 0.66
FOTOGRAMAS = 60  # lo que dura el plano 03 de los episodios de prueba
UNO = '[[plano]]\nid = "03"\npersonajes = [{ pose = "perro_de_pie" }]\n'
DOS = '[[plano]]\nid = "03"\npersonajes = [{ pose = "tutor_de_pie" }, { pose = "perro_de_pie" }]\n'
CUERPO_DEL_PERRO = (100, 80, 300, 290)  # la fila 289 es la última: el suelo
CAJA_OREJA = (130, 0, 230, 100)
CAJA_COLA = (280, 180, 430, 265)
OJO = (230, 120, 250, 140)
INICIO = 6  # del gesto de los tests
ANGULO = 30.0  # el máximo que admite un gesto
PUNTA_SUBE = 12  # píxeles que sube la punta de la cola con ese ángulo (se dobla, no gira entera)
PICO = INICIO + ANTICIPACION + ACCION  # el primer fotograma con todo el ángulo
MARCA = '\n[[plano]]\nid = "03"'  # donde empieza, al final de actuacion.toml, la línea del plano 03

ZONA_OREJAS = f'\n[[zona]]\nparte = "orejas"\ncaja = {list(CAJA_OREJA)}\nunion = [180, 80]\npunta = [180, 20]\n'
ZONA_COLA = f'\n[[zona]]\nparte = "cola"\ncaja = {list(CAJA_COLA)}\nunion = [310, 220]\npunta = [395, 220]\n'
IGNORA_COLA = '\n[[ignora]]\nparte = "cola"\ncaja = [300, 205, 400, 235]\n'
FICHA = 'ilustracion = "perro_de_pie.png"\n'
CON_OJO = FICHA + f"ojo = {list(OJO)}\n"
COMPLETA = CON_OJO + IGNORA_COLA + ZONA_OREJAS + ZONA_COLA


def crear_perro(episodio: Path, ficha: str = COMPLETA) -> None:
    """El Perro sintético: 440x300 de ilustración y el suelo en la fila 290."""
    carpeta = episodio.parent / "biblioteca" / "personajes" / "perro" / "poses"
    carpeta.mkdir(parents=True, exist_ok=True)
    imagen = Image.new("RGBA", (440, 300), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    x0, y0, x1, y1 = CUERPO_DEL_PERRO
    dibujo.rectangle((x0, y0, x1 - 1, y1 - 1), fill=(*CUERPO, 255))
    dibujo.rectangle((170, 20, 189, 79), fill=(*OREJA, 255))
    dibujo.rectangle((300, 205, 399, 234), fill=(*COLA, 255))
    dibujo.ellipse(OJO, fill=(0, 0, 0, 255))
    imagen.save(carpeta / "perro_de_pie.png")
    (carpeta / "perro_de_pie.toml").write_text(ficha, encoding="utf-8")


def gesto(parte: str, inicio: int, angulo: float, pieza: str = "perro_de_pie") -> str:
    return f'gestos = [{{ pieza = "{pieza}", parte = "{parte}", inicio = {inicio}, angulo = {angulo} }}]'


def renderizar(
    estudio: Estudio, episodio: Path, reparto: str = UNO, gestos: str = "", parpadeos: str = "", con_linea: bool = True
) -> Resultado:
    """Escribe la línea del plano 03 en actuacion.toml (cambia la de antes), su reparto y renderiza ese plano."""
    archivo = episodio / "actuacion.toml"
    texto = archivo.read_text(encoding="utf-8")
    texto = texto[: texto.index(MARCA)] if MARCA in texto else texto
    if con_linea:
        texto += (
            f'{MARCA}\npensamiento = "piensa"\nanticipacion = "mira"\naccion = "se mueve"\npausa = "quieto"\n'
            f"{gestos}\n{parpadeos}\n"
        )
    archivo.write_text(texto, encoding="utf-8")
    (episodio / "reparto.toml").write_text(reparto, encoding="utf-8")
    return estudio("renderizar-planos", episodio, "--planos", "03")


def preparar_un_perro(estudio: Estudio, episodio: Path, ficha: str = COMPLETA) -> None:
    crear_perro(episodio, ficha)
    preparar_el_lago(estudio, episodio)


def carpeta_de_fotogramas(episodio: Path) -> Path:
    return episodio / "planos" / "_fotogramas" / "03"


def leer(episodio: Path, numero: int) -> Imagen:
    with Image.open(carpeta_de_fotogramas(episodio) / f"{numero:04d}.png") as imagen:
        return np.asarray(imagen.convert("RGB")).astype(np.int_)


def hay(imagen: Imagen, color: tuple[int, int, int]) -> NDArray[np.bool_]:
    return np.asarray(np.abs(imagen - np.array(color)).max(axis=2) <= 30)


def fila_mas_alta(imagen: Imagen, color: tuple[int, int, int], columna: int | None = None) -> int:
    """La fila más alta de lo que tiene ese color (o, con `columna`, de lo que hay en esa columna)."""
    mascara = hay(imagen, color)
    filas = np.where(mascara.any(axis=1) if columna is None else mascara[:, columna])[0]
    return int(filas.min())


def centro_de_la_cola(imagen: Imagen, columna: int) -> float:
    """La fila media de la cola en una franja de cinco columnas: baja y sube con la flexión de la cola en ese punto."""
    filas = np.where(hay(imagen, COLA)[:, columna - 2 : columna + 3].any(axis=1))[0]
    return float(filas.mean())


def a_la_imagen(reposo: Imagen, caja: Caja) -> tuple[float, float, float, float]:
    """Una caja de la ilustración del Perro, en la imagen: la posición del cuerpo en un fotograma en reposo da el origen."""
    izquierda, _, _, suelo = donde_hay(reposo, CUERPO)
    x0, y0, x1, y1 = caja
    return (
        izquierda + (x0 - CUERPO_DEL_PERRO[0]) * ESCALA,
        suelo - (CUERPO_DEL_PERRO[3] - 1 - y0) * ESCALA,
        izquierda + (x1 - CUERPO_DEL_PERRO[0]) * ESCALA,
        suelo - (CUERPO_DEL_PERRO[3] - 1 - y1) * ESCALA,
    )


def columna_de_la_cola(reposo: Imagen, x: int) -> int:
    return round(a_la_imagen(reposo, (x, 0, x + 1, 1))[0])


def trozos(mascara: NDArray[np.bool_]) -> int:
    """Cuántos trozos separados (contando diagonales) tiene la máscara."""
    pendientes = {(int(f), int(c)) for f, c in zip(*np.where(mascara), strict=True)}
    cuenta = 0
    while pendientes:
        cuenta += 1
        pila = [pendientes.pop()]
        while pila:
            f, c = pila.pop()
            for vecino in ((f + a, c + b) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                if vecino in pendientes:
                    pendientes.remove(vecino)
                    pila.append(vecino)
    return cuenta


def sin_nada_escrito(episodio: Path) -> bool:
    planos = episodio / "planos"
    return not (planos / "03.png").exists() and not (planos / "03.mp4").exists() and not carpeta_de_fotogramas(episodio).exists()


# --- Una zona gira el ángulo del gesto por su peso ---


def test_la_cola_gira_por_su_peso_sin_cambiar_nada_fuera_de_su_caja_ni_abrir_huecos_en_la_union(
    estudio: Estudio, episodio: Path
) -> None:
    preparar_un_perro(estudio, episodio)
    assert renderizar(estudio, episodio).codigo == 0
    reposo = leer(episodio, PICO + 3)

    assert renderizar(estudio, episodio, gestos=gesto("cola", INICIO, ANGULO)).codigo == 0
    girada = leer(episodio, PICO + 3)  # el mismo fotograma, con todo el ángulo del gesto

    # nada cambia fuera de la caja de la zona (con unos píxeles de margen por el reescalado) y dentro sí cambia
    cambia = np.any(reposo != girada, axis=2)
    filas, columnas = np.where(cambia)
    x0, y0, x1, y1 = a_la_imagen(reposo, CAJA_COLA)
    assert columnas.min() >= x0 - 4 and columnas.max() <= x1 + 4 and filas.min() >= y0 - 4 and filas.max() <= y1 + 4
    assert cambia.sum() > 200

    # el peso: casi nada junto a la unión, y la punta sube lo que el ángulo manda; en medio, algo intermedio
    subida = {
        x: centro_de_la_cola(reposo, columna_de_la_cola(reposo, x)) - centro_de_la_cola(girada, columna_de_la_cola(reposo, x))
        for x in (320, 360, 390)
    }
    assert subida[320] <= 2 and subida[320] < subida[360] < subida[390] and subida[390] >= PUNTA_SUBE

    # en la unión no hay huecos ni cortes: el cuerpo sigue entero, y la cola es un solo trozo pegado a él
    assert not np.any(hay(reposo, CUERPO) & ~hay(girada, CUERPO))
    cola, cuerpo = hay(girada, COLA), hay(girada, CUERPO)
    assert trozos(cola) == 1
    junto_al_cuerpo = np.zeros_like(cuerpo)
    for desplazo in range(-3, 4):
        junto_al_cuerpo |= np.roll(cuerpo, desplazo, axis=1)
    assert np.any(cola & junto_al_cuerpo)


def test_las_orejas_giran_por_su_peso_y_la_cola_no_se_mueve(estudio: Estudio, episodio: Path) -> None:
    preparar_un_perro(estudio, episodio)
    assert renderizar(estudio, episodio).codigo == 0
    reposo = leer(episodio, PICO + 3)

    assert renderizar(estudio, episodio, gestos=gesto("orejas", INICIO, 25.0)).codigo == 0
    girada = leer(episodio, PICO + 3)

    assert np.array_equal(hay(reposo, COLA), hay(girada, COLA))  # la cola, igual
    izquierda_antes = np.where(hay(reposo, OREJA).any(axis=0))[0].min()
    izquierda_ahora = np.where(hay(girada, OREJA).any(axis=0))[0].min()
    assert izquierda_ahora <= izquierda_antes - 8  # la oreja se inclina hacia la izquierda (ángulo positivo: contra el reloj)


# --- La curva del gesto ---


def test_anticipacion_accion_pausa_y_vuelta_sin_rebote_ocurren_en_los_fotogramas_de_la_actuacion(
    estudio: Estudio, episodio: Path
) -> None:
    preparar_un_perro(estudio, episodio)
    assert renderizar(estudio, episodio, gestos=gesto("cola", INICIO, ANGULO)).codigo == 0

    columna = columna_de_la_cola(leer(episodio, 0), 380)
    punta = [centro_de_la_cola(leer(episodio, n), columna) for n in range(FOTOGRAMAS)]  # menor = más arriba
    reposo = punta[0]
    final = INICIO + DURACION_DEL_GESTO

    assert all(abs(p - reposo) <= 1.5 for p in punta[:INICIO])  # antes del inicio, quieta
    assert punta[INICIO + ANTICIPACION] >= reposo + 2  # anticipa: baja un poco, hacia el otro lado
    assert punta[PICO] <= reposo - PUNTA_SUBE  # actúa: sube
    assert all(abs(p - punta[PICO]) <= 1.5 for p in punta[PICO : PICO + MANTIENE])  # se mantiene
    vuelta = punta[PICO + MANTIENE : final + 1]
    assert all(a <= b for a, b in zip(vuelta, vuelta[1:], strict=False))  # vuelve sin parar a mitad
    assert max(punta[PICO + MANTIENE :]) <= reposo + 1.5  # y sin pasarse del reposo: no rebota
    assert all(abs(p - reposo) <= 1.5 for p in punta[final:])  # y se queda quieta


# --- El párpado y la respiración ---


def oscuros_en_el_cuerpo(imagen: Imagen) -> int:
    izquierda, derecha, arriba, abajo = donde_hay(imagen, CUERPO)
    return int((imagen[arriba : abajo + 1, izquierda : derecha + 1].max(axis=2) < NEGRO).sum())


def test_el_parpado_cierra_y_abre_el_ojo_en_pocos_fotogramas(estudio: Estudio, episodio: Path) -> None:
    preparar_un_perro(estudio, episodio)

    assert renderizar(estudio, episodio, parpadeos="parpadeos = [20]").codigo == 0

    abierto = oscuros_en_el_cuerpo(leer(episodio, 19))
    assert abierto > 100
    assert oscuros_en_el_cuerpo(leer(episodio, 23)) < abierto / 3  # cerrado del todo en mitad del parpadeo
    assert 20 < min(n for n in range(20, 27) if oscuros_en_el_cuerpo(leer(episodio, n)) < abierto) < 24  # empieza a cerrar enseguida
    for numero in (26, FOTOGRAMAS - 1):  # en seis fotogramas vuelve a estar abierto, y no parpadea fuera de lo pedido
        assert abs(oscuros_en_el_cuerpo(leer(episodio, numero)) - abierto) <= abierto / 10  # (la respiración mueve unos píxeles)


def test_los_dos_personajes_respiran_con_un_estiramiento_muy_leve_sin_separarse_del_suelo(
    estudio: Estudio, episodio: Path
) -> None:
    crear_pose(episodio, "tutor_de_pie", cuerpo=(100, 20, 300, 290), color=TUTOR)
    preparar_un_perro(estudio, episodio)

    assert renderizar(estudio, episodio, reparto=DOS).codigo == 0

    cuadros = [leer(episodio, n) for n in range(0, FOTOGRAMAS, 3)]
    for color, arriba in ((TUTOR, TUTOR), (CUERPO, OREJA)):
        techos = [fila_mas_alta(c, arriba) for c in cuadros]
        suelos = [donde_hay(c, color)[3] for c in cuadros]
        assert max(suelos) - min(suelos) <= 1  # los pies no se separan del suelo
        assert 1 <= max(techos) - min(techos) <= 3  # la cabeza sube y baja un poco


def test_un_plano_sin_linea_de_actuacion_sigue_siendo_una_sola_imagen(estudio: Estudio, episodio: Path) -> None:
    preparar_un_perro(estudio, episodio)
    assert renderizar(estudio, episodio).codigo == 0
    assert (episodio / "planos" / "03.mp4").is_file()

    assert renderizar(estudio, episodio, con_linea=False).codigo == 0

    assert (episodio / "planos" / "03.png").is_file()
    assert not (episodio / "planos" / "03.mp4").exists() and not carpeta_de_fotogramas(episodio).exists()


# --- El vídeo ---


def test_el_plano_con_gestos_deja_un_video_de_1080x1920_a_30_con_un_fotograma_por_fotograma(
    estudio: Estudio, episodio: Path
) -> None:
    preparar_un_perro(estudio, episodio)

    resultado = renderizar(estudio, episodio, gestos=gesto("cola", INICIO, ANGULO))

    assert resultado.codigo == 0, resultado.salida
    datos = sonda(episodio / "planos" / "03.mp4")
    assert (int(datos["width"]), int(datos["height"])) == (1080, 1920)
    assert datos["r_frame_rate"] == "30/1"
    assert int(datos["nb_read_frames"]) == FOTOGRAMAS
    assert not (episodio / "planos" / "03.png").exists()


def test_dos_renders_del_mismo_plano_salen_identicos(estudio: Estudio, episodio: Path) -> None:
    preparar_un_perro(estudio, episodio)

    def huellas() -> list[str]:
        assert renderizar(estudio, episodio, gestos=gesto("orejas", INICIO, 15.0), parpadeos="parpadeos = [20]").codigo == 0
        return [hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(carpeta_de_fotogramas(episodio).glob("*.png"))]

    assert huellas() == huellas()


# --- Lo que se rechaza ---


@pytest.mark.parametrize(
    ("ficha", "gestos", "parpadeos", "dice"),
    [
        pytest.param(CON_OJO + ZONA_OREJAS, gesto("cola", 6, 10.0), "", "«perro_de_pie» no tiene cola que mover", id="zona-que-la-pose-no-tiene"),
        pytest.param(COMPLETA, gesto("cola", 6, 10.0, pieza="perro_sentado"), "", "«perro_sentado»", id="pose-que-no-esta-en-el-plano"),
        pytest.param(COMPLETA, gesto("cola", 30, 10.0), "", "acaba en 66", id="gesto-que-no-cabe-en-el-plano"),
        pytest.param(COMPLETA, gesto("boca", 6, 10.0), "", "boca", id="la-boca-del-perro-nunca-se-mueve"),
        pytest.param(FICHA + ZONA_COLA, "", "parpadeos = [20]", "no tiene ojo", id="parpadeo-sin-ojo"),
        pytest.param(COMPLETA, "", "parpadeos = [58]", "parpadeo", id="parpadeo-que-no-cabe"),
        pytest.param(COMPLETA, "", "parpadeos = [20, 23]", "se pisan", id="parpadeos-que-se-pisan"),
        pytest.param(COMPLETA, "", "parpadeos = 20", "parpadeos", id="parpadeos-mal-escritos"),
    ],
)
def test_lo_que_no_se_puede_mover_se_rechaza_con_un_mensaje_claro_y_no_se_escribe_nada(
    estudio: Estudio, episodio: Path, ficha: str, gestos: str, parpadeos: str, dice: str
) -> None:
    preparar_un_perro(estudio, episodio, ficha)

    resultado = renderizar(estudio, episodio, gestos=gestos, parpadeos=parpadeos)

    assert resultado.codigo == 1 and any(dice in error for error in resultado.errores), resultado.salida
    assert sin_nada_escrito(episodio)


@pytest.mark.parametrize(
    ("ficha", "dice"),
    [
        pytest.param(CON_OJO + '\n[[zona]]\nparte = "boca"\ncaja = [1, 1, 50, 50]\nunion = [10, 10]\npunta = [40, 40]\n', "boca", id="zona-de-la-boca"),
        pytest.param(CON_OJO + ZONA_COLA.replace('"cola"', '"patas"'), "patas", id="zona-que-no-se-mueve"),
        pytest.param(CON_OJO + ZONA_COLA.replace("430, 265", "500, 265"), "caja", id="caja-fuera-de-la-ilustracion"),
        pytest.param(CON_OJO + ZONA_COLA.replace("union = [310, 220]", "union = [10, 10]"), "union", id="union-fuera-de-la-caja"),
        pytest.param(CON_OJO + ZONA_COLA.replace("punta = [395, 220]", "punta = [310, 220]"), "punta", id="punta-igual-a-la-union"),
        pytest.param(CON_OJO + ZONA_COLA.replace("punta = [395, 220]\n", ""), "punta", id="zona-sin-punta"),
        pytest.param(FICHA + "ojo = [230, 120, 500, 140]\n", "ojo", id="ojo-fuera-de-la-ilustracion"),
    ],
)
def test_una_ficha_con_zonas_o_ojo_mal_escritos_se_rechaza_nombrando_la_pose(
    estudio: Estudio, episodio: Path, ficha: str, dice: str
) -> None:
    preparar_un_perro(estudio, episodio, ficha)

    resultado = renderizar(estudio, episodio)

    assert resultado.codigo == 1 and any("perro_de_pie" in e and dice in e for e in resultado.errores), resultado.salida
    assert sin_nada_escrito(episodio)
