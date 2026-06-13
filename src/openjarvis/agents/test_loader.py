from pathlib import Path
from prompt_loader import load_system_prompt_override
import os

# Verificación manual de qué está haciendo la función
home = Path(os.environ.get("OPENJARVIS_HOME", "~/.openjarvis")).expanduser()
print(f"DEBUG: El loader está buscando en: {home / 'agents' / 'architect' / 'system_prompt.md'}")

prompt = load_system_prompt_override("architect")
if prompt:
    print("¡Éxito! El sistema cargó el prompt.")
else:
    print("El sistema no encontró el archivo en la ruta de arriba.")