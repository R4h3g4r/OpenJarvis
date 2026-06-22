import os
import sys
import re
import time
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
    """Explora recursivamente el directorio del proyecto y extrae el árbol y contenido de archivos clave."""
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
                                content += "\n... [TRUNCADO POR TAMAÑO] ..."
                        
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

def normalizar_ruta_archivo(ruta_base: str, ruta_candidata: str) -> str:
    """Normaliza de forma ultra-inteligente las rutas dadas por el modelo, sean absolutas o con carpetas duplicadas."""
    clean_path = ruta_candidata.strip().replace("`", "").strip()
    
    # Nombre de la carpeta del proyecto dinámico (obtenido de la ruta base)
    nombre_carpeta_proyecto = os.path.basename(ruta_base.rstrip("/\\"))
    
    # Si el LLM devolvió una ruta absoluta o parcial que contiene la carpeta del proyecto
    if nombre_carpeta_proyecto in clean_path:
        parts = clean_path.split(nombre_carpeta_proyecto + "/")
        if len(parts) > 1:
            clean_path = parts[-1]  # Tomamos únicamente la porción después de 'nombre_proyecto/'
            
    # Quitamos diagonales al inicio
    clean_path = clean_path.lstrip('/')
    
    # Retornamos la ruta física absoluta correcta dentro de la carpeta del proyecto
    return os.path.abspath(os.path.join(ruta_base, clean_path))

def extraer_archivos_de_markdown(texto: str) -> list[tuple[str, str]]:
    """Analiza de forma ultra-flexible el texto de salida del LLM para extraer (ruta_archivo, codigo)."""
    if not texto:
        return []
        
    resultados = []
    
    # 1. Intentar el delimitador estricto primero
    matches_strict = re.findall(r"=== INICIO_ARCHIVO:\s*(.*?)\s*===\n(.*?)(?=\n=== FIN_ARCHIVO)", texto, re.DOTALL)
    if matches_strict:
        for p, c in matches_strict:
            resultados.append((p.strip(), c.strip()))
        return resultados
        
    # 2. Búsqueda ultra-robusta de bloques de código Markdown usando finditer (evita cualquier error NoneType)
    pattern = r"```(?:python|typescript|tsx|ts|js|jsx|html|css|toml|xml|json)?\s*\n(.*?)\n```"
    matches = list(re.finditer(pattern, texto, re.DOTALL | re.IGNORECASE))
    
    for match in matches:
        code_content = match.group(1)
        if not code_content:
            continue
        code_content = code_content.strip()
        start_pos = match.start()
        
        # Obtenemos el texto anterior al bloque de código (hasta 500 caracteres antes)
        text_before = texto[max(0, start_pos - 500):start_pos]
        if not text_before:
            continue
            
        # Tomamos las últimas 6 líneas del texto anterior
        lines_before = text_before.strip().split('\n')[-6:]
        
        file_path = ""
        # Patrón para capturar una ruta plausible de código fuente real (evita casar versiones numéricas como 1.9.0 o 0.1.0)
        path_pattern = r"([\w\-./]+\.(?:py|tsx|ts|jsx|js|html|css|json|toml))"
        for line in reversed(lines_before):
            m = re.search(path_pattern, line)
            if m:
                candidate = m.group(1).strip()
                # Limpiar markdown
                candidate = candidate.replace("`", "").replace("*", "").replace("#", "").replace("[", "").replace("]", "").strip()
                candidate = candidate.lstrip('/')
                
                # Excluir extensiones no deseadas
                if '/' in candidate or '.' in candidate:
                    if not candidate.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.db', '.sqlite', '.exe', '.zip', '.pdf')):
                        file_path = candidate
                        break
                        
        if file_path:
            resultados.append((file_path, code_content))
            
    return resultados

def registrar_traza(query: str, respuesta: str, modelo: str, duracion_segundos: float):
    """Guarda programáticamente una traza de telemetría local en el TraceStore centralizado de OpenJarvis."""
    try:
        from openjarvis.traces.store import TraceStore
        from openjarvis.core.types import StepType, Trace, TraceStep
        
        db_path = os.path.expanduser("~/.openjarvis/traces.db")
        store = TraceStore(db_path)
        
        ahora = time.time()
        
        # 1. Crear paso de generación de pensamiento (Inferencia)
        step_gen = TraceStep(
            step_type=StepType.GENERATE,
            timestamp=ahora - duracion_segundos,
            duration_seconds=duracion_segundos,
            input={"prompt": query},
            output={"content": respuesta}
        )
        
        # 2. Crear paso de respuesta final
        step_resp = TraceStep(
            step_type=StepType.RESPOND,
            timestamp=ahora,
            duration_seconds=0.0,
            output={"content": respuesta}
        )
        
        # 3. Construir e instanciar la Traza completa
        trace = Trace(
            query=query,
            agent="run_cell",
            model=modelo,
            engine="ollama",
            steps=[step_gen, step_resp],
            result=respuesta,
            started_at=ahora - duracion_segundos,
            ended_at=ahora
        )
        trace.total_latency_seconds = duracion_segundos
        
        # Guardar en SQLite centralizado
        store.save(trace)
    except Exception:
        pass

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
            
            MANDATOS ESTRICTOS DE ARQUITECTURA SÓLIDA (WORLD-CLASS SOFTWARE MANDATES):
            1. ARQUITECTURA LIMPIA Y SEPARACIÓN DE RESPONSABILIDADES: Divide de forma rigurosa el sistema en capas lógicas:
               - Capa de Dominio (Entidades de negocio y esquemas).
               - Capa de Repositorio (Persistencia, consultas, base de datos).
               - Capa de Servicio / Operaciones (Lógica de negocio, transacciones, delegación explícita).
               - Capa de API / Controladores (Endpoints, ruteadores, mapeo HTTP, validación de entrada).
            2. PRINCIPIOS SOLID Y DRY: Prohibido duplicar código. Toda lógica compleja debe estar encapsulada y delegada de forma explícita en métodos reutilizables.
            3. TIPADO ESTÁTICO ESTRICTO: En Python, exige el uso de 'type hints' en todos los argumentos y retornos de funciones (módulo `typing`). En React, exige TypeScript estricto con interfaces claras. Prohibido el tipo `any`.
            4. MANEJO DE EXCEPCIONES INTEGRAL: Diseña un control de errores exhaustivo con bloques `try/except` en Python y `try/catch` en React para cada punto crítico.
            5. PROHIBIDO proponer soluciones en Java, Maven, pom.xml, C# o lenguajes que no coincidan con los activos detectados ({lenguajes_reales}). Toda tu propuesta debe estar alineada estrictamente con los lenguajes reales detectados.
            
            Estructura tu reporte de arquitectura detallando:
              1. DIAGNÓSTICO DE ESTRUCTURA Y ARCHIVOS: Analiza la jerarquía de archivos inyectada. Propón una reestructuración limpia si es necesario.
              2. REVISIÓN CRÍTICA DE BACKEND (PYTHON / FASTAPI / SQLALCHEMY): Evalúa la calidad, imports, controladores y base de datos en los archivos python inyectados.
              3. REVISIÓN CRÍTICA DE FRONTEND (REACT / VITE / TS): Evalúa el uso de componentes, hooks de datos, llamadas de API y package.json de React inyectados.
              4. MEJORAS DE CÓDIGO ESPECÍFICAS: Describe los cambios exactos de lógica de programación por cada archivo, respetando los lenguajes originales del proyecto.
            """
            
            # Inferencia directa sin ReAct, 100% veloz y confiable, sin timeouts
            t_start = time.time()
            plan_arquitecto = j.ask(prompt_arquitecto, model=model_text)
            registrar_traza(f"Célula IA (Arquitecto) - Plan de {os.path.basename(ruta.rstrip('/\\'))}", plan_arquitecto, model_text, time.time() - t_start)
            
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
            
            Instrucciones de auditoría técnica rigurosa:
            - ATENCIÓN: El proyecto está en {lenguajes_reales}. No audites ni propongas soluciones en Java, Maven, pom.xml o lenguajes incorrectos.
            - Audita de forma implacable la viabilidad del código, excepciones, imports rotos, fallos de compilación, linters y tipos de datos del proyecto ({lenguajes_reales}).
            - Exige y evalúa:
              1. BUGS POTENCIALES Y RIESGOS LÓGICOS en las propuestas de reestructuración del Arquitecto.
              2. ROBUSTEZ DE EXCEPCIONES Y TIPADOS: Propón manejos de excepciones específicos (Try/Except en Python, Try-Catch en JS/React) y tipado estático robusto.
              3. PLAN DE PRUEBAS AUTOMATIZADAS: Sugiere la creación de pruebas unitarias y de integración detalladas para asegurar la calidad de la lógica.
            """
            
            t_start = time.time()
            reporte_qa = j.ask(prompt_qa, model=model_code) # Usamos el modelo ultra-experto en lógica
            registrar_traza("Célula IA (Analista QA) - Auditoría del Plan", reporte_qa, model_code, time.time() - t_start)
            
            console.print(Panel(
                f"[bold magenta]🕵️‍♂️ REPORTE DE AUDITORÍA QA:[/bold magenta]\n\n{reporte_qa}",
                title="[bold white]Fase 2 - Analista QA[/bold white]",
                border_style="magenta"
            ))
            
            # FASE 3: EL DOCUMENTADOR REDACTA EL DOCUMENTO FINAL EN DISCO
            console.print("\n[bold yellow]✍️  Fase 3: El Documentador está redactando el manual técnico en disco...[/bold yellow]")
            
            mejores_path = os.path.join(ruta, "PLAN_DE_MEJORAS.md")
            prompt_doc = f"""
            Eres el Technical Writer Senior. Tu trabajo es consolidar la información en un formato profesional Markdown.
            Escribe un documento final ordenado y estructurado con un tono pulido e industrial.
            
            --- PLAN DE MEJORAS PROPUESTO ---
            {plan_arquitecto}
            
            --- REPORTE DE AUDITORÍA DE QA ---
            {reporte_qa}
            
            Instrucciones de redacción técnica:
            - PROHIBIDO proponer nada que no sea {lenguajes_reales}. No uses Java ni Maven ni XML.
            - PROHIBIDO utilizar jerga de marketing, administración o capacitación. El tono debe ser puramente de ingeniería de software.
            - Estructura el archivo PLAN_DE_MEJORAS.md exactamente con estas secciones:
              1. DIAGNÓSTICO TÉCNICO DE CALIDAD DE CÓDIGO (Hallazgos puntuales de arquitectura en los archivos reales del backend y frontend).
              2. ARQUITECTURA DE ARCHIVOS PROPUESTA (Árbol visual de carpetas modificado bajo principios de Arquitectura Limpia).
              3. PLAN DE REFACCIÓN BACKEND PYTHON / FASTAPI (Lógica exacta de código, imports, rutas, controladores, servicios y bases de datos con tipados y manejo de errores).
              4. PLAN DE REFACCIÓN FRONTEND REACT / TYPESCRIPT (Estructura de componentes, hooks de datos, llamadas a API y package.json).
              5. ESPECIFICACIÓN DE SEGURIDAD Y CONTROL QA (Pruebas unitarias, excepciones try/except, linters y tipados estáticos).
            
            Entrega ÚNICAMENTE el código Markdown final del documento. No agregues saludos ni explicaciones previas. Prohibido usar Java, Maven, pom.xml o lenguajes que no estén en el proyecto.
            """
            
            t_start = time.time()
            reporte_final_md = j.ask(prompt_doc, model=model_text)
            registrar_traza("Célula IA (Documentador) - Reporte Final Markdown", reporte_final_md, model_text, time.time() - t_start)
            
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
            console.print("[bold cyan]🏗️  Fase 1: El Arquitecto está designing el Blueprint...[/bold cyan]")
            prompt_arquitecto = f"""
            Eres el Arquitecto de Software Senior. 
            RUTA ABSOLUTA DEL PROYECTO: {ruta}
            
            TAREA DE NEGOCIO: {tarea}
            
            --- LENGUAJES ACTIVOS REALES DETECTADOS EN EL PROYECTO ---
            {lenguajes_reales}
            
            MANDATOS DE ARQUITECTURA Y PATRONES DE DISEÑO ESTRICTOS:
            1. ARQUITECTURA LIMPIA Y DELEGACIÓN: Diseña el sistema delegando responsabilidades de forma explícita. Separa el Backend en capas independientes:
               - `api/`: Controllers, rutas de FastAPI, HTTPException, etc.
               - `service/`: Operations, lógica de negocio pura, validaciones complejas.
               - `repository/`: Database, SQLAlchemy, sesiones de DB, modelos de datos relacionales.
               Y el Frontend en:
               - `components/`: Componentes de interfaz puros de presentación.
               - `hooks/`: Custom React hooks para fetching y manipulación de estado.
               - `services/`: api.ts para las llamadas HTTP crudas.
            2. SOLID & DRY: Prohibido tener lógica duplicada. Diseña el código usando principios SÓLIDOS y patrones reconocidos (e.g. Dependency Injection, Repository Pattern, Singleton, Controller-Service).
            3. TIPADO ESTÁTICO RIGUROSO: Exige siempre el tipado fuerte y explícito en todos los archivos de Python (type hints) y React (TypeScript). Prohibido el uso de `any`.
            4. MANEJO DE EXCEPCIONES Y LOGGING: Especifica el control de errores exhaustivo y la limpieza de conexiones (por ejemplo, try-catch y try-finally con session.close()).
            
            ENTREGABLE: Escribe un plan técnico detallado. Por cada archivo requerido, 
            indica la ruta de destino exacta relativa al proyecto y el bloque de código completo que debe contener. 
            Toda tu propuesta y código DEBEN estar alineados estrictamente con los lenguajes reales detectados ({lenguajes_reales}).
            NO propongas Java, Maven, XML o pom.xml si el proyecto real está en Python/React.
            NO uses herramientas de sistema. Solo entrega el texto del diseño estructurado.
            """
            
            t_start = time.time()
            plan_arquitecto = j.ask(prompt_arquitecto, model=model_text)
            registrar_traza(f"Célula IA (Architect) - Diseñar Blueprint para {os.path.basename(ruta.rstrip('/\\'))}", plan_arquitecto, model_text, time.time() - t_start)
            console.print("✅ Blueprint generado exitosamente.\n")
            
            # Mostrar Blueprint de Arquitectura
            console.print(Panel(f"[bold cyan]PLAN TÉCNICO DEL ARQUITECTO:[/bold cyan]\n\n{plan_arquitecto}", title="[bold white]Blueprint de Arquitectura[/bold white]", border_style="cyan"))
            
            # FASE 2: EL DEVELOPER (MODO INFERENCIA DIRECTA Y ROBUSTA, SIN COMPLEJOS REACT LOOPS)
            console.print("\n[bold green]👨‍💻 Fase 2: El Developer está programando los archivos de código...[/bold green]")
            prompt_dev = f"""
            Eres el Developer Senior de la célula de desarrollo.
            Tu misión es tomar el plano técnico del Arquitecto y programar el código fuente completo, real y funcional para cada archivo propuesto.
            
            --- PLAN DEL ARQUITECTO ---
            {plan_arquitecto}
            --- FIN DEL PLAN ---
            
            LENGUAJES ACTIVOS DEL PROYECTO: {lenguajes_reales}
            
            REGLAS DE CODIFICACIÓN E INGENIERÍA DE EXCELENCIA:
            1. ARQUITECTURA LIMPIA Y DELEGACIÓN: Separa y delega estrictamente tus archivos de código de acuerdo al plano del Arquitecto. Prohibido mezclar lógica de negocio dentro de los controladores de rutas.
            2. CÓDIGO COMPLETO Y FUNCIONAL: Escribe TODO el código fuente funcional de cada archivo de principio a fin de forma impecable. PROHIBIDO usar placeholders, comentarios de omisión tipo '...' o dejar cosas incompletas. Cada import, clase, método y manejo de excepciones debe estar completamente escrito.
            3. MANEJO DE EXCEPCIONES Y RESILIENCIA: Todo acceso a base de datos, llamadas HTTP o I/O debe estar encapsulado en bloques `try/except` robustos en Python y `try/catch` en React. En los controladores y servicios de Python, asegura el cierre de sesiones de base de datos en bloques `try/finally {('session.close()')}`.
            4. TIPADO ESTÁTICO: Utiliza tipado fuerte y explícito en todos los archivos de Python (type hints) y React (TypeScript). Prohibido el uso de `any`.
            5. Por cada archivo que vayas a programar, escribe el nombre del archivo claramente en una línea y luego encierra su código en un bloque estándar de markdown. Sigue este formato exacto para cada archivo:
            
            Ruta: [ruta_relativa_del_archivo_desde_el_proyecto]
            ```python (o de acuerdo al lenguaje del archivo: typescript, tsx, css, html, etc.)
            [código completo y funcional del archivo aquí]
            ```
            """
            
            reintentos_max = 3
            intento = 1
            archivos_escritos = []
            
            while intento <= reintentos_max:
                if intento > 1:
                    console.print(Panel(
                        f"[bold yellow]⚠️ INTENTO {intento-1} FALLIDO: No se detectaron archivos válidos en disco.[/bold yellow]\n"
                        f"[bold cyan]🔄 Activando protocolo de Auto-Curación (Self-Healing) de la célula...[/bold cyan]\n"
                        f"[white]Jarvis está auto-analizando su error de formato anterior para corregirse a sí mismo en el Intento {intento}...[/white]",
                        title="[bold red]Self-Healing Protocol[/bold red]",
                        border_style="yellow"
                    ))
                    # Retroalimentamos al modelo inyectando el error anterior y reforzando las marcas de bloque
                    prompt_actual = prompt_dev + (
                        f"\n\n[ALERTA DE AUTO-CURACIÓN - REINTENTO {intento}]: En tu intento anterior NO estructuraste "
                        f"correctamente las rutas y bloques de código de markdown. "
                        f"Asegúrate de escribir estrictamente la palabra 'Ruta: [ruta_relativa]' justo en la línea "
                        f"anterior a abrir el bloque de código con triple backtick (```). "
                        f"Por favor, regenera todos los archivos de nuevo siguiendo este formato de manera rigurosa."
                    )
                else:
                    prompt_actual = prompt_dev
                
                # Inferencia directa rápida, 100% veloz y confiable
                t_start = time.time()
                resultado_dev = j.ask(prompt_actual, model=model_code)
                registrar_traza("Célula IA (Developer) - Generación de Código Fuente", resultado_dev, model_code, time.time() - t_start)
                
                # PARSEO PROGRAMÁTICO CON ULTRA-REDUNDANCIAS
                matches = extraer_archivos_de_markdown(resultado_dev)
                
                for rel_path, content in matches:
                    # Normalizamos de forma ultra-inteligente la ruta para evitar el anidamiento de /Users/will/...
                    clean_path = normalizar_ruta_archivo(ruta, rel_path)
                    clean_content = content.strip()
                    
                    # Escribimos el archivo físicamente en disco
                    try:
                        os.makedirs(os.path.dirname(clean_path), exist_ok=True)
                        with open(clean_path, 'w', encoding='utf-8') as f_out:
                            f_out.write(clean_content)
                        
                        display_rel_path = os.path.relpath(clean_path, ruta)
                        console.print(f"[bold green]✓ Archivo escrito con éxito en disco: {display_rel_path}[/bold green]")
                        archivos_escritos.append(display_rel_path)
                    except Exception as e_write:
                        console.print(f"[bold red]❌ Error al escribir {rel_path}: {e_write}[/bold red]")
                
                if archivos_escritos:
                    console.print(f"[bold green]✅ Developer finalizó con éxito en el Intento {intento}. {len(archivos_escritos)} archivos creados físicamente en disco.[/bold green]\n")
                    break
                else:
                    intento += 1
            
            if not archivos_escritos:
                console.print("[bold red]❌ Error: La célula de IA colapsó tras 3 intentos de Auto-Curación. Por favor, verifique el estado del motor local de Ollama.[/bold red]\n")
            
            # FASE 3: EL ANALISTA QA (MODO AUDITORÍA DIRECTA)
            console.print("[bold magenta]🕵️‍♂️ Fase 3: El Analista QA está auditando el trabajo...[/bold magenta]")
            prompt_qa = f"""
            Eres un Analista QA de Software Senior con 20 años de experiencia.
            El Developer acaba de programar los siguientes archivos: {', '.join(archivos_escritos)}
            
            PLAN ORIGINAL:
            {plan_arquitecto}
            
            RESPUESTA DEL DEVELOPER:
            {resultado_dev}
            
            Realiza una auditoría estricta de la calidad técnica:
            1. Valida que el código no contenga placeholders incompletos.
            2. Revisa que el tipado estático (type hints en Python y TypeScript en React) sea estricto y correcto.
            3. Verifica que todo acceso a base de datos tenga un try-except-finally con cierre seguro de conexiones.
            4. Diseña y especifica el plan de pruebas unitarias (`pytest` y `jest`) para asegurar la cobertura.
            
            Genera un REPORTE DE AUDITORÍA riguroso indicando si apruebas o rechazas la construcción de los archivos programados.
            """
            
            t_start = time.time()
            reporte_qa = j.ask(prompt_qa, model=model_code)
            registrar_traza("Célula IA (Analista QA) - Auditoría de Compilación", reporte_qa, model_code, time.time() - t_start)
            console.print("[bold magenta]✅ Reporte de QA finalizado.[/bold magenta]\n")

            # FASE 4: EL DOCUMENTADOR
            console.print("[bold yellow]✍️  Fase 4: El Documentador está redactando el manual técnico...[/bold yellow]")
            readme_path = os.path.join(ruta, "README.md")
            
            prompt_doc = f"""
            Eres un Technical Writer Senior.
            Aquí tienes el plan del Arquitecto:
            {plan_arquitecto}
            
            Y el reporte del Analista QA:
            {reporte_qa}
            
            Escribe un manual de documentación en Markdown profesional (README.md) que detalle la arquitectura limpia implementada, la descripción de capas lógicas, los lenguajes, instrucciones de configuración de base de datos sqlite y comandos de ejecución para el frontend y backend.
            """
            
            t_start = time.time()
            readme_content = j.ask(prompt_doc, model=model_text)
            registrar_traza("Célula IA (Documentador) - Reporte Final README.md", readme_content, model_text, time.time() - t_start)
            
            try:
                with open(readme_path, 'w', encoding='utf-8') as f_readme:
                    f_readme.write(readme_content)
                console.print("[bold yellow]✅ Documentación técnica README.md escrita con éxito.[/bold yellow]\n")
            except Exception:
                pass
            
            console.print("================ REPORTE FINAL QA ================")
            console.print(reporte_qa)
            console.print("==================================================")
            console.print(Panel(f"[bold green]🎉 SPRINT FINALIZADO CON ÉXITO.[/bold green]\n📂 {len(archivos_escritos)} archivos de código creados en: [bold green]{ruta}[/bold green]", border_style="green"))

if __name__ == "__main__":
    pass
