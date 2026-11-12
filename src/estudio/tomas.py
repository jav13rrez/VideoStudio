"""Tomas: la cámara y la colocación de cada plano, para renderizarlo en Blender.

El archivo es tomas.toml, junto a planos.toml. Una toma por plano, con el mismo id. El formato está en docs/tomas.md.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeGuard

from estudio.guion import Informe

ARCHIVO = "tomas.toml"

# «Lento» y «con motivo»: lo que puede moverse la cámara dentro de un solo plano.
ACERCAMIENTO_MINIMO = 0.7  # el ancho final no baja de esta fracción del inicial (un acercamiento de hasta el 30 %)
DESVIO_DEL_ACERCAMIENTO = 0.1  # metros que puede moverse el punto al que mira en un acercamiento
DESPLAZAMIENTO_MAXIMO = 0.6  # metros que puede moverse el punto al que mira en un desplazamiento
GIRO_MAXIMO = 20.0  # grados de azimut o de elevación que puede girar la cámara en un desplazamiento
VARIACION_DE_ANCHO_EN_DESPLAZAMIENTO = 0.1  # fracción que puede cambiar el ancho en un desplazamiento

FIJA, ACERCAMIENTO, DESPLAZAMIENTO = "fija", "acercamiento", "desplazamiento"

Punto = tuple[float, float, float]

_CAMPOS_DE_LA_TOMA = ("id", "mira", "ancho", "azimut", "elevacion", "hasta", "personajes", "objetos")
_CAMPOS_DEL_DESTINO = ("mira", "ancho", "azimut", "elevacion")
_CAMPOS_DE_LA_COLOCACION = ("pieza", "en", "espejo", "ojos", "boca")


@dataclass(frozen=True)
class Colocacion:
    pieza: str  # una pieza de la biblioteca: tutor_sentado_frente, perro_de_pie_perfil, bocadillo…
    en: Punto  # dónde se pone, en metros del escenario (z = altura)
    espejo: bool = False  # si se da la vuelta, para que mire hacia el otro lado
    ojos: str | None = None  # el juego de ojos, por su nombre
    boca: str | None = None  # el juego de bocas, por su nombre


@dataclass(frozen=True)
class Vista:
    """Cómo se ve la escena en un momento: a dónde mira la cámara, desde qué ángulo y cuánto cabe a lo ancho."""

    mira: Punto
    ancho: float  # metros de escena que caben a lo ancho en el punto al que mira: más pequeño, más cerca
    azimut: float  # grados alrededor del punto: 0 es de frente, positivo hacia la derecha de la imagen
    elevacion: float  # grados sobre la horizontal

    def como_datos(self) -> dict[str, Any]:
        return {"mira": list(self.mira), "ancho": self.ancho, "azimut": self.azimut, "elevacion": self.elevacion}


@dataclass(frozen=True)
class Toma:
    id: str
    desde: Vista
    hasta: Vista | None  # solo si la cámara se mueve
    personajes: tuple[Colocacion, ...]
    objetos: tuple[Colocacion, ...]

    def como_datos(self) -> dict[str, Any]:
        return {
            **self.desde.como_datos(),
            "hasta": self.hasta.como_datos() if self.hasta else None,
            "personajes": [_colocacion_como_datos(c) for c in self.personajes],
            "objetos": [_colocacion_como_datos(c) for c in self.objetos],
        }


def _colocacion_como_datos(colocacion: Colocacion) -> dict[str, Any]:
    return {
        "pieza": colocacion.pieza,
        "en": list(colocacion.en),
        "espejo": colocacion.espejo,
        "ojos": colocacion.ojos,
        "boca": colocacion.boca,
    }


def tipo_de_camara(texto: str) -> str:
    """fija, acercamiento o desplazamiento, según lo que dice el campo `camara` del plano."""
    primera = texto.strip().lower().split(" ")[0] if texto.strip() else ""
    for tipo in (ACERCAMIENTO, DESPLAZAMIENTO):
        if primera.startswith(tipo):
            return tipo
    return FIJA


def camaras_de_los_planos(carpeta: Path) -> dict[str, str]:
    """El tipo de cámara de cada plano de planos.toml, por su id."""
    datos = tomllib.loads((carpeta / "planos.toml").read_text(encoding="utf-8-sig"))
    return {plano["id"]: tipo_de_camara(plano["camara"]) for plano in datos.get("plano", [])}


def leer_tomas(carpeta: Path, camaras: dict[str, str]) -> tuple[dict[str, Toma], Informe]:
    """Las tomas del episodio por id del plano, y los errores. `camaras` es el tipo de cámara de cada plano."""
    informe = Informe()
    archivo = carpeta / ARCHIVO
    if not archivo.is_file():
        informe.errores.append(
            f"No encuentro {ARCHIVO} en la carpeta del episodio: ahí van la cámara y la colocación de cada plano "
            "(formato en docs/tomas.md)."
        )
        return {}, informe
    try:
        datos = tomllib.loads(archivo.read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as error:
        informe.errores.append(f"{ARCHIVO}: no entiendo el archivo ({error}).")
        return {}, informe
    for clave in [clave for clave in datos if clave != "toma"]:
        informe.errores.append(f"{ARCHIVO}: no conozco «{clave}»; solo puede haber tomas, cada una con [[toma]].")
    tablas = datos.get("toma", [])
    if not isinstance(tablas, list):
        informe.errores.append(f"{ARCHIVO}: cada toma empieza con [[toma]], con dos corchetes.")
        return {}, informe
    tomas: dict[str, Toma] = {}
    for tabla in tablas:
        toma = _leer_toma(tabla, camaras, informe)
        if toma is None:
            continue
        if toma.id in tomas:
            informe.errores.append(f"{ARCHIVO}: hay dos tomas con el id «{toma.id}».")
        tomas[toma.id] = toma
    return tomas, informe


def _leer_toma(tabla: object, camaras: dict[str, str], informe: Informe) -> Toma | None:
    if not isinstance(tabla, dict):
        informe.errores.append(f"{ARCHIVO}: cada toma empieza con [[toma]], con dos corchetes.")
        return None
    id_ = tabla.get("id")
    if not isinstance(id_, str):
        informe.errores.append(f"{ARCHIVO}: una toma no tiene «id», el del plano al que corresponde.")
        return None
    nombre = f"{ARCHIVO}, toma «{id_}»"
    errores = len(informe.errores)
    if id_ not in camaras:
        informe.errores.append(f"{nombre}: no hay ningún plano «{id_}» en planos.toml.")
    for clave in [clave for clave in tabla if clave not in _CAMPOS_DE_LA_TOMA]:
        informe.errores.append(f"{nombre}: no conozco «{clave}».")
    desde = _leer_vista(tabla, None, nombre, informe)
    hasta = None
    if "hasta" in tabla:
        destino = tabla["hasta"]
        if not isinstance(destino, dict):
            informe.errores.append(f"{nombre}: «hasta» es una tabla, como hasta = {{ ancho = 0.8 }}.")
        else:
            for clave in [clave for clave in destino if clave not in _CAMPOS_DEL_DESTINO]:
                informe.errores.append(f"{nombre}: «hasta» no tiene «{clave}»; solo {', '.join(_CAMPOS_DEL_DESTINO)}.")
            hasta = _leer_vista(destino, desde, nombre, informe) if desde else None
    personajes = _leer_colocaciones(tabla, "personajes", nombre, informe)
    objetos = _leer_colocaciones(tabla, "objetos", nombre, informe)
    if desde is None or len(informe.errores) > errores:
        return None
    _comprobar_movimiento(camaras.get(id_, FIJA), desde, hasta, nombre, informe)
    if len(informe.errores) > errores:
        return None
    return Toma(id_, desde, hasta, personajes, objetos)


def _leer_vista(tabla: dict[str, Any], base: Vista | None, nombre: str, informe: Informe) -> Vista | None:
    """La vista que describe la tabla; los campos que faltan salen de `base` (en `hasta`)."""
    errores = len(informe.errores)
    mira = _leer_punto(tabla.get("mira", list(base.mira) if base else None), "mira", nombre, informe)
    ancho = tabla.get("ancho", base.ancho if base else None)
    azimut = tabla.get("azimut", base.azimut if base else 0.0)
    elevacion = tabla.get("elevacion", base.elevacion if base else 0.0)
    if not _es_numero(ancho) or ancho <= 0:
        informe.errores.append(f"{nombre}: el «ancho» es un número de metros mayor que 0, como ancho = 1.5.")
        return None
    if not _es_numero(azimut):
        informe.errores.append(f"{nombre}: «azimut» es un número de grados, como azimut = 10.")
        return None
    if not _es_numero(elevacion):
        informe.errores.append(f"{nombre}: «elevacion» es un número de grados, como elevacion = 10.")
        return None
    if len(informe.errores) > errores or mira is None:
        return None
    return Vista(mira, float(ancho), float(azimut), float(elevacion))


def _leer_punto(valor: object, campo: str, nombre: str, informe: Informe) -> Punto | None:
    if isinstance(valor, list) and len(valor) == 3 and all(_es_numero(v) for v in valor):
        return (float(valor[0]), float(valor[1]), float(valor[2]))
    informe.errores.append(f"{nombre}: «{campo}» son tres números, x, y y z en metros, como {campo} = [0.0, 1.0, 1.2].")
    return None


def _leer_colocaciones(tabla: dict[str, Any], clave: str, nombre: str, informe: Informe) -> tuple[Colocacion, ...]:
    lista = tabla.get(clave, [])
    if not isinstance(lista, list):
        informe.errores.append(f'{nombre}: «{clave}» es una lista de piezas, como {clave} = [{{ pieza = "…", en = [0, 1, 0] }}].')
        return ()
    colocaciones = []
    for pieza in lista:
        if not isinstance(pieza, dict):
            informe.errores.append(f"{nombre}: cada elemento de «{clave}» es una tabla con «pieza» y «en».")
            continue
        for campo in [campo for campo in pieza if campo not in _CAMPOS_DE_LA_COLOCACION]:
            informe.errores.append(f"{nombre}: en «{clave}», no conozco «{campo}».")
        nombre_de_la_pieza = pieza.get("pieza")
        if not isinstance(nombre_de_la_pieza, str):
            informe.errores.append(f"{nombre}: en «{clave}», una pieza no tiene «pieza» (su nombre en la biblioteca).")
            continue
        if "en" not in pieza:
            informe.errores.append(f"{nombre}: la pieza «{nombre_de_la_pieza}» no tiene «en»: dónde se pone.")
            continue
        punto = _leer_punto(pieza["en"], "en", f"{nombre}, pieza «{nombre_de_la_pieza}»", informe)
        textos = [pieza.get("ojos"), pieza.get("boca")]
        espejo = pieza.get("espejo", False)
        if not isinstance(espejo, bool) or any(t is not None and not isinstance(t, str) for t in textos):
            informe.errores.append(f"{nombre}: la pieza «{nombre_de_la_pieza}» tiene «espejo» (true o false), «ojos» o «boca» mal escritos.")
            continue
        if punto is not None:
            colocaciones.append(Colocacion(nombre_de_la_pieza, punto, espejo, textos[0], textos[1]))
    return tuple(colocaciones)


def _comprobar_movimiento(tipo: str, desde: Vista, hasta: Vista | None, nombre: str, informe: Informe) -> None:
    if tipo == FIJA:
        if hasta is not None:
            informe.errores.append(f"{nombre}: la cámara del plano es fija en planos.toml, así que la toma no puede llevar «hasta».")
        return
    if hasta is None:
        informe.errores.append(f"{nombre}: la cámara del plano se mueve ({tipo}) y la toma no dice hasta dónde: falta «hasta».")
        return
    desvio = max(abs(a - b) for a, b in zip(desde.mira, hasta.mira))
    giro = max(abs(hasta.azimut - desde.azimut), abs(hasta.elevacion - desde.elevacion))
    problemas = []
    if tipo == ACERCAMIENTO:
        if not ACERCAMIENTO_MINIMO * desde.ancho <= hasta.ancho <= desde.ancho:
            problemas.append(
                f"el ancho va de {desde.ancho} a {hasta.ancho} "
                f"(tiene que acabar entre {ACERCAMIENTO_MINIMO * desde.ancho:.2f} y {desde.ancho})"
            )
        if desvio > DESVIO_DEL_ACERCAMIENTO:
            problemas.append(f"el punto al que mira se mueve {desvio:.2f} m (como mucho {DESVIO_DEL_ACERCAMIENTO})")
        if giro > 0:
            problemas.append("la cámara gira, y un acercamiento no gira")
    else:
        if desvio > DESPLAZAMIENTO_MAXIMO:
            problemas.append(f"el punto al que mira se mueve {desvio:.2f} m (como mucho {DESPLAZAMIENTO_MAXIMO})")
        if giro > GIRO_MAXIMO:
            problemas.append(f"la cámara gira {giro:.0f}° (como mucho {GIRO_MAXIMO:.0f}°)")
        if abs(hasta.ancho - desde.ancho) / desde.ancho > VARIACION_DE_ANCHO_EN_DESPLAZAMIENTO:
            problemas.append("el ancho cambia demasiado para un desplazamiento")
    if problemas:
        informe.errores.append(f"{nombre}: el movimiento de cámara no es lento: {'; '.join(problemas)}.")


def _es_numero(valor: object) -> TypeGuard[float]:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)
