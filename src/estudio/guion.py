"""Comprobación del guion y las fuentes de un episodio.

El formato de los dos archivos está en docs/formato-del-guion.md.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

PERSONAJES = ("Perro", "Tutor")
PALABRAS_CONVERSACION = (150, 170)  # para que el episodio dure 55-70 s
PALABRAS_CTA = 15  # unos 5 segundos
MARCAS = ("gancho", "remate", "cta")

# [marca] [marca] Personaje: texto
_FRASE = re.compile(r"^(?P<marcas>(?:\[[^\]]*\]\s*)*)(?P<personaje>[^:\[\]]+?)\s*:\s*(?P<texto>\S.*)$")
_MARCA = re.compile(r"\[[^\]]*\]")
_MARCA_DE_FUENTE = re.compile(r"\[fuente:\s*(?P<id>[\w-]+)\s*\]")
# - [x] id: descripción — enlace o referencia
_FUENTE = re.compile(r"^- \[(?P<revisada>[ xX])\] (?P<id>[\w-]+):\s*\S")


@dataclass(frozen=True)
class Palabra:
    texto: str  # como se escribe, con su puntuación y sin asteriscos
    acentuada: bool


@dataclass
class Frase:
    linea: int
    personaje: str
    texto: str
    marcas: set[str]

    @property
    def es_cta(self) -> bool:
        return "cta" in self.marcas

    @property
    def ids_de_fuente(self) -> list[str]:
        return _MARCA_DE_FUENTE.findall(self.texto)

    @property
    def palabras(self) -> list[Palabra]:
        """Las palabras que se dicen, en orden: sin marcas ni asteriscos de acento."""
        palabras = []
        acentuando = False  # dentro de un *tramo acentuado*, que puede abarcar varias palabras
        for trozo in _MARCA.sub(" ", self.texto).split():
            acentuada = False
            for caracter in trozo:
                if caracter == "*":
                    acentuando = not acentuando
                elif acentuando and caracter.isalnum():
                    acentuada = True
            texto = trozo.replace("*", "")
            if any(caracter.isalnum() for caracter in texto):
                palabras.append(Palabra(texto, acentuada))
        return palabras


@dataclass
class Fuente:
    linea: int
    id: str
    revisada: bool


@dataclass
class Informe:
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


def comprobar_guion(carpeta: Path) -> tuple[list[Frase], Informe]:
    """Las frases del guion, y los errores y avisos que impiden o no pasar a la parada 1."""
    informe = Informe()
    guion = carpeta / "guion.md"
    if not guion.is_file():
        informe.errores.append(f"No encuentro el guion: tiene que estar en {guion}.")
        return [], informe
    frases = _leer_guion(guion, informe)
    if not frases:
        informe.errores.append("El guion no tiene frases.")
        return frases, informe
    fuentes = _leer_fuentes(carpeta / "fuentes.md", informe)
    ids = {fuente.id for fuente in fuentes}

    for frase in frases:
        if frase.personaje not in PERSONAJES:
            informe.errores.append(
                f"guion.md, línea {frase.linea}: habla «{frase.personaje}»; solo pueden hablar «Perro» y «Tutor»."
            )
        if frase.es_cta and frase.personaje == "Tutor":
            informe.errores.append(f"guion.md, línea {frase.linea}: el CTA lo tiene que decir el Perro, no el Tutor.")
        for id_fuente in frase.ids_de_fuente:
            if id_fuente not in ids:
                informe.errores.append(
                    f"guion.md, línea {frase.linea}: la marca apunta a la fuente «{id_fuente}», "
                    "que no está en fuentes.md."
                )

    primer_cta = next((i for i, frase in enumerate(frases) if frase.es_cta), None)
    if primer_cta is not None:
        detras = [frase for frase in frases[primer_cta:] if not frase.es_cta]
        if detras:
            informe.errores.append(
                f"guion.md, línea {frases[primer_cta].linea}: el CTA tiene que ir al final, "
                f"pero detrás hay frases de la conversación (desde la línea {detras[0].linea})."
            )

    conversacion = [frase for frase in frases if not frase.es_cta]
    if not conversacion or "gancho" not in conversacion[0].marcas:
        informe.avisos.append(
            "Falta la marca de gancho: la primera frase de la conversación tiene que llevar [gancho]."
        )
    if not conversacion or "remate" not in conversacion[-1].marcas:
        informe.avisos.append(
            "Falta la marca de remate: la última frase de la conversación tiene que llevar [remate]."
        )

    palabras = sum(len(frase.palabras) for frase in conversacion)
    minimo, maximo = PALABRAS_CONVERSACION
    if not minimo <= palabras <= maximo:
        informe.avisos.append(
            f"La conversación (sin el CTA) tiene {palabras} palabras; "
            f"debería tener entre {minimo} y {maximo} para que el episodio dure 55-70 segundos."
        )

    palabras_cta = sum(len(frase.palabras) for frase in frases if frase.es_cta)
    if primer_cta is None:
        informe.avisos.append("El guion no tiene CTA: marca con [cta] la frase o las dos frases finales del Perro.")
    elif palabras_cta > PALABRAS_CTA:
        informe.avisos.append(
            f"El CTA tiene {palabras_cta} palabras; no debería pasar de unas {PALABRAS_CTA} (unos 5 segundos)."
        )

    usadas = {id_fuente for frase in frases for id_fuente in frase.ids_de_fuente}
    for fuente in fuentes:
        if fuente.id not in usadas:
            informe.avisos.append(
                f"fuentes.md, línea {fuente.linea}: ninguna frase usa la fuente «{fuente.id}»."
            )
        if not fuente.revisada:
            informe.avisos.append(
                f"fuentes.md, línea {fuente.linea}: la fuente «{fuente.id}» no está revisada; "
                "márcala con [x] cuando la compruebes."
            )
    return frases, informe


def _leer_guion(archivo: Path, informe: Informe) -> list[Frase]:
    frases = []
    for numero, linea in _lineas(archivo):
        encaje = _FRASE.match(linea)
        if not encaje:
            informe.errores.append(
                f"guion.md, línea {numero}: no entiendo esta línea; cada frase se escribe «Perro: texto» "
                "o «Tutor: texto», con sus marcas delante si las lleva."
            )
            continue
        marcas = set()
        for marca in _MARCA.findall(encaje["marcas"]):
            if marca[1:-1] in MARCAS:
                marcas.add(marca[1:-1])
            else:
                informe.errores.append(
                    f"guion.md, línea {numero}: no conozco la marca {marca}; "
                    "delante de una frase solo pueden ir [gancho], [remate] y [cta]."
                )
        texto = encaje["texto"].strip()
        for marca in _MARCA.findall(texto):
            if not _MARCA_DE_FUENTE.fullmatch(marca):
                informe.errores.append(
                    f"guion.md, línea {numero}: no entiendo la marca {marca}. Dentro del texto solo van "
                    "marcas de fuente, escritas [fuente: id] y una por fuente; "
                    "[gancho], [remate] y [cta] van delante del personaje."
                )
        if texto.count("*") % 2:
            informe.errores.append(
                f"guion.md, línea {numero}: hay un asterisco sin pareja; las palabras acentuadas van "
                "entre dos asteriscos, *así* o *varias seguidas*."
            )
        frases.append(Frase(numero, encaje["personaje"].strip(), texto, marcas))
    return frases


def _leer_fuentes(archivo: Path, informe: Informe) -> list[Fuente]:
    if not archivo.exists():
        return []
    fuentes = []
    for numero, linea in _lineas(archivo):
        encaje = _FUENTE.match(linea)
        if not encaje:
            informe.errores.append(
                f"fuentes.md, línea {numero}: no entiendo esta línea; cada fuente se escribe "
                "«- [ ] id: descripción — enlace o referencia», con [x] si ya está revisada."
            )
            continue
        fuentes.append(Fuente(numero, encaje["id"], encaje["revisada"] != " "))
    return fuentes


def _lineas(archivo: Path) -> Iterator[tuple[int, str]]:
    """Las líneas con contenido, con su número; se saltan las vacías y los títulos (#)."""
    # utf-8-sig: algunos editores de Windows empiezan el archivo con un carácter invisible (BOM).
    for numero, linea in enumerate(archivo.read_text(encoding="utf-8-sig").splitlines(), start=1):
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            yield numero, linea
