# Registro — Prompt #1: Generación Inicial de API

---

## Prompt #1

**Fecha y hora:** 2026-05-12 14:35

**Propósito en una línea:** Crear una API REST completa en FastAPI para gestionar préstamos de libros en una biblioteca universitaria con datos en memoria.

**Etapa del taller:** 1

**IA usada:** GitHub Copilot

---

### Prompt enviado (literal)

```
Crea la carperta proyecto-v1 en la raíz, construye una API REST en Python para gestionar préstamos de libros en una biblioteca universitaria. Necesito endpoints para listar libros, crear préstamos, devolver libros y consultar préstamos vigentes. Usa FastAPI, datos en memoria.
```

---

### Resumen de la respuesta de la IA

Creó 3 archivos: `main.py` (API con FastAPI incluyendo 6 endpoints principales), `requirements.txt` (con dependencias: FastAPI, Uvicorn, Pydantic, python-dateutil), y `README.md` (documentación completa con ejemplos de uso). La IA incluyó 5 libros y 3 usuarios precargados en memoria, implementó validaciones automáticas (disponibilidad, existencia de recursos), estados de préstamo (activo/devuelto), y fechas de vencimiento. Tomó la decisión de incluir Pydantic para validación de modelos y python-dateutil para manejo de fechas (no fue solicitado explícitamente). La API está lista para ejecutarse con documentación automática en `/docs`.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.
- [ ] Parcialmente. Faltó: [...]
- [ ] No, se desvió. Hizo: [...]

**¿La acepté tal cual o la modifiqué?**

- [x] Tal cual.
- [ ] La modifiqué a mano. Cambios: [...]
- [ ] Le pedí corrección con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechacé completamente. Razón: [...]

**¿Qué aprendí de esta interacción?**

La IA entiende bien requerimientos técnicos específicos (FastAPI, datos en memoria) cuando se menciona el framework. Incluye automáticamente features útiles sin solicitarlos (modelos Pydantic, validaciones, documentación Swagger). Un prompt conciso pero con tecnologías explícitas genera respuestas de calidad. La decisión de precargar datos de ejemplo facilita testing inmediato.

---
