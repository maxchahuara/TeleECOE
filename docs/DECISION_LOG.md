# Registro de decisiones

Este documento guarda decisiones importantes del proyecto y su razón. Sirve para no rediscutir lo ya decidido.

## Formato

```md
## YYYY-MM-DD - Título de la decisión

Decisión:

Contexto:

Alternativas consideradas:

Consecuencias:
```

---

## 2026-05-11 - Renombrar el producto como TeleECOE

Decisión:
Desde este punto el sistema se referirá como **TeleECOE** en documentación y conversación de trabajo.

Contexto:
El proyecto venía con el nombre técnico/heredado `SistemaEvaluacion v2`, pero el usuario pidió renombrarlo a TeleECOE para continuar el desarrollo con una identidad más clara.

Alternativas consideradas:
- Mantener `SistemaEvaluacion v2` como nombre visible.
- Usar TeleECOE como nombre del producto, conservando temporalmente rutas/carpetas heredadas.

Consecuencias:
- La documentación nueva usará TeleECOE.
- Las rutas de carpeta pueden seguir llamándose `SistemaEvaluacion v2` por ahora para evitar cambios innecesarios o riesgosos.
- Un renombrado visual/código completo puede pedirse luego como cambio específico.

---

## 2026-05-11 - Separar chat administrativo de cambios de producto

Decisión:
Usar documentos Markdown versionados para solicitudes concretas de cambios del producto, manteniendo el chat como canal de administración, coordinación y aprobación.

Contexto:
El usuario quiere evitar dar instrucciones fragmentadas en el chat y prefiere poder editar documentos en lenguaje natural que LUCINA pueda leer, comparar contra Git e implementar.

Alternativas consideradas:
- Portal web local para editar documentos.
- GitHub Issues/Projects.
- Solo chat.
- Markdown versionado en el repositorio.

Consecuencias:
- Se empieza con Markdown + Git por simplicidad y trazabilidad.
- El portal local queda como mejora futura si el flujo manual se vuelve incómodo.
- GitHub Issues/Projects queda recomendado para después de crear el repo remoto privado.

---

## 2026-05-11 - No construir portal de edición todavía

Decisión:
No construir un portal de edición en esta etapa inicial.

Contexto:
Un portal agregaría superficie de mantenimiento y posibles problemas de seguridad antes de estabilizar la aplicación principal.

Alternativas consideradas:
- Crear portal `/admin-docs` ahora.
- Usar Markdown editable con Git.

Consecuencias:
- Se reduce complejidad inicial.
- Si el flujo con Markdown funciona, no se necesita portal.
- Si editar Markdown se vuelve incómodo, se diseñará un mini portal local posteriormente.
