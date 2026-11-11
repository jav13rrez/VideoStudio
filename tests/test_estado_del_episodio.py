"""Crear un episodio y seguir su estado: paradas aprobadas, escenarios y personajes nuevos, y horas por etapa.

La carpeta de ejemplo, 001-olfato, no tiene estado.toml: es como un episodio en el que nada está aprobado.
Su lista de planos marca «parque» como escenario nuevo, y la biblioteca de los tests no tiene personajes,
así que el Perro y el Tutor también esperan su primera aprobación.
"""

import shutil
import tomllib
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from ayudas import CONFIGURACION, Estudio, Resultado, cambiar

HOY = date.today()


def estado_guardado(episodio: Path) -> dict[str, Any]:
    return tomllib.loads((episodio / "estado.toml").read_text(encoding="utf-8"))


@pytest.fixture
def estudio_vacio(tmp_path: Path) -> Path:
    """Un estudio sin episodios: solo su configuración."""
    shutil.copy(CONFIGURACION, tmp_path / CONFIGURACION.name)
    return tmp_path


def linea(resultado: Resultado, empieza: str) -> str:
    """La línea de la salida que empieza así."""
    encontradas = [linea for linea in resultado.salida.splitlines() if linea.startswith(empieza)]
    assert len(encontradas) == 1, resultado.salida
    return encontradas[0]


# --- Crear un episodio ---


def test_crear_un_episodio_deja_la_carpeta_con_el_numero_siguiente_su_estructura_y_su_estado_inicial(
    estudio: Estudio, episodio: Path
) -> None:
    resultado = estudio("crear-episodio", episodio.parent / "paseo")

    assert resultado.codigo == 0, resultado.salida
    nuevo = episodio.parent / "002-paseo"
    assert "002-paseo" in resultado.salida
    for archivo in ("contenido.md", "guion.md", "fuentes.md", "estado.toml"):
        assert (nuevo / archivo).is_file(), archivo
    assert estado_guardado(nuevo) == {}

    estado = estudio("estado", nuevo)
    assert estado.codigo == 0, estado.salida
    assert "guion" in linea(estado, "Paso:")
    assert "parada 1" in linea(estado, "Esperando:")
    assert "ninguna" in linea(estado, "Paradas aprobadas:")


def test_la_numeracion_sigue_a_la_carpeta_de_numero_mas_alto_y_no_cuenta_las_demas(
    estudio: Estudio, estudio_vacio: Path
) -> None:
    for carpeta in ("001-olfato", "005-correa", "biblioteca", "notas-007"):
        (estudio_vacio / carpeta).mkdir()

    assert estudio("crear-episodio", estudio_vacio / "juego").codigo == 0

    assert (estudio_vacio / "006-juego").is_dir()


def test_el_primer_episodio_de_una_carpeta_es_el_001(estudio: Estudio, estudio_vacio: Path) -> None:
    assert estudio("crear-episodio", estudio_vacio / "episodios" / "olfato").codigo == 0

    assert (estudio_vacio / "episodios" / "001-olfato").is_dir()


@pytest.mark.parametrize("nombre", ["Paseo", "paseo largo", "002-paseo", "pasëo", "-paseo"])
def test_un_nombre_corto_que_no_es_de_minusculas_numeros_y_guiones_no_crea_nada(
    estudio: Estudio, estudio_vacio: Path, nombre: str
) -> None:
    resultado = estudio("crear-episodio", estudio_vacio / nombre)

    assert resultado.codigo == 1
    assert any("nombre corto" in error for error in resultado.errores), resultado.salida
    assert [archivo.name for archivo in estudio_vacio.iterdir()] == [CONFIGURACION.name]


def test_un_episodio_fuera_del_estudio_no_se_crea(estudio: Estudio, tmp_path: Path) -> None:
    resultado = estudio("crear-episodio", tmp_path / "olfato")

    assert resultado.codigo == 1
    assert any("estudio.toml" in error for error in resultado.errores), resultado.salida
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("orden", "argumentos"), [("estado", ()), ("aprobar", ("parada", "1")), ("registrar-horas", ("guion", "1"))]
)
def test_una_carpeta_de_episodio_que_no_existe_da_un_error_claro(
    estudio: Estudio, estudio_vacio: Path, orden: str, argumentos: tuple[str, ...]
) -> None:
    resultado = estudio(orden, estudio_vacio / "009-no-existe", *argumentos)

    assert resultado.codigo == 1
    assert any("No existe" in error for error in resultado.errores), resultado.salida
    assert not (estudio_vacio / "009-no-existe").exists()


# --- Paradas ---


def test_aprobar_una_parada_la_anota_con_su_fecha_y_el_episodio_pasa_al_paso_siguiente(
    estudio: Estudio, episodio: Path
) -> None:
    resultado = estudio("aprobar", episodio, "parada", "1")

    assert resultado.codigo == 0, resultado.salida
    assert estado_guardado(episodio)["paradas"] == {"1": HOY}
    estado = estudio("estado", episodio)
    assert f"parada 1 el {HOY.isoformat()}" in linea(estado, "Paradas aprobadas:")
    assert "versión previa" in linea(estado, "Paso:")
    assert "parada 2" in linea(estado, "Esperando:")


def test_una_parada_no_se_aprueba_antes_que_la_anterior(estudio: Estudio, episodio: Path) -> None:
    resultado = estudio("aprobar", episodio, "parada", "2")

    assert resultado.codigo == 1
    assert any("parada 1" in error for error in resultado.errores), resultado.salida
    assert not (episodio / "estado.toml").exists()


@pytest.mark.parametrize("parada", ["4", "0", "una"])
def test_solo_hay_paradas_1_2_y_3(estudio: Estudio, episodio: Path, parada: str) -> None:
    resultado = estudio("aprobar", episodio, "parada", parada)

    assert resultado.codigo == 1
    assert any("1, 2 o 3" in error for error in resultado.errores), resultado.salida


def test_aprobar_otra_vez_una_parada_avisa_y_conserva_la_fecha_de_la_primera_vez(
    estudio: Estudio, episodio: Path
) -> None:
    assert estudio("aprobar", episodio, "parada", "1").codigo == 0
    cambiar(episodio / "estado.toml", HOY.isoformat(), "2026-01-02")

    resultado = estudio("aprobar", episodio, "parada", "1")

    assert resultado.codigo == 0, resultado.salida
    assert any("2026-01-02" in aviso for aviso in resultado.avisos), resultado.salida
    assert estado_guardado(episodio)["paradas"] == {"1": date(2026, 1, 2)}


def test_con_las_tres_paradas_aprobadas_solo_queda_subirlo_a_mano(estudio: Estudio, episodio: Path) -> None:
    for parada in ("1", "2", "3"):
        assert estudio("aprobar", episodio, "parada", parada).codigo == 0

    estado = estudio("estado", episodio)

    assert "exportación y la publicación" in linea(estado, "Paso:")
    assert "a mano" in linea(estado, "Esperando:")


# --- Escenarios y personajes nuevos ---


def test_el_estado_dice_que_escenarios_y_personajes_nuevos_esperan_aprobacion(
    estudio: Estudio, episodio: Path
) -> None:
    estado = estudio("estado", episodio)

    assert estado.codigo == 0, estado.salida
    assert "parque" in linea(estado, "Escenarios nuevos por aprobar:")
    assert linea(estado, "Personajes nuevos por aprobar:").endswith("Perro, Tutor.")


def test_mientras_haya_escenarios_o_personajes_por_aprobar_el_estado_dice_que_tambien_los_espera(
    estudio: Estudio, episodio: Path
) -> None:
    assert estudio("aprobar", episodio, "parada", "1").codigo == 0
    assert "escenarios y personajes nuevos" in linea(estudio("estado", episodio), "Esperando:")

    for que, nombre in (("escenario", "parque"), ("personaje", "Perro"), ("personaje", "Tutor")):
        assert estudio("aprobar", episodio, que, nombre).codigo == 0

    assert "escenarios y personajes nuevos" not in linea(estudio("estado", episodio), "Esperando:")


def test_escenarios_nuevos_mal_escrito_no_cuenta_letra_a_letra(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio / "planos.toml", 'escenarios_nuevos = ["parque"]', 'escenarios_nuevos = "parque"')

    assert "ninguno" in linea(estudio("estado", episodio), "Escenarios nuevos por aprobar:")
    assert estudio("aprobar", episodio, "escenario", "p").codigo == 1


def test_un_personaje_que_ya_esta_en_la_biblioteca_no_espera_aprobacion(estudio: Estudio, episodio: Path) -> None:
    (episodio.parent / "biblioteca" / "personajes" / "Perro").mkdir(parents=True)

    estado = estudio("estado", episodio)

    assert linea(estado, "Personajes nuevos por aprobar:").endswith("Tutor.")


def test_aprobar_un_escenario_nuevo_lo_anota_y_deja_de_esperar(estudio: Estudio, episodio: Path) -> None:
    resultado = estudio("aprobar", episodio, "escenario", "parque")

    assert resultado.codigo == 0, resultado.salida
    assert estado_guardado(episodio)["escenarios"] == {"parque": HOY}
    estado = estudio("estado", episodio)
    assert "ninguno" in linea(estado, "Escenarios nuevos por aprobar:")
    assert f"parque el {HOY.isoformat()}" in linea(estado, "Escenarios aprobados:")


def test_aprobar_un_personaje_nuevo_lo_anota_y_deja_de_esperar(estudio: Estudio, episodio: Path) -> None:
    assert estudio("aprobar", episodio, "personaje", "Tutor").codigo == 0

    assert estado_guardado(episodio)["personajes"] == {"Tutor": HOY}
    estado = estudio("estado", episodio)
    assert linea(estado, "Personajes nuevos por aprobar:").endswith("Perro.")


@pytest.mark.parametrize(("que", "nombre"), [("escenario", "salon"), ("escenario", "playa"), ("personaje", "Gato")])
def test_solo_se_aprueban_escenarios_y_personajes_que_esperan_aprobacion(
    estudio: Estudio, episodio: Path, que: str, nombre: str
) -> None:
    resultado = estudio("aprobar", episodio, que, nombre)

    assert resultado.codigo == 1
    assert any(nombre in error for error in resultado.errores), resultado.salida
    assert not (episodio / "estado.toml").exists()


def test_sin_lista_de_planos_no_hay_escenarios_ni_personajes_que_esperen(estudio: Estudio, episodio: Path) -> None:
    (episodio / "planos.toml").unlink()

    estado = estudio("estado", episodio)

    assert "ninguno" in linea(estado, "Escenarios nuevos por aprobar:")
    assert "ninguno" in linea(estado, "Personajes nuevos por aprobar:")


# --- Horas ---


def test_el_registro_de_horas_suma_las_horas_de_cada_etapa_y_el_total(estudio: Estudio, episodio: Path) -> None:
    for etapa, horas in (("guion", "1,5"), ("guion", "0.5"), ("voces", "2"), ("revision", "0,25")):
        resultado = estudio("registrar-horas", episodio, etapa, horas)
        assert resultado.codigo == 0, resultado.salida

    assert estado_guardado(episodio)["horas"] == {"guion": 2, "voces": 2, "revision": 0.25}
    estado = estudio("estado", episodio)
    assert linea(estado, "  guion:") == "  guion: 2 h"
    assert linea(estado, "  voces:") == "  voces: 2 h"
    assert linea(estado, "  revision:") == "  revision: 0,25 h"
    assert linea(estado, "Total:") == "Total: 4,25 h"


def test_sin_horas_registradas_el_total_es_cero(estudio: Estudio, episodio: Path) -> None:
    assert linea(estudio("estado", episodio), "Total:") == "Total: 0 h"


def test_solo_se_registran_horas_de_las_etapas_del_estudio(estudio: Estudio, episodio: Path) -> None:
    resultado = estudio("registrar-horas", episodio, "comer", "1")

    assert resultado.codigo == 1
    assert any("guion, escenarios, personajes" in error for error in resultado.errores), resultado.salida


@pytest.mark.parametrize("horas", ["0", "-1", "mucho", "nan", "inf"])
def test_las_horas_son_un_numero_mayor_que_cero(estudio: Estudio, episodio: Path, horas: str) -> None:
    resultado = estudio("registrar-horas", episodio, "guion", horas)

    assert resultado.codigo == 1
    assert any("número de horas" in error for error in resultado.errores), resultado.salida
    assert not (episodio / "estado.toml").exists()


# --- Archivo de estado roto ---


@pytest.mark.parametrize(
    "paradas", ['"1" = 2026-01-01\n"2" = 2026-01-01\n"3" = 2026-01-01\n"4" = 2026-01-01', '"3" = 2026-01-01']
)
def test_unas_paradas_guardadas_que_no_van_en_orden_dan_un_error_claro(
    estudio: Estudio, episodio: Path, paradas: str
) -> None:
    (episodio / "estado.toml").write_text(f"[paradas]\n{paradas}\n", encoding="utf-8")

    resultado = estudio("estado", episodio)

    assert resultado.codigo == 1
    assert any("estado.toml" in error for error in resultado.errores), resultado.salida


def test_un_estado_que_no_se_entiende_da_un_error_claro_y_no_se_sobrescribe(
    estudio: Estudio, episodio: Path
) -> None:
    (episodio / "estado.toml").write_text("[paradas\n", encoding="utf-8")

    for orden, argumentos in (("estado", ()), ("aprobar", ("parada", "1")), ("registrar-horas", ("guion", "1"))):
        resultado = estudio(orden, episodio, *argumentos)
        assert resultado.codigo == 1
        assert any("estado.toml" in error for error in resultado.errores), resultado.salida

    assert (episodio / "estado.toml").read_text(encoding="utf-8") == "[paradas\n"
