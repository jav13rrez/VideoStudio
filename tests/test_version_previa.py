"""Versión previa de cartón: un cartel por plano y el cierre del CTA, con la herramienta sobre carpetas de ejemplo.

La configuración de los tests da el nombre de la App, «Huellas», pero no su logo.
"""

import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

from ayudas import Estudio, cambiar, declaraciones, leer_composicion, montar, reglas, tramo

SVG = "{http://www.w3.org/2000/svg}"


def escenarios(carpeta: Path) -> dict[str, str]:
    """El escenario de cada plano de la lista de planos, por su id."""
    datos = tomllib.loads((carpeta / "planos.toml").read_text(encoding="utf-8"))
    return {plano["id"]: plano["escenario"] for plano in datos["plano"]}


def cartel(archivo: Path) -> tuple[list[str], str]:
    """Los textos de un cartel y el color de su fondo, que cubre toda la imagen."""
    raiz = ET.parse(archivo).getroot()
    assert (raiz.get("width"), raiz.get("height")) == ("1080", "1920")
    fondo = raiz.find(f"{SVG}rect")
    assert fondo is not None and (fondo.get("width"), fondo.get("height")) == ("1080", "1920")
    return ["".join(texto.itertext()) for texto in raiz.iter(f"{SVG}text")], fondo.get("fill", "")


def test_la_composicion_tiene_una_capa_de_imagen_por_plano_con_los_tiempos_de_la_linea_de_tiempo(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, linea = montar(estudio, episodio)

    assert [(capa["id"], *tramo(capa)) for capa in composicion.planos] == [
        (f"plano-{plano['id']}", plano["inicio"], plano["final"]) for plano in linea["planos"]
    ]
    assert len(composicion.planos) == 29
    # Los planos cubren todo el episodio, sin huecos.
    assert tramo(composicion.planos[0])[0] == 0 and tramo(composicion.planos[-1])[1] == linea["total"]


def test_cada_plano_sin_imagen_lleva_un_cartel_con_su_numero_y_su_escenario_sobre_un_color_liso(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, _ = montar(estudio, episodio)

    escenario_del_plano = escenarios(episodio)
    color_del_escenario: dict[str, set[str]] = {}
    for capa in composicion.planos:
        id_ = capa["id"].removeprefix("plano-")
        assert capa["src"] == f"assets/carteles/{id_}.svg"
        textos, color = cartel(episodio / capa["src"])
        assert id_ in textos and escenario_del_plano[id_] in textos
        color_del_escenario.setdefault(escenario_del_plano[id_], set()).add(color)
    # Un color por escenario, para ver de un vistazo dónde cambia: recibidor, calle, parque y salon.
    assert all(len(colores) == 1 for colores in color_del_escenario.values())
    assert len(set.union(*color_del_escenario.values())) == len(color_del_escenario) == 4


def test_sustituir_la_imagen_de_un_plano_solo_cambia_la_imagen_de_esa_capa(
    estudio: Estudio, episodio: Path
) -> None:
    montar(estudio, episodio)
    antes = (episodio / "index.html").read_text(encoding="utf-8").splitlines()

    # El render del plano 05 llega a planos/, con el id del plano por nombre.
    (episodio / "planos").mkdir()
    (episodio / "planos" / "05.png").write_bytes(b"un render del plano 05")
    resultado = estudio("montar", episodio)

    assert resultado.codigo == 0, resultado.salida
    assert "28 con cartel y 1 con su imagen" in resultado.salida
    despues = (episodio / "index.html").read_text(encoding="utf-8").splitlines()
    cambiadas = [(una, otra) for una, otra in zip(antes, despues) if una != otra]
    assert len(antes) == len(despues) and len(cambiadas) == 1
    linea_antes, linea_despues = cambiadas[0]
    assert 'id="plano-05"' in linea_antes
    assert linea_antes.replace('src="assets/carteles/05.svg"', 'src="planos/05.png"') == linea_despues
    assert leer_composicion(episodio).planos[4]["src"] == "planos/05.png"


def test_el_ultimo_plano_muestra_el_nombre_y_el_logo_de_la_app_mientras_el_perro_dice_el_cta(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, linea = montar(estudio, episodio)

    # El CTA, «Pídele a la App un plan de paseos hecho para tu perro.», cierra el episodio
    # y es justo lo que dura el último plano.
    cta = (linea["cta"]["inicio"], linea["cta"]["final"])
    assert cta[1] == linea["total"]
    assert (linea["planos"][-1]["inicio"], linea["planos"][-1]["final"]) == cta
    assert composicion.cierre is not None and tramo(composicion.cierre) == cta
    assert composicion.texto_del_cierre.strip() == "Huellas"
    assert composicion.logo is not None and (episodio / composicion.logo["src"]).is_file()


def test_sin_logo_de_la_app_el_cierre_lleva_un_marcador_y_montar_avisa(estudio: Estudio, episodio: Path) -> None:
    composicion, _ = montar(estudio, episodio)
    resultado = estudio("montar", episodio)

    assert composicion.logo is not None
    marcador = ET.parse(episodio / composicion.logo["src"]).getroot()
    assert "LOGO" in ["".join(texto.itertext()) for texto in marcador.iter(f"{SVG}text")]
    assert any("logo de la App" in aviso for aviso in resultado.avisos)
    assert not any("nombre de la App" in aviso for aviso in resultado.avisos)


def test_con_el_logo_de_la_app_el_cierre_lo_lleva_y_no_avisa(estudio: Estudio, episodio: Path) -> None:
    configuracion = episodio.parent / "estudio.toml"
    (episodio.parent / "app").mkdir()
    logo = episodio.parent / "app" / "logo.png"
    logo.write_bytes(b"el logo de la App")
    cambiar(configuracion, 'nombre = "Huellas"', 'nombre = "Huellas"\nlogo = "app/logo.png"')

    composicion, _ = montar(estudio, episodio)
    resultado = estudio("montar", episodio)

    assert composicion.logo is not None and composicion.logo["src"] == "assets/app/logo.png"
    assert (episodio / composicion.logo["src"]).read_bytes() == logo.read_bytes()
    assert not any("App" in aviso for aviso in resultado.avisos)


def test_sin_nombre_de_la_app_el_cierre_lleva_un_marcador_y_montar_avisa(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio.parent / "estudio.toml", 'nombre = "Huellas"', "")

    composicion, _ = montar(estudio, episodio)
    resultado = estudio("montar", episodio)

    assert composicion.texto_del_cierre.strip() == "Nombre de la App"
    assert any("nombre de la App" in aviso for aviso in resultado.avisos)


def test_montar_se_niega_si_el_logo_de_la_app_no_existe(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio.parent / "estudio.toml", 'nombre = "Huellas"', 'nombre = "Huellas"\nlogo = "app/logo.png"')
    assert estudio("generar-voces", episodio).codigo == 0

    resultado = estudio("montar", episodio)

    assert resultado.codigo == 1
    assert any("logo de la App" in error and "logo.png" in error for error in resultado.errores)
    assert not (episodio / "index.html").exists()


def test_sin_cta_no_hay_cierre(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio / "guion.md", "[cta] Perro:", "Perro:")

    composicion, linea = montar(estudio, episodio)

    assert linea["cta"] is None
    assert composicion.cierre is None and composicion.logo is None


def test_sin_lista_de_planos_la_composicion_no_tiene_capas_de_imagen(estudio: Estudio, episodio: Path) -> None:
    (episodio / "planos.toml").unlink()

    composicion, _ = montar(estudio, episodio)

    assert composicion.planos == []
    assert composicion.cierre is not None


def test_los_planos_se_ven_debajo_del_cierre_y_el_cierre_debajo_de_los_subtitulos(
    estudio: Estudio, episodio: Path
) -> None:
    composicion, _ = montar(estudio, episodio)

    # Lo que decide qué se ve delante es el z-index, no el orden de las pistas de HyperFrames.
    z_index = {
        selector: int(declaraciones(cuerpo)["z-index"])
        for selector, cuerpo in reglas(composicion.estilo)
        if "z-index" in declaraciones(cuerpo)
    }
    assert z_index[".plano"] < z_index["#cierre-del-cta"] < z_index["#subtitulos"]
