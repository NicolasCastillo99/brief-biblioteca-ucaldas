## Prompt #5

**Fecha y hora:** 2026-05-19 16:56

**Proposito en una linea:** Documentar e implementar la migracion de persistencia de proyecto-v1 desde JSON o memoria local hacia SQLite.

**Etapa del taller:** 3

**IA usada:** ChatGPT Codex

---

### Prompt enviado (literal)

```
Actua como un desarrollador de software experto, especialista en arquitectura de datos y DevOps. Estoy trabajando en el desarrollo de "proyecto-v1". Necesitamos migrar nuestro sistema de persistencia de datos: actualmente el proyecto almacena y gestiona todo utilizando archivos JSON locales, y queremos pasarlo a una base de datos SQLite para mejorar la consistencia, integridad y escalabilidad del sistema.

Para este requerimiento, debes realizar obligatoriamente dos tareas: documentar el proceso segun nuestros estandares y programar la migracion completa dentro del codigo del proyecto.

TAREA 1: Documentacion en el Repositorio
- Revisar la plantilla `02-tu-trabajo\plantilla-prompts.md`.
- Revisar la carpeta `prompts/` e identificar el ultimo numero usado.
- Crear el archivo `prompts/[SIGUIENTE-NUMERO]-migracion-json-a-sqlite.md`.
- Adaptar este requerimiento tecnico a las secciones de la plantilla, dejando registro de lo que se va a implementar.

TAREA 2: Implementacion de la Migracion en `proyecto-v1`
- Disenar el esquema SQLite para reemplazar la persistencia local.
- Definir tablas, tipos de datos, llaves primarias y llaves foraneas.
- Crear un modulo de conexion y setup que inicialice automaticamente la base de datos y sus tablas al arrancar la aplicacion.
- Implementar funciones CRUD usando SQL parametrizado con `?` para evitar inyeccion SQL.
- Crear un script o funcion de migracion de una sola ejecucion para tomar los datos actuales desde JSON si existen, o desde los datos semilla actuales si no existen archivos JSON.
- Integrar `main.py` para reemplazar diccionarios globales por SQLite sin romper los endpoints existentes.
- Mantener la interfaz de negocio lo mas intacta posible.

Contexto tecnico:
- Proyecto: `proyecto-v1`.
- Framework: FastAPI.
- Persistencia actual observada: diccionarios en memoria (`libros_db`, `usuarios_db`, `prestamos_db`).
- Modelos: `Libro`, `Usuario`, `PrestamoCreate`, `Prestamo`, `PrestamoResponse`.
- Endpoints a conservar: `GET /libros`, `GET /libros/{libro_id}`, `POST /prestamos`, `POST /prestamos/{prestamo_id}/devolver`, `GET /prestamos/vigentes`, `GET /usuarios/{usuario_id}/prestamos`, `GET /health`.
- Datos semilla:
  - Clean Code, Robert C. Martin, 978-0132350884, disponible 3, total 5.
  - The Pragmatic Programmer, Andrew Hunt, 978-0201616224, disponible 2, total 3.
  - Design Patterns, Gang of Four, 978-0201633610, disponible 1, total 2.
  - Python Fluent, Luciano Ramalho, 978-1491946237, disponible 4, total 4.
  - Refactoring, Martin Fowler, 978-0201485677, disponible 0, total 2.
  - Juan Perez, juan.perez@ucaldas.edu.co, carnet 2021-001.
  - Maria Garcia, maria.garcia@ucaldas.edu.co, carnet 2021-002.
  - Carlos Lopez, carlos.lopez@ucaldas.edu.co, carnet 2022-001.

Entregables:
- Archivo Markdown de registro en `prompts/`.
- Modulo SQLite nuevo.
- Script de migracion.
- `main.py` integrado con SQLite.
- Confirmacion de pruebas o verificaciones basicas.
```

---

### Resumen de la respuesta de la IA

Creo `proyecto-v1/database.py` con esquema SQLite, conexion centralizada, `PRAGMA foreign_keys = ON`, datos semilla, migracion desde JSON y funciones CRUD con parametros `?`. Modifico `proyecto-v1/main.py` para reemplazar los diccionarios en memoria por SQLite manteniendo los endpoints principales. Creo `proyecto-v1/migrar_json_a_sqlite.py` como script de migracion idempotente y este archivo de registro en `prompts/`.

---

### Mi evaluacion

**La respuesta cumplio con lo que pedi?**

- [x] Completamente.
- [ ] Parcialmente. Falto: [...]
- [ ] No, se desvio. Hizo: [...]

**La acepte tal cual o la modifique?**

- [x] Tal cual.
- [ ] La modifique a mano. Cambios: [...]
- [ ] Le pedi correccion con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechace completamente. Razon: [...]

**Que aprendi de esta interaccion?**

Cuando el proyecto no tiene archivos JSON reales, conviene pedir una migracion que soporte JSON si aparece, pero que tambien use datos semilla para mantener la aplicacion funcional.
