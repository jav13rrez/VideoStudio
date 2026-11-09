"""Montaje: la composición de HyperFrames del episodio, generada a partir de la línea de tiempo.

La carpeta del episodio es el proyecto de HyperFrames: la composición es su index.html y enlaza las voces
desde voces/. Por ahora lleva las voces y los subtítulos sobre un fondo liso. Los tiempos van en segundos,
que es lo que lee HyperFrames, y él los ajusta al fotograma. El formato está en docs/montaje.md.
"""

import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
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
FOTOGRAMAS_DE_ENTRADA = 6  # lo que dura la animación de entrada de una tarjeta acentuada
LETRA_MAXIMA, LETRA_MINIMA = 78, 42  # px: el tamaño de los subtítulos que recomienda HyperFrames
BORDE = 10  # px de borde alrededor de cada letra
# Lo que cabe entre los márgenes de 120 px, menos el borde a cada lado de la línea.
ANCHO_DEL_TEXTO = ANCHO - 2 * 120 - 2 * BORDE
# La letra de los subtítulos (Montserrat 900, licencia OFL en letras/OFL.txt) va con el estudio y se copia en
# cada episodio con un nombre propio, para que HyperFrames no la busque en internet: así el render no depende
# de la red ni de que Google cambie la letra.
LETRA = Path(__file__).parent / "letras" / "montserrat-latin-900-normal.woff2"
COPIA_DE_LA_LETRA = "assets/fonts/subtitulos.woff2"


@dataclass(frozen=True)
class Colores:
    relleno: str  # el color de las letras
    borde: str  # el del borde que las rodea


COLORES = {"Tutor": Colores("#FFFFFF", "#000000"), "Perro": Colores("#E0FFFF", "#800000")}

# El borde se dibuja con 24 copias del texto en el color del borde, a BORDE px alrededor (sombras sin difuminar).
# El borde de texto del navegador (-webkit-text-stroke) deja picos en las esquinas agudas, como las tildes.
_CONTORNO = ", ".join(
    f"{round(BORDE * math.cos(angulo), 2) + 0.0:g}px {round(BORDE * math.sin(angulo), 2) + 0.0:g}px 0 var(--borde)"
    for angulo in (2 * math.pi * paso / 24 for paso in range(24))
)

# Sin GSAP ni nada que se descargue: la animación de entrada es CSS, que HyperFrames también lleva fotograma
# a fotograma desde el principio de cada tarjeta.
_COMPOSICION = Template("""\
<!doctype html>
<!-- Generado por la herramienta del estudio (uv run estudio montar). No se edita a mano. -->
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=$ancho, height=$alto" />
    <style>
      @font-face {
        font-family: "Subtitulos"; font-weight: 900; font-style: normal;
        src: url("$letra") format("woff2");
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: ${ancho}px; height: ${alto}px; overflow: hidden; background: $fondo; }
      #root { position: relative; width: 100%; height: 100%; background: $fondo; }
      #subtitulos { position: absolute; inset: 0; }
      /* Subtítulos abajo en el centro, sobre la línea del primer cuarto de la pantalla contando desde abajo
         (480 px), por decisión del creador, y con 120 px a cada lado, fuera de los botones de las aplicaciones.
         Cada tarjeta va en una línea (el script de abajo ajusta su tamaño). */
      .texto {
        position: absolute; left: 120px; right: 120px; bottom: 480px;
        display: flex; justify-content: center; white-space: nowrap;
        font-family: "Subtitulos"; font-weight: 900; font-size: ${letra_maxima}px; line-height: 1.15;
        color: var(--relleno); text-shadow: $contorno;
      }
$colores
      .animada .texto { animation: entrada ${entrada}s cubic-bezier(0.34, 1.8, 0.64, 1) both; }
      @keyframes entrada { from { transform: scale(0.6); } to { transform: scale(1); } }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="episodio" data-start="0" data-duration="$duracion"
         data-width="$ancho" data-height="$alto" data-fps="$fps" data-no-timeline>
$voces
      <div id="subtitulos" data-track-kind="captions">
$subtitulos
      </div>
    </div>
    <script>
      // Cada tarjeta, en una sola línea: desde ${letra_maxima} px, bajando de 2 en 2 hasta que cabe, y nunca por
      // debajo de ${letra_minima} px. Es lo que recomienda HyperFrames para los subtítulos.
      const ajustar = window.__hyperframes && window.__hyperframes.fitTextFontSize;
      for (const texto of ajustar ? document.querySelectorAll("#subtitulos .texto") : []) {
        const opciones = { fontFamily: "Subtitulos", fontWeight: 900, maxWidth: $ancho_del_texto,
                           baseFontSize: $letra_maxima, minFontSize: $letra_minima, step: 2 };
        texto.style.fontSize = ajustar(texto.textContent, opciones).fontSize + "px";
      }
    </script>
  </body>
</html>
""")


def montar(carpeta: Path, linea: LineaDeTiempo) -> None:
    """Deja la composición del episodio en la carpeta, con la letra de los subtítulos."""

    def en_segundos(fotogramas: int) -> str:
        return f"{fotogramas / linea.fps:.6f}".rstrip("0").rstrip(".")

    def tiempos(inicio: int, final: int) -> str:
        return f'data-start="{en_segundos(inicio)}" data-duration="{en_segundos(final - inicio)}"'

    voces = [
        f'      <audio id="voz-{frase.numero:02d}" class="clip" src="{frase.audio}" '
        f'{tiempos(frase.inicio, frase.final)} data-track-index="0" data-volume="1"></audio>'
        for frase in linea.frases
    ]
    subtitulos = [
        f'        <div id="subtitulo-{numero:03d}" class="clip tarjeta {tarjeta.personaje}'
        f'{" animada" if tarjeta.animada else ""}" {tiempos(tarjeta.inicio, tarjeta.final)} data-track-index="1">'
        f'<p class="texto">{escape(tarjeta.texto)}</p></div>'
        for numero, tarjeta in enumerate(linea.subtitulos, start=1)
    ]
    colores = [
        f"      .{personaje} {{ --relleno: {colores.relleno}; --borde: {colores.borde}; }}"
        for personaje, colores in COLORES.items()
    ]
    html = _COMPOSICION.substitute(
        ancho=ANCHO,
        alto=ALTO,
        fps=linea.fps,
        fondo=FONDO,
        letra=COPIA_DE_LA_LETRA,
        contorno=_CONTORNO,
        letra_maxima=LETRA_MAXIMA,
        letra_minima=LETRA_MINIMA,
        ancho_del_texto=ANCHO_DEL_TEXTO,
        entrada=en_segundos(FOTOGRAMAS_DE_ENTRADA),
        duracion=en_segundos(linea.total),
        colores="\n".join(colores),
        voces="\n".join(voces),
        subtitulos="\n".join(subtitulos),
    )
    copia = carpeta / COPIA_DE_LA_LETRA
    copia.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LETRA, copia)
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
    salida.unlink(missing_ok=True)  # si el render falla, que no quede el vídeo de la vez anterior
    sys.stdout.flush()  # que lo nuestro salga antes que los mensajes de HyperFrames
    # Se ejecuta dentro de la carpeta del episodio, sin escribir su ruta en la orden: en Windows, npx pasa por
    # cmd.exe, que malinterpreta rutas con & o %. --strict: no renderiza si la composición tiene errores;
    # --quiet: solo los mensajes que importan.
    orden = [npx, "--yes", HYPERFRAMES, "render", ".", "--output", VIDEO, "--quality", "draft", "--strict", "--quiet"]
    proceso = subprocess.run(orden, cwd=carpeta, check=False)
    if proceso.returncode != 0 or not salida.is_file():
        return [
            f"HyperFrames no ha podido renderizar el vídeo (terminó con el código {proceso.returncode}). "
            "El motivo está en sus mensajes, encima de este."
        ]
    return []
