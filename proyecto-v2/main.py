import uvicorn
from fastapi import FastAPI
from app.config import DEBUG, PORT, HOST
from app.routes import libros, prestamos, estudiantes

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Préstamo de Libros",
    description="API REST para gestión de préstamos en biblioteca universitaria",
    version="1.0.0",
)

# Registrar routers
app.include_router(libros.router)
app.include_router(prestamos.router)
app.include_router(estudiantes.router)


@app.get("/", tags=["root"])
def read_root():
    """Endpoint raíz de la API"""
    return {
        "mensaje": "Bienvenido al Sistema de Préstamo de Libros",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check del servidor"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
