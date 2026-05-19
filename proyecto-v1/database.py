import json
import sqlite3
from datetime import datetime, timedelta
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

            CREATE TABLE IF NOT EXISTS estudiantes (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                programa TEXT NOT NULL,
                semestre INTEGER NOT NULL CHECK (semestre > 0),
                tipo TEXT NOT NULL CHECK (tipo IN ('pregrado', 'posgrado'))
            );

            CREATE TABLE IF NOT EXISTS api_libros (
                id TEXT PRIMARY KEY,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                sala TEXT NOT NULL,
                alta_demanda INTEGER NOT NULL CHECK (alta_demanda IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS ejemplares (
                id TEXT PRIMARY KEY,
                libro_id TEXT NOT NULL,
                estado TEXT NOT NULL CHECK (estado IN ('disponible', 'prestado', 'baja')),
                FOREIGN KEY (libro_id) REFERENCES api_libros(id)
            );

            CREATE TABLE IF NOT EXISTS api_prestamos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id TEXT NOT NULL,
                ejemplar_id TEXT NOT NULL,
                libro_id TEXT NOT NULL,
                fecha_prestamo TEXT NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                fecha_devolucion TEXT,
                estado TEXT NOT NULL CHECK (estado IN ('activo', 'devuelto', 'vencido')),
                plazo INTEGER NOT NULL,
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
                FOREIGN KEY (ejemplar_id) REFERENCES ejemplares(id),
                FOREIGN KEY (libro_id) REFERENCES api_libros(id)
            );

            CREATE TABLE IF NOT EXISTS multas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prestamo_id INTEGER NOT NULL,
                estudiante_id TEXT NOT NULL,
                dias_retraso INTEGER NOT NULL CHECK (dias_retraso >= 0),
                valor INTEGER NOT NULL CHECK (valor >= 0),
                estado TEXT NOT NULL CHECK (estado IN ('pendiente', 'pagada')),
                fecha_generacion TEXT NOT NULL,
                FOREIGN KEY (prestamo_id) REFERENCES api_prestamos(id),
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
            );

            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libro_id TEXT NOT NULL,
                estudiante_id TEXT NOT NULL,
                fecha_solicitud TEXT NOT NULL,
                estado TEXT NOT NULL CHECK (estado IN ('activa', 'cancelada', 'atendida')),
                FOREIGN KEY (libro_id) REFERENCES api_libros(id),
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
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


def crear_estudiante(estudiante: Dict[str, Any]) -> Dict[str, Any]:
    with get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO estudiantes (id, nombre, programa, semestre, tipo)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    estudiante["id"],
                    estudiante["nombre"],
                    estudiante["programa"],
                    estudiante["semestre"],
                    estudiante["tipo"],
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("estudiante_duplicado") from exc
    return obtener_estudiante(estudiante["id"]) or estudiante


def obtener_estudiante(estudiante_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM estudiantes WHERE id = ?",
            (estudiante_id,),
        ).fetchone()
    return row_to_dict(row)


def crear_api_libro(libro: Dict[str, Any]) -> Dict[str, Any]:
    with get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO api_libros (id, titulo, autor, sala, alta_demanda)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    libro["id"],
                    libro["titulo"],
                    libro["autor"],
                    libro["sala"],
                    1 if libro["alta_demanda"] else 0,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("libro_duplicado") from exc
    return obtener_api_libro(libro["id"]) or libro


def obtener_api_libro(libro_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM api_libros WHERE id = ?",
            (libro_id,),
        ).fetchone()
    return _format_api_libro(row_to_dict(row))


def listar_api_libros() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM api_libros ORDER BY id").fetchall()
    return [_format_api_libro(dict(row)) for row in rows]


def _format_api_libro(libro: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if libro is None:
        return None
    return {
        "id": libro["id"],
        "titulo": libro["titulo"],
        "autor": libro["autor"],
        "sala": libro["sala"],
        "altaDemanda": bool(libro["alta_demanda"]),
    }


def crear_ejemplar(libro_id: str, ejemplar_id: str) -> Dict[str, Any]:
    if obtener_api_libro(libro_id) is None:
        raise ValueError("libro_no_encontrado")
    with get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO ejemplares (id, libro_id, estado)
                VALUES (?, ?, ?)
                """,
                (ejemplar_id, libro_id, "disponible"),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("ejemplar_duplicado") from exc
    result = obtener_ejemplar(ejemplar_id)
    if result is None:
        raise ValueError("ejemplar_no_encontrado")
    return result


def obtener_ejemplar(ejemplar_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT e.id, e.libro_id, e.estado, l.titulo AS libro_titulo
            FROM ejemplares e
            JOIN api_libros l ON l.id = e.libro_id
            WHERE e.id = ?
            """,
            (ejemplar_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "libroId": row["libro_id"],
        "estado": row["estado"],
        "libroTitulo": row["libro_titulo"],
    }


def listar_ejemplares_libro(libro_id: str) -> List[Dict[str, Any]]:
    if obtener_api_libro(libro_id) is None:
        raise ValueError("libro_no_encontrado")
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT e.id, e.libro_id, e.estado, l.titulo AS libro_titulo
            FROM ejemplares e
            JOIN api_libros l ON l.id = e.libro_id
            WHERE e.libro_id = ?
            ORDER BY e.id
            """,
            (libro_id,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "libroId": row["libro_id"],
            "estado": row["estado"],
            "libroTitulo": row["libro_titulo"],
        }
        for row in rows
    ]


def _actualizar_prestamos_vencidos(conn: sqlite3.Connection, ahora: str) -> None:
    conn.execute(
        """
        UPDATE api_prestamos
        SET estado = 'vencido'
        WHERE estado = 'activo' AND fecha_vencimiento < ?
        """,
        (ahora,),
    )


def crear_api_prestamo(
    estudiante_id: str,
    ejemplar_id: str,
    fecha_prestamo: Optional[str] = None,
) -> Dict[str, Any]:
    fecha_inicio = datetime.fromisoformat(fecha_prestamo) if fecha_prestamo else datetime.now()
    fecha_inicio_iso = fecha_inicio.isoformat()
    ahora_iso = datetime.now().isoformat()

    with get_connection() as conn:
        _actualizar_prestamos_vencidos(conn, ahora_iso)

        estudiante = conn.execute(
            "SELECT * FROM estudiantes WHERE id = ?",
            (estudiante_id,),
        ).fetchone()
        if estudiante is None:
            raise ValueError("estudiante_no_encontrado")

        ejemplar = conn.execute(
            """
            SELECT e.id, e.estado, e.libro_id, l.titulo, l.alta_demanda
            FROM ejemplares e
            JOIN api_libros l ON l.id = e.libro_id
            WHERE e.id = ?
            """,
            (ejemplar_id,),
        ).fetchone()
        if ejemplar is None:
            raise ValueError("ejemplar_no_encontrado")

        multas_pendientes = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM multas
            WHERE estudiante_id = ? AND estado = ?
            """,
            (estudiante_id, "pendiente"),
        ).fetchone()["total"]
        if multas_pendientes:
            raise ValueError("multa_pendiente")

        vencidos = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM api_prestamos
            WHERE estudiante_id = ? AND estado = ?
            """,
            (estudiante_id, "vencido"),
        ).fetchone()["total"]
        if vencidos:
            raise ValueError("prestamo_vencido")

        if ejemplar["estado"] != "disponible":
            raise ValueError("ejemplar_no_disponible")

        activos = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM api_prestamos
            WHERE estudiante_id = ? AND estado = ?
            """,
            (estudiante_id, "activo"),
        ).fetchone()["total"]
        limite = 3 if estudiante["tipo"] == "pregrado" else 5
        if activos >= limite:
            raise ValueError("limite_prestamos")

        plazo = 3 if ejemplar["alta_demanda"] else 15
        fecha_vencimiento = fecha_inicio + timedelta(days=plazo)
        estado = "vencido" if fecha_vencimiento < datetime.now() else "activo"

        cursor = conn.execute(
            """
            INSERT INTO api_prestamos (
                estudiante_id, ejemplar_id, libro_id, fecha_prestamo,
                fecha_vencimiento, fecha_devolucion, estado, plazo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                estudiante_id,
                ejemplar_id,
                ejemplar["libro_id"],
                fecha_inicio_iso,
                fecha_vencimiento.isoformat(),
                None,
                estado,
                plazo,
            ),
        )
        conn.execute(
            "UPDATE ejemplares SET estado = ? WHERE id = ?",
            ("prestado", ejemplar_id),
        )

        prestamo_id = cursor.lastrowid

    result = obtener_api_prestamo(prestamo_id)
    if result is None:
        raise ValueError("prestamo_no_encontrado")
    return result


def obtener_api_prestamo(prestamo_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                p.id,
                p.estudiante_id,
                p.ejemplar_id,
                p.libro_id,
                p.fecha_prestamo,
                p.fecha_vencimiento,
                p.fecha_devolucion,
                p.estado,
                p.plazo,
                l.titulo AS libro_titulo
            FROM api_prestamos p
            JOIN api_libros l ON l.id = p.libro_id
            WHERE p.id = ?
            """,
            (prestamo_id,),
        ).fetchone()
    return _format_api_prestamo(row_to_dict(row))


def _format_api_prestamo(prestamo: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if prestamo is None:
        return None
    return {
        "id": prestamo["id"],
        "estudianteId": prestamo["estudiante_id"],
        "ejemplarId": prestamo["ejemplar_id"],
        "libroId": prestamo["libro_id"],
        "libroTitulo": prestamo["libro_titulo"],
        "fechaPrestamo": prestamo["fecha_prestamo"],
        "fechaVencimiento": prestamo["fecha_vencimiento"],
        "fechaDevolucion": prestamo["fecha_vencimiento"],
        "fechaDevolucionReal": prestamo["fecha_devolucion"],
        "estado": prestamo["estado"],
        "plazo": prestamo["plazo"],
    }


def devolver_api_prestamo(prestamo_id: int) -> Dict[str, Any]:
    fecha_devolucion = datetime.now()
    with get_connection() as conn:
        _actualizar_prestamos_vencidos(conn, fecha_devolucion.isoformat())
        prestamo = conn.execute(
            "SELECT * FROM api_prestamos WHERE id = ?",
            (prestamo_id,),
        ).fetchone()
        if prestamo is None:
            raise ValueError("prestamo_no_encontrado")
        if prestamo["estado"] == "devuelto":
            raise ValueError("prestamo_ya_devuelto")

        fecha_vencimiento = datetime.fromisoformat(prestamo["fecha_vencimiento"])
        dias_retraso = max((fecha_devolucion.date() - fecha_vencimiento.date()).days, 0)
        multa = dias_retraso * 2000

        conn.execute(
            """
            UPDATE api_prestamos
            SET fecha_devolucion = ?, estado = ?
            WHERE id = ?
            """,
            (fecha_devolucion.isoformat(), "devuelto", prestamo_id),
        )
        conn.execute(
            "UPDATE ejemplares SET estado = ? WHERE id = ?",
            ("disponible", prestamo["ejemplar_id"]),
        )
        if multa > 0:
            conn.execute(
                """
                INSERT INTO multas (
                    prestamo_id, estudiante_id, dias_retraso, valor,
                    estado, fecha_generacion
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    prestamo_id,
                    prestamo["estudiante_id"],
                    dias_retraso,
                    multa,
                    "pendiente",
                    fecha_devolucion.isoformat(),
                ),
            )

    result = obtener_api_prestamo(prestamo_id)
    if result is None:
        raise ValueError("prestamo_no_encontrado")
    result["multa"] = multa
    result["diasRetraso"] = dias_retraso
    result["fechaDevolucionReal"] = fecha_devolucion.isoformat()
    return result


def listar_historial_estudiante(estudiante_id: str) -> List[Dict[str, Any]]:
    if obtener_estudiante(estudiante_id) is None:
        raise ValueError("estudiante_no_encontrado")
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                p.id,
                p.estudiante_id,
                p.ejemplar_id,
                p.libro_id,
                p.fecha_prestamo,
                p.fecha_vencimiento,
                p.fecha_devolucion,
                p.estado,
                p.plazo,
                l.titulo AS libro_titulo
            FROM api_prestamos p
            JOIN api_libros l ON l.id = p.libro_id
            WHERE p.estudiante_id = ?
            ORDER BY p.id
            """,
            (estudiante_id,),
        ).fetchall()
    return [_format_api_prestamo(dict(row)) for row in rows]


def crear_reserva(libro_id: str, estudiante_id: str) -> Dict[str, Any]:
    if obtener_api_libro(libro_id) is None:
        raise ValueError("libro_no_encontrado")
    if obtener_estudiante(estudiante_id) is None:
        raise ValueError("estudiante_no_encontrado")
    fecha = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO reservas (libro_id, estudiante_id, fecha_solicitud, estado)
            VALUES (?, ?, ?, ?)
            """,
            (libro_id, estudiante_id, fecha, "activa"),
        )
        reserva_id = cursor.lastrowid
    return {
        "id": reserva_id,
        "libroId": libro_id,
        "estudianteId": estudiante_id,
        "fechaSolicitud": fecha,
        "estado": "activa",
    }


def listar_reservas_libro(libro_id: str) -> List[Dict[str, Any]]:
    if obtener_api_libro(libro_id) is None:
        raise ValueError("libro_no_encontrado")
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM reservas
            WHERE libro_id = ?
            ORDER BY id
            """,
            (libro_id,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "libroId": row["libro_id"],
            "estudianteId": row["estudiante_id"],
            "fechaSolicitud": row["fecha_solicitud"],
            "estado": row["estado"],
        }
        for row in rows
    ]


def renovar_prestamo(prestamo_id: int) -> Dict[str, Any]:
    ahora = datetime.now()
    with get_connection() as conn:
        _actualizar_prestamos_vencidos(conn, ahora.isoformat())
        prestamo = conn.execute(
            """
            SELECT p.*, l.alta_demanda
            FROM api_prestamos p
            JOIN api_libros l ON l.id = p.libro_id
            WHERE p.id = ?
            """,
            (prestamo_id,),
        ).fetchone()
        if prestamo is None:
            raise ValueError("prestamo_no_encontrado")
        if prestamo["estado"] != "activo":
            raise ValueError("prestamo_no_renovable")

        reservas = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM reservas
            WHERE libro_id = ? AND estudiante_id <> ? AND estado = ?
            """,
            (prestamo["libro_id"], prestamo["estudiante_id"], "activa"),
        ).fetchone()["total"]
        if reservas:
            raise ValueError("lista_espera")

        multas_pendientes = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM multas
            WHERE estudiante_id = ? AND estado = ?
            """,
            (prestamo["estudiante_id"], "pendiente"),
        ).fetchone()["total"]
        if multas_pendientes:
            raise ValueError("multa_pendiente")

        plazo = 3 if prestamo["alta_demanda"] else 15
        nueva_fecha = datetime.fromisoformat(prestamo["fecha_vencimiento"]) + timedelta(days=plazo)
        conn.execute(
            """
            UPDATE api_prestamos
            SET fecha_vencimiento = ?, plazo = ?
            WHERE id = ?
            """,
            (nueva_fecha.isoformat(), plazo, prestamo_id),
        )

    result = obtener_api_prestamo(prestamo_id)
    if result is None:
        raise ValueError("prestamo_no_encontrado")
    return result


def contar_api_registros() -> Dict[str, int]:
    with get_connection() as conn:
        estudiantes = conn.execute("SELECT COUNT(*) AS total FROM estudiantes").fetchone()["total"]
        api_libros = conn.execute("SELECT COUNT(*) AS total FROM api_libros").fetchone()["total"]
        ejemplares = conn.execute("SELECT COUNT(*) AS total FROM ejemplares").fetchone()["total"]
        api_prestamos = conn.execute("SELECT COUNT(*) AS total FROM api_prestamos").fetchone()["total"]
        multas = conn.execute("SELECT COUNT(*) AS total FROM multas").fetchone()["total"]
        reservas = conn.execute("SELECT COUNT(*) AS total FROM reservas").fetchone()["total"]
    return {
        "estudiantes_totales": estudiantes,
        "api_libros_totales": api_libros,
        "ejemplares_totales": ejemplares,
        "api_prestamos_totales": api_prestamos,
        "multas_totales": multas,
        "reservas_totales": reservas,
    }
