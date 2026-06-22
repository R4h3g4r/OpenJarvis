import os
import sys
import re
from openjarvis import Jarvis
from rich.console import Console
from rich.panel import Panel

console = Console()

def limpiar_codigo(contenido: str) -> str:
    # Elimina los backticks de apertura y cierre y la etiqueta 'python'
    limpio = contenido.replace("```python", "").replace("```", "").strip()
    return limpio

# ==========================================
# EL INPUT DEL PRODUCT OWNER / ORQUESTADOR
# ==========================================
MODELO_BASE = "llama3.1:8b"
MODELO_CODIGO = "qwen2.5-coder:14b"

if len(sys.argv) > 2:
    RUTA_PROYECTO = sys.argv[1]
    REQUERIMIENTO = sys.argv[2]
    if len(sys.argv) > 3:
        MODELO_BASE = sys.argv[3]
else:
    # Fallback solo para pruebas si lo ejecutas a mano sin parámetros
    RUTA_PROYECTO = "/Users/will/Documents/OpenJarvis/OpenJarvis/workspace/erika_manicura/"
    REQUERIMIENTO = "Prueba local: Agregar archivo database.py con SQLAlchemy para SQLite."

def es_tarea_analisis(tarea: str) -> bool:
    # Palabras clave que indican que es una tarea de revisión, análisis o planificación
    keywords = ["revis", "analiz", "plan de", "plan de mejoras", "sugerencia", "estudi", "auditar", "diagnóstico", "reporte", "observaciones"]
    return any(keyword in tarea.lower() for keyword in keywords)

def run_software_factory(ruta: str, tarea: str, model_text: str = MODELO_BASE, model_code: str = MODELO_CODIGO):
    console.print(Panel(
        f"[bold green]🚀 INICIANDO SPRINT AUTÓNOMO DE LA CÉLULA DE IA[/bold green]\n"
        f"[bold white]📂 Proyecto destino:[/bold white] {ruta}\n"
        f"[bold white]📋 Requerimiento:[/bold white] {tarea}",
        title="[bold yellow]Software Factory Core[/bold yellow]",
        border_style="green"
    ))
    
    # Determinamos el tipo de flujo
    tipo_flujo = "analisis" if es_tarea_analisis(tarea) else "desarrollo"
    console.print(f"[bold yellow]⚡ Flujo de Trabajo Detectado:[/bold yellow] [bold cyan]{tipo_flujo.upper()}[/bold cyan]\n")
    
    # Instanciamos a Jarvis usando el SDK oficial
    with Jarvis() as j:
        j._ensure_engine()
        
        if tipo_flujo == "analisis":
            # ==========================================
            # FLUJO DE ANÁLISIS, REVISIÓN Y PLANIFICACIÓN
            # ==========================================
            
            # FASE 1: EL ARQUITECTO INSPECCIONA Y PLANIFICA
            console.print("[bold cyan]🏗️  Fase 1: El Arquitecto está inspeccionando el proyecto actual...[/bold cyan]")
            
            prompt_arquitecto = f"""
            Eres el Arquitecto de Software Senior de la célula.
            Tu misión es analizar el proyecto ubicado en: {ruta}
            
            SOLICITUD DEL USUARIO: {tarea}
            
            Usa las herramientas a tu disposición (`shell_exec` y `file_read`) para explorar el directorio del proyecto, 
            ver qué archivos existen, leer su código fuente principal y luego generar un PLAN DE MEJORAS técnico y estructurado.
            
            Usa `shell_exec` para hacer un `ls -R` de la ruta {ruta} para entender la estructura de archivos, 
            y luego usa `file_read` en los archivos clave que encuentres.
            
            ENTREGABLE: Entrega un reporte técnico de arquitectura detallado con observaciones claras y propuestas de mejora.
            """
            
            # El Arquitecto inspecciona con herramientas de lectura
            resultado_arch = j.ask_full(
                prompt_arquitecto,
                model=model_text,
                agent="native_react",
                tools=["shell_exec", "file_read"]
            )
            plan_arquitecto = resultado_arch["content"]
            
            console.print(Panel(
                f"[bold cyan]👷 REPORTE DEL ARQUITECTO:[/bold cyan]\n\n{plan_arquitecto}",
                title="[bold white]Fase 1 - Arquitecto[/bold white]",
                border_style="cyan"
            ))
            
            # FASE 2: EL ANALISTA QA AUDITA EL PLAN DE MEJORAS
            console.print("\n[bold magenta]🕵️‍♂️ Fase 2: El Analista QA está auditando el plan del Arquitecto...[/bold magenta]")
            prompt_qa = f"""
            Eres el Analista QA Senior de la célula con 20 años de experiencia.
            Tu misión es revisar y auditar críticamente el plan de mejoras generado por el Arquitecto para el proyecto: {ruta}.
            
            --- PLAN DEL ARQUITECTO ---
            {plan_arquitecto}
            --- FIN DEL PLAN ---
            
            Usa tus herramientas para realizar cualquier prueba o comprobación si es necesario, 
            y genera un REPORTE DE AUDITORÍA riguroso indicando si apruebas el plan, qué riesgos identificas 
            y qué mejoras sugieres agregar.
            """
            
            resultado_qa = j.ask_full(
                prompt_qa,
                model=model_code, # Usamos el modelo experto en lógica/código para auditar
                agent="native_react",
                tools=["shell_exec", "file_read"]
            )
            reporte_qa = resultado_qa["content"]
            
            console.print(Panel(
                f"[bold magenta]🕵️‍♂️ REPORTE DE AUDITORÍA QA:[/bold magenta]\n\n{reporte_qa}",
                title="[bold white]Fase 2 - Analista QA[/bold white]",
                border_style="magenta"
            ))
            
            # FASE 3: EL DOCUMENTADOR REDACTA EL DOCUMENTO FINAL
            console.print("\n[bold yellow]✍️  Fase 3: El Documentador está redactando el reporte final en Markdown...[/bold yellow]")
            
            mejores_path = os.path.join(ruta, "PLAN_DE_MEJORAS.md")
            prompt_doc = f"""
            Eres el Technical Writer Senior.
            Tu misión es sintetizar el plan del Arquitecto y la auditoría de QA para crear un documento final 
            sumamente pulido, ordenado y profesional en formato Markdown.
            
            Guarda este documento usando la herramienta `file_write` en la ruta: {mejores_path}
            
            --- PLAN DE MEJORAS PROPUESTO ---
            {plan_arquitecto}
            
            --- AUDITORÍA DE QA ---
            {reporte_qa}
            
            ENTREGABLE: Redacta un documento con una descripción del análisis, el plan de mejoras detallado,
            riesgos mitigados y pasos de implementación estructurados. Guarda el archivo directamente usando `file_write`.
            """
            
            resultado_doc = j.ask_full(
                prompt_doc,
                model=model_text,
                agent="native_react",
                tools=["file_write"]
            )
            
            console.print(Panel(
                f"[bold yellow]📝 REPORTE ESCRITO POR EL DOCUMENTADOR EN DISCO ({mejores_path}):[/bold yellow]\n\n{resultado_doc['content']}",
                title="[bold white]Fase 3 - Documentador[/bold white]",
                border_style="yellow"
            ))
            
            console.print("================ REPORTE FINAL DE ANÁLISIS ================")
            console.print(f"🎉 SPRINT DE ANÁLISIS FINALIZADO CON ÉXITO.\n"
                          f"📂 El plan final ha sido guardado de forma segura en: [bold green]{mejores_path}[/bold green]")
            console.print("==========================================================")
            
        else:
            # ==========================================
            # FLUJO DE DESARROLLO DE CÓDIGO (SPRINT)
            # ==========================================
            
            # FASE 1: EL ARQUITECTO
            console.print("[bold cyan]🏗️  Fase 1: El Arquitecto está diseñando el Blueprint...[/bold cyan]")
            prompt_arquitecto = f"""
            Eres el Arquitecto de Software Senior. 
            RUTA ABSOLUTA DEL PROYECTO: {ruta}
            
            TAREA DE NEGOCIO: {tarea}
            
            ENTREGABLE: Escribe un plan técnico detallado. Por cada archivo requerido, 
            indica la ruta exacta (usando la RUTA ABSOLUTA DEL PROYECTO como base) y el bloque de código completo que debe contener. 
            NO uses herramientas de sistema. Solo entrega el texto del diseño estructurado.
            """
            
            plan_arquitecto = j.ask(prompt_arquitecto, model=model_text)
            console.print("✅ Blueprint generado exitosamente.\n")
            
            # Mostrar Blueprint de Arquitectura
            console.print(Panel(f"[bold cyan]PLAN TÉCNICO DEL ARQUITECTO:[/bold cyan]\n\n{plan_arquitecto}", title="[bold white]Blueprint de Arquitectura[/bold white]", border_style="cyan"))
            
            # FASE 2: EL DEVELOPER
            console.print("\n[bold green]👨‍💻 Fase 2: El Developer está escribiendo los archivos en disco...[/bold green]")
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
            
            # FILTRO DE SEGURIDAD INDUSTRIAL
            if 'tool_calls' in resultado_dev:
                for call in resultado_dev['tool_calls']:
                    if call['name'] == 'file_write':
                        args = call.get('args', {})
                        if 'content' in args:
                            raw_content = args['content']
                            clean_content = raw_content.replace("```python", "").replace("```", "").strip()
                            call['args']['content'] = clean_content
                            console.print("[bold green]✨ Limpieza de backticks aplicada con éxito al archivo escrito por el Developer.[/bold green]")
            
            console.print(f"✅ Developer terminó. Archivos escritos en disco.\n")
            
            # FASE 3: EL ANALISTA QA
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
            reporte_qa = resultado_qa["content"]
            console.print("✅ Reporte de QA finalizado.\n")

            # FASE 4: EL DOCUMENTADOR
            print("✍️  Fase 4: El Documentador está redactando el manual técnico...")
            readme_path = os.path.join(ruta, "README.md")
            
            prompt_doc = f"""
            Eres un Technical Writer Senior.
            Aquí tienes el plan del Arquitecto:
            {plan_arquitecto}
            
            Y el reporte del Analista QA confirmando la existencia de los archivos:
            {reporte_qa}
            
            Usa tu herramienta `file_write` para SOBRESCRIBIR o CREAR el archivo `{readme_path}`.
            
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
            console.print("✅ Documentación técnica generada.\n")
            
            console.print("================ REPORTE FINAL QA ================")
            console.print(reporte_qa)
            console.print("==================================================")
            console.print(Panel(f"[bold green]🎉 SPRINT FINALIZADO CON ÉXITO.[/bold green]\n📂 Revisa los archivos de código creados en: [bold green]{ruta}[/bold green]", border_style="green"))

if __name__ == "__main__":
    run_software_factory(RUTA_PROYECTO, REQUERIMIENTO)
