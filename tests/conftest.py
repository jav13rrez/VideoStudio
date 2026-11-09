import shutil
from pathlib import Path

import pytest

from ayudas import APP, BIBLIOTECA, CONFIGURACION, EJEMPLO, Estudio, Resultado, leer_salida
from estudio.cli import main


@pytest.fixture
def episodio(tmp_path: Path) -> Path:
    """Una copia de la carpeta de ejemplo, con la configuración, la biblioteca y la App de los tests encima."""
    carpeta = tmp_path / EJEMPLO.name
    shutil.copytree(EJEMPLO, carpeta)
    shutil.copy(CONFIGURACION, tmp_path / CONFIGURACION.name)
    shutil.copytree(BIBLIOTECA, tmp_path / BIBLIOTECA.name)
    shutil.copytree(APP, tmp_path / APP.name)
    return carpeta


@pytest.fixture
def estudio(capsys: pytest.CaptureFixture[str]) -> Estudio:
    def _estudio(orden: str, carpeta: Path) -> Resultado:
        codigo = main([orden, str(carpeta)])
        return leer_salida(codigo, capsys.readouterr().out)

    return _estudio
