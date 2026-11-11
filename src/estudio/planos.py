"""Lista de planos: un plano por idea, cada uno desde la palabra del guion en la que empieza.

Un plano dura desde su palabra hasta la del plano siguiente, así que su duración no se escribe:
sale de la línea de tiempo. El formato está en docs/lista-de-planos.md.
"""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from estudio.configuracion import ARCHIVO as ARCHIVO_DE_CONFIGURACION
from estudio.configuracion import BIBLIOTECA
from estudio.guion import Frase, Informe

ARCHIVO = "planos.toml"
ESCENARIOS = "escenarios"  # dentro de la biblioteca, una carpeta por escenario
MAXIMO_DE_ESCENARIOS = 5

_OBLIGATORIOS = ("id", "empieza", "escenario", "encuadre", "camara", "motivo")
_OPCIONALES = ("personajes", "objeto", "sonido")
_TEXTOS = _OBLIGATORIOS + ("objeto", "sonido")  # los campos que son un texto
_NOMBRE = re.compile(r"[\w-]+")  # id y escenario: el escenario es el nombre de su carpeta
_MARCA = re.compile(r"\[[^\]]*\]")  # una marca de fuente copiada del guion junto con las palabras


@dataclass(frozen=True)
class Plano:
    id: str
    empieza: str  # las primeras palabras del plano, copiadas del guion
    escenario: str
    frase: int  # posición, desde 0, de la frase del guion en la que empieza
    palabra: int  # posición, desde 0, de su primera palabra dentro de esa frase
    sonido: str | None = None  # el sonido físico del plano, si lo hay; su efecto va en sonido.toml

    @property
    def posicion(self) -> tuple[int, int]:
        return self.frase, self.palabra


def leer_planos(carpeta: Path, frases: list[Frase], biblioteca: Path) -> tuple[list[Plano] | None, Informe]:
    """La lista de planos del episodio (None si no tiene), con los errores y avisos que da.

    Si hay errores, la lista que devuelve no vale para cronometrar.
    """
    informe = Informe()
    archivo = carpeta / ARCHIVO
    if not archivo.is_file():
        return None, informe
    try:
        datos = tomllib.loads(archivo.read_text(encoding="utf-8-sig"))
    except tomllib.TOMLDecodeError as error:
        informe.errores.append(f"{ARCHIVO}: no entiendo el archivo ({error}).")
        return [], informe

    for clave in [clave for clave in datos if clave not in ("escenarios_nuevos", "plano")]:
        informe.errores.append(
            f"{ARCHIVO}: no conozco «{clave}»; aparte de los planos, solo puede ir escenarios_nuevos."
        )
    nuevos = datos.get("escenarios_nuevos", [])
    if not (isinstance(nuevos, list) and all(isinstance(nombre, str) for nombre in nuevos)):
        informe.errores.append(
            f'{ARCHIVO}: escenarios_nuevos es una lista de nombres, como escenarios_nuevos = ["parque"].'
        )
    tablas = datos.get("plano", [])
    if not isinstance(tablas, list):
        informe.errores.append(f"{ARCHIVO}: cada plano empieza con [[plano]], con dos corchetes.")
        return [], informe
    if not tablas:
        informe.errores.append(f"{ARCHIVO}: la lista no tiene planos; cada plano empieza con [[plano]].")
    planos = [
        plano for numero, tabla in enumerate(tablas, start=1) if (plano := _leer_plano(numero, tabla, frases, informe))
    ]
    ids = [plano.id for plano in planos]
    for repetido in dict.fromkeys(id_ for id_ in ids if ids.count(id_) > 1):
        informe.errores.append(f"{ARCHIVO}: hay dos planos con el id «{repetido}»; cada plano necesita el suyo.")
    if informe.errores:
        return planos, informe  # sin todos los planos, las comprobaciones entre planos confundirían más que ayudar

    primera = next((i, 0) for i, frase in enumerate(frases) if frase.palabras)  # la primera palabra del guion
    if planos[0].posicion != primera:
        sin_cubrir = [frase.linea for frase in frases[: planos[0].frase]]
        if planos[0].palabra:
            sin_cubrir.append(frases[planos[0].frase].linea)
        informe.errores.append(
            f"{ARCHIVO}: el guion empieza sin plano y quedan sin cubrir las frases de estas líneas de guion.md: "
            f"{', '.join(map(str, sin_cubrir))}. El primer plano, «{planos[0].id}», tiene que empezar en la "
            f"primera palabra del guion, «{frases[primera[0]].palabras[0].texto}»."
        )

    for anterior, plano in zip(planos, planos[1:]):
        if plano.posicion == anterior.posicion:
            informe.errores.append(
                f"{ARCHIVO}, plano «{plano.id}»: empieza en la misma palabra que el plano anterior, «{anterior.id}». "
                "Cada plano dura hasta la palabra en la que empieza el siguiente, así que cada uno necesita la suya."
            )
        elif plano.posicion < anterior.posicion:
            informe.errores.append(
                f"{ARCHIVO}, plano «{plano.id}»: empieza en «{plano.empieza}» (línea {frases[plano.frase].linea} de "
                f"guion.md), antes que el plano anterior, «{anterior.id}», que empieza en «{anterior.empieza}» "
                f"(línea {frases[anterior.frase].linea}). Los planos van en el orden del guion."
            )

    fuera_de_la_biblioteca: dict[str, list[str]] = {}
    for plano in planos:
        if plano.escenario not in nuevos and not (biblioteca / ESCENARIOS / plano.escenario).is_dir():
            fuera_de_la_biblioteca.setdefault(plano.escenario, []).append(f"«{plano.id}»")
    for escenario, ids in fuera_de_la_biblioteca.items():
        informe.errores.append(
            f"{ARCHIVO}: el escenario «{escenario}» no está en la biblioteca (no hay carpeta "
            f"{BIBLIOTECA}/{ESCENARIOS}/{escenario} junto a {ARCHIVO_DE_CONFIGURACION}) y no va marcado como nuevo; "
            f"lo usan los planos {', '.join(ids)}. Si es nuevo, añádelo a escenarios_nuevos."
        )

    escenarios = list(dict.fromkeys(plano.escenario for plano in planos))
    if len(escenarios) > MAXIMO_DE_ESCENARIOS:
        informe.avisos.append(
            f"{ARCHIVO}: el episodio usa {len(escenarios)} escenarios ({', '.join(escenarios)}); "
            f"no debería pasar de {MAXIMO_DE_ESCENARIOS}, para reutilizar los decorados de la biblioteca."
        )

    # El cierre del CTA, con el nombre y el logo de la App, dura lo que el CTA: para que caiga entero en el
    # último plano, ese plano empieza con la primera palabra del CTA.
    cta = next((i for i, frase in enumerate(frases) if frase.es_cta and frase.palabras), None)
    if cta is not None and planos[-1].posicion != (cta, 0):
        informe.avisos.append(
            f"{ARCHIVO}: el último plano, «{planos[-1].id}», tiene que empezar en la primera palabra del CTA, "
            f"«{frases[cta].palabras[0].texto}» (línea {frases[cta].linea} de guion.md): es el plano que muestra "
            "el nombre y el logo de la App mientras el Perro dice el CTA."
        )
    return planos, informe


def _leer_plano(numero: int, tabla: object, frases: list[Frase], informe: Informe) -> Plano | None:
    """El plano número `numero` de la lista, o None si tiene errores, que deja en el informe."""
    if not isinstance(tabla, dict):
        informe.errores.append(f"{ARCHIVO}: cada plano empieza con [[plano]], con dos corchetes.")
        return None
    id_ = tabla.get("id")
    nombre = f"plano «{id_}»" if isinstance(id_, str) and _NOMBRE.fullmatch(id_) else f"plano número {numero}"
    errores = []
    for clave in [clave for clave in tabla if clave not in _OBLIGATORIOS + _OPCIONALES]:
        errores.append(
            f"no conozco el campo «{clave}»; los de un plano son {', '.join(_OBLIGATORIOS + _OPCIONALES)}."
        )
    for clave in _OBLIGATORIOS:
        if clave not in tabla:
            errores.append(f"falta «{clave}».")
    for clave in _TEXTOS:
        if clave not in tabla:
            continue
        valor = tabla[clave]
        if not isinstance(valor, str):
            errores.append(f"«{clave}» tiene que ser un texto entre comillas.")
        elif not valor.strip():
            errores.append(f"«{clave}» está vacío.")
        elif clave in ("id", "escenario") and not _NOMBRE.fullmatch(valor):
            errores.append(f"«{clave}» solo puede tener letras, números, guiones o guiones bajos, sin espacios.")
    personajes = tabla.get("personajes", {})
    if not (isinstance(personajes, dict) and all(isinstance(g, str) and g.strip() for g in personajes.values())):
        errores.append('«personajes» da el gesto de cada personaje, como personajes = { Perro = "ladea la cabeza" }.')

    empieza = tabla.get("empieza")
    posicion = None
    if isinstance(empieza, str) and empieza.strip():
        encontradas = _buscar(empieza, frases)
        if len(encontradas) == 1:
            posicion = encontradas[0]
        elif not encontradas:
            errores.append(
                f"no encuentro «{empieza}» en guion.md; «empieza» copia las primeras palabras del plano "
                "tal como están en una frase del guion."
            )
        else:
            lineas = dict.fromkeys(str(frases[frase].linea) for frase, _ in encontradas)
            errores.append(
                f"«{empieza}» aparece {len(encontradas)} veces en guion.md (líneas {', '.join(lineas)}); "
                "añade palabras hasta que aparezca una sola vez."
            )

    informe.errores += [f"{ARCHIVO}, {nombre}: {error}" for error in errores]
    if errores or posicion is None:
        return None
    return Plano(tabla["id"], tabla["empieza"], tabla["escenario"], *posicion, tabla.get("sonido"))


def _buscar(empieza: str, frases: list[Frase]) -> list[tuple[int, int]]:
    """Dónde empiezan esas palabras dentro de una frase del guion, sin mirar mayúsculas ni puntuación."""
    buscadas = [palabra for palabra in map(_sin_puntuacion, _MARCA.sub(" ", empieza).split()) if palabra]
    encontradas = []
    for numero, frase in enumerate(frases):
        palabras = [_sin_puntuacion(palabra.texto) for palabra in frase.palabras]
        for inicio in range(len(palabras) - len(buscadas) + 1):
            if buscadas and palabras[inicio : inicio + len(buscadas)] == buscadas:
                encontradas.append((numero, inicio))
    return encontradas


def _sin_puntuacion(palabra: str) -> str:
    return "".join(caracter for caracter in palabra.casefold() if caracter.isalnum())
