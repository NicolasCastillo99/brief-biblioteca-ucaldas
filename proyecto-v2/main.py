import uvicorn
from fastapi import FastAPI

from app.config import DEBUG, HOST, PORT
from app.database import DatabaseManager
from app.routes import estudiantes, libros, prestamos

app = FastAPI(
    title="Sistema de Prestamo de Libros",
    description="API REST para gestion de prestamos en biblioteca universitaria",
    version="1.0.0",
)

app.include_router(libros.router)
app.include_router(prestamos.router)
app.include_router(estudiantes.router)


@app.on_event("startup")
def startup() -> None:
    """Inicializar SQLite y crear tablas automaticamente."""
    DatabaseManager.initialize_database()


@app.get("/", tags=["root"])
def read_root():
    """Endpoint raiz de la API."""
    return {
        "mensaje": "Bienvenido al Sistema de Prestamo de Libros",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check del servidor."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
