"""Genera con Fal el arte del prototipo 2D: el Perro de perfil en dos estilos y el salón ilustrado.

Uso: uv run --with fal-client python generar.py
Lee FAL_KEY de ../../.env (nunca se imprime). Salida en ./generado/.
"""

import concurrent.futures as cf
import os
import urllib.request
from pathlib import Path

import fal_client

AQUI = Path(__file__).parent
for linea in (AQUI.parent.parent / ".env").read_text().splitlines():
    if linea.startswith("FAL_KEY="):
        os.environ["FAL_KEY"] = linea.split("=", 1)[1].strip()

MODELO = "fal-ai/nano-banana/edit"
PERRO = (
    "Redraw this exact dog (same breed, same black-and-white markings, same sitting profile pose facing left, "
    "same proportions) as a 2D cartoon character for an animated series. Plain flat light-gray background, "
    "full body visible including the tail, ears clearly distinct. "
)
ESTILO = (
    "Style: clean flat vector illustration, bold dark outline of uniform thickness, simple cel shading with two tones, "
    "no photographic fur or skin texture, big readable shapes. Plain flat light-gray background, full body visible."
)


def tutor(pose: str) -> str:
    return (
        "Redraw this exact man (same face, same hair, same clothes and colors, same proportions) as a 2D cartoon "
        f"character for an animated series, in {pose}, facing left, matching a flat vector style. No furniture. " + ESTILO
    )


def perro(pose: str) -> str:
    return (
        "Redraw this exact dog (same breed, same black-and-white markings and mottled face, same proportions) as a 2D "
        f"cartoon character for an animated series, in {pose}, facing left, with the tail and both ears clearly "
        "visible and distinct. " + ESTILO
    )


# Ya generados (no se repiten): perro_de_pie_vectorial y perro_esfinge_vectorial, con perro("the same standing profile
# pose") y perro("the same lying-down sphinx profile pose, front paws stretched forward, head up").
# El recorte de pie del Tutor no trae la cabeza (la hoja no la tiene de perfil): la segunda imagen es su cabeza ya
# ilustrada, de la versión sentada.
PEDIDOS = {
    ("tutor_de_pie_vectorial", ("origen/tutor_de_pie_perfil.png", "generado/tutor_vectorial.png")): (
        "The first image shows a man standing in profile but his head is missing (cut off at the neck). The second image "
        "is a flat vector illustration of the same man sitting, showing his head, face and short dark hair in profile. "
        "Redraw the first image as a full-body flat vector illustration of the same man standing in profile facing left, "
        "adding the head, face and hair exactly as in the second image, with the same clothes, colors and proportions "
        "as the first image. No furniture. " + ESTILO
    ),
}


def uno(item: tuple[tuple[str, str | tuple[str, ...]], str]) -> str:
    (nombre, origen), prompt = item
    origenes = (origen,) if isinstance(origen, str) else origen
    urls = [fal_client.upload_file(str(AQUI / o)) for o in origenes]
    resultado = fal_client.subscribe(MODELO, arguments={"prompt": prompt, "image_urls": urls})
    destino = AQUI / "generado" / f"{nombre}.png"
    destino.parent.mkdir(exist_ok=True)
    urllib.request.urlretrieve(resultado["images"][0]["url"], destino)
    return nombre


with cf.ThreadPoolExecutor(3) as ex:
    for nombre in ex.map(uno, PEDIDOS.items()):
        print("ok", nombre)
