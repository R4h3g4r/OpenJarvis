import subprocess
import sys
import os
import time
import pyaudio
from openjarvis import Jarvis
from openjarvis.tools.audio.ear import EarTool
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

def main():
    os.system("clear")
    console.print(Panel(
        "[bold cyan]"
        "==================================================\n"
        "           SISTEMA JARVIS EN LÍNEA (LOCAL)        \n"
        "==================================================\n"
        "  • Oído: EarTool / Teclado (Híbrido)\n"
        "  • Cerebro: LLaMA 3.1 8B (vía Ollama Local)\n"
        "  • Voz: Apple macOS Studio-quality TTS\n"
        "=================================================="
        "[/bold cyan]",
        border_style="cyan"
    ))
    
    # Inicialización del SDK
    console.print("[yellow]⚡ Cargando redes neuronales de Jarvis...[/yellow]")
    
    # Verificamos si hay micrófono físico
    has_mic = check_microphone_available()
    
    try:
        ear = None
        if has_mic:
            ear = EarTool()
            console.print("[green]✓ Micrófono detectado de forma exitosa.[/green]")
        else:
            console.print("[bold yellow]⚠️  No se detectaron micrófonos (típico en Mac mini).[/bold yellow]")
            console.print("[bold yellow]👉 Activando modo híbrido: Entrada por Teclado + Salida por Voz.[/bold yellow]\n")
            
        # Test connection with SDK
        with Jarvis() as j:
            model = j.config.intelligence.default_model
            console.print(f"[green]✓ Cerebro sincronizado con modelo: [bold]{model}[/bold][/green]")
    except Exception as e:
        console.print(f"[bold red]Error al conectar con OpenJarvis Core o Ollama: {e}[/bold red]")
        sys.exit(1)
        
    speak("Sistemas en línea, señor. Todos los núcleos locales están operativos. He detectado que estamos usando una Mac mini, por lo que he habilitado el teclado para recibir sus órdenes, pero seguiré respondiéndole con mi sintetizador de voz. ¿En qué puedo ayudarle hoy?")
    
    # El bucle de interacción de voz infinito
    with Jarvis() as j:
        while True:
            if has_mic and ear is not None:
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
                
            # Procesamos la orden con el cerebro de Jarvis
            console.print("[yellow]🧠 Procesando pensamiento...[/yellow]")
            try:
                # Usamos ask con el modelo por defecto (llama3.1:8b)
                response = j.ask(user_text)
                if not response:
                    response = "No logré procesar esa instrucción, señor."
            except Exception as e:
                response = f"Hubo un error en los núcleos de procesamiento: {e}"
                
            # Hablamos la respuesta
            speak(response)
            time.sleep(0.5)

if __name__ == "__main__":
    main()
