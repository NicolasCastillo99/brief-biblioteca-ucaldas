# Prompt #3

**Fecha y hora:** 2026-05-12 17:15

**Propósito en una línea:** Configurar sistema de gestión de prompts con plantilla markdown para auditoría y trazabilidad de decisiones.

**Etapa del taller:** 2

**IA usada:** GitHub Copilot (Claude Haiku 4.5)

---

## Prompt enviado (literal)

```
Actúa como un gestor de archivos experto. A partir de ahora, cada respuesta que generes debe estar encapsulada en un bloque de código Markdown.

Estructura de ruta: El encabezado del bloque debe indicar que el archivo pertenece a:
(02-tu-trabajo/prompts/[nombre-del-prompt].md.

Contenido del archivo: Usa la plantilla establecida en /02-tu-trabajo/plantilla-prompts.md (Prompt #[número), Fecha y hora, Propósito en una linea, Etapa del taller A usada, Prompt enviado (literal), Resumen de la respuesta de la IA)

Historial: Comienza recuperando nuestro prompt inicial y formatéalo bajo esta estructura y genera el .md en la ruta que te dije. De aqui en adelante, cada nueva instrucción se entregará como un archivo .md independiente y se guardara en la ruta que te dije.
```

---

## Resumen de la respuesta de la IA

Leí la plantilla de prompts en 02-tu-trabajo/plantilla-prompts.md e implementé el sistema de registro. Creé bloques de código markdown mostrando la estructura de dos archivos: 01-generacion-inicial.md y 02-configuracion-archivos-prompts.md con toda la plantilla completada. Usé las 5 secciones requeridas: Prompt #, Fecha y hora, Propósito, Etapa del taller, Prompt enviado, Resumen, Mi evaluación (con checkboxes), y sección de aprendizajes. Indicó que los archivos deben crearse en 02-tu-trabajo/prompts/.

---

## Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.

**¿La acepté tal cual o la modifiqué?**

- [ ] Tal cual.
- [x] La modifiqué a mano. Cambios: Pedí que creara los archivos de verdad en la carpeta, no solo mostrarlos en bloques de código.

**¿Qué aprendí de esta interacción?**

La IA entendió el sistema de gestión pero necesitaba instrucción explícita para materializar los archivos. Cuando dije "pero crea los archivos md en la carpeta", fue claro que debía usar create_file, no solo mostrar ejemplos en markdown.
