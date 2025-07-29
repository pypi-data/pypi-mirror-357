"""Configuración de ruta para las pruebas del nivel bajo."""
from pathlib import Path
import sys

p = Path(__file__).resolve()
for ancestor in p.parents:
    if ancestor.name == "holobit_sdk":
        sys.path.insert(0, str(ancestor))
        break
