"""Recorta el fondo gris de las ilustraciones del Perro y del Tutor: perro.png y tutor.png, con transparencia suave.

El Perro se queda entero, con su cara y su cola originales: orejas y cola no son piezas aparte, se doblan en animar.py
con una deformación blanda (peso 0 en la unión con el cuerpo y 1 en la punta), así no hay cortes ni huecos.

Uso: uv run --with pillow --with numpy --with scipy python piezas.py
"""

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

AQUI = Path(__file__).parent
SALIDA = AQUI / "piezas"
TOLERANCIA_FONDO = 14  # lo que se puede apartar un píxel del gris del fondo para contar como fondo


def fondo_conectado(rgb: np.ndarray) -> np.ndarray:
    """Los píxeles del gris del fondo que se alcanzan desde los bordes (no los grises de dentro del dibujo)."""
    gris = np.median(np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]), axis=0)
    parecido = np.abs(rgb.astype(int) - gris).max(axis=2) <= TOLERANCIA_FONDO
    etiquetas, _ = ndimage.label(parecido)
    en_borde = np.unique(np.concatenate([etiquetas[0], etiquetas[-1], etiquetas[:, 0], etiquetas[:, -1]]))
    return np.isin(etiquetas, en_borde[en_borde > 0])


def recortar(origen: str, destino: str) -> None:
    rgb = np.array(Image.open(AQUI / "generado" / origen).convert("RGB"))
    alfa = ndimage.gaussian_filter((~fondo_conectado(rgb)).astype(float), 0.8)
    Image.fromarray(np.dstack([rgb, (np.clip(alfa, 0, 1) * 255).astype(np.uint8)]), "RGBA").save(SALIDA / destino)


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    recortar("perro_vectorial.png", "perro.png")
    recortar("tutor_vectorial.png", "tutor.png")
    print("hecho: perro.png, tutor.png")


main()
