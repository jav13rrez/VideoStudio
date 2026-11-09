"""Comprobar un guion: la herramienta ejecutada sobre carpetas de episodio de ejemplo."""

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest

from estudio.cli import main

EJEMPLO = Path(__file__).parent / "episodios" / "001-olfato"


@dataclass
class Resultado:
    codigo: int
    salida: str
    errores: list[str]
    avisos: list[str]


def _leer(codigo: int, salida: str) -> Resultado:
    """Separa la salida de la herramienta en sus listas de errores y avisos."""
    errores: list[str] = []
    avisos: list[str] = []
    lista: list[str] | None = None
    for linea in salida.splitlines():
        if linea.startswith("Errores"):
            lista = errores
        elif linea.startswith("Avisos"):
            lista = avisos
        elif linea.startswith("  - ") and lista is not None:
            lista.append(linea[4:])
        elif not linea.strip():
            lista = None
    return Resultado(codigo, salida, errores, avisos)


Comprobar = Callable[[Path], Resultado]


@pytest.fixture
def comprobar(capsys: pytest.CaptureFixture[str]) -> Comprobar:
    def _comprobar(carpeta: Path) -> Resultado:
        codigo = main(["comprobar-guion", str(carpeta)])
        return _leer(codigo, capsys.readouterr().out)

    return _comprobar


@pytest.fixture
def episodio(tmp_path: Path) -> Path:
    """Una copia de la carpeta de ejemplo, para cambiarla en cada test."""
    carpeta = tmp_path / EJEMPLO.name
    shutil.copytree(EJEMPLO, carpeta)
    return carpeta


def escribir_episodio(carpeta: Path, palabras_conversacion: int, palabras_cta: int = 5) -> Path:
    """Un episodio sin fuentes con el número de palabras que se pida."""
    carpeta.mkdir()
    gancho = " ".join(["guau"] * (palabras_conversacion - 1))
    cta = " ".join(["app"] * palabras_cta)
    guion = f"[gancho] Perro: {gancho}\n[remate] Tutor: Vale.\n[cta] Perro: {cta}\n"
    (carpeta / "guion.md").write_text(guion, encoding="utf-8")
    return carpeta


def cambiar(archivo: Path, antes: str, despues: str) -> None:
    texto = archivo.read_text(encoding="utf-8")
    assert texto.count(antes) == 1, f"«{antes}» tiene que aparecer una vez en {archivo.name}"
    archivo.write_text(texto.replace(antes, despues), encoding="utf-8")


def test_un_guion_correcto_pasa_sin_errores_ni_avisos(comprobar: Comprobar) -> None:
    resultado = comprobar(EJEMPLO)

    assert resultado.errores == []
    assert resultado.avisos == []
    assert resultado.codigo == 0
    assert "Resultado: el guion puede pasar a la parada 1." in resultado.salida


def test_error_si_habla_un_personaje_que_no_es_el_perro_ni_el_tutor(
    comprobar: Comprobar, episodio: Path
) -> None:
    cambiar(episodio / "guion.md", "Tutor: ¿Porque huelen fatal?", "Gato: ¿Porque huelen fatal?")

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "Gato" in resultado.errores[0]
    assert "línea 4" in resultado.errores[0].lower()
    assert "no puede pasar a la parada 1" in resultado.salida


def test_error_si_el_cta_lo_dice_el_tutor(comprobar: Comprobar, episodio: Path) -> None:
    cambiar(episodio / "guion.md", "[cta] Perro:", "[cta] Tutor:")

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "CTA" in resultado.errores[0]
    assert "Tutor" in resultado.errores[0]


def test_error_si_el_cta_no_va_al_final(comprobar: Comprobar, episodio: Path) -> None:
    remate = "[remate] Tutor: Pues a partir de hoy, tú marcas el ritmo y yo leo contigo.\n"
    cta = "[cta] Perro: Pídele a la App un plan de paseos hecho para tu perro.\n"
    cambiar(episodio / "guion.md", remate + cta, cta + remate)

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "CTA" in resultado.errores[0]
    assert "final" in resultado.errores[0]


def test_error_si_una_marca_apunta_a_una_fuente_que_no_existe(
    comprobar: Comprobar, episodio: Path
) -> None:
    cambiar(episodio / "guion.md", "[fuente: nova]", "[fuente: nova] [fuente: nasa]")

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "nasa" in resultado.errores[0]
    assert "línea 7" in resultado.errores[0].lower()


@pytest.mark.parametrize("palabras", [150, 170])
def test_sin_aviso_si_la_conversacion_tiene_entre_150_y_170_palabras(
    comprobar: Comprobar, tmp_path: Path, palabras: int
) -> None:
    resultado = comprobar(escribir_episodio(tmp_path / "ep", palabras))

    assert resultado.avisos == []
    assert resultado.codigo == 0


@pytest.mark.parametrize("palabras", [149, 171])
def test_aviso_si_la_conversacion_se_sale_de_150_a_170_palabras(
    comprobar: Comprobar, tmp_path: Path, palabras: int
) -> None:
    resultado = comprobar(escribir_episodio(tmp_path / "ep", palabras))

    assert len(resultado.avisos) == 1
    assert str(palabras) in resultado.avisos[0]
    assert "150" in resultado.avisos[0] and "170" in resultado.avisos[0]
    assert resultado.codigo == 0


def test_las_marcas_no_cuentan_como_palabras(comprobar: Comprobar, episodio: Path) -> None:
    # El ejemplo tiene 164 palabras en la conversación; se le añaden 7.
    cambiar(episodio / "guion.md", "[fuente: craven]", "Y lo hago siempre así, cada día. [fuente: craven]")

    resultado = comprobar(episodio)

    assert len(resultado.avisos) == 1
    assert "171 palabras" in resultado.avisos[0]


def test_sin_aviso_si_el_cta_tiene_15_palabras(comprobar: Comprobar, tmp_path: Path) -> None:
    resultado = comprobar(escribir_episodio(tmp_path / "ep", 160, palabras_cta=15))

    assert resultado.avisos == []


def test_aviso_si_el_cta_pasa_de_15_palabras(comprobar: Comprobar, tmp_path: Path) -> None:
    resultado = comprobar(escribir_episodio(tmp_path / "ep", 160, palabras_cta=16))

    assert len(resultado.avisos) == 1
    assert "CTA" in resultado.avisos[0]
    assert "16" in resultado.avisos[0]
    assert resultado.codigo == 0


def test_aviso_si_falta_la_marca_de_gancho(comprobar: Comprobar, episodio: Path) -> None:
    cambiar(episodio / "guion.md", "[gancho] Perro:", "Perro:")

    resultado = comprobar(episodio)

    assert len(resultado.avisos) == 1
    assert "gancho" in resultado.avisos[0]
    assert resultado.codigo == 0


def test_aviso_si_falta_la_marca_de_remate(comprobar: Comprobar, episodio: Path) -> None:
    cambiar(episodio / "guion.md", "[remate] Tutor:", "Tutor:")

    resultado = comprobar(episodio)

    assert len(resultado.avisos) == 1
    assert "remate" in resultado.avisos[0]
    assert resultado.codigo == 0


def test_aviso_por_fuentes_que_ninguna_frase_usa(comprobar: Comprobar, episodio: Path) -> None:
    fuentes = episodio / "fuentes.md"
    with fuentes.open("a", encoding="utf-8") as archivo:
        archivo.write("- [x] coren: Los perros sueñan. — Coren, S. (2004). How Dogs Think. Free Press.\n")

    resultado = comprobar(episodio)

    assert len(resultado.avisos) == 1
    assert "coren" in resultado.avisos[0]
    assert "ninguna frase" in resultado.avisos[0]
    assert resultado.codigo == 0


def test_aviso_por_fuentes_que_el_creador_no_ha_revisado(comprobar: Comprobar, episodio: Path) -> None:
    cambiar(episodio / "fuentes.md", "- [x] nova:", "- [ ] nova:")

    resultado = comprobar(episodio)

    assert len(resultado.avisos) == 1
    assert "nova" in resultado.avisos[0]
    assert "revisad" in resultado.avisos[0]
    assert resultado.codigo == 0


def test_error_si_la_carpeta_no_tiene_guion(comprobar: Comprobar, tmp_path: Path) -> None:
    resultado = comprobar(tmp_path)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "guion.md" in resultado.errores[0]


def test_error_si_una_linea_del_guion_no_sigue_el_formato(comprobar: Comprobar, episodio: Path) -> None:
    cambiar(episodio / "guion.md", "Tutor: ¿Y si te meto prisa?", "Tutor - ¿Y si te meto prisa?")

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "línea 12" in resultado.errores[0].lower()


@pytest.mark.parametrize("marca", ["[ctaa]", "[CTA]"])
def test_error_si_una_frase_lleva_una_marca_desconocida(
    comprobar: Comprobar, episodio: Path, marca: str
) -> None:
    cambiar(episodio / "guion.md", "[cta] Perro:", f"{marca} Perro:")

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert marca in resultado.errores[0]


@pytest.mark.parametrize(
    ("antes", "despues", "marca"),
    [
        ("[fuente: nova]", "[Fuente: nova]", "[Fuente: nova]"),
        ("[fuente: nova]", "[fuente nova]", "[fuente nova]"),
        ("[fuente: nova]", "[fuente: nova, craven]", "[fuente: nova, craven]"),
        ("[gancho] Perro: ¿Sabes", "Perro: [gancho] ¿Sabes", "[gancho]"),
    ],
)
def test_error_si_dentro_de_una_frase_hay_una_marca_mal_escrita(
    comprobar: Comprobar, episodio: Path, antes: str, despues: str, marca: str
) -> None:
    cambiar(episodio / "guion.md", antes, despues)

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert marca in resultado.errores[0]


def test_error_si_el_guion_no_tiene_frases(comprobar: Comprobar, tmp_path: Path) -> None:
    (tmp_path / "guion.md").write_text("# Guion\n\n", encoding="utf-8")

    resultado = comprobar(tmp_path)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "frases" in resultado.errores[0]


def test_un_guion_guardado_con_bom_pasa_igual(comprobar: Comprobar, episodio: Path) -> None:
    """Algunos editores de Windows ponen un carácter invisible (BOM) al principio del archivo."""
    for nombre in ("guion.md", "fuentes.md"):
        archivo = episodio / nombre
        archivo.write_text(archivo.read_text(encoding="utf-8"), encoding="utf-8-sig")

    resultado = comprobar(episodio)

    assert resultado.errores == []
    assert resultado.avisos == []


def test_error_si_una_linea_de_las_fuentes_no_sigue_el_formato(
    comprobar: Comprobar, episodio: Path
) -> None:
    cambiar(episodio / "fuentes.md", "- [x] nova:", "- [] nova:")

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert any("fuentes.md, línea 4" in error for error in resultado.errores)


def test_aviso_si_el_guion_no_tiene_cta(comprobar: Comprobar, episodio: Path) -> None:
    cambiar(episodio / "guion.md", "[cta] Perro: Pídele a la App un plan de paseos hecho para tu perro.\n", "")

    resultado = comprobar(episodio)

    assert len(resultado.avisos) == 1
    assert "CTA" in resultado.avisos[0]
    assert resultado.codigo == 0


def test_error_si_una_fuente_no_dice_nada_despues_de_su_id(comprobar: Comprobar, episodio: Path) -> None:
    fuentes = episodio / "fuentes.md"
    lineas = fuentes.read_text(encoding="utf-8").splitlines()
    assert lineas[3].startswith("- [x] nova:")
    lineas[3] = "- [x] nova:"
    fuentes.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    resultado = comprobar(episodio)

    assert resultado.codigo == 1
    assert any("fuentes.md, línea 4" in error for error in resultado.errores)
