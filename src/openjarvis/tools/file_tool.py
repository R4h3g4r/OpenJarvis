import os
from types import SimpleNamespace
from openjarvis.tools._stubs import BaseTool
from openjarvis.core.types import ToolResult

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Guarda el código generado en workspace/<proyecto>/."
    
    # Nuevo atributo para saber dónde guardar
    project_folder = "default"

    @property
    def spec(self):
        return SimpleNamespace(
            name=self.name,
            description=self.description,
            requires_confirmation=False,
            timeout_seconds=30.0,
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        )

    def execute(self, filename: str, content: str) -> ToolResult:
        # Creamos la ruta: workspace/nombre_proyecto/
        target_dir = os.path.join("workspace", self.project_folder)
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, filename)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return ToolResult(
            tool_name=self.name, 
            content=f"ÉXITO: {filename} guardado en {target_dir}", 
            success=True
        )