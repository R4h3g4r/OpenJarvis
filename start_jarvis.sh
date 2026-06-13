#!/bin/bash

# Script para levantar OpenJarvis (Backend + Frontend)
# Guardar como start_jarvis.sh y ejecutar con: chmod +x start_jarvis.sh && ./start_jarvis.sh

PROJECT_ROOT="/Users/will/Documents/OpenJarvis/OpenJarvis"

echo "🚀 Iniciando el Ecosistema OpenJarvis..."

# Función para matar procesos al cerrar (limpieza)
cleanup() {
    echo "🛑 Deteniendo servicios..."
    pkill -P $$
    exit
}
trap cleanup SIGINT SIGTERM

# 1. Levantar el Backend de Python
echo "🐍 Levantando el motor de Python en el puerto 8000..."
cd $PROJECT_ROOT
source .venv/bin/activate
python -m src.openjarvis.cli serve --port 8000 &

# 2. Levantar el Frontend de Tauri/Vite
echo "🌐 Levantando la interfaz en el puerto 5173..."
cd $PROJECT_ROOT/frontend
npm run dev &

echo "✅ Todo listo. Frontend en http://localhost:5173"
echo "✅ Backend en http://localhost:8000"
echo "Presiona CTRL+C para detener todo."

# Mantener el script vivo
wait