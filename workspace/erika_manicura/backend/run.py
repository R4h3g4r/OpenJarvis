import uvicorn

if __name__ == "__main__":
    # Levanta el servidor FastAPI en el puerto 8000 con recarga automática para desarrollo
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
