"""Configuración de ruta para las pruebas unitarias."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'holobit_sdk'))
