"""Dibujar los planos en 2D: el escenario, las poses del reparto y la sombra de contacto, sin pasar por Blender.

Planos con uno o dos personajes (en fila, de izquierda a derecha). Un plano de cámara fija y sin línea en actuacion.toml
deja una sola imagen (planos/<id>.png, de 1080x1920); uno con línea y personajes, con la cámara en movimiento o en el
que habla el Tutor, deja un vídeo (planos/<id>.mp4, con un fotograma por fotograma de la línea de tiempo): los
personajes respiran, el Perro mueve las orejas y la cola con sus gestos y parpadea, el Tutor abre la mandíbula en sus
palabras acentuadas (movimiento_2d.py, boca_del_tutor.py), y la cámara recorta un lienzo 1,5 veces mayor con
acercamientos y desplazamientos (camara_2d.py).
Nada se dibuja a medias: si algo falla, la orden da todos los errores y no escribe ninguna imagen. El formato y las
reglas están en docs/dibujo-2d.md y docs/estilo-2d.md.
"""

import math
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from estudio.actuacion import ARCHIVO as ARCHIVO_DE_ACTUACION
from estudio.actuacion import DURACION_DEL_GESTO, DURACION_DEL_PARPADEO, Linea, angulo_en, es_del_tutor, leer_actuacion
from estudio.boca_del_tutor import Palabras, angulo_de_la_boca, palabras_acentuadas
from estudio.camara_2d import LIENZO, VISTA_ENTERA, comprobar, recorte, vista_en
from estudio.configuracion import Configuracion
from estudio.cronometraje import LineaDeTiempo, PlanoCronometrado
from estudio.escenarios import ALTO, ANCHO, NOMBRES, Escenario, dibujar_escenario, dibujar_roca
from estudio.movimiento_2d import cierre_del_ojo, estiramiento, pose_movida, premultiplicar
from estudio.planos import Plano
from estudio.poses import Pose, cargar_pose
from estudio.renderizar_planos import CARPETA, FOTOGRAMAS, componer_video, elegir
from estudio.reparto import ARCHIVO as ARCHIVO_DE_REPARTO
from estudio.reparto import Reparto, leer_reparto
from estudio.tomas import camaras_de_los_planos

ESCALA = 0.66  # de las ilustraciones: todas se dibujan con la misma convención de píxeles por metro
ESCALA_MINIMA = 0.45  # hasta donde se reducen juntos dos personajes que no caben a lo ancho; por debajo, la orden no dibuja
SEPARACION = 20  # píxeles de imagen entre las siluetas de dos personajes en fila
MAXIMO_DE_PERSONAJES = 2
_SOBRA_DE_LA_SOMBRA = 20  # lo que la sombra de contacto sobresale a cada lado de la silueta
HUNDIMIENTO = 10  # lo que el techo de la roca queda por encima del asiento: el cuerpo va algo hundido en ella
ROCA_DETRAS = 60  # lo que la roca sobresale por detrás de la espalda, para que se vea
FASES_DE_LA_RESPIRACION = (0.0, 1.3)  # de cada personaje, por orden en el plano: no respiran a la vez


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

    def ampliada(self, factor: float) -> "Colocada":
        """La misma colocación en un lienzo `factor` veces mayor."""
        roca = self.roca
        return Colocada(
            self.pose,
            self.escala * factor,
            (round(self.esquina[0] * factor), round(self.esquina[1] * factor)),
            round(self.centro * factor),
            Roca(round(roca.izquierda * factor), round(roca.derecha * factor), round(roca.techo * factor)) if roca else None,
        )


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
    actuadas, errores_de_actuacion = _leer_actuacion(carpeta, {plano.id for plano in planos})
    errores += errores_de_actuacion
    palabras = palabras_acentuadas(linea)
    poses: dict[str, tuple[Pose | None, list[str]]] = {}
    for plano in elegidos:
        errores += _errores_del_plano(plano, escenarios, camaras, repartos, configuracion, poses, fotogramas)
        if plano.id in actuadas and plano.id in repartos:
            errores += _errores_del_movimiento(plano, actuadas[plano.id], repartos[plano.id], poses)
    if any(_se_anima(plano, actuadas, repartos, poses, palabras) for plano in elegidos) and shutil.which("ffmpeg") is None:
        errores.append("No encuentro ffmpeg, que hace falta para componer el vídeo de los planos con movimiento.")
    if errores:
        return errores
    for plano in elegidos:
        escenario = _escenario(escenarios[plano.id])
        colocadas = _colocar(_poses_cargadas(repartos[plano.id].poses, poses), escenario.suelo_y)
        assert colocadas is not None, "que caben se comprueba antes de dibujar"
        if _se_anima(plano, actuadas, repartos, poses, palabras):
            errores = _dibujar_con_movimiento(
                carpeta, plano, escenario, colocadas, actuadas.get(plano.id), repartos[plano.id], palabras, linea.fps
            )
            if errores:
                return errores
        else:
            _guardar(carpeta, plano.id, _componer(escenario, colocadas))
    return []


def _leer_actuacion(carpeta: Path, ids_de_planos: set[str]) -> tuple[dict[str, Linea], list[str]]:
    """Las líneas de actuacion.toml por plano. El archivo es opcional: un plano sin línea no se mueve."""
    if not (carpeta / ARCHIVO_DE_ACTUACION).is_file():
        return {}, []
    return leer_actuacion(carpeta, ids_de_planos, [])


def _se_anima(
    plano: PlanoCronometrado,
    actuadas: dict[str, Linea],
    repartos: dict[str, Reparto],
    poses: dict[str, tuple[Pose | None, list[str]]],
    palabras: Palabras,
) -> bool:
    """Con la cámara en movimiento, con línea de actuación y algún personaje, o con el Tutor hablando, el plano es un vídeo."""
    if plano.id not in repartos:
        return False
    reparto = repartos[plano.id]
    return reparto.hasta is not None or (plano.id in actuadas and bool(reparto.poses)) or _habla_el_tutor(plano, reparto, poses, palabras)


def _habla_el_tutor(
    plano: PlanoCronometrado, reparto: Reparto, poses: dict[str, tuple[Pose | None, list[str]]], palabras: Palabras
) -> bool:
    """Si en el plano hay una palabra acentuada del Tutor y una pose suya con zona de boca que abrir."""
    con_boca = any(
        pose is not None and any(zona.parte == "boca" for zona in pose.zonas)
        for nombre in reparto.poses
        if es_del_tutor(nombre) and (pose := poses.get(nombre, (None, []))[0]) is not None
    )
    return con_boca and any(inicio < plano.final and final > plano.inicio for inicio, final in palabras)


def _errores_del_movimiento(
    plano: PlanoCronometrado, actuacion: Linea, reparto: Reparto, poses: dict[str, tuple[Pose | None, list[str]]]
) -> list[str]:
    """Lo que la actuación del plano pide y sus poses no pueden dar: zonas que no tienen, gestos y parpadeos que no caben."""
    id_, duracion = plano.id, plano.final - plano.inicio
    cargadas = {pose.nombre: pose for pose in _poses_cargadas(reparto.poses, poses)}
    errores = []
    for gesto in actuacion.gestos:
        if gesto.pieza not in reparto.poses:
            errores.append(f"Plano «{id_}»: el gesto es de «{gesto.pieza}», que no está en su reparto.")
        elif gesto.pieza in cargadas and not any(zona.parte == gesto.parte for zona in cargadas[gesto.pieza].zonas):
            errores.append(f"Plano «{id_}»: «{gesto.pieza}» no tiene {gesto.parte} que mover.")
        elif gesto.inicio + DURACION_DEL_GESTO > duracion:
            errores.append(
                f"Plano «{id_}»: el gesto de «{gesto.parte}» de «{gesto.pieza}» empieza en {gesto.inicio} y acaba en "
                f"{gesto.inicio + DURACION_DEL_GESTO}, y el plano tiene {duracion} fotogramas."
            )
    if actuacion.parpadeos and len(cargadas) == len(reparto.poses) and not any(pose.ojo for pose in cargadas.values()):
        errores.append(
            f"Plano «{id_}»: pide parpadeos, pero no tiene ojo ninguna de sus poses (la ficha lleva «ojo» con la caja del ojo)."
        )
    errores += [
        f"Plano «{id_}»: el parpadeo que empieza en {inicio} acaba en {inicio + DURACION_DEL_PARPADEO}, y el plano tiene {duracion} fotogramas."
        for inicio in actuacion.parpadeos
        if inicio + DURACION_DEL_PARPADEO > duracion
    ]
    return errores


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
    errores = comprobar(id_, camaras[id_], repartos[id_].desde, repartos[id_].hasta)
    if escenarios[id_] not in NOMBRES:
        errores.append(
            f"El plano «{id_}» usa el escenario «{escenarios[id_]}», que no tiene receta 2D; "
            f"los que hay: {', '.join(sorted(NOMBRES))}."
        )
    if fotogramas is not None:
        errores.append(f"El plano «{id_}» se dibuja entero: el dibujo 2D no hace rangos de fotogramas (--fotogramas).")
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
    imagen = _fondo(escenario, colocadas)
    for colocada in colocadas:
        ilustracion = colocada.pose.ilustracion
        figura = ilustracion.resize(
            (round(ilustracion.width * colocada.escala), round(ilustracion.height * colocada.escala)),
            Image.Resampling.LANCZOS,
        )
        imagen.paste(figura, colocada.esquina, figura)
    return imagen.convert("RGB")


def _fondo(escenario: Escenario, colocadas: list[Colocada], factor: float = 1.0) -> Image.Image:
    """Lo que no se mueve del plano: el escenario, las sombras de contacto y las rocas.

    Con `factor` mayor que 1 es el lienzo ampliado de la cámara: las `colocadas` ya vienen a ese tamaño."""
    imagen = escenario.fondo.copy() if factor == 1 else escenario.ampliado(factor)
    suelo, sobra = round(escenario.suelo_y * factor), round(_SOBRA_DE_LA_SOMBRA * factor)
    for colocada in colocadas:
        imagen = Image.alpha_composite(imagen, _sombra(colocada.centro, suelo, colocada.mitad + sobra, factor))
        if colocada.roca is not None:
            roca = colocada.roca
            imagen = Image.alpha_composite(
                imagen, _sombra((roca.izquierda + roca.derecha) // 2, suelo, (roca.derecha - roca.izquierda) // 2 + sobra, factor)
            )
    for roca in (c.roca for c in colocadas if c.roca is not None):
        base = dibujar_roca(roca.derecha - roca.izquierda, suelo - roca.techo, factor)
        imagen.paste(base, (roca.izquierda, roca.techo), base)
    return imagen


def _dibujar_con_movimiento(
    carpeta: Path,
    plano: PlanoCronometrado,
    escenario: Escenario,
    colocadas: list[Colocada],
    actuacion: Linea | None,
    reparto: Reparto,
    palabras: Palabras,
    fps: int,
) -> list[str]:
    """Deja planos/_fotogramas/<id>/ con un fotograma por fotograma del plano y el vídeo planos/<id>.mp4.

    Los personajes respiran, el Tutor abre la boca en sus palabras acentuadas y, si el plano tiene actuación, el Perro mueve
    sus zonas y parpadea. Con la cámara en movimiento, todo se compone en un lienzo mayor y cada fotograma es un recorte
    suyo, así que personajes y escenario se mueven juntos."""
    _limpiar(carpeta, plano.id)
    destino = carpeta / CARPETA / FOTOGRAMAS / plano.id
    destino.mkdir(parents=True)
    duracion = plano.final - plano.inicio
    factor = LIENZO if reparto.hasta is not None else 1.0
    colocadas = [c.ampliada(factor) for c in colocadas] if factor != 1 else colocadas
    suelo = round(escenario.suelo_y * factor)
    fondo = _fondo(escenario, colocadas, factor)
    premultiplicadas = {c.pose.nombre: premultiplicar(c.pose) for c in colocadas}
    gestos, parpadeos = (actuacion.gestos, actuacion.parpadeos) if actuacion else ((), ())
    for numero in range(duracion):
        caja = None if reparto.hasta is None else recorte(vista_en(reparto.desde or VISTA_ENTERA, reparto.hasta, numero, duracion), *fondo.size)
        region = (0, 0, *fondo.size) if caja is None else _region(caja, fondo.size)
        imagen = fondo.copy() if caja is None else fondo.crop(region)
        for orden, colocada in enumerate(colocadas):
            pose = colocada.pose
            angulos: dict[str, float] = {}
            for gesto in gestos:
                if gesto.pieza == pose.nombre:
                    angulos[gesto.parte] = angulos.get(gesto.parte, 0.0) + angulo_en(gesto, numero)
            if es_del_tutor(pose.nombre):
                angulos["boca"] = angulo_de_la_boca(plano.inicio + numero, palabras)
            ilustracion = pose_movida(pose, premultiplicadas[pose.nombre], angulos, cierre_del_ojo(numero, parpadeos))
            alto = round(ilustracion.height * colocada.escala * estiramiento(numero, FASES_DE_LA_RESPIRACION[orden], fps))
            figura = ilustracion.resize((round(ilustracion.width * colocada.escala), alto), Image.Resampling.LANCZOS)
            # se estira sobre la línea de suelo: lo que apoya se queda donde estaba
            arriba = suelo - round(pose.suelo * alto / ilustracion.height)
            imagen.paste(figura, (colocada.esquina[0] - region[0], arriba - region[1]), figura)
        if caja is not None:
            visto = (caja[0] - region[0], caja[1] - region[1], caja[2] - region[0], caja[3] - region[1])
            imagen = imagen.resize((ANCHO, ALTO), Image.Resampling.LANCZOS, box=visto)
        imagen.convert("RGB").save(destino / f"{numero:04d}.png", format="PNG", compress_level=1)
    return componer_video(carpeta, plano, fps)


def _region(caja: tuple[float, float, float, float], tamano: tuple[int, int]) -> tuple[int, int, int, int]:
    """Las filas y columnas enteras del lienzo que contienen la caja, para no copiar el lienzo entero en cada fotograma."""
    return (
        max(0, math.floor(caja[0])),
        max(0, math.floor(caja[1])),
        min(tamano[0], math.ceil(caja[2])),
        min(tamano[1], math.ceil(caja[3])),
    )


def _sombra(centro: int, suelo: int, mitad: int, factor: float = 1.0) -> Image.Image:
    capa = Image.new("RGBA", (round(ANCHO * factor), round(ALTO * factor)), (0, 0, 0, 0))
    ImageDraw.Draw(capa).ellipse(
        (centro - mitad, suelo - round(16 * factor), centro + mitad, suelo + round(26 * factor)), fill=(20, 60, 20, 90)
    )
    return capa


def _limpiar(carpeta: Path, id_: str) -> None:
    """Quita lo de la vez anterior (la imagen, el vídeo y los fotogramas), que ya no vale."""
    base = carpeta / CARPETA
    base.mkdir(exist_ok=True)
    (base / f"{id_}.png").unlink(missing_ok=True)
    (base / f"{id_}.mp4").unlink(missing_ok=True)
    shutil.rmtree(base / FOTOGRAMAS / id_, ignore_errors=True)


def _guardar(carpeta: Path, id_: str, imagen: Image.Image) -> None:
    """Deja planos/<id>.png y quita lo de la vez anterior (el vídeo y los fotogramas), que ya no vale."""
    _limpiar(carpeta, id_)
    imagen.save(carpeta / CARPETA / f"{id_}.png", format="PNG")
