import subprocess
import sys
import os
import re
import time
import pyaudio
from openjarvis import Jarvis
from openjarvis.tools.audio.ear import EarTool
from openjarvis.core.types import Message, Role, StepType, Trace, TraceStep
from rich.console import Console
from rich.panel import Panel

console = Console()

def speak(text: str):
    # Print on screen with cinematic styling
    console.print(Panel(f"[bold cyan]JARVIS:[/bold cyan] {text}", border_style="cyan", title="[bold white]Response[/bold white]"))
    # Speak out loud using macOS built-in TTS
    try:
        subprocess.run(["say", text], check=True)
    except Exception as e:
        pass

def listen_mic(ear: EarTool, duration: int = 5) -> str:
    console.print(f"\n[bold green]🎤 [Escuchando micrófono por {duration} segundos...] Habla ahora...[/bold green]")
    try:
        resultado = ear.execute(duration=duration)
        transcription = resultado.content.strip()
        return transcription
    except Exception as e:
        console.print(f"[bold red]Error al escuchar micrófono: {e}[/bold red]")
        return ""

def check_microphone_available() -> bool:
    p = pyaudio.PyAudio()
    has_mic = False
    try:
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev.get('maxInputChannels', 0) > 0:
                has_mic = True
                break
    except Exception:
        pass
    finally:
        p.terminate()
    return has_mic

def registrar_traza(query: str, respuesta: str, modelo: str, duracion_segundos: float):
    """Guarda programáticamente una traza de telemetría local en el TraceStore centralizado de OpenJarvis."""
    try:
        from openjarvis.traces.store import TraceStore
        
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
            agent="cinematic_jarvis",
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
        # Falla silenciosa en caso de error de concurrencia de base de datos
        pass

def main():
    os.system("clear")
    console.print(Panel(
        "[bold cyan]"
        "==================================================\n"
        "           SISTEMA JARVIS EN LÍNEA (LOCAL)        \n"
        "==================================================\n"
        "  • Oído: EarTool / Teclado (Híbrido Seleccionable)\n"
        "  • Memoria: Historial Conversacional Activo (Stateful)\n"
        "  • Telemetría: Traces.db Conexión Web en Tiempo Real\n"
        "  • Cerebro: LLaMA 3.1 8B (vía Ollama Local)\n"
        "  • Voz: Apple macOS Studio-quality TTS\n"
        "=================================================="
        "[/bold cyan]",
        border_style="cyan"
    ))
    
    # Selección de Interfaz Interactiva
    console.print("[bold yellow]🤖 Seleccione su método de interfaz, señor:[/bold yellow]")
    console.print("  [bold cyan][1][/bold cyan] [bold white]Modo Voz[/bold white] (Hablar por Micrófono)")
    console.print("  [bold cyan][2][/bold cyan] [bold white]Modo Híbrido[/bold white] (Escribir por Teclado + Voz de Jarvis)")
    
    try:
        seleccion = console.input("\n[bold white]📋 Elija una opción (1 o 2) [Por defecto: 2]: [/bold white]").strip()
        if not seleccion:
            seleccion = "2"
    except (KeyboardInterrupt, EOFError):
        seleccion = "2"
        
    os.system("clear")
    console.print(Panel(
        "[bold cyan]"
        "==================================================\n"
        "           SISTEMA JARVIS EN LÍNEA (LOCAL)        \n"
        "==================================================\n"
        "  • Oído: EarTool / Teclado (Híbrido Seleccionable)\n"
        "  • Memoria: Historial Conversacional Activo (Stateful)\n"
        "  • Telemetría: Traces.db Conexión Web en Tiempo Real\n"
        "  • Cerebro: LLaMA 3.1 8B (vía Ollama Local)\n"
        "  • Voz: Apple macOS Studio-quality TTS\n"
        "=================================================="
        "[/bold cyan]",
        border_style="cyan"
    ))
    
    # Inicialización del SDK
    console.print("[yellow]⚡ Cargando redes neuronales de Jarvis...[/yellow]")
    
    has_mic = False
    ear = None
    
    if seleccion == "1":
        has_mic = check_microphone_available()
        if has_mic:
            ear = EarTool()
            console.print("[green]✓ Modo Voz Activo: Micrófono detectado e inicializado.[/green]")
        else:
            console.print("[bold red]⚠️ No se detectaron micrófonos físicos activos.[/bold red]")
            console.print("[bold yellow]👉 Forzando Modo Híbrido (Teclado) por seguridad.[/bold yellow]\n")
            seleccion = "2"
            
    if seleccion == "2":
        console.print("[green]✓ Modo Híbrido Activo: Entrada por teclado habilitada.[/green]")
        console.print("[green]✓ Salida de Audio: Sintetizador de voz de macOS activo.[/green]\n")
        
    try:
        # Test connection with SDK
        with Jarvis() as j:
            model = j.config.intelligence.default_model
            console.print(f"[green]✓ Cerebro sincronizado con modelo: [bold]{model}[/bold][/green]")
    except Exception as e:
        console.print(f"[bold red]Error al conectar con OpenJarvis Core o Ollama: {e}[/bold red]")
        sys.exit(1)
        
    if seleccion == "1":
        speak("Sistemas en línea, señor. Todos los núcleos locales están operativos. He activado los receptores de audio. ¿En qué puedo ayudarle hoy?")
    else:
        speak("Sistemas en línea, señor. He habilitado el teclado para recibir sus órdenes, pero seguiré respondiéndole con mi sintetizador de voz. ¿En qué puedo ayudarle hoy?")
    
    # Inicialización del Historial Conversacional
    messages_history: list[Message] = []
    
    # El bucle de interacción de voz infinito
    with Jarvis() as j:
        # Recuperamos la configuración del modelo de Jarvis
        model_name = j.config.intelligence.default_model or "llama3.1:8b"
        temperature = j.config.intelligence.temperature or 0.7
        max_tokens = j.config.intelligence.max_tokens or 2048
        
        # Inicializamos el motor del SDK
        j._ensure_engine()
        
        # Prompt de sistema para personificar a Jarvis
        system_prompt = (
            "Eres JARVIS, el asistente virtual inteligente de Tony Stark. "
            "Responde de forma concisa, educada, elegante y con un toque de ingenio británico. "
            "Trata siempre al usuario como 'señor'. Mantén tus respuestas en un rango de 3 a 7 líneas "
            "para que sean óptimas de leer y de hablar, a menos que se te solicite una explicación técnica detallada."
        )
        messages_history.append(Message(role=Role.SYSTEM, content=system_prompt))
        
        while True:
            if seleccion == "1" and has_mic and ear is not None:
                # Escuchamos al usuario usando el micrófono
                user_text = listen_mic(ear, duration=5)
                if not user_text or user_text == "No se detectó voz.":
                    continue
                console.print(f"[bold white]TÚ (Voz):[/bold white] [yellow]{user_text}[/yellow]")
            else:
                # Entrada por teclado
                try:
                    user_text = console.input("\n[bold white]📋 Señor, ingrese su orden: [/bold white]").strip()
                except (KeyboardInterrupt, EOFError):
                    user_text = "salir"
                
                if not user_text:
                    continue
                console.print(f"[bold white]TÚ (Teclado):[/bold white] [yellow]{user_text}[/yellow]")
            
            # Verificamos comandos de salida
            exit_phrases = ["salir", "adios", "adiós", "terminar", "apagar", "shutdown", "exit"]
            if any(phrase in user_text.lower() for phrase in exit_phrases):
                speak("Apagando sistemas de voz. Hasta luego, señor.")
                break
                
            # COMANDO ESPECIAL: Aplicar o Ejecutar el Plan de Mejoras guardado en PLAN_DE_MEJORAS.md
            is_exec_plan = any(phrase in user_text.lower() for phrase in ["ejecuta el plan", "aplica el plan", "ejecutar el plan", "aplica las mejoras", "ejecuta las mejoras"])
            if is_workspace_action := is_exec_plan or user_text.lower().startswith("/cell ") or "ejecuta la célula" in user_text.lower() or "ejecuta la celula" in user_text.lower():
                # Ruta del proyecto dinámica: detecta si el usuario especificó una ruta en su mensaje
                match_path = re.search(r"(/Users/[\w\-./]+/workspace/[\w\-./]+)", user_text)
                if not match_path:
                    match_path = re.search(r"(workspace/[\w\-./]+)", user_text)
                
                if match_path:
                    extracted_path = match_path.group(1).rstrip('/') + '/'
                    if not extracted_path.startswith('/'):
                        ruta_proyecto = os.path.abspath(os.path.join("/Users/will/Documents/OpenJarvis/OpenJarvis/", extracted_path)) + '/'
                    else:
                        ruta_proyecto = extracted_path
                else:
                    ruta_proyecto = "/Users/will/Documents/OpenJarvis/OpenJarvis/workspace/erika_manicura/"
                
                mejores_path = os.path.join(ruta_proyecto, "PLAN_DE_MEJORAS.md")
                
                tarea_celula = ""
                
                if is_exec_plan:
                    # Intentamos leer el archivo PLAN_DE_MEJORAS.md
                    if os.path.exists(mejores_path):
                        try:
                            with open(mejores_path, 'r', encoding='utf-8') as f_plan:
                                plan_md = f_plan.read().strip()
                            speak("Excelente decisión, señor. He leído el archivo PLAN_DE_MEJORAS.md de su espacio de trabajo. Inicializando el protocolo de desarrollo de la Célula de IA para implementar este plan.")
                            # La tarea es el plan de mejoras leído
                            tarea_celula = f"Implementar el siguiente plan de mejoras técnico:\n\n{plan_md}"
                        except Exception as e_p:
                            speak(f"Señor, tuve un problema al leer el plan de mejoras de disco: {e_p}. Procederé con una implementación estándar.")
                    else:
                        speak("Señor, no he encontrado un archivo PLAN_DE_MEJORAS.md en su proyecto. Le sugiero primero generar un plan de mejoras de su proyecto.")
                        continue
                else:
                    # Extraemos la orden para comando general
                    if user_text.lower().startswith("/cell "):
                        tarea_celula = user_text[6:].strip()
                    else:
                        tarea_celula = user_text.lower().replace("ejecuta la célula", "").replace("ejecuta la celula", "").strip()
                
                if not tarea_celula:
                    tarea_celula = "Optimizar la organización de archivos de erika_manicura y agregar comentarios descriptivos en el código."
                
                speak("Sistemas cargados. Desplegando Arquitecto, Developer (Qwen 2.5 Coder), Analista QA y Documentador para ejecutar el sprint autónomo en su carpeta de trabajo.")
                
                try:
                    # Importamos dinámicamente y ejecutamos el sprint de desarrollo
                    from run_cell import run_software_factory
                    flujo_forzado = "desarrollo" if is_exec_plan else None
                    run_software_factory(ruta_proyecto, tarea_celula, force_flow=flujo_forzado)
                    
                    # Al terminar, avisamos al señor
                    speak("Sprint de desarrollo finalizado con éxito, señor. El código ha sido programado de forma autónoma con Qwen 2.5 Coder, auditado rigurosamente por el Analista de Calidad y documentado en el README de su espacio de trabajo. Puede revisar la carpeta 'erika_manicura' ahora mismo.")
                except Exception as ex_cell:
                    speak(f"Señor, tuvimos una interrupción al desplegar los agentes: {ex_cell}")
                continue
                
            # Agregar orden actual del usuario al historial
            messages_history.append(Message(role=Role.USER, content=user_text))
            
            # Procesamos la orden con el cerebro de Jarvis
            console.print("[yellow]🧠 Procesando pensamiento con memoria activa...[/yellow]")
            t_start = time.time()
            try:
                # Ejecutamos la inferencia con el historial de la conversación
                result = j._engine.generate(
                    messages_history,
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                response = result.get("content", "").strip()
                if not response:
                    response = "No logré procesar esa instrucción, señor."
                
                # Registro automático de trazas para el Dashboard
                t_end = time.time()
                registrar_traza(user_text, response, model_name, t_end - t_start)
                
            except Exception as e:
                response = f"Hubo un error en los núcleos de procesamiento: {e}"
                
            # Guardamos la respuesta del asistente en el historial
            messages_history.append(Message(role=Role.ASSISTANT, content=response))
            
            # Hablamos la respuesta
            speak(response)
            time.sleep(0.5)

if __name__ == "__main__":
    main()
