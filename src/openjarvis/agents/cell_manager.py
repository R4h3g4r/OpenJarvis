import re
import traceback
import json
from openjarvis.agents.orchestrator import OrchestratorAgent
from openjarvis.agents.prompt_loader import load_system_prompt_override
from openjarvis.tools.file_tool import WriteFileTool

class DevelopmentCellManager:
    def __init__(self, engine, models_config: dict):
        self.engine = engine
        self.write_tool = WriteFileTool()
        
        # Instanciación de los 4 agentes
        self.agents = {
            "architect": OrchestratorAgent(
                engine, models_config["architect"], mode="structured", 
                system_prompt=load_system_prompt_override("architect")
            ),
            "dev": OrchestratorAgent(
                engine, models_config["dev"], tools=[self.write_tool], mode="structured", 
                system_prompt=load_system_prompt_override("dev")
            ),
            "qa": OrchestratorAgent(
                engine, models_config["qa"], mode="structured", 
                system_prompt=load_system_prompt_override("qa")
            ),
            "doc": OrchestratorAgent(
                engine, models_config["doc"], tools=[self.write_tool], mode="structured", 
                system_prompt=load_system_prompt_override("doc")
            )
        }

    def _slugify(self, text):
        return re.sub(r'[^a-z0-9]+', '_', text.lower().strip())

    def _extract_and_save_code(self, content):
        """Rescate robusto: Busca bloques de código markdown y filtra instrucciones basura."""
        # Busca cualquier bloque de código markdown (python, bash o sin etiqueta)
        match = re.search(r"```[a-z]*\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
        
        if match:
            code = match.group(1).strip()
            # Filtro de seguridad: descarta si el modelo alucina instrucciones en lugar de código
            if len(code) > 10 and not any(phrase in code.lower() for phrase in ["tu respuesta debe", "aquí tienes", "instrucciones"]):
                print(f"[!!!] Rescatando {len(code)} caracteres de código real...")
                self.write_tool.execute(filename="app.py", content=code)
                return True
        
        print("[DEBUG] No se encontró bloque de código válido o el bloque parece instrucción.")
        return False

    def run_development_cycle(self, user_request: str):
        project_name = self._slugify(user_request)
        self.write_tool.project_folder = project_name
        
        print(f"\n[DEBUG] Iniciando ciclo para: {project_name}")
        
        try:
            # 1. Arquitecto
            print("[DEBUG] Arquitecto trabajando...")
            arch_res = self.agents["architect"].run(f"Diseña: {user_request}")
            print(f"--- Diseño ---\n{arch_res.content[:200]}...")
            
            # 2. Dev con red de seguridad
            print("[DEBUG] Dev trabajando...")
            dev_res = self.agents["dev"].run(f"Implementa: {arch_res.content}")
            
            # IMPRESIÓN CRUDA PARA DEBUG (útil para ver qué está enviando realmente el modelo)
            print(f"\n--- [DEBUG] RESPUESTA CRUDA DEL DEV ---\n{dev_res.content[:500]}...\n--------------------------------")
            
            # Rescate manual si la herramienta falló
            if not self._extract_and_save_code(dev_res.content):
                print("[DEBUG] El Dev no usó la herramienta ni escribió bloques de código válidos.")

            # 3. QA
            print("[DEBUG] QA trabajando...")
            qa_res = self.agents["qa"].run(f"Audita:\n{dev_res.content}")
            
            # 4. Doc
            print("[DEBUG] Documentador trabajando...")
            doc_res = self.agents["doc"].run(f"Documenta el desarrollo del proyecto {project_name}.")
            
            return {"arch": arch_res, "dev": dev_res, "qa": qa_res, "doc": doc_res}

        except Exception as e:
            print("\n[!!!] ERROR DETECTADO:")
            traceback.print_exc()
            return None