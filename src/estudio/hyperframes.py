"""HyperFrames, llamado como programa externo con npx en la versión fijada del estudio (docs/montaje.md)."""

import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path

# Versión fijada: HyperFrames saca versiones casi a diario, y un cambio suyo no debe cambiar los episodios.
HYPERFRAMES = "hyperframes@0.9.26"


class ErrorDeHyperFrames(Exception):
    pass


def ejecutar(argumentos: list[str], carpeta: Path, entorno: Mapping[str, str] | None = None) -> None:
    """Ejecuta una orden de HyperFrames dentro de la carpeta, sin enseñar sus mensajes salvo si falla.

    Las rutas van relativas a la carpeta: en Windows, npx pasa por cmd.exe, que malinterpreta rutas con & o %.
    """
    npx = shutil.which("npx")
    if npx is None:
        raise ErrorDeHyperFrames(
            "no encuentro npx, que viene con Node.js: hace falta instalar Node.js 22 o más nuevo "
            "(https://nodejs.org) y volver a intentarlo."
        )
    orden = [npx, "--yes", HYPERFRAMES, *argumentos]
    proceso = subprocess.run(orden, cwd=carpeta, env=entorno, capture_output=True, text=True, check=False)
    if proceso.returncode != 0:
        mensajes = [linea for linea in (proceso.stdout + proceso.stderr).splitlines() if linea.strip()]
        motivo = mensajes[-1].strip() if mensajes else "sin mensajes"
        raise ErrorDeHyperFrames(f"HyperFrames terminó con el código {proceso.returncode} ({motivo}).")
