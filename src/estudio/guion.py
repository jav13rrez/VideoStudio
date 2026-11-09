"""Comprobación del guion y las fuentes de un episodio.

El formato de los dos archivos está en docs/formato-del-guion.md.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

PERSONAJES = ("Perro", "Tutor")
PALABRAS_CONVERSACION = (150, 170)  # para que el episodio dure 55-70 s
PALABRAS_CTA = 15  # unos 5 segundos
MARCAS = ("gancho", "remate", "cta")

# [marca] [marca] Personaje: texto
_FRASE = re.compile(r"^(?P<marcas>(?:\[[^\]]*\]\s*)*)(?P<personaje>[^:\[\]]+?)\s*:\s*(?P<texto>\S.*)$")
_MARCA_DE_FUENTE = re.compile(r"\[fuente:\s*(?P<id>[^\]]*?)\s*\]")
# - [x] id: descripción — enlace o referencia
_FUENTE = re.compile(r"^- \[(?P<revisada>[ xX])\] (?P<id>[\w-]+):")


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
    def fuentes(self) -> list[str]:
        return _MARCA_DE_FUENTE.findall(self.texto)

    @property
    def palabras(self) -> int:
        """Las palabras que se dicen: sin marcas de fuente ni asteriscos de acento."""
        dicho = _MARCA_DE_FUENTE.sub(" ", self.texto).replace("*", "")
        return sum(1 for trozo in dicho.split() if any(c.isalnum() for c in trozo))


@dataclass
class Fuente:
    linea: int
    id: str
    revisada: bool


@dataclass
class Informe:
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


def comprobar_guion(carpeta: Path) -> Informe:
    informe = Informe()
    guion = carpeta / "guion.md"
    if not guion.is_file():
        informe.errores.append(f"No encuentro el guion: tiene que estar en {guion}.")
        return informe
    frases = _leer_guion(guion, informe)
    fuentes = _leer_fuentes(carpeta / "fuentes.md", informe)
    ids = {fuente.id for fuente in fuentes}

    for frase in frases:
        if frase.personaje not in PERSONAJES:
            informe.errores.append(
                f"guion.md, línea {frase.linea}: habla «{frase.personaje}»; solo pueden hablar «Perro» y «Tutor»."
            )
        if frase.es_cta and frase.personaje == "Tutor":
            informe.errores.append(f"guion.md, línea {frase.linea}: el CTA lo tiene que decir el Perro, no el Tutor.")
        for id in frase.fuentes:
            if id not in ids:
                informe.errores.append(
                    f"guion.md, línea {frase.linea}: la marca apunta a la fuente «{id}», que no está en fuentes.md."
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

    palabras = sum(frase.palabras for frase in conversacion)
    minimo, maximo = PALABRAS_CONVERSACION
    if not minimo <= palabras <= maximo:
        informe.avisos.append(
            f"La conversación (sin el CTA) tiene {palabras} palabras; "
            f"debería tener entre {minimo} y {maximo} para que el episodio dure 55-70 segundos."
        )

    palabras_cta = sum(frase.palabras for frase in frases if frase.es_cta)
    if primer_cta is None:
        informe.avisos.append("El guion no tiene CTA: marca con [cta] la frase o las dos frases finales del Perro.")
    elif palabras_cta > PALABRAS_CTA:
        informe.avisos.append(
            f"El CTA tiene {palabras_cta} palabras; no debería pasar de unas {PALABRAS_CTA} (unos 5 segundos)."
        )

    usadas = {id for frase in frases for id in frase.fuentes}
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
    return informe


def _leer_guion(archivo: Path, informe: Informe) -> list[Frase]:
    frases = []
    for numero, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), start=1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        encaje = _FRASE.match(linea)
        if not encaje:
            informe.errores.append(
                f"guion.md, línea {numero}: no entiendo esta línea; cada frase se escribe «Perro: texto» "
                "o «Tutor: texto», con sus marcas delante si las lleva."
            )
            continue
        marcas = set()
        for marca in re.findall(r"\[([^\]]*)\]", encaje["marcas"]):
            if marca.strip().lower() in MARCAS:
                marcas.add(marca.strip().lower())
            else:
                informe.errores.append(
                    f"guion.md, línea {numero}: no conozco la marca [{marca}]; "
                    "delante de una frase solo pueden ir [gancho], [remate] y [cta]."
                )
        frases.append(Frase(numero, encaje["personaje"].strip(), encaje["texto"].strip(), marcas))
    return frases


def _leer_fuentes(archivo: Path, informe: Informe) -> list[Fuente]:
    if not archivo.exists():
        return []
    fuentes = []
    for numero, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), start=1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        encaje = _FUENTE.match(linea)
        if not encaje:
            informe.errores.append(
                f"fuentes.md, línea {numero}: no entiendo esta línea; cada fuente se escribe "
                "«- [ ] id: descripción — enlace o referencia», con [x] si ya está revisada."
            )
            continue
        fuentes.append(Fuente(numero, encaje["id"], encaje["revisada"] != " "))
    return fuentes
