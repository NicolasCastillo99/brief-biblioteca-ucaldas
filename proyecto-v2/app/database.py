from __future__ import annotations

import os
import sqlite3
from pathlib import Path


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS libros (
        id TEXT PRIMARY KEY,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        ubicacion TEXT NOT NULL,
        alta_demanda INTEGER NOT NULL DEFAULT 0 CHECK (alta_demanda IN (0, 1))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS estudiantes (
        id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        programa TEXT NOT NULL,
        semestre INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        multas_pendientes REAL NOT NULL DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ejemplares (
        id TEXT PRIMARY KEY,
        libro_id TEXT NOT NULL,
        estado TEXT NOT NULL,
        FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE ON UPDATE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS prestamos (
        id TEXT PRIMARY KEY,
        estudiante_id TEXT NOT NULL,
        ejemplar_id TEXT NOT NULL,
        fecha_prestamo TEXT NOT NULL,
        fecha_devolucion_esperada TEXT NOT NULL,
        fecha_devolucion_real TEXT,
        estado TEXT NOT NULL,
        renovado INTEGER NOT NULL DEFAULT 0 CHECK (renovado IN (0, 1)),
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id) ON DELETE RESTRICT ON UPDATE CASCADE,
        FOREIGN KEY (ejemplar_id) REFERENCES ejemplares(id) ON DELETE RESTRICT ON UPDATE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS multas (
        id TEXT PRIMARY KEY,
        estudiante_id TEXT NOT NULL,
        prestamo_id TEXT NOT NULL UNIQUE,
        monto REAL NOT NULL,
        dias_retraso INTEGER NOT NULL,
        pagada INTEGER NOT NULL DEFAULT 0 CHECK (pagada IN (0, 1)),
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id) ON DELETE RESTRICT ON UPDATE CASCADE,
        FOREIGN KEY (prestamo_id) REFERENCES prestamos(id) ON DELETE CASCADE ON UPDATE CASCADE
    )
    """,
]


class DatabaseManager:
    """Gestiona conexiones SQLite reutilizables por archivo de base de datos."""

    _connections: dict[str, sqlite3.Connection] = {}

    @classmethod
    def resolve_db_path(cls, db_path: str | None = None) -> str:
        if db_path:
            resolved_path = Path(db_path)
            if resolved_path.parent:
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
            return str(resolved_path)

        configured_path = os.getenv("SQLITE_DB_PATH")
        if configured_path:
            resolved_path = Path(configured_path)
            if resolved_path.parent:
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
            return str(resolved_path)

        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return str(data_dir / "biblioteca.sqlite3")

    @classmethod
    def get_connection(cls, db_path: str | None = None) -> sqlite3.Connection:
        resolved_path = cls.resolve_db_path(db_path)
        if resolved_path not in cls._connections:
            connection = sqlite3.connect(resolved_path, check_same_thread=False)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            cls._connections[resolved_path] = connection
            cls.initialize_database(resolved_path)
        return cls._connections[resolved_path]

    @classmethod
    def initialize_database(cls, db_path: str | None = None) -> None:
        connection = cls._connections.get(cls.resolve_db_path(db_path))
        if connection is None:
            connection = cls.get_connection(db_path)

        with connection:
            for statement in SCHEMA_STATEMENTS:
                connection.execute(statement)

    @classmethod
    def clear_database(cls, db_path: str | None = None) -> None:
        connection = cls.get_connection(db_path)
        with connection:
            connection.execute("DELETE FROM multas")
            connection.execute("DELETE FROM prestamos")
            connection.execute("DELETE FROM ejemplares")
            connection.execute("DELETE FROM estudiantes")
            connection.execute("DELETE FROM libros")

    @classmethod
    def close_connection(cls, db_path: str | None = None) -> None:
        resolved_path = cls.resolve_db_path(db_path)
        connection = cls._connections.pop(resolved_path, None)
        if connection is not None:
            connection.close()

    @classmethod
    def close_all(cls) -> None:
        for connection in cls._connections.values():
            connection.close()
        cls._connections.clear()
