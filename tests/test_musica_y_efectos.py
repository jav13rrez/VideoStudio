"""Música y efectos: sonido.toml del episodio, con la herramienta sobre la carpeta de ejemplo, sin renderizar.

Los audios de prueba se escriben aquí mismo: ondas cuadradas, cuyo nivel es su amplitud, y efectos con un
único pico, para saber de antemano dónde está su golpe.
"""

import math
import tomllib
import wave
from array import array
from pathlib import Path

from ayudas import FPS, Composicion, Estudio, cambiar, leer_composicion, montar

MAXIMO = 32767  # la muestra más alta de un WAV de 16 bits

# Los sonidos físicos que pide la lista de planos del ejemplo, con el segundo del archivo en que está su golpe
# (el del resoplido, en el primer medio fotograma del archivo, como el de muchos golpes secos).
GOLPES = {"olfateo": 0.25, "llaves sobre el mueble": 0.5, "resoplido": 0.005, "correa que se tensa": 1.2}


def escribir_wav(
    archivo: Path,
    segundos: float,
    amplitud: float,
    *,
    pico: float | None = None,
    canales: int = 1,
    muestras_por_segundo: int = 24_000,
) -> None:
    """Una onda cuadrada de esa amplitud (de 0 a 1) y, si se pide, una sola muestra al máximo en el segundo `pico`."""
    archivo.parent.mkdir(parents=True, exist_ok=True)
    total = round(segundos * muestras_por_segundo)
    valor = round(amplitud * MAXIMO)
    muestras = array("h", (valor if i % 2 else -valor for i in range(total)))
    if pico is not None:
        muestras[round(pico * muestras_por_segundo)] = MAXIMO
    intercaladas = array("h", (muestra for muestra in muestras for _ in range(canales)))
    with wave.open(str(archivo), "wb") as audio:
        audio.setnchannels(canales)
        audio.setsampwidth(2)
        audio.setframerate(muestras_por_segundo)
        audio.writeframes(intercaladas.tobytes())


def con_sonido(episodio: Path, segundos_de_musica: float, amplitud_de_la_musica: float = 0.5) -> None:
    """Deja en el episodio una música, un efecto por cada sonido de la lista de planos y su sonido.toml."""
    escribir_wav(
        episodio / "sonido" / "musica.wav",
        segundos_de_musica,
        amplitud_de_la_musica,
        canales=2,
        muestras_por_segundo=44_100,
    )
    efectos = ""
    for numero, (sonido, golpe) in enumerate(GOLPES.items(), start=1):
        escribir_wav(
            episodio / "sonido" / f"efecto-{numero}.wav", golpe + 0.6, 0.05, pico=golpe, muestras_por_segundo=48_000
        )
        efectos += f"""
[[efecto]]
sonido = "{sonido}"
archivo = "sonido/efecto-{numero}.wav"
licencia = "CC0 1.0"
fuente = "https://freesound.org/s/{numero}/"
"""
    (episodio / "sonido.toml").write_text(
        f"""\
[musica]
archivo = "sonido/musica.wav"
licencia = "CC0 1.0"
fuente = "https://freesound.org/s/100/"
{efectos}""",
        encoding="utf-8",
    )


def segundos(valor: str | None) -> float:
    return float(valor) if valor else 0.0


def capas(composicion: Composicion, prefijo: str) -> list[dict[str, str]]:
    return [audio for audio in composicion.audios if audio.get("id", "").startswith(prefijo)]


def sonidos_de_los_planos(episodio: Path) -> dict[str, str]:
    datos = tomllib.loads((episodio / "planos.toml").read_text(encoding="utf-8"))
    return {plano["id"]: plano["sonido"] for plano in datos["plano"] if "sonido" in plano}


def total_del_episodio(estudio: Estudio, episodio: Path) -> int:
    """Los fotogramas que dura el episodio de ejemplo con las voces de prueba."""
    _, linea = montar(estudio, episodio)
    total: int = linea["total"]
    return total


def test_la_musica_suena_hasta_el_ultimo_fotograma_y_su_final_cae_en_el_final_del_episodio(
    estudio: Estudio, episodio: Path
) -> None:
    total = total_del_episodio(estudio, episodio)
    duracion = total / FPS + 10.3  # más larga que el episodio: se recorta por el principio
    con_sonido(episodio, duracion)

    composicion, _ = montar(estudio, episodio)

    [musica] = capas(composicion, "musica")
    assert musica["src"] == "sonido/musica.wav"
    assert segundos(musica["data-start"]) == 0
    assert round((segundos(musica["data-start"]) + segundos(musica["data-duration"])) * FPS) == total
    # Lo que suena es el final del archivo: acaba justo donde acaba el episodio, así que resuelve en su último
    # fotograma.
    assert abs(segundos(musica.get("data-media-start")) + segundos(musica["data-duration"]) - duracion) < 1e-5


def test_una_musica_mas_corta_que_el_episodio_entra_mas_tarde_para_acabar_en_el_ultimo_fotograma(
    estudio: Estudio, episodio: Path
) -> None:
    total = total_del_episodio(estudio, episodio)
    con_sonido(episodio, 20.01)

    resultado = estudio("montar", episodio)

    [musica] = capas(leer_composicion(episodio), "musica")
    assert segundos(musica.get("data-media-start")) == 0
    final_del_archivo = segundos(musica["data-start"]) + 20.01
    assert (total - 1) / FPS < final_del_archivo <= total / FPS
    assert any("música" in aviso and "dura menos" in aviso for aviso in resultado.avisos), resultado.salida


def test_el_golpe_de_cada_efecto_cae_en_el_fotograma_de_su_plano(estudio: Estudio, episodio: Path) -> None:
    con_sonido(episodio, 90)

    composicion, linea = montar(estudio, episodio)

    sonidos = sonidos_de_los_planos(episodio)
    planos = [plano for plano in linea["planos"] if plano["id"] in sonidos]
    efectos = capas(composicion, "efecto")
    assert len(efectos) == len(planos) == 5
    archivos = {sonido: f"sonido/efecto-{numero}.wav" for numero, sonido in enumerate(GOLPES, start=1)}
    for plano, efecto in zip(planos, efectos, strict=True):
        sonido = sonidos[plano["id"]]
        assert efecto["src"] == archivos[sonido]
        # El golpe suena (no queda en el trozo recortado) y cae en el fotograma del plano.
        assert segundos(efecto.get("data-media-start")) <= GOLPES[sonido], plano["id"]
        golpe = segundos(efecto["data-start"]) + GOLPES[sonido] - segundos(efecto.get("data-media-start"))
        assert math.floor(golpe * FPS) == plano["inicio"], plano["id"]
        # HyperFrames ajusta al fotograma el inicio de cada capa: el recorte fino va en data-media-start.
        inicio = segundos(efecto["data-start"]) * FPS
        assert abs(inicio - round(inicio)) < 1e-4
    # El plano 01 empieza en el fotograma 0 y su golpe está a 0,25 s del principio del archivo: se recorta.
    assert segundos(efectos[0]["data-start"]) == 0 and segundos(efectos[0].get("data-media-start")) > 0


def test_las_voces_quedan_por_encima_de_la_musica(estudio: Estudio, episodio: Path) -> None:
    con_sonido(episodio, 90, amplitud_de_la_musica=0.9)
    assert estudio("generar-voces", episodio).codigo == 0
    # Voces de prueba con sonido (las del proveedor falso son silencio), con la misma duración.
    for voz in (episodio / "voces").glob("*.wav"):
        with wave.open(str(voz), "rb") as audio:
            duracion = audio.getnframes() / audio.getframerate()
        escribir_wav(voz, duracion, 0.3)

    resultado = estudio("montar", episodio)

    assert resultado.codigo == 0, resultado.salida
    composicion = leer_composicion(episodio)
    [musica] = capas(composicion, "musica")
    assert all(float(voz["data-volume"]) == 1 for voz in capas(composicion, "voz-"))
    nivel_de_la_musica = 20 * math.log10(0.9 * float(musica["data-volume"]))
    assert nivel_de_la_musica <= 20 * math.log10(0.3) - 18 + 0.01


def test_con_voces_en_silencio_la_musica_sigue_baja(estudio: Estudio, episodio: Path) -> None:
    con_sonido(episodio, 90, amplitud_de_la_musica=0.9)

    composicion, _ = montar(estudio, episodio)

    [musica] = capas(composicion, "musica")
    assert float(musica["data-volume"]) < 0.2


def test_da_error_si_la_musica_no_tiene_su_licencia_anotada(estudio: Estudio, episodio: Path) -> None:
    con_sonido(episodio, 90)
    cambiar(episodio / "sonido.toml", 'licencia = "CC0 1.0"\nfuente = "https://freesound.org/s/100/"\n', "")
    assert estudio("generar-voces", episodio).codigo == 0

    resultado = estudio("montar", episodio)

    assert resultado.codigo == 1
    assert any("música" in error and "licencia" in error for error in resultado.errores), resultado.salida
    assert not (episodio / "index.html").exists()


def test_da_error_si_un_efecto_usado_no_dice_de_donde_sale(estudio: Estudio, episodio: Path) -> None:
    con_sonido(episodio, 90)
    cambiar(episodio / "sonido.toml", 'fuente = "https://freesound.org/s/3/"\n', "")
    assert estudio("generar-voces", episodio).codigo == 0

    resultado = estudio("montar", episodio)

    assert resultado.codigo == 1
    assert any("resoplido" in error and "fuente" in error for error in resultado.errores), resultado.salida


def test_da_error_si_un_archivo_de_sonido_no_esta_o_no_es_un_wav(estudio: Estudio, episodio: Path) -> None:
    con_sonido(episodio, 90)
    (episodio / "sonido" / "musica.wav").write_bytes(b"ID3 esto es un mp3")
    (episodio / "sonido" / "efecto-2.wav").unlink()
    assert estudio("generar-voces", episodio).codigo == 0

    resultado = estudio("montar", episodio)

    assert resultado.codigo == 1
    assert any("sonido/musica.wav" in error and "WAV" in error for error in resultado.errores), resultado.salida
    assert any("sonido/efecto-2.wav" in error and "no está" in error for error in resultado.errores)


def test_un_sonido_de_la_lista_de_planos_sin_efecto_es_un_aviso(estudio: Estudio, episodio: Path) -> None:
    con_sonido(episodio, 90)
    cambiar(episodio / "sonido.toml", 'sonido = "resoplido"', 'sonido = "estornudo"')

    composicion, _ = montar(estudio, episodio)
    resultado = estudio("montar", episodio)

    assert len(capas(composicion, "efecto")) == 4
    assert any("resoplido" in aviso for aviso in resultado.avisos), resultado.salida


def test_sin_sonido_toml_se_monta_sin_musica_ni_efectos_y_se_avisa(estudio: Estudio, episodio: Path) -> None:
    composicion, _ = montar(estudio, episodio)
    resultado = estudio("montar", episodio)

    assert resultado.codigo == 0
    assert not capas(composicion, "musica") and not capas(composicion, "efecto")
    assert any("sonido.toml" in aviso for aviso in resultado.avisos)


def test_si_una_voz_no_se_puede_medir_se_avisa_y_la_musica_sigue_baja(estudio: Estudio, episodio: Path) -> None:
    con_sonido(episodio, 90, amplitud_de_la_musica=0.9)
    assert estudio("generar-voces", episodio).codigo == 0
    # Una grabación de 24 bits, como las de algunas grabadoras.
    with wave.open(str(episodio / "voces" / "frase-01.wav"), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(3)
        audio.setframerate(24_000)
        audio.writeframes(bytes(3 * 24_000))

    resultado = estudio("montar", episodio)

    assert resultado.codigo == 0, resultado.salida
    assert any("nivel de las voces" in aviso for aviso in resultado.avisos), resultado.salida
    [musica] = capas(leer_composicion(episodio), "musica")
    assert float(musica["data-volume"]) < 0.2
