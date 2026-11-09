"""Lista de planos: la herramienta ejecutada sobre carpetas de episodio de ejemplo.

La lista de planos se comprueba al cronometrar, y sus planos entran en la línea de tiempo.
Las cuentas a mano salen de los mismos dos datos que en test_voces_y_cronometraje.py:
- el proveedor de voz falso habla a 3 palabras por segundo: cada palabra dura 10 fotogramas a 30 fps;
- la configuración de los tests pone 6 fotogramas de pausa entre frases (salvo que el test la cambie).
La biblioteca de los tests (tests/episodios/biblioteca) tiene los escenarios recibidor, calle y salon.
"""

import json
import shutil
from itertools import count, islice
from pathlib import Path

import pytest

from ayudas import BIBLIOTECA, CONFIGURACION, Estudio, Resultado, cambiar, linea_de_tiempo


def cronometrar(estudio: Estudio, carpeta: Path) -> Resultado:
    assert estudio("generar-voces", carpeta).codigo == 0
    return estudio("cronometrar", carpeta)


def plano(id: str, empieza: str, escenario: str = "salon") -> str:
    """Un plano completo en el formato de planos.toml."""
    return (
        f'[[plano]]\nid = "{id}"\nempieza = "{empieza}"\nescenario = "{escenario}"\n'
        'encuadre = "plano medio"\ncamara = "fija"\nmotivo = "escuchar"\n\n'
    )


def mini_episodio(raiz: Path, frases: list[int], planos: str, cta: int = 0, pausa: int = 6) -> Path:
    """Un episodio del Perro con frases de tantas palabras como se pida, p1 p2 p3…, y su lista de planos."""
    shutil.copy(CONFIGURACION, raiz / "estudio.toml")
    cambiar(raiz / "estudio.toml", "pausa_entre_frases = 6", f"pausa_entre_frases = {pausa}")
    shutil.copytree(BIBLIOTECA, raiz / "biblioteca")
    carpeta = raiz / "ep"
    carpeta.mkdir()
    palabras = (f"p{numero}" for numero in count(1))
    lineas = [f"Perro: {' '.join(islice(palabras, cuantas))}" for cuantas in frases]
    if cta:
        lineas.append(f"[cta] Perro: {' '.join(islice(palabras, cta))}")
    (carpeta / "guion.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    (carpeta / "planos.toml").write_text(planos, encoding="utf-8")
    return carpeta


def avisos_de_planos(resultado: Resultado) -> list[str]:
    """Los avisos sobre la duración de los planos, sin el de la duración del episodio."""
    return [aviso for aviso in resultado.avisos if aviso.startswith("El plano")]


# --- La lista de planos de ejemplo ---


def test_la_lista_de_planos_de_ejemplo_pasa_sin_errores_ni_avisos(estudio: Estudio, episodio: Path) -> None:
    resultado = cronometrar(estudio, episodio)

    assert resultado.errores == []
    assert resultado.avisos == []
    assert resultado.codigo == 0
    assert "Planos: 29, en 4 escenarios." in resultado.salida


def test_cada_plano_empieza_en_el_fotograma_de_su_palabra_y_dura_hasta_el_siguiente(
    estudio: Estudio, episodio: Path
) -> None:
    linea = linea_de_tiempo(estudio, episodio)

    planos = linea["planos"]
    assert len(planos) == 29
    # El plano 01 empieza en «¿Sabes por qué», al principio, y el 02 en «cuando vuelves» (8.ª palabra).
    assert planos[0] == {"id": "01", "inicio": 0, "final": 70}
    # El plano 07 empieza en «Tú tienes», a mitad de la frase 5: justo donde empieza la palabra «Tú».
    tu = linea["frases"][4]["palabras"][8]
    assert tu["texto"] == "Tú"
    assert planos[6] == {"id": "07", "inicio": tu["inicio"], "final": 480}
    assert tu["inicio"] == 424
    # Sin huecos: cada plano acaba donde empieza el siguiente, y el último, donde acaba el episodio.
    for anterior, siguiente in zip(planos, planos[1:]):
        assert anterior["final"] == siguiente["inicio"]
    assert planos[-1] == {"id": "29", "inicio": 1736, "final": linea["total"]}


def test_el_primer_plano_empieza_en_el_fotograma_0_aunque_la_voz_tarde_en_arrancar(
    estudio: Estudio, episodio: Path
) -> None:
    estudio("generar-voces", episodio)
    # Una voz real puede empezar con un poco de silencio: 0,2 s (6 fotogramas) antes de la primera palabra.
    marcas = episodio / "voces" / "frase-01.json"
    datos = json.loads(marcas.read_text(encoding="utf-8"))
    datos["duracion"] += 0.2
    for palabra in datos["palabras"]:
        palabra["inicio"] += 0.2
        palabra["final"] += 0.2
    marcas.write_text(json.dumps(datos), encoding="utf-8")

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 0, resultado.salida
    linea = json.loads((episodio / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    assert linea["frases"][0]["palabras"][0]["inicio"] == 6
    # «cuando», la 8.ª palabra: 0,2 s + 7 palabras de 1/3 s = 2,53 s, el fotograma 76.
    assert linea["planos"][0] == {"id": "01", "inicio": 0, "final": 76}


def test_sin_lista_de_planos_la_linea_de_tiempo_sale_sin_planos(estudio: Estudio, episodio: Path) -> None:
    (episodio / "planos.toml").unlink()

    resultado = cronometrar(estudio, episodio)

    assert resultado.codigo == 0
    assert resultado.avisos == []
    assert "no hay lista de planos" in resultado.salida
    linea = json.loads((episodio / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    assert linea["planos"] == []


# --- Errores ---


def test_error_si_el_principio_del_guion_queda_sin_cubrir(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio / "planos.toml", 'empieza = "¿Sabes por qué"', 'empieza = "por qué te huelo"')

    resultado = cronometrar(estudio, episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "sin cubrir" in resultado.errores[0]
    assert "líneas de guion.md: 3." in resultado.errores[0]
    assert "«¿Sabes»" in resultado.errores[0]
    assert not (episodio / "linea-de-tiempo.json").exists()


def test_error_si_alguna_frase_entera_queda_sin_cubrir(estudio: Estudio, tmp_path: Path) -> None:
    carpeta = mini_episodio(tmp_path, [6, 6, 6], plano("a", "p13") + plano("b", "p16"))

    resultado = cronometrar(estudio, carpeta)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "sin cubrir" in resultado.errores[0]
    assert "líneas de guion.md: 1, 2." in resultado.errores[0]


def test_error_si_un_plano_va_fuera_de_orden(estudio: Estudio, episodio: Path) -> None:
    # El 03 pasa a empezar en «con quién» y el 04 en «Porque me cuentan», que va antes en el guion.
    cambiar(episodio / "planos.toml", 'empieza = "Porque me cuentan"', 'empieza = "PROVISIONAL"')
    cambiar(episodio / "planos.toml", 'empieza = "con quién"', 'empieza = "Porque me cuentan"')
    cambiar(episodio / "planos.toml", 'empieza = "PROVISIONAL"', 'empieza = "con quién"')

    resultado = cronometrar(estudio, episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "«04»" in resultado.errores[0]
    assert "«03»" in resultado.errores[0]
    assert "orden del guion" in resultado.errores[0]
    assert not (episodio / "linea-de-tiempo.json").exists()


def test_error_si_dos_planos_empiezan_en_la_misma_palabra(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio / "planos.toml", 'empieza = "con quién"', 'empieza = "Porque me cuentan"')

    resultado = cronometrar(estudio, episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "«04»" in resultado.errores[0]
    assert "misma palabra" in resultado.errores[0]


def test_error_si_un_escenario_no_esta_en_la_biblioteca_ni_marcado_como_nuevo(
    estudio: Estudio, episodio: Path
) -> None:
    cambiar(episodio / "planos.toml", 'escenarios_nuevos = ["parque"]\n', "")

    resultado = cronometrar(estudio, episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "«parque»" in resultado.errores[0]
    assert "biblioteca" in resultado.errores[0]
    assert "escenarios_nuevos" in resultado.errores[0]
    assert "«17»" in resultado.errores[0]  # el primer plano del parque
    assert not (episodio / "linea-de-tiempo.json").exists()


def test_la_biblioteca_es_la_carpeta_biblioteca_junto_a_la_configuracion_del_estudio(
    estudio: Estudio, episodio: Path
) -> None:
    shutil.rmtree(episodio.parent / "biblioteca" / "escenarios" / "salon")

    resultado = cronometrar(estudio, episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert "«salon»" in resultado.errores[0]


def test_un_escenario_marcado_como_nuevo_no_tiene_que_estar_en_la_biblioteca(
    estudio: Estudio, tmp_path: Path
) -> None:
    planos = 'escenarios_nuevos = ["playa"]\n\n' + plano("a", "p1", "playa") + plano("b", "p6", "salon")
    carpeta = mini_episodio(tmp_path, [10], planos)

    resultado = cronometrar(estudio, carpeta)

    assert resultado.codigo == 0, resultado.salida
    assert resultado.errores == []


def test_los_errores_de_los_planos_salen_aunque_falten_las_voces(estudio: Estudio, episodio: Path) -> None:
    cambiar(episodio / "planos.toml", 'escenarios_nuevos = ["parque"]\n', "")

    resultado = estudio("cronometrar", episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 2
    assert "generar-voces" in resultado.errores[0]
    assert "«parque»" in resultado.errores[1]


@pytest.mark.parametrize(
    ("antes", "despues", "se_menciona"),
    [
        ('empieza = "Tengo hasta"', 'empieza = "Tengo mucho"', ["«06»", "«Tengo mucho»", "no encuentro"]),
        # «tengo» aparece en dos frases: en la línea 7 y en la 15.
        ('empieza = "Tengo hasta"', 'empieza = "Tengo"', ["«06»", "«Tengo»", "2 veces", "7, 15"]),
        ('empieza = "Tengo hasta"', 'empieza = "¿…?"', ["«06»", "empieza"]),
        ('empieza = "Tengo hasta"\n', "", ["«06»", "falta", "«empieza»"]),
        ('id = "01"', 'id = "01"\ncolor = "rojo"', ["«01»", "«color»"]),
        ('id = "01"', "id = 1", ["plano número 1", "«id»"]),
        ('id = "02"', 'id = "01"', ["«01»", "dos planos"]),
        ('id = "01"', 'id = "plano 1"', ["«id»", "espacios"]),
        ('escenario = "salon"\nencuadre = "plano medio del Perro mirando a cámara', 'escenario = "sala de estar"\n'
         'encuadre = "plano medio del Perro mirando a cámara', ["«29»", "«escenario»", "espacios"]),
        ("personajes = { Perro = \"mira a cámara", "personajes = { Perro = 3, Gato = \"mira a cámara",
         ["«29»", "«personajes»"]),
        ('escenarios_nuevos = ["parque"]', 'escenario_nuevo = ["parque"]', ["«escenario_nuevo»"]),
        ('escenarios_nuevos = ["parque"]', 'escenarios_nuevos = "parque"', ["escenarios_nuevos"]),
        ('escenarios_nuevos = ["parque"]', 'escenarios_nuevos = ["parque"', ["planos.toml", "no entiendo"]),
    ],
)
def test_error_si_la_lista_de_planos_no_sigue_el_formato(
    estudio: Estudio, episodio: Path, antes: str, despues: str, se_menciona: list[str]
) -> None:
    cambiar(episodio / "planos.toml", antes, despues)

    resultado = cronometrar(estudio, episodio)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1, resultado.errores
    for texto in se_menciona:
        assert texto in resultado.errores[0]
    assert not (episodio / "linea-de-tiempo.json").exists()


@pytest.mark.parametrize(
    ("planos", "se_menciona"),
    [
        ('escenarios_nuevos = ["playa"]\n', "no tiene planos"),
        ('[plano]\nid = "a"\n', "[[plano]]"),
    ],
)
def test_error_si_la_lista_de_planos_no_tiene_planos(
    estudio: Estudio, tmp_path: Path, planos: str, se_menciona: str
) -> None:
    carpeta = mini_episodio(tmp_path, [10], planos)

    resultado = cronometrar(estudio, carpeta)

    assert resultado.codigo == 1
    assert len(resultado.errores) == 1
    assert se_menciona in resultado.errores[0]


# --- Avisos ---


@pytest.mark.parametrize(
    ("palabras", "pausa", "duracion", "aviso"),
    [
        (4, 4, 44, True),  # 4 palabras de 10 fotogramas y la pausa hasta la frase siguiente
        (4, 5, 45, False),
        (9, 0, 90, False),
        (9, 1, 91, True),
    ],
)
def test_aviso_si_un_plano_dura_menos_de_45_o_mas_de_90_fotogramas(
    estudio: Estudio, tmp_path: Path, palabras: int, pausa: int, duracion: int, aviso: bool
) -> None:
    # El plano «a» cubre la primera frase; el «b», la segunda, de 6 palabras (60-65 fotogramas).
    planos = plano("a", "p1") + plano("b", f"p{palabras + 1}")
    carpeta = mini_episodio(tmp_path, [palabras, 6], planos, pausa=pausa)

    resultado = cronometrar(estudio, carpeta)

    assert resultado.codigo == 0
    linea = json.loads((carpeta / "linea-de-tiempo.json").read_text(encoding="utf-8"))
    assert linea["planos"][0]["final"] - linea["planos"][0]["inicio"] == duracion
    if aviso:
        assert avisos_de_planos(resultado) == [
            f"El plano «a» dura {duracion} fotogramas ({duracion / 30:.2f} s); ".replace(".", ",", 1)
            + "debería durar entre 45 y 90 fotogramas (1,5-3 s)."
        ]
    else:
        assert avisos_de_planos(resultado) == []


def test_un_plano_que_empieza_en_el_cta_puede_pasar_de_90_fotogramas(estudio: Estudio, tmp_path: Path) -> None:
    # El CTA, de 12 palabras, dura 120 fotogramas: el último plano lo acompaña entero.
    carpeta = mini_episodio(tmp_path, [6], plano("a", "p1") + plano("cta", "p7"), cta=12)

    resultado = cronometrar(estudio, carpeta)

    assert resultado.codigo == 0
    assert avisos_de_planos(resultado) == []


def test_un_plano_que_empieza_antes_del_cta_no_puede_pasar_de_90_fotogramas(
    estudio: Estudio, tmp_path: Path
) -> None:
    # El plano «b» empieza en la última frase de la conversación y sigue durante todo el CTA.
    carpeta = mini_episodio(tmp_path, [6, 6], plano("a", "p1") + plano("b", "p7"), cta=5)

    resultado = cronometrar(estudio, carpeta)

    assert resultado.codigo == 0
    assert len(avisos_de_planos(resultado)) == 1
    assert "«b» dura 116 fotogramas" in avisos_de_planos(resultado)[0]


@pytest.mark.parametrize(("escenarios", "aviso"), [(5, False), (6, True)])
def test_aviso_si_el_episodio_usa_mas_de_5_escenarios(
    estudio: Estudio, tmp_path: Path, escenarios: int, aviso: bool
) -> None:
    nombres = [f"escenario-{numero}" for numero in range(1, escenarios + 1)]
    nuevos = ", ".join(f'"{nombre}"' for nombre in nombres)
    planos = f"escenarios_nuevos = [{nuevos}]\n\n" + "".join(
        plano(str(numero), f"p{5 * numero - 4}", nombre) for numero, nombre in enumerate(nombres, start=1)
    )
    carpeta = mini_episodio(tmp_path, [5 * escenarios], planos)

    resultado = cronometrar(estudio, carpeta)

    assert resultado.codigo == 0
    sobre_escenarios = [aviso for aviso in resultado.avisos if "escenarios" in aviso]
    if aviso:
        assert len(sobre_escenarios) == 1
        assert "6 escenarios" in sobre_escenarios[0]
        assert "escenario-6" in sobre_escenarios[0]
    else:
        assert sobre_escenarios == []
