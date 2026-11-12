"""Se ejecuta DENTRO de Blender: blender -b --python render_toma.py -- trabajo.json

Por cada plano del trabajo: abre el escenario de la biblioteca, trae los personajes y objetos de su toma, pone la
cámara y renderiza los fotogramas pedidos con EEVEE. Lo escribe la herramienta del estudio (renderizar_planos.py);
el formato del trabajo y de las tomas está en docs/tomas.md.
"""

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

LENTE = 40.0  # mm
SENSOR = 36.0  # mm, a lo largo del lado mayor de la imagen (el vertical, en 1080x1920)
FORMATO = 1080 / 1920
ANCHO_DEL_SENSOR = SENSOR * FORMATO  # lo que cuenta en horizontal
APERTURA = 2.8  # como los escenarios de la biblioteca: profundidad de campo enfocada en el punto al que mira


def main() -> None:
    trabajo = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
    for plano in trabajo["planos"]:
        renderizar_plano(trabajo, plano)


def renderizar_plano(trabajo: dict, plano: dict) -> None:
    bpy.ops.wm.open_mainfile(filepath=plano["blend"])
    escena = bpy.context.scene
    toma = plano["toma"]
    for colocacion in toma["personajes"]:
        colocar(escena, trabajo["biblioteca"], "personajes", colocacion)
    for colocacion in toma["objetos"]:
        colocar(escena, trabajo["biblioteca"], "objetos", colocacion)
    camara = crear_camara(escena)
    configurar_render(escena, plano)
    fotogramas = [0] if plano["fija"] else range(plano["desde"], plano["hasta"] + 1)
    for numero in fotogramas:
        avance = 0.0 if plano["fija"] or plano["duracion"] < 2 else numero / (plano["duracion"] - 1)
        poner_camara(camara, vista_en(toma, avance))
        destino = plano["imagen"] if plano["fija"] else str(Path(plano["fotogramas"]) / f"{numero:04d}.png")
        escena.render.filepath = destino
        bpy.ops.render.render(write_still=True)
        print(f"plano {plano['id']}: fotograma {numero} -> {destino}")


def colocar(escena: bpy.types.Scene, biblioteca: str, tipo: str, colocacion: dict) -> None:
    """Trae una pieza de la biblioteca (un personaje o un objeto) y la pone donde dice la toma."""
    pieza = colocacion["pieza"]
    nombre = pieza.split("_")[0]
    archivo = str(Path(biblioteca) / tipo / nombre / f"{nombre}.blend")
    prefijo = "PERSONAJE_" if tipo == "personajes" else "OBJETO_"
    with bpy.data.libraries.load(archivo, link=False) as (origen, destino):
        destino.collections = [c for c in origen.collections if c == prefijo + nombre]
    if not destino.collections:
        raise SystemExit(f"La biblioteca no tiene la colección {prefijo + nombre} en {archivo}.")
    coleccion = destino.collections[0]
    escena.collection.children.link(coleccion)
    raiz = next((o for o in coleccion.objects if o.parent is None and o.name.startswith(pieza)), None)
    if raiz is None:
        raise SystemExit(f"No hay la pieza «{pieza}» en {archivo}.")
    propias = {raiz, *raiz.children_recursive}
    for objeto in list(coleccion.objects):
        if objeto not in propias:
            bpy.data.objects.remove(objeto, do_unlink=True)
    raiz.location = Vector(colocacion["en"])
    if colocacion["espejo"]:
        raiz.scale.x = -1
    for propiedad, clave in (("ojos", "ojos_nombres"), ("boca", "boca_nombres")):
        elegido = colocacion.get(propiedad)
        if elegido is None:
            continue
        nombres = list(raiz.get(clave, []))
        if elegido not in nombres:
            raise SystemExit(f"«{pieza}» no tiene {propiedad} «{elegido}»; tiene {', '.join(nombres)}.")
        raiz[propiedad] = nombres.index(elegido)
    bpy.context.view_layer.update()


def crear_camara(escena: bpy.types.Scene) -> bpy.types.Object:
    datos = bpy.data.cameras.new("cam_toma")
    datos.lens = LENTE
    datos.sensor_width = SENSOR
    datos.sensor_fit = "AUTO"
    datos.dof.use_dof = True
    datos.dof.aperture_fstop = APERTURA
    camara = bpy.data.objects.new("cam_toma", datos)
    escena.collection.objects.link(camara)
    escena.camera = camara
    return camara


def configurar_render(escena: bpy.types.Scene, plano: dict) -> None:
    escena.render.engine = "BLENDER_EEVEE"
    escena.render.resolution_x = plano["ancho_px"]
    escena.render.resolution_y = plano["alto_px"]
    escena.render.resolution_percentage = 100
    escena.render.image_settings.file_format = "PNG"
    escena.render.image_settings.color_mode = "RGB"
    escena.eevee.taa_render_samples = plano["muestras"]


def vista_en(toma: dict, avance: float) -> dict:
    """La vista de la cámara cuando ha avanzado `avance` (de 0 a 1) del movimiento, suavizado al principio y al final."""
    if toma["hasta"] is None:
        return toma
    t = avance * avance * (3 - 2 * avance)
    desde, hasta = toma, toma["hasta"]
    return {
        "mira": [a + (b - a) * t for a, b in zip(desde["mira"], hasta["mira"])],
        "ancho": desde["ancho"] + (hasta["ancho"] - desde["ancho"]) * t,
        "azimut": desde["azimut"] + (hasta["azimut"] - desde["azimut"]) * t,
        "elevacion": desde["elevacion"] + (hasta["elevacion"] - desde["elevacion"]) * t,
    }


def poner_camara(camara: bpy.types.Object, vista: dict) -> None:
    """Coloca la cámara mirando al punto, a la distancia a la que caben `ancho` metros a lo ancho."""
    distancia = vista["ancho"] * LENTE / ANCHO_DEL_SENSOR
    azimut, elevacion = math.radians(vista["azimut"]), math.radians(vista["elevacion"])
    mira = Vector(vista["mira"])
    camara.location = mira + distancia * Vector(
        (math.sin(azimut) * math.cos(elevacion), -math.cos(azimut) * math.cos(elevacion), math.sin(elevacion))
    )
    camara.rotation_euler = (mira - camara.location).to_track_quat("-Z", "Y").to_euler()
    camara.data.dof.focus_distance = distancia


main()
