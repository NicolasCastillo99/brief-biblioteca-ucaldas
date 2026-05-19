import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "biblioteca.db"

SEED_LIBROS = [
    {
        "id": 1,
        "titulo": "Clean Code",
        "autor": "Robert C. Martin",
        "isbn": "978-0132350884",
        "cantidad_disponible": 3,
        "cantidad_total": 5,
    },
    {
        "id": 2,
        "titulo": "The Pragmatic Programmer",
        "autor": "Andrew Hunt",
        "isbn": "978-0201616224",
        "cantidad_disponible": 2,
        "cantidad_total": 3,
    },
    {
        "id": 3,
        "titulo": "Design Patterns",
        "autor": "Gang of Four",
        "isbn": "978-0201633610",
        "cantidad_disponible": 1,
        "cantidad_total": 2,
    },
    {
        "id": 4,
        "titulo": "Python Fluent",
        "autor": "Luciano Ramalho",
        "isbn": "978-1491946237",
        "cantidad_disponible": 4,
        "cantidad_total": 4,
    },
    {
        "id": 5,
        "titulo": "Refactoring",
        "autor": "Martin Fowler",
        "isbn": "978-0201485677",
        "cantidad_disponible": 0,
        "cantidad_total": 2,
    },
]

SEED_USUARIOS = [
    {
        "id": 1,
        "nombre": "Juan Perez",
        "email": "juan.perez@ucaldas.edu.co",
        "carnet": "2021-001",
    },
    {
        "id": 2,
        "nombre": "Maria Garcia",
        "email": "maria.garcia@ucaldas.edu.co",
        "carnet": "2021-002",
    },
    {
        "id": 3,
        "nombre": "Carlos Lopez",
        "email": "carlos.lopez@ucaldas.edu.co",
        "carnet": "2022-001",
    },
]

JSON_CANDIDATES = [
    BASE_DIR / "biblioteca.json",
    BASE_DIR / "datos.json",
    BASE_DIR / "data.json",
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                isbn TEXT NOT NULL UNIQUE,
                cantidad_disponible INTEGER NOT NULL CHECK (cantidad_disponible >= 0),
                cantidad_total INTEGER NOT NULL CHECK (cantidad_total >= 0),
                CHECK (cantidad_disponible <= cantidad_total)
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                carnet TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS prestamos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libro_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                fecha_prestamo TEXT NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                fecha_devolucion TEXT,
                estado TEXT NOT NULL CHECK (estado IN ('activo', 'devuelto', 'vencido')),
                FOREIGN KEY (libro_id) REFERENCES libros(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            """
        )


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows]


def _normalize_collection(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, dict):
        return [item for item in data.values() if isinstance(item, dict)]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def _read_json_file(path: Path) -> Dict[str, List[Dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {"libros": [], "usuarios": [], "prestamos": []}

    return {
        "libros": _normalize_collection(data.get("libros", [])),
        "usuarios": _normalize_collection(data.get("usuarios", [])),
        "prestamos": _normalize_collection(data.get("prestamos", [])),
    }


def _read_legacy_json_data() -> Dict[str, List[Dict[str, Any]]]:
    for candidate in JSON_CANDIDATES:
        if candidate.exists():
            return _read_json_file(candidate)

    separate_files = {
        "libros": BASE_DIR / "libros.json",
        "usuarios": BASE_DIR / "usuarios.json",
        "prestamos": BASE_DIR / "prestamos.json",
    }
    if any(path.exists() for path in separate_files.values()):
        data: Dict[str, List[Dict[str, Any]]] = {}
        for key, path in separate_files.items():
            if path.exists():
                with path.open("r", encoding="utf-8") as file:
                    data[key] = _normalize_collection(json.load(file))
            else:
                data[key] = []
        return data

    return {"libros": SEED_LIBROS, "usuarios": SEED_USUARIOS, "prestamos": []}


def migrate_json_to_sqlite() -> Dict[str, Any]:
    init_db()
    data = _read_legacy_json_data()

    with get_connection() as conn:
        libros_count = _insert_libros(conn, data["libros"])
        usuarios_count = _insert_usuarios(conn, data["usuarios"])
        prestamos_count = _insert_prestamos(conn, data["prestamos"])

    return {
        "libros": libros_count,
        "usuarios": usuarios_count,
        "prestamos": prestamos_count,
        "db_path": str(DB_PATH),
    }


def seed_if_empty() -> None:
    init_db()
    with get_connection() as conn:
        total_libros = conn.execute("SELECT COUNT(*) AS total FROM libros").fetchone()["total"]
        total_usuarios = conn.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()["total"]
        if total_libros == 0:
            _insert_libros(conn, SEED_LIBROS)
        if total_usuarios == 0:
            _insert_usuarios(conn, SEED_USUARIOS)


def _insert_libros(conn: sqlite3.Connection, libros: List[Dict[str, Any]]) -> int:
    count = 0
    for libro in libros:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO libros (
                id, titulo, autor, isbn, cantidad_disponible, cantidad_total
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                libro["id"],
                libro["titulo"],
                libro["autor"],
                libro["isbn"],
                libro["cantidad_disponible"],
                libro["cantidad_total"],
            ),
        )
        count += cursor.rowcount
    return count


def _insert_usuarios(conn: sqlite3.Connection, usuarios: List[Dict[str, Any]]) -> int:
    count = 0
    for usuario in usuarios:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO usuarios (id, nombre, email, carnet)
            VALUES (?, ?, ?, ?)
            """,
            (usuario["id"], usuario["nombre"], usuario["email"], usuario["carnet"]),
        )
        count += cursor.rowcount
    return count


def _insert_prestamos(conn: sqlite3.Connection, prestamos: List[Dict[str, Any]]) -> int:
    count = 0
    for prestamo in prestamos:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO prestamos (
                id, libro_id, usuario_id, fecha_prestamo,
                fecha_vencimiento, fecha_devolucion, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prestamo["id"],
                prestamo["libro_id"],
                prestamo["usuario_id"],
                prestamo["fecha_prestamo"],
                prestamo["fecha_vencimiento"],
                prestamo.get("fecha_devolucion"),
                prestamo["estado"],
            ),
        )
        count += cursor.rowcount
    return count


def listar_libros() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM libros ORDER BY id").fetchall()
    return rows_to_dicts(rows)


def obtener_libro(libro_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM libros WHERE id = ?", (libro_id,)).fetchone()
    return row_to_dict(row)


def obtener_usuario(usuario_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return row_to_dict(row)


def crear_prestamo(
    libro_id: int,
    usuario_id: int,
    fecha_prestamo: str,
    fecha_vencimiento: str,
    estado: str,
) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO prestamos (
                libro_id, usuario_id, fecha_prestamo,
                fecha_vencimiento, fecha_devolucion, estado
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (libro_id, usuario_id, fecha_prestamo, fecha_vencimiento, None, estado),
        )
        conn.execute(
            """
            UPDATE libros
            SET cantidad_disponible = cantidad_disponible - 1
            WHERE id = ? AND cantidad_disponible > 0
            """,
            (libro_id,),
        )
        prestamo_id = cursor.lastrowid
        row = conn.execute(
            """
            SELECT
                p.id,
                p.libro_id,
                p.usuario_id,
                p.fecha_prestamo,
                p.fecha_vencimiento,
                p.fecha_devolucion,
                p.estado,
                l.titulo AS libro_titulo,
                u.nombre AS usuario_nombre
            FROM prestamos p
            JOIN libros l ON l.id = p.libro_id
            JOIN usuarios u ON u.id = p.usuario_id
            WHERE p.id = ?
            """,
            (prestamo_id,),
        ).fetchone()
    return dict(row)


def obtener_prestamo_response(prestamo_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                p.id,
                p.libro_id,
                p.usuario_id,
                p.fecha_prestamo,
                p.fecha_vencimiento,
                p.fecha_devolucion,
                p.estado,
                l.titulo AS libro_titulo,
                u.nombre AS usuario_nombre
            FROM prestamos p
            JOIN libros l ON l.id = p.libro_id
            JOIN usuarios u ON u.id = p.usuario_id
            WHERE p.id = ?
            """,
            (prestamo_id,),
        ).fetchone()
    return row_to_dict(row)


def devolver_prestamo(prestamo_id: int, fecha_devolucion: str) -> Dict[str, Any]:
    with get_connection() as conn:
        prestamo = conn.execute(
            "SELECT * FROM prestamos WHERE id = ?",
            (prestamo_id,),
        ).fetchone()
        if prestamo is None:
            raise ValueError("prestamo_no_encontrado")
        if prestamo["estado"] == "devuelto":
            raise ValueError("prestamo_ya_devuelto")

        conn.execute(
            """
            UPDATE prestamos
            SET fecha_devolucion = ?, estado = ?
            WHERE id = ?
            """,
            (fecha_devolucion, "devuelto", prestamo_id),
        )
        conn.execute(
            """
            UPDATE libros
            SET cantidad_disponible = cantidad_disponible + 1
            WHERE id = ?
            """,
            (prestamo["libro_id"],),
        )

    result = obtener_prestamo_response(prestamo_id)
    if result is None:
        raise ValueError("prestamo_no_encontrado")
    return result


def listar_prestamos_vigentes() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                p.id,
                p.libro_id,
                p.usuario_id,
                p.fecha_prestamo,
                p.fecha_vencimiento,
                p.fecha_devolucion,
                p.estado,
                l.titulo AS libro_titulo,
                u.nombre AS usuario_nombre
            FROM prestamos p
            JOIN libros l ON l.id = p.libro_id
            JOIN usuarios u ON u.id = p.usuario_id
            WHERE p.estado = ?
            ORDER BY p.id
            """,
            ("activo",),
        ).fetchall()
    return rows_to_dicts(rows)


def listar_prestamos_usuario(usuario_id: int, solo_vigentes: bool = True) -> List[Dict[str, Any]]:
    sql = """
        SELECT
            p.id,
            p.libro_id,
            p.usuario_id,
            p.fecha_prestamo,
            p.fecha_vencimiento,
            p.fecha_devolucion,
            p.estado,
            l.titulo AS libro_titulo,
            u.nombre AS usuario_nombre
        FROM prestamos p
        JOIN libros l ON l.id = p.libro_id
        JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.usuario_id = ?
    """
    params: List[Any] = [usuario_id]
    if solo_vigentes:
        sql += " AND p.estado = ?"
        params.append("activo")
    sql += " ORDER BY p.id"

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return rows_to_dicts(rows)


def contar_registros() -> Dict[str, int]:
    with get_connection() as conn:
        libros = conn.execute("SELECT COUNT(*) AS total FROM libros").fetchone()["total"]
        usuarios = conn.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()["total"]
        prestamos = conn.execute("SELECT COUNT(*) AS total FROM prestamos").fetchone()["total"]
    return {
        "libros_totales": libros,
        "usuarios_totales": usuarios,
        "prestamos_totales": prestamos,
    }
