"""Dibujar los planos en 2D: el escenario, las poses del reparto y la sombra de contacto, sin pasar por Blender.

Por ahora solo planos de cámara fija con un personaje, que dejan una sola imagen (planos/<id>.png, de 1080x1920).
Nada se dibuja a medias: si algo falla, la orden da todos los errores y no escribe ninguna imagen. El formato y las
reglas están en docs/dibujo-2d.md y docs/estilo-2d.md.
"""

import shutil
from pathlib import Path

from PIL import Image, ImageDraw

from estudio.configuracion import Configuracion
from estudio.cronometraje import LineaDeTiempo, PlanoCronometrado
from estudio.escenarios import ALTO, ANCHO, NOMBRES, Escenario, dibujar_escenario
from estudio.planos import Plano
from estudio.poses import Pose, cargar_pose
from estudio.renderizar_planos import CARPETA, FOTOGRAMAS, elegir
from estudio.reparto import ARCHIVO as ARCHIVO_DE_REPARTO
from estudio.reparto import Reparto, leer_reparto
from estudio.tomas import FIJA, camaras_de_los_planos

ESCALA = 0.66  # de las ilustraciones: todas se dibujan con la misma convención de píxeles por metro
_SOBRA_DE_LA_SOMBRA = 20  # lo que la sombra de contacto sobresale a cada lado de la silueta


def dibujar_planos(
    carpeta: Path,
    linea: LineaDeTiempo,
    planos: list[Plano],
    configuracion: Configuracion,
    seleccion: str | None,
    fotogramas: str | None,
) -> list[str]:
    """Dibuja los planos elegidos (todos, si no se elige ninguno); devuelve los errores que lo impiden."""
    if not planos:
        return ["El episodio no tiene lista de planos (planos.toml): no hay nada que dibujar."]
    elegidos, errores = elegir(linea, seleccion)
    if errores:
        return errores
    repartos, errores = leer_reparto(carpeta, {plano.id for plano in planos})
    escenarios = {plano.id: plano.escenario for plano in planos}
    camaras = camaras_de_los_planos(carpeta)
    poses: dict[str, tuple[Pose | None, list[str]]] = {}
    for plano in elegidos:
        errores += _errores_del_plano(plano, escenarios, camaras, repartos, configuracion, poses, fotogramas)
    if errores:
        return errores
    for plano in elegidos:
        pose = _pose_del_plano(repartos[plano.id], poses)
        _guardar(carpeta, plano.id, _componer(_escenario(escenarios[plano.id]), pose))
    return []


def _errores_del_plano(
    plano: PlanoCronometrado,
    escenarios: dict[str, str],
    camaras: dict[str, str],
    repartos: dict[str, Reparto],
    configuracion: Configuracion,
    poses: dict[str, tuple[Pose | None, list[str]]],
    fotogramas: str | None,
) -> list[str]:
    id_ = plano.id
    if id_ not in repartos:
        return [f"El plano «{id_}» no tiene reparto en {ARCHIVO_DE_REPARTO}: faltan las poses de sus personajes."]
    errores = []
    if camaras[id_] != FIJA:
        errores.append(
            f"El plano «{id_}» no es de cámara fija ({camaras[id_]}): por ahora el dibujo 2D solo hace planos de cámara fija."
        )
    if escenarios[id_] not in NOMBRES:
        errores.append(
            f"El plano «{id_}» usa el escenario «{escenarios[id_]}», que no tiene receta 2D; "
            f"los que hay: {', '.join(sorted(NOMBRES))}."
        )
    if fotogramas is not None:
        errores.append(f"El plano «{id_}» es una sola imagen: no tiene rango de fotogramas, se dibuja entero.")
    nombres = repartos[id_].poses
    if len(nombres) > 1:
        errores.append(
            f"El plano «{id_}» lleva {len(nombres)} personajes y por ahora el dibujo 2D dibuja un solo personaje por plano."
        )
    for nombre in nombres:
        if nombre not in poses:
            poses[nombre] = cargar_pose(configuracion.biblioteca, nombre)
        pose, de_la_pose = poses[nombre]
        errores += [f"Plano «{id_}»: {error}" for error in de_la_pose]
        if pose is not None and not _cabe(pose, escenarios[id_]):
            errores.append(f"Plano «{id_}»: la pose «{nombre}» no cabe en el plano, es más grande que la imagen.")
    return errores


def _pose_del_plano(reparto: Reparto, poses: dict[str, tuple[Pose | None, list[str]]]) -> Pose | None:
    return poses[reparto.poses[0]][0] if reparto.poses else None


def _escenario(nombre: str) -> Escenario:
    escenario = dibujar_escenario(nombre)
    assert escenario is not None, f"el escenario «{nombre}» se comprueba antes de dibujar"
    return escenario


def _donde_va(pose: Pose, suelo_y: int) -> tuple[int, int]:
    """La esquina de la ilustración escalada: la silueta centrada en la imagen y lo que apoya, en la línea de suelo."""
    izquierda, _, derecha, _ = pose.silueta
    return round(ANCHO / 2 - (izquierda + derecha) / 2 * ESCALA), round(suelo_y - pose.suelo * ESCALA)


def _cabe(pose: Pose, escenario: str) -> bool:
    """Si la silueta, ya escalada y colocada, queda dentro de la imagen."""
    receta = dibujar_escenario(escenario)
    if receta is None:
        return True  # el escenario sin receta ya da su propio error
    x, y = _donde_va(pose, receta.suelo_y)
    izquierda, arriba, derecha, _ = pose.silueta
    return x + izquierda * ESCALA >= 0 and x + derecha * ESCALA <= ANCHO and y + arriba * ESCALA >= 0


def _componer(escenario: Escenario, pose: Pose | None) -> Image.Image:
    """El plano: el escenario, la sombra de contacto y la pose apoyada en la línea de suelo."""
    imagen = escenario.fondo.copy()
    if pose is None:
        return imagen.convert("RGB")
    izquierda, _, derecha, _ = pose.silueta
    figura = pose.ilustracion.resize(
        (round(pose.ilustracion.width * ESCALA), round(pose.ilustracion.height * ESCALA)), Image.Resampling.LANCZOS
    )
    mitad = round((derecha - izquierda) * ESCALA / 2) + _SOBRA_DE_LA_SOMBRA
    imagen = Image.alpha_composite(imagen, _sombra(ANCHO // 2, escenario.suelo_y, mitad))
    imagen.paste(figura, _donde_va(pose, escenario.suelo_y), figura)
    return imagen.convert("RGB")


def _sombra(centro: int, suelo: int, mitad: int) -> Image.Image:
    capa = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    ImageDraw.Draw(capa).ellipse((centro - mitad, suelo - 16, centro + mitad, suelo + 26), fill=(20, 60, 20, 90))
    return capa


def _guardar(carpeta: Path, id_: str, imagen: Image.Image) -> None:
    """Deja planos/<id>.png y quita lo de la vez anterior (el vídeo y los fotogramas), que ya no vale."""
    base = carpeta / CARPETA
    base.mkdir(exist_ok=True)
    (base / f"{id_}.mp4").unlink(missing_ok=True)
    shutil.rmtree(base / FOTOGRAMAS / id_, ignore_errors=True)
    imagen.save(base / f"{id_}.png", format="PNG")
