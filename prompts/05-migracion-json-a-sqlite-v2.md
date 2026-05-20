# Prompt #05

**Fecha y hora:** 2026-05-19 17:30

**Propósito en una línea:** Documentar y registrar la migración de persistencia de `proyecto-v2` desde JSON local hacia SQLite sin romper las interfaces existentes.

**Etapa del taller:** 3

**IA usada:** ChatGPT Codex

---

### Prompt enviado (literal)

```
Actúa como un desarrollador de software experto, especialista en arquitectura de datos y prácticas DevOps. Estoy trabajando en la evolución de "proyecto-v2". Nuestro objetivo actual es migrar el sistema de persistencia: pasaremos de almacenar todo en archivos JSON locales a una base de datos SQLite para garantizar consistencia, integridad de datos y escalabilidad. 

Como contexto del dominio del problema, el sistema es una gestión de biblioteca. Basándote en nuestro script de inicialización actual, las entidades y repositorios que manejamos son:
- Libro (Campos sugeridos: id, titulo, autor, ubicacion, alta_demanda)
- Ejemplar (id, libro_id [FK], estado)
- Estudiante (id, nombre, carrera, semestre, tipo_estudiante)
- Prestamo (id, estudiante_id [FK], ejemplar_id [FK], fecha_prestamo, fecha_devolucion)
- Multa (asociada a préstamos/estudiantes)

Para cumplir con este requerimiento, debes ejecutar obligatoriamente las siguientes dos tareas en un solo turno de respuesta:

---

### TAREA 1: Documentación en el Repositorio (Sistema de Archivos)
1. **Análisis de Plantilla y Directorio:**
   - Revisa de forma simulada la estructura de la plantilla en `02-tu-trabajo/plantilla-prompts.md`.
   - Identifica el último número de prompt en la carpeta `prompts/`. Si el último archivo es, por ejemplo, `03-configurar-api.md`, el tuyo deberá iniciar con `04-`.
2. **Generación del Archivo Markdown:**
   - Redacta el contenido de un archivo técnico bajo la ruta: `prompts/[SIGUIENTE-NUMERO]-migracion-json-a-sqlite-v2.md`.
   - Estructura el archivo adaptando este requerimiento a las secciones de la plantilla (Objetivo, Contexto, Instrucciones Técnicas, Impacto).

---

### TAREA 2: Implementación de la Migración (Código de "proyecto-v2")
Desarrolla e integra el código necesario para la migración a SQLite. Debes entregar bloques de código limpios, modulares y listos para producción que cumplan con:

1. **Diseño del Esquema SQL:** Define las sentencias `CREATE TABLE` con tipos de datos correctos (`TEXT`, `INTEGER`, `REAL`), declarando explícitamente las Llaves Primarias (`PRIMARY KEY`) y Llaves Foráneas (`FOREIGN KEY`) para mantener la integridad referencial entre Libros, Ejemplares, Estudiantes, Préstamos y Multas.
2. **Módulo de Conexión y Setup:** Código (usando la librería nativa `sqlite3` de Python o el ORM del proyecto) que inicialice la base de datos y cree de forma automática las tablas si no existen al arrancar la aplicación.
3. **Refactorización de Repositorios (CRUD):** Muestra cómo se reemplazarían las funciones de lectura/escritura del JSON en los repositorios por consultas SQL parametrizadas (`INSERT`, `SELECT`, `UPDATE`, `DELETE`). Es obligatorio usar parámetros seguros (ej. `?`) para mitigar riesgos de Inyección SQL.
4. **Script de Migración Única:** Diseña una función utilitaria que lea los archivos JSON actuales, mapee/transforme los datos al nuevo esquema e inserte la información en la base de datos SQLite de manera limpia, asegurando que no se pierda la data existente.
5. **Compatibilidad de Interfaces:** Mantén intactas las firmas de los métodos actuales de los repositorios y servicios (`crear_libro`, `crear_estudiante`, etc.) para que el cambio de persistencia sea transparente y no rompa las capas superiores del backend o frontend.

---

### Entregables Esperados:
1. El contenido completo que deberá ir dentro del archivo Markdown en `prompts/`.
2. El código fuente de la solución de persistencia (módulo de conexión, ejemplos de repositorios refactorizados y el script de migración de JSON a SQLite).
```

---

### Resumen de la respuesta de la IA

Creó la capa SQLite para `proyecto-v2`, incluyendo `app/database.py` con el esquema, manejo de conexión reutilizable y `PRAGMA foreign_keys = ON`. También agregó repositorios adaptados a SQLite, el script `migrate_json_to_sqlite.py`, ajustes en `main.py`, `seed_data.py` y soporte de pruebas en `tests/conftest.py`. Además dejó este archivo en `prompts/`, pero no siguió la plantilla pedida: lo redactó como especificación técnica con secciones de Objetivo, Contexto, Instrucciones Técnicas e Impacto, en vez de registrarlo como bitácora del prompt. El commit relacionado quedó registrado como `feat: sqlite migration`.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [ ] Completamente.
- [x] Parcialmente. Faltó: seguir la estructura real de `02-tu-trabajo/plantilla-prompts.md`, registrar el prompt como bitácora y no como documento técnico.
- [ ] No, se desvió. Hizo: [...]

**¿La acepté tal cual o la modifiqué?**

- [ ] Tal cual.
- [x] La modifiqué a mano. Cambios: reescribí este archivo para ajustarlo a la plantilla, conservando la fecha y hora originales, el prompt literal y corrigiendo la etapa del taller a 3.
- [ ] Le pedí corrección con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechacé completamente. Razón: [...]

**¿Qué aprendí de esta interacción?**

Si pido que se use una plantilla, conviene validar que la IA copie no solo el tema del requerimiento sino también la estructura exacta del archivo de seguimiento.
