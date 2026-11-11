"""Montaje: la composición de HyperFrames del episodio, generada a partir de la línea de tiempo.

La carpeta del episodio es el proyecto de HyperFrames: la composición es su index.html y enlaza las voces
desde voces/. Lleva una imagen por plano (su render de planos/ o, si aún no lo tiene, un cartel), las voces,
la música y los efectos de sonido.toml, los subtítulos y el cierre del CTA con el nombre y el logo de la App. Los tiempos van en segundos, que es lo
que lee HyperFrames, y él los ajusta al fotograma. El formato está en docs/montaje.md.
"""

import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path
from string import Template

from estudio import hyperframes
from estudio.app import ARCHIVO as ARCHIVO_DE_LA_APP
from estudio.app import CARPETA as CARPETA_DE_LA_APP
from estudio.app import App, leer_app
from estudio.cronometraje import LineaDeTiempo, Tramo
from estudio.guion import Informe
from estudio.planos import Plano
from estudio.sonido import Pista, colocar_sonido

ARCHIVO = "index.html"
VIDEO = "versiones/previa.mp4"
ANCHO, ALTO = 1080, 1920
FONDO = "#3B4A5A"  # gris azulado: lo que se ve si el episodio no tiene lista de planos
# La imagen de cada plano, cuando la tiene (su render), va en planos/ con el id del plano por nombre: planos/05.png.
# Mientras no la tiene, la composición lleva su cartel, que la herramienta genera en CARTELES.
IMAGENES = "planos"
CARTELES = "assets/carteles"
# Un color liso por escenario, en el orden en que aparecen, para ver de un vistazo dónde cambia el escenario.
# Oscuros y apagados, para que encima se lean los dos colores de los subtítulos.
COLORES_DE_LOS_CARTELES = (FONDO, "#5A4636", "#3E5A45", "#5A3E52", "#5A5436")
COPIAS_DE_LA_APP = "assets/app"  # el logo de la App, copiado en la carpeta del episodio, o su marcador
COPIA_DEL_LOGO = f"{COPIAS_DE_LA_APP}/logo"  # más la extensión del logo
MARCADOR_DEL_LOGO = f"{COPIAS_DE_LA_APP}/marcador-del-logo.svg"
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

# Los carteles y el marcador del logo son imágenes SVG: texto, sin nada que instalar. Una imagen SVG no puede
# cargar letras, así que llevan una del sistema.
_CARTEL = Template("""\
<svg xmlns="http://www.w3.org/2000/svg" width="$ancho" height="$alto" viewBox="0 0 $ancho $alto">
  <!-- Cartel generado por la herramienta del estudio. Lo sustituye la imagen del plano en planos/. -->
  <rect width="$ancho" height="$alto" fill="$color" />
  <g fill="#FFFFFF" font-family="Arial, Helvetica, sans-serif" font-weight="bold" text-anchor="middle">
    <text x="$centro" y="800" font-size="56" letter-spacing="12" fill-opacity="0.6">PLANO</text>
    <text x="$centro" y="1060" font-size="$tamano_del_id">$id</text>
    <text x="$centro" y="1170" font-size="$tamano_del_escenario" fill-opacity="0.8">$escenario</text>
  </g>
</svg>
""")
_MARCADOR_DEL_LOGO = f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240" viewBox="0 0 240 240">
  <!-- Marcador del logo de la App, mientras no esté en {CARPETA_DE_LA_APP}/{ARCHIVO_DE_LA_APP}. -->
  <rect x="6" y="6" width="228" height="228" rx="40" fill="#FFFFFF" fill-opacity="0.12"
        stroke="#FFFFFF" stroke-width="6" stroke-dasharray="20 14" />
  <text x="120" y="136" fill="#FFFFFF" font-family="Arial, Helvetica, sans-serif" font-weight="bold"
        font-size="44" letter-spacing="4" text-anchor="middle">LOGO</text>
</svg>
"""

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
      /* Lo que se ve delante lo decide el z-index, no data-track-index: planos, cierre del CTA y subtítulos. */
      .plano { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; }
      #cierre-del-cta { position: absolute; inset: 0; z-index: 1; }
      #subtitulos { position: absolute; inset: 0; z-index: 2; }
      /* Las letras de los subtítulos y del nombre de la App, en una línea (el script de abajo ajusta su tamaño)
         y con el borde alrededor de cada letra, en los colores de quien habla: el nombre, en los del Tutor. */
      .texto, .nombre {
        white-space: nowrap; font-family: "Subtitulos"; font-weight: 900; font-size: ${letra_maxima}px;
        line-height: 1.15; color: var(--relleno); text-shadow: $contorno;
      }
      /* Subtítulos abajo en el centro, sobre la línea del primer cuarto de la pantalla contando desde abajo
         (480 px), por decisión del creador, y con 120 px a cada lado, fuera de los botones de las aplicaciones. */
      .texto { position: absolute; left: 120px; right: 120px; bottom: 480px; display: flex; justify-content: center; }
      /* El cierre del CTA: el logo y el nombre de la App arriba en el centro, a 260 px del borde de arriba,
         por debajo de las pestañas de TikTok e Instagram y lejos de los subtítulos. */
      .cierre {
        position: absolute; top: 260px; left: 120px; right: 120px;
        display: flex; flex-direction: column; align-items: center; gap: 32px;
      }
      .logo { width: 240px; height: 240px; object-fit: contain; }
$colores
      .animada .texto { animation: entrada ${entrada}s cubic-bezier(0.34, 1.8, 0.64, 1) both; }
      @keyframes entrada { from { transform: scale(0.6); } to { transform: scale(1); } }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="episodio" data-start="0" data-duration="$duracion"
         data-width="$ancho" data-height="$alto" data-fps="$fps" data-no-timeline>
$capas
      <div id="subtitulos" data-track-kind="captions">
$subtitulos
      </div>
    </div>
    <script>
      // Cada tarjeta, y el nombre de la App, en una sola línea: desde ${letra_maxima} px, bajando de 2 en 2 hasta
      // que cabe, y nunca por debajo de ${letra_minima} px. Es lo que recomienda HyperFrames para los subtítulos.
      const ajustar = window.__hyperframes && window.__hyperframes.fitTextFontSize;
      for (const texto of ajustar ? document.querySelectorAll("#subtitulos .texto, .cierre .nombre") : []) {
        const opciones = { fontFamily: "Subtitulos", fontWeight: 900, maxWidth: $ancho_del_texto,
                           baseFontSize: $letra_maxima, minFontSize: $letra_minima, step: 2 };
        texto.style.fontSize = ajustar(texto.textContent, opciones).fontSize + "px";
      }
    </script>
  </body>
</html>
""")


def montar(carpeta: Path, linea: LineaDeTiempo, planos: list[Plano], carpeta_de_la_app: Path) -> Informe:
    """Deja la composición del episodio en la carpeta, con lo que usa: la letra, los carteles y el logo.

    Si hay CTA, lee la documentación de la App para su cierre; lee también la música y los efectos. Devuelve lo
    que les falta (avisos) y lo que no se entiende (errores); con errores no escribe nada.
    """
    app: App | None = None
    informe = Informe()
    if linea.cta is not None:
        app, informe = leer_app(carpeta_de_la_app)
    pistas, informe_del_sonido = colocar_sonido(carpeta, linea, planos)
    informe.errores += informe_del_sonido.errores
    informe.avisos += informe_del_sonido.avisos
    if informe.errores:
        return informe

    # Los carteles y la copia del logo se generan de nuevo cada vez: así no quedan carteles de planos que ya
    # tienen su imagen, ni marcadores o logos viejos.
    for generados in (CARTELES, COPIAS_DE_LA_APP):
        shutil.rmtree(carpeta / generados, ignore_errors=True)
    capas = _capas_de_los_planos(carpeta, linea, planos)
    capas += [
        f'      <audio id="voz-{frase.numero:02d}" class="clip" src="{frase.audio}" '
        f'{_tiempos(frase.inicio, frase.final, linea.fps)} data-track-index="0" data-volume="1"></audio>'
        for frase in linea.frases
    ]
    capas += [_capa_de_sonido(pista, linea.fps) for pista in pistas]
    if app is not None and linea.cta is not None:
        capas += _cierre(carpeta, linea.cta, linea.fps, app)
    subtitulos = [
        f'        <div id="subtitulo-{numero:03d}" class="clip tarjeta {tarjeta.personaje}'
        f'{" animada" if tarjeta.animada else ""}" {_tiempos(tarjeta.inicio, tarjeta.final, linea.fps)} '
        f'data-track-index="1"><p class="texto">{escape(tarjeta.texto)}</p></div>'
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
        entrada=_en_segundos(FOTOGRAMAS_DE_ENTRADA, linea.fps),
        duracion=_en_segundos(linea.total, linea.fps),
        colores="\n".join(colores),
        capas="\n".join(capas),
        subtitulos="\n".join(subtitulos),
    )
    copia = carpeta / COPIA_DE_LA_LETRA
    copia.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LETRA, copia)
    (carpeta / ARCHIVO).write_text(html, encoding="utf-8")
    return informe


def imagen_del_plano(carpeta: Path, plano: str) -> str | None:
    """La imagen propia del plano (su render), desde la carpeta del episodio, si ya la tiene."""
    imagen = f"{IMAGENES}/{plano}.png"
    return imagen if (carpeta / imagen).is_file() else None


def _capas_de_los_planos(carpeta: Path, linea: LineaDeTiempo, planos: list[Plano]) -> list[str]:
    """Una capa de imagen por plano: su imagen, si ya la tiene; si no, su cartel, que deja en CARTELES."""
    escenarios = {plano.id: plano.escenario for plano in planos}
    colores = {
        escenario: COLORES_DE_LOS_CARTELES[numero % len(COLORES_DE_LOS_CARTELES)]
        for numero, escenario in enumerate(dict.fromkeys(escenarios.values()))
    }
    capas = []
    for plano in linea.planos:
        imagen = imagen_del_plano(carpeta, plano.id)
        if imagen is None:
            imagen = f"{CARTELES}/{plano.id}.svg"
            escenario = escenarios[plano.id]
            (carpeta / imagen).parent.mkdir(parents=True, exist_ok=True)
            (carpeta / imagen).write_text(_cartel(plano.id, escenario, colores[escenario]), encoding="utf-8")
        capas.append(
            f'      <img id="plano-{escape(plano.id)}" class="clip plano" src="{escape(imagen)}" '
            f'{_tiempos(plano.inicio, plano.final, linea.fps)} data-track-index="2" alt="" />'
        )
    return capas


def _cartel(plano: str, escenario: str, color: str) -> str:
    """El cartel del plano: su número y su escenario sobre un color liso, en una imagen SVG de 1080x1920."""
    return _CARTEL.substitute(
        ancho=ANCHO,
        alto=ALTO,
        centro=ANCHO // 2,
        color=color,
        id=escape(plano),
        escenario=escape(escenario),
        # Más pequeño cuanto más largo, para que quepa a lo ancho.
        tamano_del_id=min(300, 1500 // len(plano)),
        tamano_del_escenario=min(80, 1500 // len(escenario)),
    )


def _capa_de_sonido(pista: Pista, fps: int) -> str:
    """Una capa de audio de música (pista 4) o de efecto (pista 5)."""
    recorte = f' data-media-start="{pista.recorte:.6f}"' if pista.recorte > 0 else ""
    return (
        f'      <audio id="{pista.id}" class="clip" src="{escape(pista.archivo)}" '
        f'{_tiempos(pista.inicio, pista.final, fps)}{recorte} '
        f'data-track-index="{pista.pista}" data-volume="{pista.volumen:.6f}"></audio>'
    )


def _cierre(carpeta: Path, cta: Tramo, fps: int, app: App) -> list[str]:
    """El cierre del CTA: el logo de la App (copiado en la carpeta del episodio, o su marcador) y su nombre."""
    logo = f"{COPIA_DEL_LOGO}{app.logo.suffix.lower()}" if app.logo else MARCADOR_DEL_LOGO
    (carpeta / logo).parent.mkdir(parents=True, exist_ok=True)
    if app.logo:
        shutil.copyfile(app.logo, carpeta / logo)
    else:
        (carpeta / logo).write_text(_MARCADOR_DEL_LOGO, encoding="utf-8")
    return [
        f'      <div id="cierre-del-cta" class="clip" {_tiempos(cta.inicio, cta.final, fps)} data-track-index="3">',
        f'        <div class="cierre Tutor"><img class="logo" src="{escape(logo)}" alt="" />'
        f'<p class="nombre">{escape(app.nombre)}</p></div>',
        "      </div>",
    ]


def _en_segundos(fotogramas: int, fps: int) -> str:
    return f"{fotogramas / fps:.6f}".rstrip("0").rstrip(".")


def _tiempos(inicio: int, final: int, fps: int) -> str:
    """Los atributos de tiempo de una capa de HyperFrames, en segundos."""
    return f'data-start="{_en_segundos(inicio, fps)}" data-duration="{_en_segundos(final - inicio, fps)}"'


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
    orden = [npx, "--yes", hyperframes.HYPERFRAMES, "render", ".", "--output", VIDEO, "--quality", "draft", "--strict", "--quiet"]
    proceso = subprocess.run(orden, cwd=carpeta, check=False)
    if proceso.returncode != 0 or not salida.is_file():
        return [
            f"HyperFrames no ha podido renderizar el vídeo (terminó con el código {proceso.returncode}). "
            "El motivo está en sus mensajes, encima de este."
        ]
    return []
