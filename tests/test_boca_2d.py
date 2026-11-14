"""La boca del Tutor en el dibujo 2D (ticket 06 de estudio-2d): una zona blanda de la mandíbula que se abre en las palabras acentuadas.

El Tutor sintético es un cuerpo morado con una mandíbula verde, apoyada por su extremo derecho y con la punta (la barbilla) a
la izquierda: abrir la boca baja la punta. Los tests miran, fotograma a fotograma, a qué altura queda la punta de la mandíbula
y lo comparan con las palabras acentuadas de la línea de tiempo del episodio de ejemplo. Nunca entran ilustraciones reales.
Formato en docs/dibujo-2d.md.
"""

import json
import re
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image, ImageDraw

from ayudas import Estudio, Resultado, cambiar
from test_dibujar_planos import TUTOR, crear_pose
from test_renderizar_planos import preparar

Imagen = NDArray[np.int_]
MANDIBULA = (10, 200, 10)
TUTOR_Y_PERRO = 'personajes = [{ pose = "tutor_de_pie" }, { pose = "perro_de_pie" }]\n'
FICHA = """ilustracion = "tutor_de_pie.png"

[[zona]]
parte = "boca"
caja = [150, 100, 300, 190]
union = [270, 140]
punta = [180, 140]
"""
LINEA_DE_ACTUACION = (
    '\n[[plano]]\nid = "{id}"\npensamiento = "piensa"\nanticipacion = "mira"\naccion = "habla"\npausa = "quieto"\n'
)


def crear_tutor(episodio: Path, ficha: str = FICHA) -> None:
    carpeta = episodio.parent / "biblioteca" / "personajes" / "tutor" / "poses"
    carpeta.mkdir(parents=True, exist_ok=True)
    imagen = Image.new("RGBA", (400, 300), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.rectangle((100, 40, 299, 289), fill=(*TUTOR, 255))
    dibujo.rectangle((180, 130, 269, 149), fill=(*MANDIBULA, 255))
    imagen.save(carpeta / "tutor_de_pie.png")
    (carpeta / "tutor_de_pie.toml").write_text(ficha, encoding="utf-8")


def a_lago(episodio: Path, id_: str) -> None:
    texto = (episodio / "planos.toml").read_text(encoding="utf-8")
    nuevo, cambios = re.subn(rf'(id = "{id_}"\nempieza = "[^"]*"\nescenario = ")[^"]*(")', r"\1lago\2", texto)
    assert cambios == 1
    (episodio / "planos.toml").write_text(nuevo, encoding="utf-8")


def dibujar(estudio: Estudio, episodio: Path, id_: str, reparto: str = TUTOR_Y_PERRO, con_linea: bool = False) -> Resultado:
    if con_linea:
        archivo = episodio / "actuacion.toml"
        archivo.write_text(archivo.read_text(encoding="utf-8") + LINEA_DE_ACTUACION.format(id=id_), encoding="utf-8")
    (episodio / "reparto.toml").write_text(f'[[plano]]\nid = "{id_}"\n{reparto}', encoding="utf-8")
    return estudio("renderizar-planos", episodio, "--planos", id_)


def preparar_con_el_tutor_hablando(estudio: Estudio, episodio: Path) -> dict[str, dict[str, int]]:
    """El plano 05 (donde habla el Tutor) pasa al lago, con *nariz* acentuada en su frase, y se cronometra."""
    crear_tutor(episodio)
    crear_pose(episodio)
    a_lago(episodio, "05")
    cambiar(episodio / "guion.md", "¿Todo eso con la nariz?", "¿Todo eso con la *nariz*?")
    return preparar(estudio, episodio)


def fotograma(episodio: Path, id_: str, numero: int) -> Imagen:
    with Image.open(episodio / "planos" / "_fotogramas" / id_ / f"{numero:04d}.png") as imagen:
        return np.asarray(imagen.convert("RGB")).astype(np.int_)


def punta_de_la_mandibula(imagen: Imagen, columna: int) -> float:
    """La fila media de la mandíbula en una franja de diez columnas junto a su punta: baja cuando la boca se abre."""
    verde = np.abs(imagen[:, columna : columna + 10] - np.array(MANDIBULA)).max(axis=2) <= 30
    return float(np.where(verde.any(axis=1))[0].mean())


def columna_de_la_punta(imagen: Imagen) -> int:
    verde = np.abs(imagen - np.array(MANDIBULA)).max(axis=2) <= 30
    return int(np.where(verde.any(axis=0))[0].min())


def acentuadas_del_tutor(episodio: Path) -> list[tuple[int, int]]:
    datos = json.loads((episodio / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    return [(p["inicio"], p["final"]) for f in datos["frases"] if f["personaje"] == "Tutor" for p in f["palabras"] if p["acentuada"]]


# --- La boca se abre solo cuando habla ---


def test_la_mandibula_se_abre_solo_en_las_palabras_acentuadas_del_tutor_fotograma_a_fotograma(
    estudio: Estudio, episodio: Path
) -> None:
    linea = preparar_con_el_tutor_hablando(estudio, episodio)

    resultado = dibujar(estudio, episodio, "05")

    assert resultado.codigo == 0, resultado.salida
    assert (episodio / "planos" / "05.mp4").is_file() and not (episodio / "planos" / "05.png").exists()  # sin línea de actuación, se anima sola
    (palabra,) = acentuadas_del_tutor(episodio)
    inicio, final = linea["05"]["inicio"], linea["05"]["final"]
    assert inicio <= palabra[0] < palabra[1] <= final
    cuadros = [fotograma(episodio, "05", n) for n in range(final - inicio)]
    columna = columna_de_la_punta(cuadros[0])
    puntas = [punta_de_la_mandibula(c, columna) for c in cuadros]
    reposo = float(np.median([p for n, p in enumerate(puntas) if not palabra[0] <= inicio + n < palabra[1]]))
    for numero, punta in enumerate(puntas):
        if palabra[0] <= inicio + numero < palabra[1]:
            assert punta >= reposo + 3, (numero, punta, reposo)  # abierta dentro de la palabra
        else:
            assert abs(punta - reposo) <= 1.5, (numero, punta, reposo)  # cerrada fuera de ella
    dentro = [p for n, p in enumerate(puntas) if palabra[0] <= inicio + n < palabra[1]]
    assert max(dentro) - min(dentro) >= 1.5  # y alterna entre abierta grande y abierta pequeña


def test_un_plano_donde_el_tutor_no_habla_no_cambia_la_boca_en_ningun_fotograma(estudio: Estudio, episodio: Path) -> None:
    crear_tutor(episodio)
    crear_pose(episodio)
    a_lago(episodio, "07")  # habla el Perro, con palabras acentuadas
    cambiar(episodio / "guion.md", "¿Todo eso con la nariz?", "¿Todo eso con la *nariz*?")  # y el Tutor habla en otro plano
    linea = preparar(estudio, episodio)
    assert acentuadas_del_tutor(episodio) and not any(
        linea["07"]["inicio"] <= a < linea["07"]["final"] for a, _ in acentuadas_del_tutor(episodio)
    )

    resultado = dibujar(estudio, episodio, "07", con_linea=True)  # con línea, el plano se anima: respira

    assert resultado.codigo == 0, resultado.salida
    cuadros = [fotograma(episodio, "07", n) for n in range(linea["07"]["final"] - linea["07"]["inicio"])]
    columna = columna_de_la_punta(cuadros[0])
    puntas = [punta_de_la_mandibula(c, columna) for c in cuadros]
    assert max(puntas) - min(puntas) <= 1.5  # solo respira


def test_un_tutor_sin_zona_de_boca_no_mueve_la_boca_aunque_hable(estudio: Estudio, episodio: Path) -> None:
    preparar_con_el_tutor_hablando(estudio, episodio)
    crear_tutor(episodio, ficha='ilustracion = "tutor_de_pie.png"\n')

    resultado = dibujar(estudio, episodio, "05")

    assert resultado.codigo == 0, resultado.salida
    assert (episodio / "planos" / "05.png").is_file() and not (episodio / "planos" / "05.mp4").exists()  # nada se mueve: una imagen


# --- Lo que se rechaza ---


@pytest.mark.parametrize(
    ("ficha", "dice"),
    [
        pytest.param(FICHA.replace("[150, 100, 300, 190]", "[150, 100, 500, 190]"), "caja", id="caja-fuera-de-la-ilustracion"),
        pytest.param(FICHA.replace("punta = [180, 140]", "punta = [270, 140]"), "punta", id="punta-igual-a-la-union"),
        pytest.param(FICHA.replace("union = [270, 140]\n", ""), "union", id="falta-la-union"),
    ],
)
def test_una_zona_de_boca_mal_escrita_se_rechaza_nombrando_la_pose(estudio: Estudio, episodio: Path, ficha: str, dice: str) -> None:
    preparar_con_el_tutor_hablando(estudio, episodio)
    crear_tutor(episodio, ficha)

    resultado = dibujar(estudio, episodio, "05")

    assert resultado.codigo == 1 and any("tutor_de_pie" in e and dice in e for e in resultado.errores), resultado.salida
    assert not (episodio / "planos" / "05.png").exists() and not (episodio / "planos" / "05.mp4").exists()


def test_la_zona_de_boca_solo_vale_para_el_tutor(estudio: Estudio, episodio: Path) -> None:
    preparar_con_el_tutor_hablando(estudio, episodio)
    carpeta = episodio.parent / "biblioteca" / "personajes" / "perro" / "poses"
    (carpeta / "perro_de_pie.toml").write_text('ilustracion = "perro_de_pie.png"\n' + FICHA[FICHA.index("\n[[zona]]") :], encoding="utf-8")

    resultado = dibujar(estudio, episodio, "05")

    assert resultado.codigo == 1 and any("perro_de_pie" in e and "boca" in e and "Perro" in e for e in resultado.errores), resultado.salida
