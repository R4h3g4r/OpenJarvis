import os

files_to_fix = [
    "src/openjarvis/core/config.py",
    "src/openjarvis/intelligence/model_catalog.py",
    "src/openjarvis/cli/deep_research_setup_cmd.py",
    "src/openjarvis/cli/channels_cmd.py"
]

for filepath in files_to_fix:
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Reemplazamos qwen3.5:4b por qwen2.5:3b (el que descargaste)
        new_content = content.replace("qwen3.5:4b", "qwen2.5:3b")
        
        with open(filepath, 'w') as file:
            file.write(new_content)
        print(f"✅ Arreglado: {filepath}")
    except Exception as e:
        print(f"❌ Error en {filepath}: {e}")