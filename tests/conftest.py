import shutil
from pathlib import Path

import pytest

from ayudas import CONFIGURACION, EJEMPLO


@pytest.fixture
def episodio(tmp_path: Path) -> Path:
    """Una copia de la carpeta de ejemplo, con la configuración del estudio de los tests encima."""
    carpeta = tmp_path / EJEMPLO.name
    shutil.copytree(EJEMPLO, carpeta)
    shutil.copy(CONFIGURACION, tmp_path / CONFIGURACION.name)
    return carpeta
