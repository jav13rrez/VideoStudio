"""Hoja de publicación: descripción con el CTA, enlaces con seguimiento por plataforma y recordatorios de subida.

La documentación de la App de los tests (tests/episodios/app/app.toml) da el enlace base: https://huellas.example/app.
"""

import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from ayudas import Estudio, cambiar

PLATAFORMAS = {"YouTube": "youtube", "TikTok": "tiktok", "Instagram": "instagram"}


def hoja(episodio: Path) -> str:
    return (episodio / "publicacion.md").read_text(encoding="utf-8")


def enlaces(texto: str) -> dict[str, str]:
    """El enlace de cada plataforma, de las líneas «- Plataforma: enlace»."""
    return dict(re.findall(r"^- (YouTube|TikTok|Instagram): (\S+)$", texto, re.MULTILINE))


def test_hay_un_enlace_por_plataforma_con_su_fuente_su_medio_y_el_episodio_como_campana(
    estudio: Estudio, episodio: Path
) -> None:
    resultado = estudio("hoja-de-publicacion", episodio)

    assert resultado.codigo == 0, resultado.salida
    assert "publicacion.md" in resultado.salida
    encontrados = enlaces(hoja(episodio))
    assert set(encontrados) == set(PLATAFORMAS)
    for plataforma, fuente in PLATAFORMAS.items():
        partes = urlsplit(encontrados[plataforma])
        assert (partes.scheme, partes.netloc, partes.path) == ("https", "huellas.example", "/app")
        assert parse_qs(partes.query) == {
            "utm_source": [fuente], "utm_medium": ["social"], "utm_campaign": ["001-olfato"]
        }


def test_el_enlace_base_conserva_lo_que_ya_lleva(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio.parent / "app" / "app.toml", "/app", "/app?idioma=es#descarga")

    assert estudio("hoja-de-publicacion", episodio).codigo == 0

    partes = urlsplit(enlaces(hoja(episodio))["TikTok"])
    assert parse_qs(partes.query)["idioma"] == ["es"]
    assert parse_qs(partes.query)["utm_source"] == ["tiktok"]
    assert partes.fragment == "descarga"


def test_la_descripcion_de_cada_plataforma_lleva_el_cta_del_guion_y_su_enlace(
    estudio: Estudio, episodio: Path
) -> None:
    cambiar(episodio / "guion.md", "plan de paseos", "plan de *paseos*")

    assert estudio("hoja-de-publicacion", episodio).codigo == 0

    texto = hoja(episodio)
    for plataforma, enlace in enlaces(texto).items():
        descripcion = texto.split(f"### {plataforma}\n", 1)[1].split("\n#", 1)[0]
        assert "Pídele a la App un plan de paseos hecho para tu perro." in descripcion
        assert enlace in descripcion
        assert "*" not in descripcion


def test_la_hoja_recuerda_el_aviso_de_marca_propia_la_etiqueta_de_ia_y_la_subida_a_mano(
    estudio: Estudio, episodio: Path
) -> None:
    assert estudio("hoja-de-publicacion", episodio).codigo == 0

    recordatorios = hoja(episodio).split("## Recordatorios de subida", 1)[1].lower()
    assert "marca propia" in recordatorios
    assert "etiqueta de ia" in recordatorios
    assert "a mano" in recordatorios
    assert "exportacion/001-olfato.mp4" in recordatorios


def test_sin_enlace_de_la_app_no_hay_hoja(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio.parent / "app" / "app.toml", 'enlace = "https://huellas.example/app"', "")

    resultado = estudio("hoja-de-publicacion", episodio)

    assert resultado.codigo == 1
    assert any("enlace" in error and "app/app.toml" in error for error in resultado.errores)
    assert not (episodio / "publicacion.md").exists()


def test_un_enlace_que_no_es_una_direccion_web_no_vale(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio.parent / "app" / "app.toml", "https://huellas.example/app", "huellas.example/app")

    resultado = estudio("hoja-de-publicacion", episodio)

    assert resultado.codigo == 1
    assert any("enlace" in error and "https://" in error for error in resultado.errores)
    assert not (episodio / "publicacion.md").exists()


def test_sin_cta_en_el_guion_no_hay_hoja(estudio: Estudio, episodio: Path) -> None:
    cambiar(
        episodio / "guion.md",
        "[cta] Perro: Pídele a la App un plan de paseos hecho para tu perro.\n",
        "",
    )

    resultado = estudio("hoja-de-publicacion", episodio)

    assert resultado.codigo == 1
    assert any("CTA" in error for error in resultado.errores)
    assert not (episodio / "publicacion.md").exists()


def test_con_errores_en_el_guion_no_hay_hoja(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio / "guion.md", "[remate] Tutor:", "[final] Tutor:")

    resultado = estudio("hoja-de-publicacion", episodio)

    assert resultado.codigo == 1
    assert any("[final]" in error for error in resultado.errores)
    assert not (episodio / "publicacion.md").exists()


def test_desde_dentro_de_la_carpeta_la_campana_sigue_siendo_el_episodio(
    estudio: Estudio, episodio: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(episodio)

    assert estudio("hoja-de-publicacion", Path(".")).codigo == 0

    for enlace in enlaces(hoja(episodio)).values():
        assert parse_qs(urlsplit(enlace).query)["utm_campaign"] == ["001-olfato"]
