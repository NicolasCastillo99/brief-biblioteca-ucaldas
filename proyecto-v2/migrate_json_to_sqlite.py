"""
Migracion unica desde archivos JSON locales hacia SQLite.

Uso:
    python migrate_json_to_sqlite.py
    python migrate_json_to_sqlite.py path/a/json_data path/a/biblioteca.sqlite3
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from app.database import DatabaseManager
from app.models.entities import Ejemplar, Estudiante, Libro, Multa, Prestamo
from app.repositories.ejemplar_repository import EjemplarRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.libro_repository import LibroRepository
from app.repositories.multa_repository import MultaRepository
from app.repositories.prestamo_repository import PrestamoRepository


def _load_json_file(file_path: Path) -> list[dict[str, Any]]:
    if not file_path.exists():
        return []

    data = json.loads(file_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "data", file_path.stem):
            value = data.get(key)
            if isinstance(value, list):
                return value
    raise ValueError(f"Estructura JSON no soportada en {file_path}")


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _normalize_libro(item: dict[str, Any]) -> Libro:
    return Libro(
        id=str(item["id"]),
        titulo=item["titulo"],
        autor=item["autor"],
        ubicacion=item.get("ubicacion", "Sin ubicacion"),
        alta_demanda=bool(item.get("alta_demanda", False)),
    )


def _normalize_ejemplar(item: dict[str, Any]) -> Ejemplar:
    return Ejemplar(
        id=str(item["id"]),
        libro_id=str(item["libro_id"]),
        estado=item.get("estado", "disponible"),
    )


def _normalize_estudiante(item: dict[str, Any]) -> Estudiante:
    return Estudiante(
        id=str(item["id"]),
        nombre=item["nombre"],
        programa=item.get("programa") or item.get("carrera", "Sin programa"),
        semestre=int(item.get("semestre", 1)),
        tipo=item.get("tipo") or item.get("tipo_estudiante", "pregrado"),
        multas_pendientes=float(item.get("multas_pendientes", 0.0)),
    )


def _normalize_prestamo(item: dict[str, Any]) -> Prestamo:
    fecha_prestamo = _parse_date(item.get("fecha_prestamo")) or date.today()
    fecha_esperada = _parse_date(item.get("fecha_devolucion_esperada"))
    if fecha_esperada is None:
        fecha_esperada = _parse_date(item.get("fecha_devolucion"))
    if fecha_esperada is None:
        fecha_esperada = fecha_prestamo + timedelta(days=15)

    return Prestamo(
        id=str(item["id"]),
        estudiante_id=str(item["estudiante_id"]),
        ejemplar_id=str(item["ejemplar_id"]),
        fecha_prestamo=fecha_prestamo,
        fecha_devolucion_esperada=fecha_esperada,
        fecha_devolucion_real=_parse_date(item.get("fecha_devolucion_real")),
        estado=item.get("estado", "activo"),
        renovado=bool(item.get("renovado", False)),
    )


def _normalize_multa(item: dict[str, Any]) -> Multa:
    return Multa(
        id=str(item["id"]),
        estudiante_id=str(item["estudiante_id"]),
        prestamo_id=str(item["prestamo_id"]),
        monto=float(item.get("monto", 0)),
        dias_retraso=int(item.get("dias_retraso", 0)),
        pagada=bool(item.get("pagada", False)),
    )


def migrate_json_directory(json_dir: str | Path, db_path: str | None = None) -> dict[str, int]:
    """
    Lee la persistencia legada en JSON y la inserta en SQLite.

    El directorio debe contener archivos como:
    - libros.json
    - ejemplares.json
    - estudiantes.json
    - prestamos.json
    - multas.json
    """

    source_dir = Path(json_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"No existe el directorio origen: {source_dir}")

    DatabaseManager.initialize_database(db_path)

    libro_repo = LibroRepository(db_path=db_path)
    ejemplar_repo = EjemplarRepository(db_path=db_path)
    estudiante_repo = EstudianteRepository(db_path=db_path)
    prestamo_repo = PrestamoRepository(db_path=db_path)
    multa_repo = MultaRepository(db_path=db_path)

    summary = {
        "libros": 0,
        "ejemplares": 0,
        "estudiantes": 0,
        "prestamos": 0,
        "multas": 0,
    }

    for item in _load_json_file(source_dir / "libros.json"):
        libro = _normalize_libro(item)
        if not libro_repo.exists(libro.id):
            libro_repo.create(libro, libro.id)
            summary["libros"] += 1

    for item in _load_json_file(source_dir / "estudiantes.json"):
        estudiante = _normalize_estudiante(item)
        if not estudiante_repo.exists(estudiante.id):
            estudiante_repo.create(estudiante, estudiante.id)
            summary["estudiantes"] += 1

    for item in _load_json_file(source_dir / "ejemplares.json"):
        ejemplar = _normalize_ejemplar(item)
        if not ejemplar_repo.exists(ejemplar.id):
            ejemplar_repo.create(ejemplar, ejemplar.id)
            summary["ejemplares"] += 1

    for item in _load_json_file(source_dir / "prestamos.json"):
        prestamo = _normalize_prestamo(item)
        if not prestamo_repo.exists(prestamo.id):
            prestamo_repo.create(prestamo, prestamo.id)
            summary["prestamos"] += 1

    for item in _load_json_file(source_dir / "multas.json"):
        multa = _normalize_multa(item)
        if not multa_repo.exists(multa.id):
            multa_repo.create(multa, multa.id)
            summary["multas"] += 1

    return summary


if __name__ == "__main__":
    json_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/json")
    db_path = sys.argv[2] if len(sys.argv) > 2 else None
    result = migrate_json_directory(json_dir, db_path)
    print("Migracion completada:")
    for key, value in result.items():
        print(f"  - {key}: {value}")
