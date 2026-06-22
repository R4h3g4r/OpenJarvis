import os
import sys
from openjarvis import Jarvis

def limpiar_codigo(contenido: str) -> str:
    # Elimina los backticks de apertura y cierre y la etiqueta 'python'
    limpio = contenido.replace("```python", "").replace("```", "").strip()
    return limpio

# ==========================================
# EL INPUT DEL PRODUCT OWNER / ORQUESTADOR
# ==========================================
# Esperamos 2 o 3 parámetros: [1] Ruta del proyecto, [2] Requerimiento, [3] Modelo base opcional
MODELO_BASE = "llama3.1:8b"
MODELO_CODIGO = "qwen2.5-coder:14b"

if len(sys.argv) > 2:
    RUTA_PROYECTO = sys.argv[1]
    REQUERIMIENTO = sys.argv[2]
    if len(sys.argv) > 3:
        MODELO_BASE = sys.argv[3]
else:
    # Fallback solo para pruebas si lo ejecutas a mano sin parámetros
    RUTA_PROYECTO = "/Users/will/Documents/OpenJarvis/OpenJarvis/workspace/erika_manicura/backend/"
    REQUERIMIENTO = "Prueba local: Agregar archivo database.py con SQLAlchemy para SQLite."

def run_software_factory(ruta: str, tarea: str, model_text: str = MODELO_BASE, model_code: str = MODELO_CODIGO):
    print(f"🚀 INICIANDO SPRINT AUTÓNOMO DE LA CÉLULA...")
    print(f"📂 Proyecto destino: {ruta}\n")
    
    # Instanciamos a Jarvis usando el SDK oficial (El motor, la memoria y la seguridad)
    with Jarvis() as j:
        
        # ==========================================
        # FASE 1: EL ARQUITECTO (El Estratega)
        # ==========================================
        print("🏗️  Fase 1: El Arquitecto está diseñando el Blueprint...")
        prompt_arquitecto = f"""
        Eres el Arquitecto de Software Senior. 
        RUTA ABSOLUTA DEL PROYECTO: {ruta}
        
        TAREA DE NEGOCIO: {tarea}
        
        ENTREGABLE: Escribe un plan técnico detallado. Por cada archivo requerido, 
        indica la ruta exacta (usando la RUTA ABSOLUTA DEL PROYECTO como base) y el bloque de código completo que debe contener. 
        NO uses herramientas de sistema. Solo entrega el texto del diseño estructurado.
        """
        
        # El Arquitecto piensa y devuelve texto puro
        plan_arquitecto = j.ask(prompt_arquitecto, model=model_text)
        print("✅ Blueprint generado exitosamente.\n")
        # ==========================================
        # FASE 2: EL DEVELOPER (El Músculo)
        # ==========================================
        print("👨‍💻 Fase 2: El Developer está escribiendo los archivos en disco...")
        
        prompt_dev = f"""
        Eres un Developer backend. Tu objetivo es crear archivos dentro de la carpeta: {ruta}
        --- PLAN DEL ARQUITECTO ---
        {plan_arquitecto}
        --- FIN DEL PLAN ---
        
        REGLAS DE SALIDA:
        1. Invoca `file_write` con la RUTA COMPLETA: {ruta}nombre_del_archivo.
        2. PASA EL CÓDIGO PURO en el parámetro 'content'.
        3. NO incluyas markdown (```python o ```) en el contenido. Solo entrega el código fuente.
        """
        
        resultado_dev = j.ask_full(
            prompt_dev, 
            model=model_code, 
            agent="native_react", 
            tools=["file_write"]
        )
        
        # FILTRO DE SEGURIDAD INDUSTRIAL: Interceptamos la llamada antes de que sea procesada
        # Si el modelo incluye backticks, se eliminan aquí antes de escribir el archivo
        if 'tool_calls' in resultado_dev:
            for call in resultado_dev['tool_calls']:
                if call['name'] == 'file_write':
                    args = call.get('args', {})
                    if 'content' in args:
                        # Limpieza extrema: eliminamos bloques markdown
                        raw_content = args['content']
                        clean_content = raw_content.replace("```python", "").replace("```", "").strip()
                        call['args']['content'] = clean_content
                        print("✨ Limpieza de backticks aplicada con éxito.")
        
        print(f"✅ Developer terminó. Archivos escritos en disco.\n")
        # ==========================================
        # FASE 3: EL ANALISTA QA (El Guardián)
        # ==========================================
        print("🕵️‍♂️ Fase 3: El Analista QA está auditando el trabajo...")
        prompt_qa = f"""
        Eres un Analista QA de Software con 20 años de experiencia.
        El Developer acaba de crear archivos basándose en este plan:
        {plan_arquitecto}
        
        Usa tu herramienta `shell_exec` para hacer un `ls -la {ruta}` 
        y usa `file_read` si necesitas verificar el contenido.
        
        Genera un REPORTE DE AUDITORÍA estricto indicando si apruebas o rechazas la construcción.
        """
        
        resultado_qa = j.ask_full(
            prompt_qa, 
            model=model_code, 
            agent="native_react", 
            tools=["shell_exec", "file_read"]
        )
        print("✅ Reporte de QA finalizado.\n")

        # ==========================================
        # FASE 4: EL DOCUMENTADOR (El Escribano)
        # ==========================================
        print("✍️  Fase 4: El Documentador está redactando el manual técnico...")
        
        # Construimos la ruta dinámica del README
        readme_path = os.path.join(ruta, "README.md")
        
        prompt_doc = f"""
        Eres un Technical Writer Senior.
        Aquí tienes el plan del Arquitecto:
        {plan_arquitecto}
        
        Y el reporte del Analista QA confirmando la existencia de los archivos:
        {resultado_qa['content']}
        
        Usa tu herramienta `file_write` para SOBRESCRIBIR o CREAR el archivo 
        `{readme_path}`.
        
        Redacta una documentación profesional en Markdown que incluya:
        1. Descripción del proyecto y los nuevos cambios aplicados.
        2. Explicación de la arquitectura.
        3. Instrucciones de instalación y ejecución.
        
        REGLA ESTRICTA: Ejecuta la herramienta de inmediato, sin cháchara previa.
        """
        
        resultado_doc = j.ask_full(
            prompt_doc, 
            model=model_text, 
            agent="native_react",
            tools=["file_write"]
        )
        print("✅ Documentación técnica generada.\n")
        
        print("================ REPORTE FINAL QA ================")
        print(resultado_qa["content"])
        print("==================================================")
        print(f"🎉 SPRINT FINALIZADO CON ÉXITO. Revisa tu carpeta '{ruta}'.")

if __name__ == "__main__":
    run_software_factory(RUTA_PROYECTO, REQUERIMIENTO)