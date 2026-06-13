from openjarvis.tools.audio.ear import EarTool

def run_test():
    print("Iniciando EarTool desde el paquete...")
    ear = EarTool()
    print("¡Escuchando! Habla ahora...")
    resultado = ear.execute(duration=5)
    print(f"Transcripción: {resultado.content}")

if __name__ == "__main__":
    run_test()