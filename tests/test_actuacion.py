"""Actuación (ticket 19): una línea por plano, la boca del Tutor en las palabras acentuadas y los gestos del Perro.

Los tests usan el Blender falso de test_renderizar_planos, que apunta en llamadas.jsonl lo que se le pide.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from ayudas import Estudio, cambiar
from test_renderizar_planos import blender, llamadas, planos_de, preparar  # noqa: F401  (blender es un fixture)

ESTADO_DE_LA_PIEZA = dict[str, Any]


def sentar_al_perro(episodio: Path) -> None:
    cambiar(episodio / "tomas.toml", "perro_de_pie_frente", "perro_sentado_frente")


def actuaciones(estudio_planos: list[str], gestos: dict[str, str] | None = None) -> str:
    gestos = gestos or {}
    return "\n".join(
        f'[[plano]]\nid = "{id_}"\npensamiento = "piensa {id_}"\nanticipacion = "mira antes"\n'
        f'accion = "hace algo"\npausa = "se queda quieto"\n{gestos.get(id_, "")}\n'
        for id_ in estudio_planos
    )


def escribir(episodio: Path, planos: list[str], gestos: dict[str, str] | None = None) -> None:
    (episodio / "actuacion.toml").write_text(actuaciones(planos, gestos), encoding="utf-8")


def estados(llamada: dict[str, Any], id_: str) -> list[dict[str, ESTADO_DE_LA_PIEZA]]:
    plano = next(p for p in planos_de(llamada) if p["id"] == id_)
    datos: list[dict[str, ESTADO_DE_LA_PIEZA]] = plano["actuacion"]
    return datos


def con_el_tutor_hablando(estudio: Estudio, episodio: Path) -> dict[str, dict[str, int]]:
    cambiar(episodio / "guion.md", "¿Porque huelen fatal?", "¿Porque huelen *fatal*?")
    return preparar(estudio, episodio)


def test_sin_actuacion_toml_no_se_renderiza(estudio: Estudio, episodio: Path, blender: Path) -> None:  # noqa: F811
    preparar(estudio, episodio)
    (episodio / "actuacion.toml").unlink()

    resultado = estudio("renderizar-planos", episodio, "--planos", "02")

    assert resultado.codigo == 1 and any("actuacion.toml" in error for error in resultado.errores)
    assert llamadas(blender) == []


@pytest.mark.parametrize("campo", ["pensamiento", "anticipacion", "accion", "pausa"])
def test_cada_plano_necesita_su_linea_de_actuacion_completa(
    estudio: Estudio, episodio: Path, blender: Path, campo: str  # noqa: F811
) -> None:
    preparar(estudio, episodio)
    escribir(episodio, ["01", "02", "04"])
    texto = (episodio / "actuacion.toml").read_text(encoding="utf-8")
    (episodio / "actuacion.toml").write_text(texto.replace(f"{campo} =", f"sobra_{campo} =", 1), encoding="utf-8")

    resultado = estudio("renderizar-planos", episodio, "--planos", "01-02,04")

    assert resultado.codigo == 1 and any(campo in error for error in resultado.errores)
    assert llamadas(blender) == []


def test_un_plano_sin_linea_de_actuacion_se_rechaza(estudio: Estudio, episodio: Path, blender: Path) -> None:  # noqa: F811
    preparar(estudio, episodio)
    escribir(episodio, ["01", "04"])

    resultado = estudio("renderizar-planos", episodio, "--planos", "01-02,04")

    assert resultado.codigo == 1 and any("«02»" in error and "actuación" in error for error in resultado.errores)


def test_la_boca_del_tutor_solo_cambia_en_las_palabras_acentuadas(
    estudio: Estudio, episodio: Path, blender: Path  # noqa: F811
) -> None:
    linea = con_el_tutor_hablando(estudio, episodio)
    escribir(episodio, ["01", "02", "04"])

    resultado = estudio("renderizar-planos", episodio, "--planos", "02")

    assert resultado.codigo == 0, resultado.salida
    datos = json.loads((episodio / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    acentuadas = [
        (p["inicio"], p["final"]) for f in datos["frases"] if f["personaje"] == "Tutor" for p in f["palabras"] if p["acentuada"]
    ]
    assert len(acentuadas) == 1
    inicio_del_plano = linea["02"]["inicio"]
    bocas = [estado["tutor_sentado_frente"]["boca"] for estado in estados(llamadas(blender)[0], "02")]
    dentro = [(inicio_del_plano + i) for i, _ in enumerate(bocas)]
    for fotograma, boca in zip(dentro, bocas, strict=True):
        en_palabra = any(a <= fotograma < b for a, b in acentuadas)
        assert (boca in ("abierta_grande", "abierta_pequena")) == en_palabra, (fotograma, boca)
        if not en_palabra:
            assert boca == "sonrisa"  # la boca de la toma
    assert len(set(bocas)) > 1


def test_un_plano_de_camara_fija_con_boca_animada_deja_un_video_y_no_una_imagen(
    estudio: Estudio, episodio: Path, blender: Path  # noqa: F811
) -> None:
    linea = con_el_tutor_hablando(estudio, episodio)
    escribir(episodio, ["01", "02", "04"])

    estudio("renderizar-planos", episodio, "--planos", "02")

    por_id = {p["id"]: p for p in planos_de(llamadas(blender)[0])}
    assert por_id["02"]["fija"] is False
    assert (episodio / "planos" / "02.mp4").is_file() and not (episodio / "planos" / "02.png").exists()
    duracion = linea["02"]["final"] - linea["02"]["inicio"]
    assert (por_id["02"]["desde"], por_id["02"]["hasta"]) == (0, duracion - 1)


def test_el_perro_no_mueve_la_boca_en_ningun_fotograma(estudio: Estudio, episodio: Path, blender: Path) -> None:  # noqa: F811
    sentar_al_perro(episodio)
    con_el_tutor_hablando(estudio, episodio)
    escribir(episodio, ["01", "02", "04"], {"01": 'gestos = [{ pieza = "perro_sentado_frente", parte = "orejas", inicio = 5, angulo = 15 }]'})

    estudio("renderizar-planos", episodio, "--planos", "01-02,04")

    for plano in planos_de(llamadas(blender)[0]):
        for estado in plano["actuacion"] or []:
            for pieza, partes in estado.items():
                assert pieza.startswith("tutor") or "boca" not in partes, (plano["id"], pieza)


def test_un_gesto_del_perro_anticipa_actua_se_mantiene_y_vuelve_al_reposo_sin_rebotar(
    estudio: Estudio, episodio: Path, blender: Path  # noqa: F811
) -> None:
    sentar_al_perro(episodio)
    preparar(estudio, episodio)
    gesto = 'gestos = [{ pieza = "perro_sentado_frente", parte = "orejas", inicio = 4, angulo = 20 }]'
    escribir(episodio, ["01", "02", "04"], {"01": gesto})

    resultado = estudio("renderizar-planos", episodio, "--planos", "01")

    assert resultado.codigo == 0, resultado.salida
    angulos = [estado["perro_sentado_frente"]["orejas"] for estado in estados(llamadas(blender)[0], "01")]
    assert angulos[:4] == [0.0] * 4  # quieto hasta que empieza el gesto
    pico = angulos.index(max(angulos))
    primer_movimiento = next(i for i, a in enumerate(angulos) if a != 0)
    assert min(angulos[primer_movimiento:pico]) < 0  # anticipación: primero tira hacia el otro lado
    assert max(angulos) == pytest.approx(20)
    despues = angulos[pico:]
    assert all(a >= b for a, b in zip(despues, despues[1:], strict=False))  # baja sin rebotar
    assert min(despues) == 0 and despues[-1] == 0  # acaba en reposo, sin pasarse


@pytest.mark.parametrize(
    ("gestos", "error"),
    [
        ('gestos = [{ pieza = "perro_sentado_frente", parte = "orejas", inicio = 4, angulo = 80 }]', "angulo"),
        ('gestos = [{ pieza = "perro_sentado_frente", parte = "boca", inicio = 4, angulo = 10 }]', "boca"),
        ('gestos = [{ pieza = "perro_que_no_esta", parte = "cola", inicio = 4, angulo = 10 }]', "perro_que_no_esta"),
        ('gestos = [{ pieza = "perro_sentado_frente", parte = "orejas", inicio = 100000, angulo = 10 }]', "acaba"),
        ('gestos = [{ pieza = "perro_sentado_frente", parte = "cola", inicio = 4, angulo = 10 }]', "no tiene cola"),
        (
            'gestos = [{ pieza = "perro_sentado_frente", parte = "cola", inicio = 4, angulo = 10 },'
            ' { pieza = "perro_sentado_frente", parte = "cola", inicio = 6, angulo = 10 }]',
            "se pisan",
        ),
    ],
)
def test_los_gestos_mal_escritos_se_rechazan_sin_llamar_a_blender(
    estudio: Estudio, episodio: Path, blender: Path, gestos: str, error: str  # noqa: F811
) -> None:
    sentar_al_perro(episodio)
    preparar(estudio, episodio)
    escribir(episodio, ["01", "02", "04"], {"01": gestos})

    resultado = estudio("renderizar-planos", episodio, "--planos", "01")

    assert resultado.codigo == 1 and any(error in e for e in resultado.errores), resultado.salida
    assert llamadas(blender) == []
