"""generar-poses: genera la ilustración de una pose a partir de la hoja del creador, con confirmación antes de gastar.

Solo se usa el proveedor `falso`, que dibuja una ilustración de prueba sin gastar y sin clave. Los tests miran lo que
sale: los archivos de la biblioteca, la ficha y lo que la orden escribe en pantalla. Formato en docs/dibujo-2d.md.
"""

import re
import tomllib
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from ayudas import Estudio, Resultado
from test_dibujar_planos import dibujar, imagen_del_plano, preparar_el_lago

CLAVE = "clave-secreta-de-prueba-123"
FALSO = ("--proveedor", "falso")
GENERAR = (*FALSO, "--confirmar")


def _personaje(episodio: Path, pose: str) -> Path:
    return episodio.parent / "biblioteca" / "personajes" / pose.split("_")[0]


def ilustracion_de(episodio: Path, pose: str) -> Path:
    return _personaje(episodio, pose) / "poses" / f"{pose}.png"


def ficha_de(episodio: Path, pose: str) -> Path:
    return _personaje(episodio, pose) / "poses" / f"{pose}.toml"


def crear_hoja(episodio: Path, pose: str) -> Path:
    """La hoja del creador con la vista de perfil que necesita la pose."""
    carpeta = episodio.parent / "biblioteca" / "personajes" / "_trabajo" / "hojas"
    carpeta.mkdir(parents=True, exist_ok=True)
    hoja = carpeta / f"{pose}_perfil_izq.png"
    Image.new("RGB", (300, 400), (200, 200, 200)).save(hoja)
    return hoja


def generar(estudio: Estudio, episodio: Path, pose: str, *argumentos: str) -> Resultado:
    return estudio("generar-poses", episodio, pose, *argumentos)


def ficha(episodio: Path, pose: str) -> dict[str, Any]:
    datos: dict[str, Any] = tomllib.loads(ficha_de(episodio, pose).read_text(encoding="utf-8"))
    return datos


@pytest.fixture(autouse=True)
def sin_clave_de_fal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FAL_KEY", raising=False)


# --- Confirmación y coste ---


def test_sin_confirmacion_dice_cuantas_imagenes_y_cuanto_cuestan_y_no_genera_nada(
    estudio: Estudio, episodio: Path
) -> None:
    crear_hoja(episodio, "tutor_sentado")

    resultado = generar(estudio, episodio, "tutor_sentado", *FALSO)

    assert resultado.codigo == 1
    assert "1 imagen" in resultado.salida
    assert "0,00 €" in resultado.salida
    assert "--confirmar" in resultado.salida
    assert not ilustracion_de(episodio, "tutor_sentado").exists()
    assert not ficha_de(episodio, "tutor_sentado").exists()


def test_con_confirmacion_deja_la_ilustracion_y_su_ficha(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "tutor_sentado")

    resultado = generar(estudio, episodio, "tutor_sentado", *GENERAR)

    assert resultado.codigo == 0, resultado.salida
    with Image.open(ilustracion_de(episodio, "tutor_sentado")) as imagen:
        assert imagen.mode == "RGBA"
        minimo, maximo = imagen.getchannel("A").getextrema()
        assert maximo == 255  # tiene silueta opaca...
        assert minimo == 0  # ...sobre un fondo transparente
    assert ficha(episodio, "tutor_sentado")["ilustracion"] == "tutor_sentado.png"


def test_la_ilustracion_generada_se_puede_usar_en_un_plano(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "perro_de_pie")
    assert generar(estudio, episodio, "perro_de_pie", *GENERAR).codigo == 0
    preparar_el_lago(estudio, episodio)

    resultado = dibujar(estudio, episodio, '[[plano]]\nid = "03"\npersonajes = [{ pose = "perro_de_pie" }]\n')

    assert resultado.codigo == 0, resultado.salida
    assert imagen_del_plano(episodio).shape[:2] == (1920, 1080)


# --- La ficha anota cómo se hizo ---


def test_la_ficha_anota_el_modelo_el_texto_y_la_fecha(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "tutor_sentado")
    generar(estudio, episodio, "tutor_sentado", *GENERAR)

    generacion = ficha(episodio, "tutor_sentado")["generacion"]

    assert generacion["modelo"] == "falso"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", generacion["fecha"])
    assert generacion["fecha"] == date.today().isoformat()
    assert generacion["texto"].strip()


def test_el_texto_sigue_la_plantilla_fija_del_estilo_de_la_casa(estudio: Estudio, episodio: Path) -> None:
    for pose in ("tutor_sentado", "perro_tumbado"):
        crear_hoja(episodio, pose)
        generar(estudio, episodio, pose, *GENERAR)

    tutor = ficha(episodio, "tutor_sentado")["generacion"]["texto"]
    perro = ficha(episodio, "perro_tumbado")["generacion"]["texto"]

    for texto in (tutor, perro):
        assert "uniform thickness" in texto  # contorno uniforme
        assert "two tones" in texto  # dos tonos
        assert "flat" in texto  # plano
        assert "facing left" in texto
    assert "man" in tutor and "sitting" in tutor
    assert "dog" in perro and "lying down" in perro
    assert tutor != perro


def test_pedir_dos_veces_la_misma_pose_da_el_mismo_texto(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "tutor_sentado")
    generar(estudio, episodio, "tutor_sentado", *GENERAR)
    primero = ficha(episodio, "tutor_sentado")["generacion"]["texto"]

    assert generar(estudio, episodio, "tutor_sentado", *GENERAR, "--reemplazar").codigo == 0

    assert ficha(episodio, "tutor_sentado")["generacion"]["texto"] == primero


def test_una_pose_con_ficha_conserva_sus_medidas_al_regenerarla(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "tutor_sentado")
    generar(estudio, episodio, "tutor_sentado", *GENERAR)
    # la ficha con las medidas que el creador o el agente le han puesto a mano, y que la generación no debe tocar
    ficha_de(episodio, "tutor_sentado").write_text(
        'ilustracion = "tutor_sentado.png"\nasiento = 61.5\ntrasero = 0.25\n\n'
        '[[ignora]]\nparte = "cola"\ncaja = [1, 2, 3, 4]\n\n'
        '[generacion]\nmodelo = "antiguo"\ntexto = "uno viejo"\nfecha = "2020-01-01"\n',
        encoding="utf-8",
    )

    resultado = generar(estudio, episodio, "tutor_sentado", *GENERAR, "--reemplazar")

    assert resultado.codigo == 0, resultado.salida
    datos = ficha(episodio, "tutor_sentado")
    assert datos["asiento"] == 61.5
    assert datos["trasero"] == 0.25
    assert datos["ignora"] == [{"parte": "cola", "caja": [1, 2, 3, 4]}]
    assert datos["generacion"]["modelo"] == "falso"
    assert ficha_de(episodio, "tutor_sentado").read_text(encoding="utf-8").count("[generacion]") == 1


# --- No pisar lo que ya hay ---


def test_no_pisa_una_pose_que_ya_existe_sin_que_se_pida(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "tutor_sentado")
    generar(estudio, episodio, "tutor_sentado", *GENERAR)
    ilustracion = ilustracion_de(episodio, "tutor_sentado")
    ilustracion.write_bytes(b"aprobada por el creador")

    resultado = generar(estudio, episodio, "tutor_sentado", *GENERAR)

    assert resultado.codigo == 1
    assert "--reemplazar" in resultado.salida
    assert ilustracion.read_bytes() == b"aprobada por el creador"


def test_con_reemplazar_vuelve_a_dibujar_la_ilustracion(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "tutor_sentado")
    generar(estudio, episodio, "tutor_sentado", *GENERAR)
    ilustracion = ilustracion_de(episodio, "tutor_sentado")
    ilustracion.write_bytes(b"una mala")

    assert generar(estudio, episodio, "tutor_sentado", *GENERAR, "--reemplazar").codigo == 0

    with Image.open(ilustracion) as imagen:
        assert imagen.size[0] > 0


# --- Avisos antes de generar ---


def test_avisa_si_a_la_hoja_le_falta_la_vista_que_necesita_la_pose_y_no_genera(
    estudio: Estudio, episodio: Path
) -> None:
    resultado = generar(estudio, episodio, "perro_tumbado", *GENERAR)

    assert resultado.codigo == 1
    assert any("perro_tumbado_perfil_izq.png" in error for error in resultado.errores), resultado.salida
    assert not ilustracion_de(episodio, "perro_tumbado").exists()
    assert not ficha_de(episodio, "perro_tumbado").exists()


def test_con_la_vista_que_falta_ni_siquiera_pide_confirmacion(estudio: Estudio, episodio: Path) -> None:
    resultado = generar(estudio, episodio, "perro_tumbado", *FALSO)

    assert resultado.codigo == 1
    assert "1 imagen" not in resultado.salida


@pytest.mark.parametrize(
    ("pose", "dice"),
    [
        ("gato_sentado", "tutor"),  # un personaje que no conoce
        ("tutor_volando", "sentado"),  # una postura que no conoce
        ("tutor", "personaje"),  # sin postura
    ],
)
def test_una_pose_que_no_conoce_lo_dice_y_ensena_las_que_hay(
    estudio: Estudio, episodio: Path, pose: str, dice: str
) -> None:
    resultado = generar(estudio, episodio, pose, *GENERAR)

    assert resultado.codigo == 1
    assert dice in resultado.salida
    assert not (episodio.parent / "biblioteca" / "personajes" / pose.split("_")[0] / "poses").exists()


def test_un_proveedor_que_no_conoce_lo_dice_y_ensena_los_que_hay(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "tutor_sentado")

    resultado = generar(estudio, episodio, "tutor_sentado", "--proveedor", "inventado", "--confirmar")

    assert resultado.codigo == 1
    assert "falso" in resultado.salida and "fal" in resultado.salida
    assert not ilustracion_de(episodio, "tutor_sentado").exists()


# --- La clave del proveedor real ---


def test_con_fal_sin_clave_dice_donde_ponerla_y_no_genera(estudio: Estudio, episodio: Path) -> None:
    crear_hoja(episodio, "tutor_sentado")

    resultado = generar(estudio, episodio, "tutor_sentado", "--proveedor", "fal", "--confirmar")

    assert resultado.codigo == 1
    assert "FAL_KEY" in resultado.salida
    assert ".env" in resultado.salida
    assert not ilustracion_de(episodio, "tutor_sentado").exists()


def test_la_clave_se_lee_de_env_y_nunca_se_escribe_en_pantalla_ni_en_archivos(
    estudio: Estudio, episodio: Path
) -> None:
    crear_hoja(episodio, "tutor_sentado")
    (episodio.parent / ".env").write_text(f"FAL_KEY={CLAVE}\n", encoding="utf-8")

    resultado = generar(estudio, episodio, "tutor_sentado", "--proveedor", "fal", "--confirmar")

    assert resultado.codigo == 1  # el proveedor fal todavía no genera (ticket 08)
    assert "ticket 08" in resultado.salida
    assert "FAL_KEY" not in resultado.salida  # con la clave puesta, ya no pide ponerla
    assert CLAVE not in resultado.salida
    assert not ilustracion_de(episodio, "tutor_sentado").exists()
    assert not ficha_de(episodio, "tutor_sentado").exists()


def test_con_el_proveedor_falso_no_hace_falta_clave_ni_se_escribe_la_del_entorno(
    estudio: Estudio, episodio: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    crear_hoja(episodio, "tutor_sentado")
    monkeypatch.setenv("FAL_KEY", CLAVE)

    resultado = generar(estudio, episodio, "tutor_sentado", *GENERAR)

    assert resultado.codigo == 0, resultado.salida
    assert CLAVE not in resultado.salida
    assert CLAVE not in ficha_de(episodio, "tutor_sentado").read_text(encoding="utf-8")
