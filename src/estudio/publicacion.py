"""La hoja de publicación de un episodio: descripción, enlaces con seguimiento y recordatorios de subida.

El formato está en docs/hoja-de-publicacion.md. La herramienta no publica nada: sube el creador, a mano.
"""

from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from estudio import app as documentacion_de_la_app
from estudio import revision
from estudio.configuracion import ErrorDeConfiguracion, leer_configuracion
from estudio.guion import comprobar_guion

ARCHIVO = "publicacion.md"
MEDIO = "social"  # utm_medium: el que las analíticas agrupan como redes sociales
PLATAFORMAS = {"YouTube": "youtube", "TikTok": "tiktok", "Instagram": "instagram"}  # nombre y utm_source
_DONDE = f"{documentacion_de_la_app.CARPETA}/{documentacion_de_la_app.ARCHIVO}"


def generar_hoja(carpeta: Path) -> list[str]:
    """Escribe la hoja de publicación en la carpeta del episodio; devuelve los errores que lo impiden."""
    carpeta = carpeta.resolve()  # su nombre es la campaña, también si llega como «.»
    frases, informe = comprobar_guion(carpeta)
    errores = list(informe.errores)
    cta = " ".join(frase.dicho for frase in frases if frase.es_cta)
    if not errores and not cta:
        errores.append("El guion no tiene CTA: marca con [cta] la frase o las dos frases finales del Perro.")
    enlace, de_la_app = _enlace_base(carpeta)
    errores += de_la_app
    if errores or enlace is None:
        return errores
    enlaces = {plataforma: _con_seguimiento(enlace, fuente, carpeta.name) for plataforma, fuente in PLATAFORMAS.items()}
    (carpeta / ARCHIVO).write_text(_hoja(carpeta, cta, enlaces), encoding="utf-8")
    return []


def _con_seguimiento(enlace: str, fuente: str, campana: str) -> str:
    """El enlace con las etiquetas de fuente, medio y campaña, conservando lo que ya llevaba."""
    partes = urlsplit(enlace)
    etiquetas = [(clave, valor) for clave, valor in parse_qsl(partes.query) if not clave.startswith("utm_")]
    etiquetas += [("utm_source", fuente), ("utm_medium", MEDIO), ("utm_campaign", campana)]
    return urlunsplit(partes._replace(query=urlencode(etiquetas)))


def _enlace_base(carpeta: Path) -> tuple[str | None, list[str]]:
    """El enlace a la App de la documentación de la App, o los errores que impiden usarlo."""
    try:
        configuracion = leer_configuracion(carpeta)
    except ErrorDeConfiguracion as error:
        return None, [str(error)]
    app, informe = documentacion_de_la_app.leer_app(configuracion.app)  # sus avisos son del cierre del CTA
    if informe.errores:
        return None, informe.errores
    if app.enlace is None:
        return None, [
            f"Falta el enlace a la App (enlace, en {_DONDE} junto a estudio.toml); "
            "sin él no se pueden hacer los enlaces con seguimiento."
        ]
    enlace = app.enlace.strip()
    partes = urlsplit(enlace)
    if partes.scheme not in ("http", "https") or not partes.netloc:
        return None, [
            f"{_DONDE}: «enlace» tiene que ser una dirección web completa, que empiece por https://, "
            f'como enlace = "https://…".'
        ]
    return enlace, []


def _hoja(carpeta: Path, cta: str, enlaces: dict[str, str]) -> str:
    exportacion = revision.ruta_de_la_exportacion(carpeta)
    lineas = [
        f"# Hoja de publicación de {carpeta.name}",
        "",
        f"La genera `uv run estudio hoja-de-publicacion {carpeta.name}`: no la edites a mano, vuelve a generarla.",
        "",
        "## Enlaces con seguimiento",
        "",
        *(f"- {plataforma}: {enlace}" for plataforma, enlace in enlaces.items()),
        "",
        "## Descripción",
    ]
    for plataforma, enlace in enlaces.items():
        lineas += ["", f"### {plataforma}", "", cta, "", enlace]
    lineas += [
        "",
        "## Recordatorios de subida",
        "",
        f"- Sube tú el vídeo, a mano, a cada plataforma: `{exportacion}`. Antes, comprueba la exportación con "
        f"`uv run estudio comprobar-exportacion {carpeta.name}`. La herramienta no publica nada.",
        "- Marca el aviso de marca propia en las plataformas que lo pidan al subir (en TikTok, por ejemplo, "
        "la divulgación del contenido como tu propia marca): el vídeo anuncia tu App, y sin el aviso pueden limitarlo.",
        "- No marques la etiqueta de IA: por defecto, los episodios del estudio no la llevan.",
        "- Usa en cada plataforma su propio enlace, para saber de dónde llega cada alta. En TikTok e Instagram "
        "los enlaces de la descripción no se pueden pulsar: pon el de esa plataforma en la bio del perfil.",
        "",
    ]
    return "\n".join(lineas)
