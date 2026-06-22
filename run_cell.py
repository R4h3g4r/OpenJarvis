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
else:
    # Fallback solo para pruebas si lo ejecutas a mano sin parámetros
    RUTA_PROYECTO = "/Users/will/Documents/OpenJarvis/OpenJarvis/workspace/erika_manicura/"
    REQUERIMIENTO = "Prueba local: Agregar archivo database.py con SQLAlchemy para SQLite."

def es_tarea_analisis(tarea: str) -> bool:
    # Soporte ultra-robusto contra typos de usuarios como "analices" (con c) o "plan me"
    keywords = ["revis", "analiz", "analic", "plan", "mejora", "sugerencia", "estudi", "auditar", "diagnóstico", "reporte", "observaciones"]
    return any(keyword in tarea.lower() for keyword in keywords)

def detectar_lenguajes_proyecto(ruta: str) -> str:
    """Detecta de forma programática y física qué lenguajes y frameworks están activos en el workspace."""
    has_python = False
    has_react = False
    has_typescript = False
    
    ruta_norm = os.path.abspath(ruta)
    if not os.path.exists(ruta_norm):
        return "Python y React"
        
    for root, dirs, files in os.walk(ruta_norm):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.venv']]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext == '.py':
                has_python = True
            elif ext in ['.tsx', '.jsx']:
                has_react = True
            elif ext == '.ts':
                has_typescript = True
                
    langs = []
    if has_python:
        langs.append("Python (Backend, típicamente FastAPI y SQLAlchemy)")
    if has_react:
        langs.append("React con TypeScript/Vite" if has_typescript else "React con JavaScript/Vite")
    elif has_typescript:
        langs.append("TypeScript")
        
    if not langs:
        return "Python (para backend) y React/TypeScript (para frontend)"
    return " y ".join(langs)

def obtener_contexto_codigo(ruta: str) -> str:
    """Explora recursivamente el proyecto y extrae un contexto ultra-enfocado de alta densidad, apto para Ollama."""
    tree_lines = []
    file_contents = []
    
    # Normalizar ruta para evitar problemas con diagonales dobles
    ruta_norm = os.path.abspath(ruta)
    
    if not os.path.exists(ruta_norm):
        return f"[Error] El directorio '{ruta_norm}' no existe en disco."
        
    for root, dirs, files in os.walk(ruta_norm):
        # Ignorar carpetas ocultas, virtuales o pesadas de node
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.venv', '.git', '.github']]
        
        # Calcular sangría para el árbol visual
        level = root.replace(ruta_norm, '').count(os.sep)
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root) if os.path.basename(root) else root
        tree_lines.append(f"{indent}├── {folder_name}/")
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            # FILTRO DE SEGURIDAD DE CONTEXTO: Ignorar archivos basura, pesados o de bloqueo (ej: package-lock.json de 90KB)
            if f.startswith('.') or f == '.DS_Store' or f in ['PLAN_DE_MEJORAS.md', 'README.md', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'bun.lockb', 'poetry.lock', 'uv.lock']:
                continue
            tree_lines.append(f"{subindent}└── {f}")
            
            # Si es un archivo de texto de código fuente real, leemos su contenido
            file_path = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            
            # Solo leer archivos de código fuente reales para mantener el contexto ligero y evitar fallos del modelo local
            if ext in ['.py', '.ts', '.tsx', '.js', '.jsx', '.html', '.css', '.toml']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file_obj:
                        lines = file_obj.readlines()
                        
                        # FILTRADO DE ALTA DENSIDAD:
                        # Si es un manifiesto o archivo pequeño, leemos completo.
                        # Si es un archivo de código grande, solo leemos las primeras 35 líneas para ver los imports, la estructura y funciones sin saturar la memoria de Ollama.
                        if f in ['requirements.txt', 'package.json', 'run.py', 'vite.config.ts', 'database.py']:
                            content = "".join(lines).strip()
                        else:
                            content = "".join(lines[:35]).strip()
                            if len(lines) > 35:
                                content += "\n... [TRUNCADO PARA PRESERVAR MEMORIA DEL CONTEXTO] ..."
                        
                        rel_path = os.path.relpath(file_path, ruta_norm)
                        file_contents.append(
                            f"📄 [b]ARCHIVO: {rel_path}[/b]\n"
                            f"```\n{content}\n```"
                        )
                except Exception as e:
                    file_contents.append(f"❌ Error al leer {f}: {e}")
                    
    contexto = "🌲 [bold cyan]ÁRBOL DE DIRECTORIOS Y ARCHIVOS DEL PROYECTO ACTUAL:[/bold cyan]\n" + "\n".join(tree_lines) + "\n\n"
    contexto += "📝 [bold cyan]CÓDIGO FUENTE REAL (Vista previa de alta densidad de imports y funciones):[/bold cyan]\n" + "\n\n".join(file_contents)
    return contexto

def run_software_factory(ruta: str, tarea: str, model_text: str = MODELO_BASE, model_code: str = MODELO_CODIGO, force_flow: str = None):
    console.print(Panel(
        f"[bold green]🚀 INICIANDO SPRINT AUTÓNOMO DE LA CÉLULA DE IA[/bold green]\n"
        f"[bold white]📂 Proyecto destino:[/bold white] {ruta}\n"
        f"[bold white]📋 Requerimiento:[/bold white] {tarea}",
        title="[bold yellow]Software Factory Core[/bold yellow]",
        border_style="green"
    ))
    
    # Detectamos de forma física los lenguajes activos del proyecto
    lenguajes_reales = detectar_lenguajes_proyecto(ruta)
    console.print(f"[bold green]🔍 Lenguajes detectados físicamente en el proyecto:[/bold green] [bold white]{lenguajes_reales}[/bold white]")
    
    # Determinamos el tipo de flujo de forma robusta o forzada
    if force_flow is not None:
        tipo_flujo = force_flow
    else:
        tipo_flujo = "analisis" if es_tarea_analisis(tarea) else "desarrollo"
        
    console.print(f"[bold yellow]⚡ Flujo de Trabajo Detectado:[/bold yellow] [bold cyan]{tipo_flujo.upper()}[/bold cyan]\n")
    
    # Instanciamos a Jarvis usando el SDK oficial
    with Jarvis() as j:
        j._ensure_engine()
        
        if tipo_flujo == "analisis":
            # ==========================================
            # FLUJO DE ANÁLISIS, REVISIÓN Y PLANIFICACIÓN
            # ==========================================
            
            # FASE 0: EXPLORACIÓN PROGRAMÁTICA EN MILISEGUNDOS
            console.print("[bold yellow]🔍 Fase 0: Extrayendo contexto completo del código local programáticamente...[/bold yellow]")
            codigo_contexto = obtener_contexto_codigo(ruta)
            console.print("[green]✓ Contexto de código cargado e inyectado con éxito.[/green]\n")
            
            # FASE 1: EL ARQUITECTO ANALIZA E INVENTA EL PLAN
            console.print("[bold cyan]🏗️  Fase 1: El Arquitecto está redactando el plan de mejoras...[/bold cyan]")
            
            prompt_arquitecto = f"""
            Eres el Arquitecto de Software Senior de la célula.
            Tu misión es realizar un análisis del código fuente y de la estructura de archivos inyectada a continuación, 
            para diseñar un PLAN TÉCNICO DE MEJORAS Y ARQUITECTURA 100% orientado a código.
            
            REQUERIMIENTO DEL USUARIO: {tarea}
            
            --- LENGUAJES ACTIVOS REALES DETECTADOS EN EL PROYECTO ---
            Este proyecto está programado e implementado ÚNICAMENTE en: {lenguajes_reales}
            
            --- CONTEXTO COMPLETO DEL PROYECTO LOCAL ---
            {codigo_contexto}
            --- FIN DEL CONTEXTO ---
            
            Instrucciones de contenido estricto:
            - ATENCIÓN ABSOLUTA: El proyecto utiliza de forma real {lenguajes_reales}. 
            - ESTÁ COMPLETAMENTE PROHIBIDO proponer soluciones en Java, Maven, pom.xml, C# o lenguajes que no coincidan con los activos detectados ({lenguajes_reales}). Toda tu propuesta debe estar alineada estrictamente con los lenguajes reales detectados.
            - NO propongas discursos corporativos, de capacitación de equipos o de recursos humanos.
            - Sé sumamente técnico, concreto y específico. Menciona nombres de archivos reales del proyecto, imports y rutas.
            - Estructura tu reporte de arquitectura detallando:
              1. DIAGNÓSTICO DE ESTRUCTURA Y ARCHIVOS: Analiza la jerarquía de archivos inyectada. Propón una reestructuración limpia si es necesario.
              2. REVISIÓN CRÍTICA DE BACKEND (PYTHON / FASTAPI / SQLALCHEMY): Evalúa la calidad, imports, controladores y base de datos en los archivos python inyectados.
              3. REVISIÓN CRÍTICA DE FRONTEND (REACT / VITE / TS): Evalúa el uso de componentes, hooks de datos, llamadas de API y package.json de React inyectados.
              4. MEJORAS DE CÓDIGO ESPECÍFICAS: Describe los cambios exactos de lógica de programación por cada archivo, respetando los lenguajes originales del proyecto.
            """
            
            # Inferencia directa sin ReAct, 100% veloz y confiable, sin timeouts
            plan_arquitecto = j.ask(prompt_arquitecto, model=model_text)
            
            console.print(Panel(
                f"[bold cyan]👷 REPORTE DEL ARQUITECTO:[/bold cyan]\n\n{plan_arquitecto}",
                title="[bold white]Fase 1 - Arquitecto[/bold white]",
                border_style="cyan"
            ))
            
            # FASE 2: EL ANALISTA QA AUDITA EL PLAN DE MEJORAS
            console.print("\n[bold magenta]🕵️‍♂️ Fase 2: El Analista QA está auditando críticamente el plan del Arquitecto...[/bold magenta]")
            prompt_qa = f"""
            Eres el Analista QA Senior de la célula con 20 años de experiencia en auditoría técnica.
            Tu misión es auditar críticamente el plan de mejoras propuesto por el Arquitecto sobre el código real inyectado.
            
            --- LENGUAJES ACTIVOS REALES DETECTADOS EN EL PROYECTO ---
            {lenguajes_reales}
            
            --- CONTEXTO COMPLETO DEL PROYECTO LOCAL ---
            {codigo_contexto}
            
            --- PLAN PROPUESTO POR EL ARQUITECTO ---
            {plan_arquitecto}
            --- FIN DEL PLAN ---
            
            Instrucciones de auditoría técnica:
            - ATENCIÓN: El proyecto está en {lenguajes_reales}. No audites ni propongas soluciones en Java, Maven, pom.xml o lenguajes incorrectos.
            - Concéntrate exclusivamente en la viabilidad del código, excepciones, imports rotos, fallos de compilación, linters y tipos de datos del proyecto ({lenguajes_reales}).
            - Genera un REPORTE DE AUDITORÍA riguroso indicando si apruebas el plan y qué riesgos identificas.
            """
            
            reporte_qa = j.ask(prompt_qa, model=model_code) # Usamos el modelo ultra-experto en lógica
            
            console.print(Panel(
                f"[bold magenta]🕵️‍♂️ REPORTE DE AUDITORÍA QA:[/bold magenta]\n\n{reporte_qa}",
                title="[bold white]Fase 2 - Analista QA[/bold white]",
                border_style="magenta"
            ))
            
            # FASE 3: EL DOCUMENTADOR REDACTA EL DOCUMENTO FINAL EN DISCO
            console.print("\n[bold yellow]✍️  Fase 3: El Documentador está redactando el reporte final en Markdown...[/bold yellow]")
            
            mejores_path = os.path.join(ruta, "PLAN_DE_MEJORAS.md")
            prompt_doc = f"""
            Eres el Technical Writer Senior. Tu trabajo es consolidar la información en un formato profesional Markdown.
            Escribe un documento final ordenado y estructurado con un tono pulido e industrial.
            
            --- PLAN DE MEJORAS PROPUESTO ---
            {plan_arquitecto}
            
            --- REPORTE DE AUDITORÍA DE QA ---
            {reporte_qa}
            
            Genera un archivo Markdown completo que contenga:
            1. Resumen Ejecutivo del Análisis.
            2. Áreas de Oportunidad Identificadas (Puntos Débiles basados en el análisis real).
            3. Plan de Acción Técnico Detallado (Pasos concretos de desarrollo utilizando estrictamente los lenguajes {lenguajes_reales}).
            4. Riesgos y Mitigación Operativa (Auditoría QA).
            
            Entrega ÚNICAMENTE el código Markdown final del documento. No agregues saludos ni explicaciones previas. Prohibido usar Java, Maven, pom.xml o lenguajes que no estén en el proyecto.
            """
            
            reporte_final_md = j.ask(prompt_doc, model=model_text)
            
            # Guardamos el archivo directamente usando Python de forma programática (100% robusto, cero fallas)
            try:
                # Asegurar de crear carpetas si no existen
                os.makedirs(os.path.dirname(mejores_path), exist_ok=True)
                with open(mejores_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(reporte_final_md)
                console.print(f"[bold green]✓ Archivo escrito con éxito en disco: {mejores_path}[/bold green]\n")
            except Exception as e_write:
                console.print(f"[bold red]❌ Error al escribir el archivo final: {e_write}[/bold red]")
            
            console.print(Panel(
                f"[bold yellow]📝 REPORTE ESCRITO EN DISCO:[/bold yellow]\n\n{reporte_final_md}",
                title="[bold white]Fase 3 - Documentador (Documento Final)[/bold white]",
                border_style="yellow"
            ))
            
            console.print("================ REPORTE FINAL DE ANÁLISIS ================")
            console.print(f"🎉 SPRINT DE ANÁLISIS FINALIZADO CON ÉXITO.\n"
                          f"📂 El plan de mejoras ha sido guardado de forma segura en: [bold green]{mejores_path}[/bold green]")
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
            
            --- LENGUAJES ACTIVOS REALES DETECTADOS EN EL PROYECTO ---
            {lenguajes_reales}
            
            ENTREGABLE: Escribe un plan técnico detallado. Por cada archivo requerido, 
            indica la ruta exacta (usando la RUTA ABSOLUTA DEL PROYECTO como base) y el bloque de código completo que debe contener. 
            Toda tu propuesta y código DEBEN estar alineados estrictamente con los lenguajes reales detectados ({lenguajes_reales}).
            NO propongas Java, Maven, XML o pom.xml si el proyecto real está en Python/React.
            NO uses herramientas de sistema. Solo entrega el texto del diseño estructurado.
            """
            
            plan_arquitecto = j.ask(prompt_arquitecto, model=model_text)
            console.print("✅ Blueprint generado exitosamente.\n")
            
            # Mostrar Blueprint de Arquitectura
            console.print(Panel(f"[bold cyan]PLAN TÉCNICO DEL ARQUITECTO:[/bold cyan]\n\n{plan_arquitecto}", title="[bold white]Blueprint de Arquitectura[/bold white]", border_style="cyan"))
            
            # FASE 2: EL DEVELOPER
            console.print("\n[bold green]👨‍💻 Fase 2: El Developer está escribiendo los archivos en disco...[/bold green]")
            prompt_dev = f"""
            Eres un Developer backend. Tu objetivo es crear o modificar archivos dentro de la carpeta: {ruta}
            --- PLAN DEL ARQUITECTO ---
            {plan_arquitecto}
            --- FIN DEL PLAN ---
            
            LENGUAJES DEL PROYECTO: {lenguajes_reales}
            
            REGLAS DE SALIDA:
            1. Invoca `file_write` con la RUTA COMPLETA de archivos de Python o React de tu proyecto: {ruta}nombre_del_archivo.
            2. PASA EL CÓDIGO PURO Y COMPLETO en el parámetro 'content'. No uses placeholders como '...' o '// rest of code'. Escribe todo el código fuente funcional.
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
            El Developer acab de crear archivos basándose en este plan:
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
            
            Y el reporte del Analista QA confirming la existencia de los archivos:
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
    pass
