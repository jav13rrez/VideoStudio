"""Montaje: la composición de HyperFrames del episodio, generada a partir de la línea de tiempo.

La carpeta del episodio es el proyecto de HyperFrames: la composición es su index.html y enlaza las voces
desde voces/. Por ahora lleva las voces y los subtítulos sobre un fondo liso. Los tiempos van en segundos,
que es lo que lee HyperFrames, y él los ajusta al fotograma. El formato está en docs/montaje.md.
"""

import shutil
import subprocess
import sys
from html import escape
from pathlib import Path
from string import Template

from estudio.cronometraje import LineaDeTiempo

ARCHIVO = "index.html"
VIDEO = "versiones/previa.mp4"
# Versión fijada: HyperFrames saca versiones casi a diario, y un cambio suyo no debe cambiar los episodios.
HYPERFRAMES = "hyperframes@0.9.26"
ANCHO, ALTO = 1080, 1920
FONDO = "#3B4A5A"
COLORES = {"Tutor": ("#FFFFFF", "#000000"), "Perro": ("#E0FFFF", "#800000")}  # relleno y borde del texto

# Sin GSAP ni nada que se descargue: la animación de entrada es CSS, que HyperFrames también lleva fotograma
# a fotograma desde el principio de cada tarjeta. Así el render no depende de internet.
_COMPOSICION = Template("""\
<!doctype html>
<!-- Generado por la herramienta del estudio (uv run estudio montar). No se edita a mano. -->
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=$ancho, height=$alto" />
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: ${ancho}px; height: ${alto}px; overflow: hidden; background: $fondo; }
      #root { position: relative; width: 100%; height: 100%; background: $fondo; }
      /* Subtítulos abajo en el centro, dentro de la zona segura del 9:16: el texto acaba a 1330 px del borde
         de arriba y deja 120 px a cada lado, fuera de los botones de las aplicaciones. Si no cabe en una
         línea, crece hacia arriba. El borde se pinta por fuera de cada letra (paint-order). */
      .texto {
        position: absolute; left: 120px; right: 120px; bottom: 590px;
        display: flex; justify-content: center; text-align: center;
        font-family: "Montserrat"; font-weight: 900; font-size: 88px; line-height: 1.15;
        color: var(--relleno); -webkit-text-stroke: 20px var(--borde); paint-order: stroke fill;
      }
$colores
      .animada .texto { animation: entrada 0.2s cubic-bezier(0.34, 1.8, 0.64, 1) both; }
      @keyframes entrada { from { transform: scale(0.6); } to { transform: scale(1); } }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="episodio" data-start="0" data-duration="$duracion"
         data-width="$ancho" data-height="$alto" data-fps="$fps" data-no-timeline>
$voces
$subtitulos
    </div>
  </body>
</html>
""")


def montar(carpeta: Path, linea: LineaDeTiempo) -> None:
    """Deja la composición del episodio en la carpeta."""

    def segundos(fotogramas: int) -> str:
        return f"{fotogramas / linea.fps:.6f}".rstrip("0").rstrip(".")

    def tiempos(inicio: int, final: int) -> str:
        return f'data-start="{segundos(inicio)}" data-duration="{segundos(final - inicio)}"'

    voces = [
        f'      <audio id="voz-{frase.numero:02d}" class="clip" src="{frase.audio}" '
        f'{tiempos(frase.inicio, frase.final)} data-track-index="0" data-volume="1"></audio>'
        for frase in linea.frases
    ]
    subtitulos = [
        f'      <div id="subtitulo-{numero:03d}" class="clip tarjeta {tarjeta.personaje}'
        f'{" animada" if tarjeta.animada else ""}" {tiempos(tarjeta.inicio, tarjeta.final)} data-track-index="1">'
        f'<p class="texto">{escape(tarjeta.texto)}</p></div>'
        for numero, tarjeta in enumerate(linea.subtitulos, start=1)
    ]
    colores = [
        f"      .{personaje} {{ --relleno: {relleno}; --borde: {borde}; }}"
        for personaje, (relleno, borde) in COLORES.items()
    ]
    html = _COMPOSICION.substitute(
        ancho=ANCHO,
        alto=ALTO,
        fps=linea.fps,
        fondo=FONDO,
        duracion=segundos(linea.total),
        colores="\n".join(colores),
        voces="\n".join(voces),
        subtitulos="\n".join(subtitulos),
    )
    (carpeta / ARCHIVO).write_text(html, encoding="utf-8")


def renderizar(carpeta: Path) -> list[str]:
    """Renderiza la composición de la carpeta a VIDEO con HyperFrames; devuelve los errores que lo impiden."""
    npx = shutil.which("npx")
    if npx is None:
        return [
            "No encuentro npx, que viene con Node.js: para renderizar con HyperFrames hace falta instalar "
            "Node.js 22 o más nuevo (https://nodejs.org) y volver a intentarlo."
        ]
    salida = carpeta / VIDEO
    salida.parent.mkdir(exist_ok=True)
    sys.stdout.flush()  # que lo nuestro salga antes que los mensajes de HyperFrames
    # --strict: no renderiza si la composición tiene errores; --quiet: solo los mensajes que importan.
    orden = [npx, "--yes", HYPERFRAMES, "render", str(carpeta), "--output", str(salida)]
    proceso = subprocess.run([*orden, "--quality", "draft", "--strict", "--quiet"], check=False)
    if proceso.returncode != 0 or not salida.is_file():
        return [
            f"HyperFrames no ha podido renderizar el vídeo (terminó con el código {proceso.returncode}). "
            "El motivo está en sus mensajes, encima de este."
        ]
    return []
