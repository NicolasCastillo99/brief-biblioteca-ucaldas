# Prompt #05

**Fecha y hora:** 2026-05-19 17:30  
**Propósito en una línea:** Diseñar e implementar la migración de persistencia de JSON local a SQLite en `proyecto-v2`.  
**Etapa del taller:** 4  
**IA usada:** ChatGPT Codex

---

## Objetivo

Migrar el sistema de persistencia de `proyecto-v2` desde archivos JSON locales hacia una base de datos SQLite, manteniendo la compatibilidad con las interfaces actuales de repositorios y servicios para que el cambio sea transparente para las capas superiores de la aplicación.

## Contexto

El dominio corresponde a un sistema de gestión de biblioteca universitaria. A partir del script de inicialización y de la arquitectura actual del proyecto, las entidades relevantes son:

- `Libro`: `id`, `titulo`, `autor`, `ubicacion`, `alta_demanda`
- `Ejemplar`: `id`, `libro_id`, `estado`
- `Estudiante`: `id`, `nombre`, `programa/carrera`, `semestre`, `tipo/tipo_estudiante`, `multas_pendientes`
- `Prestamo`: `id`, `estudiante_id`, `ejemplar_id`, `fecha_prestamo`, `fecha_devolucion_esperada`, `fecha_devolucion_real`, `estado`, `renovado`
- `Multa`: `id`, `estudiante_id`, `prestamo_id`, `monto`, `dias_retraso`, `pagada`

Actualmente `proyecto-v2` usa repositorios en memoria. La evolución requerida consiste en reemplazar esa persistencia por SQLite sin romper métodos existentes como `crear_libro`, `crear_estudiante`, `crear_prestamo`, `registrar_devolucion` y demás contratos consumidos por servicios y rutas.

## Instrucciones Técnicas

1. Diseñar el esquema SQL con sentencias `CREATE TABLE IF NOT EXISTS` para `libros`, `ejemplares`, `estudiantes`, `prestamos` y `multas`.
2. Declarar explícitamente:
   - `PRIMARY KEY` sobre los identificadores de cada entidad.
   - `FOREIGN KEY` entre `ejemplares.libro_id -> libros.id`.
   - `FOREIGN KEY` entre `prestamos.estudiante_id -> estudiantes.id`.
   - `FOREIGN KEY` entre `prestamos.ejemplar_id -> ejemplares.id`.
   - `FOREIGN KEY` entre `multas.estudiante_id -> estudiantes.id`.
   - `FOREIGN KEY` entre `multas.prestamo_id -> prestamos.id`.
3. Implementar un módulo compartido de conexión con `sqlite3` que:
   - habilite `PRAGMA foreign_keys = ON`;
   - cree automáticamente el archivo y las tablas al arrancar;
   - reutilice una conexión compartida por ruta de base de datos.
4. Refactorizar los repositorios para sustituir estructuras en memoria o lectura/escritura JSON por consultas SQL parametrizadas usando `?`:
   - `INSERT`
   - `SELECT`
   - `UPDATE`
   - `DELETE`
5. Mantener intactas las firmas públicas de repositorios y servicios existentes para no afectar el resto del backend.
6. Serializar correctamente tipos de dominio:
   - `bool` en `INTEGER` (`0/1`)
   - fechas en `TEXT` formato ISO (`YYYY-MM-DD`)
   - montos monetarios en `REAL`
7. Crear un script de migración única desde JSON que:
   - lea archivos como `libros.json`, `ejemplares.json`, `estudiantes.json`, `prestamos.json`, `multas.json`;
   - transforme aliases de campos cuando existan diferencias (`carrera` -> `programa`, `tipo_estudiante` -> `tipo`);
   - inserte la información en el orden correcto para respetar las llaves foráneas;
   - evite duplicados si una entidad ya existe en SQLite.
8. Ajustar inicialización, `seed_data` y pruebas para que la nueva persistencia SQLite sea consistente y repetible.

## Impacto

- Se mejora la consistencia e integridad referencial del sistema.
- La persistencia deja de depender de estructuras volátiles en memoria o archivos JSON dispersos.
- Se habilita una base sólida para consultas más complejas, auditoría y crecimiento funcional.
- El riesgo de regresión se reduce al conservar las interfaces públicas actuales.
- La migración única protege la información ya existente y facilita el cambio de versión en ambientes locales o de prueba.
