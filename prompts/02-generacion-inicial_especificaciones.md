# Prompt #1

**Fecha y hora:** 2026-05-12 10:30

**Propósito en una línea:** Generar la arquitectura y estructura inicial del proyecto API de préstamo de libros según especificación.

**Etapa del taller:** 1

**IA usada:** GitHub Copilot (Claude Haiku 4.5)

---

## Prompt enviado (literal)

```
Rol: Actúa como un Arquitecto de Software Senior y Desarrollador Backend experto en Python y FastAPI.

Contexto y Referencia:
Tu tarea es implementar un proyecto basado estrictamente en las especificaciones del archivo 02-tu-trabajo\plantilla-especificacion.md. Es obligatorio que leas y analices este archivo antes de proponer cualquier solución.

Stack Tecnológico:

Lenguaje/Framework: Python + FastAPI.

Persistencia: Datos en memoria (usar estructuras de datos de Python como diccionarios/listas). No utilizar bases de datos (SQL o NoSQL).

Seguridad: Sin autenticación ni autorización para esta fase.

Interfaz: Solo API REST (Sin frontend).

Testing: Implementar pruebas unitarias con Pytest.

Reglas Críticas de Desarrollo:

Fidelidad: No inventes funcionalidades, endpoints o lógica de negocio que no estén explícitamente detallados en la plantilla.

Estructura: Si la plantilla no define una estructura de carpetas, aplica una arquitectura limpia (p. ej., separando rutas, modelos y servicios).

Gestión de Ambigüedad: Si encuentras requisitos contradictorios o incompletos en el archivo .md, detente y solicita aclaraciones antes de proceder.

Configuración Inicial: Antes de la lógica, debes generar los archivos base: .gitignore (para Python), README.md detallado y .env.example.

Instrucción de Salida (Paso 1):
No generes el código de la lógica de negocio todavía. Tu primera respuesta debe contener:

Un breve resumen de lo que entendiste de las especificaciones leídas.

Una visualización del árbol de estructura de archivos propuesto.

Una lista de los archivos de configuración inicial que crearás.

Espera mi aprobación del árbol de archivos para proceder con la implementación.
```

---

## Resumen de la respuesta de la IA

La IA propuso una arquitectura en capas muy clara separando: modelos, repositorios, servicios, rutas y excepciones. Creó un árbol de carpetas que incluye tests organizados por categoría (test_models, test_services, test_routes). Propuso archivos de configuración (.gitignore, .env.example, requirements.txt, README.md) sin crear nada aún. Reconoció el campo faltante `Libro.alta_demanda` requerido por RN5. La IA esperó aprobación antes de implementar, siguiendo instrucciones precisas.

---

## Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.

**¿La acepté tal cual o la modifiqué?**

- [x] Tal cual.

**¿Qué aprendí de esta interacción?**

La IA es muy cuidadosa al seguir instrucciones explícitas de "no hagas esto todavía". Cuando le pido resumen + árbol + pendiente-de-aprobación, lo respeta fielmente sin pasarse de vueltas implementando código innecesario.
