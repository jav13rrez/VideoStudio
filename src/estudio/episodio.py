"""Crear un episodio y seguir su estado: paradas aprobadas, escenarios y personajes nuevos, y horas por etapa.

El estado se guarda en estado.toml, dentro de la carpeta del episodio, y solo lo escribe la herramienta.
El paso en el que está el episodio no se guarda: sale de las paradas aprobadas. El formato está en
docs/estado-del-episodio.md.
"""

import math
import re
import tomllib
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path

from estudio.configuracion import ErrorDeConfiguracion, leer_configuracion
from estudio.planos import ARCHIVO as ARCHIVO_DE_PLANOS

ARCHIVO = "estado.toml"
PERSONAJES = "personajes"  # dentro de la biblioteca, una carpeta por personaje, como los escenarios
ETAPAS = ("guion", "escenarios", "personajes", "animacion", "voces", "sonido", "revision")
_NOMBRE_CORTO = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
_NUMERO = re.compile(r"(\d{3})-")  # una carpeta de episodio empieza por su número: 001-olfato
_NUMERO_DELANTE = re.compile(r"\d+-")
_DECIMALES = 2  # las horas se guardan y se muestran con dos decimales, al cuarto de hora y más fino

# Qué aprueba el creador en cada parada.
PARADAS = {
    "1": "el guion, las fuentes y el CTA",
    "2": "el ritmo de la versión previa",
    "3": "el episodio final con su hoja de contactos",
}
# El paso del episodio según cuántas paradas lleva aprobadas: qué se hace y qué espera.
_PASOS = (
    ("1 de 4, el guion", f"que apruebes {PARADAS['1']} (parada 1)"),
    (
        "2 de 4, la lista de planos, los escenarios y personajes, las voces y la versión previa",
        f"que apruebes {PARADAS['2']} (parada 2)",
    ),
    ("3 de 4, el render y el montaje final", f"que apruebes {PARADAS['3']} (parada 3)"),
    (
        "4 de 4, la exportación y la publicación",
        "nada más del estudio: comprueba la exportación, saca la hoja de publicación y súbelo tú a mano",
    ),
)

_ESTRUCTURA = {
    "contenido.md": (
        "# Contenido\n\n"
        "El tema y la información del episodio, con tus palabras. Si traes fuentes, ponlas aquí también.\n"
    ),
    "guion.md": (
        "# Guion\n\n<!-- Lo escribe el agente a partir del contenido. Formato: docs/formato-del-guion.md. -->\n"
    ),
    "fuentes.md": "# Fuentes\n\n<!-- Una fuente por línea. Formato: docs/formato-del-guion.md. -->\n",
}
_CABECERA = (
    "# Estado del episodio. Lo escribe la herramienta del estudio: no lo edites a mano.\n"
    "# Para verlo en lenguaje llano: uv run estudio estado <carpeta del episodio>.\n"
)


class ErrorDeEstado(Exception):
    pass


# Lo que se aprueba y la sección de estado.toml donde se anota, cada aprobación con su fecha.
SECCIONES = {"parada": "paradas", "escenario": "escenarios", "personaje": "personajes"}


@dataclass(frozen=True)
class Estado:
    # Por cada cosa que se aprueba (parada, escenario o personaje), las aprobadas con su fecha.
    aprobaciones: dict[str, dict[str, date]] = field(default_factory=lambda: {que: {} for que in SECCIONES})
    horas: dict[str, float] = field(default_factory=dict)  # por etapa

    @property
    def paso(self) -> tuple[str, str]:
        """El paso en el que está el episodio y lo que espera."""
        return _PASOS[len(self.aprobaciones["parada"])]

    def aprobado(self, que: str, nombre: str) -> date | None:
        return self.aprobaciones[que].get(nombre)


@dataclass(frozen=True)
class Nuevos:
    """Los escenarios y personajes de la lista de planos que todavía no están en la biblioteca."""

    escenarios: list[str]
    personajes: list[str]

    def por_aprobar(self, que: str, estado: Estado) -> list[str]:
        """Los escenarios o personajes nuevos que el creador aún no ha aprobado."""
        nuevos = self.escenarios if que == "escenario" else self.personajes
        return [nombre for nombre in nuevos if estado.aprobado(que, nombre) is None]


# --- Crear ---


def crear_episodio(ruta: Path) -> tuple[Path | None, list[str]]:
    """Crea la carpeta del episodio junto a las demás, con el número siguiente; devuelve la carpeta o los errores."""
    nombre = ruta.name
    if not _NOMBRE_CORTO.fullmatch(nombre) or _NUMERO_DELANTE.match(nombre):
        return None, [
            f"«{nombre}» no vale como nombre corto: usa minúsculas sin tildes, números y guiones, sin espacios "
            "y sin el número delante (lo pone la herramienta), como «olfato» o «paseo-largo»."
        ]
    padre = ruta.parent
    try:
        leer_configuracion(padre)
    except ErrorDeConfiguracion as error:
        return None, [f"Los episodios van dentro del estudio. {error}"]
    hermanas = list(padre.iterdir()) if padre.is_dir() else []
    numeros = [int(m.group(1)) for d in hermanas if d.is_dir() and (m := _NUMERO.match(d.name))]
    carpeta = padre / f"{max(numeros, default=0) + 1:03d}-{nombre}"
    try:
        carpeta.mkdir(parents=True)
        for archivo, texto in _ESTRUCTURA.items():
            (carpeta / archivo).write_text(texto, encoding="utf-8")
        guardar_estado(carpeta, Estado())
    except OSError as error:
        return None, [f"No he podido crear {carpeta}: {error.strerror or error}."]
    return carpeta, []


# --- Leer y guardar ---


def leer_estado(carpeta: Path) -> Estado:
    """El estado guardado; si el episodio no tiene estado.toml, nada está aprobado todavía."""
    if not carpeta.is_dir():
        raise ErrorDeEstado(f"No existe la carpeta del episodio {carpeta}.")
    archivo = carpeta / ARCHIVO
    if not archivo.is_file():
        return Estado()
    try:
        datos = tomllib.loads(archivo.read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as error:
        raise ErrorDeEstado(
            f"{ARCHIVO}: no entiendo el archivo ({error}). Lo escribe la herramienta: "
            "si se ha tocado a mano, recupéralo con git."
        ) from error
    aprobaciones = {que: _fechas(datos, seccion) for que, seccion in SECCIONES.items()}
    paradas = list(aprobaciones["parada"])
    if sorted(paradas) != list(PARADAS)[: len(paradas)]:
        raise ErrorDeEstado(f"{ARCHIVO}: las paradas aprobadas tienen que ser la 1, la 1 y la 2, o las tres.")
    return Estado(aprobaciones, _horas(datos))


def guardar_estado(carpeta: Path, estado: Estado) -> None:
    """Escribe estado.toml; un fallo del disco llega como ErrorDeEstado."""
    secciones = [
        (seccion, {clave: valor.isoformat() for clave, valor in sorted(estado.aprobaciones[que].items())})
        for que, seccion in SECCIONES.items()
    ]
    secciones.append(("horas", {e: repr(float(estado.horas[e])) for e in ETAPAS if e in estado.horas}))
    texto = _CABECERA + "".join(
        f"\n[{nombre}]\n" + "".join(f"{_clave(clave)} = {valor}\n" for clave, valor in valores.items())
        for nombre, valores in secciones
        if valores
    )
    try:
        (carpeta / ARCHIVO).write_text(texto, encoding="utf-8")
    except OSError as error:
        raise ErrorDeEstado(f"No he podido guardar {ARCHIVO}: {error.strerror or error}.") from error


def _fechas(datos: dict[str, object], seccion: str) -> dict[str, date]:
    tabla = datos.get(seccion, {})
    if not (isinstance(tabla, dict) and all(isinstance(valor, date) for valor in tabla.values())):
        raise ErrorDeEstado(f"{ARCHIVO}: la sección [{seccion}] tiene que dar una fecha por nombre, como 2026-11-11.")
    return dict(tabla)


def _horas(datos: dict[str, object]) -> dict[str, float]:
    tabla = datos.get("horas", {})
    if not (
        isinstance(tabla, dict)
        and all(etapa in ETAPAS for etapa in tabla)
        and all(isinstance(h, int | float) and not isinstance(h, bool) for h in tabla.values())
    ):
        raise ErrorDeEstado(f"{ARCHIVO}: la sección [horas] tiene que dar un número por etapa ({', '.join(ETAPAS)}).")
    return {etapa: float(horas) for etapa, horas in tabla.items()}


def _clave(texto: str) -> str:
    return '"' + texto.replace("\\", "\\\\").replace('"', '\\"') + '"'


# --- Aprobar ---


def aprobar(carpeta: Path, que: str, nombre: str) -> tuple[list[str], list[str]]:
    """Anota con la fecha de hoy la aprobación de una parada, un escenario o un personaje: (errores, avisos)."""
    if que not in SECCIONES:
        return [f"Solo se aprueba una parada, un escenario o un personaje, no «{que}»."], []
    estado = leer_estado(carpeta)
    errores = _parada_aprobable(estado, nombre) if que == "parada" else _nuevo_aprobable(carpeta, que, nombre)
    if errores:
        return errores, []
    cuando = estado.aprobado(que, nombre)
    if cuando is not None:
        return [], [f"La aprobación de {que} «{nombre}» ya estaba anotada el {cuando.isoformat()}; no cambio la fecha."]
    con_la_nueva = {**estado.aprobaciones[que], nombre: date.today()}
    guardar_estado(carpeta, replace(estado, aprobaciones={**estado.aprobaciones, que: con_la_nueva}))
    return [], []


def _parada_aprobable(estado: Estado, parada: str) -> list[str]:
    if parada not in PARADAS:
        return [f"La parada «{parada}» no existe: las paradas son la 1, 2 o 3."]
    anteriores = [p for p in PARADAS if int(p) < int(parada) and estado.aprobado("parada", p) is None]
    if anteriores:
        return [f"Antes de la parada {parada} hay que aprobar la parada {anteriores[0]} ({PARADAS[anteriores[0]]})."]
    return []


def _nuevo_aprobable(carpeta: Path, que: str, nombre: str) -> list[str]:
    nuevos = nuevos_del_episodio(carpeta)
    candidatos = nuevos.escenarios if que == "escenario" else nuevos.personajes
    if nombre in candidatos:
        return []
    return [
        f"«{nombre}» no es un {que} nuevo de este episodio: se aprueban los de {ARCHIVO_DE_PLANOS} que no están "
        f"en la biblioteca ({', '.join(candidatos) or 'ahora no hay ninguno'})."
    ]


def nuevos_del_episodio(carpeta: Path) -> Nuevos:
    """Los escenarios marcados como nuevos en la lista de planos y los personajes que no están en la biblioteca.

    Si no hay lista de planos todavía, no hay ninguno. Lo que no se entiende de ella tampoco cuenta: los errores
    de la lista de planos los dice cronometrar.
    """
    archivo = carpeta / ARCHIVO_DE_PLANOS
    if not archivo.is_file():
        return Nuevos([], [])
    try:
        datos = tomllib.loads(archivo.read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError:
        return Nuevos([], [])
    marcados = datos.get("escenarios_nuevos", [])
    escenarios = [e for e in marcados if isinstance(e, str)] if isinstance(marcados, list) else []
    planos = datos.get("plano", [])
    planos = [p for p in planos if isinstance(p, dict)] if isinstance(planos, list) else []
    nombres = {n for p in planos if isinstance(p.get("personajes"), dict) for n in p["personajes"]}
    biblioteca = leer_configuracion(carpeta).biblioteca / PERSONAJES
    return Nuevos(escenarios, sorted(n for n in nombres if not (biblioteca / n).is_dir()))


# --- Horas ---


def registrar_horas(carpeta: Path, etapa: str, horas: str) -> list[str]:
    """Suma las horas a las de la etapa; devuelve los errores que lo impiden."""
    if etapa not in ETAPAS:
        return [f"«{etapa}» no es una etapa del estudio; las etapas son: {', '.join(ETAPAS)}."]
    try:
        numero = float(horas.replace(",", "."))
    except ValueError:
        numero = math.nan
    if not (math.isfinite(numero) and numero > 0):
        return [f"«{horas}» no es un número de horas mayor que cero, como 1,5 (hora y media)."]
    estado = leer_estado(carpeta)
    suma = round(estado.horas.get(etapa, 0) + numero, _DECIMALES)
    guardar_estado(carpeta, replace(estado, horas={**estado.horas, etapa: suma}))
    return []


def horas_en_texto(horas: float) -> str:
    """Las horas como se escriben en español: 2 h, 0,25 h."""
    return f"{round(horas, _DECIMALES):g}".replace(".", ",") + " h"
