from database import migrate_json_to_sqlite


def main() -> None:
    result = migrate_json_to_sqlite()
    print("Migracion completada hacia SQLite")
    print(f"Base de datos: {result['db_path']}")
    print(f"Libros insertados: {result['libros']}")
    print(f"Usuarios insertados: {result['usuarios']}")
    print(f"Prestamos insertados: {result['prestamos']}")


if __name__ == "__main__":
    main()
