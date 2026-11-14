"""Dibujar los planos en 2D: el escenario, las poses del reparto y la sombra de contacto, sin pasar por Blender.

Por ahora solo planos de cámara fija con uno o dos personajes (en fila, de izquierda a derecha), que dejan una sola
imagen (planos/<id>.png, de 1080x1920).
Nada se dibuja a medias: si algo falla, la orden da todos los errores y no escribe ninguna imagen. El formato y las
reglas están en docs/dibujo-2d.md y docs/estilo-2d.md.
"""

import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from estudio.configuracion import Configuracion
from estudio.cronometraje import LineaDeTiempo, PlanoCronometrado
from estudio.escenarios import ALTO, ANCHO, NOMBRES, Escenario, dibujar_escenario, dibujar_roca
from estudio.planos import Plano
from estudio.poses import Pose, cargar_pose
from estudio.renderizar_planos import CARPETA, FOTOGRAMAS, elegir
from estudio.reparto import ARCHIVO as ARCHIVO_DE_REPARTO
from estudio.reparto import Reparto, leer_reparto
from estudio.tomas import FIJA, camaras_de_los_planos

ESCALA = 0.66  # de las ilustraciones: todas se dibujan con la misma convención de píxeles por metro
ESCALA_MINIMA = 0.45  # hasta donde se reducen juntos dos personajes que no caben a lo ancho; por debajo, la orden no dibuja
SEPARACION = 20  # píxeles de imagen entre las siluetas de dos personajes en fila
MAXIMO_DE_PERSONAJES = 2
_SOBRA_DE_LA_SOMBRA = 20  # lo que la sombra de contacto sobresale a cada lado de la silueta
HUNDIMIENTO = 10  # lo que el techo de la roca queda por encima del asiento: el cuerpo va algo hundido en ella
ROCA_DETRAS = 60  # lo que la roca sobresale por detrás de la espalda, para que se vea


@dataclass(frozen=True)
class Roca:
    """La roca bajo una pose sentada: sus columnas y la fila de su techo; su base es la línea de suelo."""

    izquierda: int
    derecha: int
    techo: int


@dataclass(frozen=True)
class Colocada:
    """Una pose ya colocada en el plano."""

    pose: Pose
    escala: float
    esquina: tuple[int, int]  # de la ilustración escalada
    centro: int  # columna del centro de su silueta, donde cae su sombra
    roca: Roca | None = None  # solo las poses sentadas

    @property
    def mitad(self) -> int:
        """La mitad del ancho de su silueta, ya escalada."""
        izquierda, _, derecha, _ = self.pose.silueta
        return round((derecha - izquierda) * self.escala / 2)


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
        escenario = _escenario(escenarios[plano.id])
        colocadas = _colocar(_poses_cargadas(repartos[plano.id].poses, poses), escenario.suelo_y)
        assert colocadas is not None, "que caben se comprueba antes de dibujar"
        _guardar(carpeta, plano.id, _componer(escenario, colocadas))
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
    if len(nombres) > MAXIMO_DE_PERSONAJES:
        errores.append(
            f"El plano «{id_}» lleva {len(nombres)} personajes y por ahora el dibujo 2D dibuja hasta dos personajes por plano."
        )
        return errores
    for nombre in nombres:
        if nombre not in poses:
            poses[nombre] = cargar_pose(configuracion.biblioteca, nombre)
        errores += [f"Plano «{id_}»: {error}" for error in poses[nombre][1]]
    cargadas = _poses_cargadas(nombres, poses)
    receta = dibujar_escenario(escenarios[id_])
    if receta is not None and len(cargadas) == len(nombres) and _colocar(cargadas, receta.suelo_y) is None:
        errores.append(_no_caben(id_, nombres))
    return errores


def _poses_cargadas(nombres: tuple[str, ...], poses: dict[str, tuple[Pose | None, list[str]]]) -> list[Pose]:
    """Las poses que se han podido cargar, en el orden del reparto."""
    return [pose for nombre in nombres if (pose := poses[nombre][0]) is not None]


def _no_caben(id_: str, nombres: tuple[str, ...]) -> str:
    if len(nombres) == 1:
        return f"Plano «{id_}»: la pose «{nombres[0]}» no cabe en el plano, es más grande que la imagen."
    return (
        f"Plano «{id_}»: las poses {' y '.join(f'«{nombre}»' for nombre in nombres)} no caben juntas en el plano, "
        "ni siquiera reducidas a la escala mínima."
    )


def _escenario(nombre: str) -> Escenario:
    escenario = dibujar_escenario(nombre)
    assert escenario is not None, f"el escenario «{nombre}» se comprueba antes de dibujar"
    return escenario


def _colocar(poses: list[Pose], suelo_y: int) -> list[Colocada] | None:
    """Las poses en fila, de izquierda a derecha, a una misma escala y con lo que apoya en la línea de suelo.

    La silueta (la cola incluida) de cada una guarda la separación fija con la vecina y el grupo queda centrado. Si no
    caben a lo ancho a la escala normal, se reducen juntas, hasta la escala mínima; una sola pose no se reduce. Si no
    caben, o sobresalen por arriba, devuelve None.
    """
    if not poses:
        return []
    anchos = [pose.silueta[2] - pose.silueta[0] for pose in poses]
    libre = ANCHO - SEPARACION * (len(poses) - 1)
    escala = min(ESCALA, libre / sum(anchos))
    if escala < (ESCALA_MINIMA if len(poses) > 1 else ESCALA):
        return None
    if any((pose.suelo - pose.silueta[1]) * escala > suelo_y for pose in poses):
        return None
    izquierda = (ANCHO - (sum(anchos) * escala + SEPARACION * (len(poses) - 1))) / 2
    colocadas = []
    for pose, ancho in zip(poses, anchos, strict=True):
        colocadas.append(
            Colocada(
                pose,
                escala,
                (round(izquierda - pose.silueta[0] * escala), round(suelo_y - pose.suelo * escala)),
                round(izquierda + ancho * escala / 2),
                _roca(pose, izquierda, ancho * escala, suelo_y, escala),
            )
        )
        izquierda += ancho * escala + SEPARACION
    return colocadas


def _roca(pose: Pose, izquierda: float, ancho: float, suelo_y: int, escala: float) -> Roca | None:
    """La roca de una pose sentada: centrada en su trasero, con roca detrás de la espalda y el techo sobre el asiento.

    `izquierda` y `ancho` son los de la silueta ya escalada. La roca no pasa por delante de la silueta.
    """
    if pose.asiento is None or pose.trasero is None:
        return None
    espalda_al_trasero = pose.trasero * ancho
    centro = izquierda + espalda_al_trasero
    mitad = espalda_al_trasero + ROCA_DETRAS
    return Roca(
        round(centro - mitad),
        round(min(centro + mitad, izquierda + ancho)),
        round(suelo_y - pose.asiento * escala) - HUNDIMIENTO,
    )


def _componer(escenario: Escenario, colocadas: list[Colocada]) -> Image.Image:
    """El plano: el escenario, la sombra de contacto de cada una y las poses apoyadas en la línea de suelo."""
    imagen = escenario.fondo.copy()
    for colocada in colocadas:
        imagen = Image.alpha_composite(
            imagen, _sombra(colocada.centro, escenario.suelo_y, colocada.mitad + _SOBRA_DE_LA_SOMBRA)
        )
        if colocada.roca is not None:
            roca = colocada.roca
            imagen = Image.alpha_composite(
                imagen,
                _sombra(
                    (roca.izquierda + roca.derecha) // 2, escenario.suelo_y, (roca.derecha - roca.izquierda) // 2 + _SOBRA_DE_LA_SOMBRA
                ),
            )
    for roca in (c.roca for c in colocadas if c.roca is not None):
        base = dibujar_roca(roca.derecha - roca.izquierda, escenario.suelo_y - roca.techo)
        imagen.paste(base, (roca.izquierda, roca.techo), base)
    for colocada in colocadas:
        ilustracion = colocada.pose.ilustracion
        figura = ilustracion.resize(
            (round(ilustracion.width * colocada.escala), round(ilustracion.height * colocada.escala)),
            Image.Resampling.LANCZOS,
        )
        imagen.paste(figura, colocada.esquina, figura)
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
