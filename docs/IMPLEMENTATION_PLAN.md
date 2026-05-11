# Plan de implementación

Este documento se usa para convertir cambios solicitados en trabajo técnico concreto.

## Flujo recomendado

1. El usuario edita `docs/CAMBIOS_SOLICITADOS.md`.
2. LUCINA revisa el diff contra Git.
3. LUCINA resume qué cambió y separa:
   - requisitos claros,
   - dudas/bloqueos,
   - riesgos,
   - archivos/funciones probablemente afectados.
4. Si no hay bloqueos, LUCINA implementa.
5. LUCINA verifica con prueba mínima.
6. LUCINA actualiza documentación si aplica.
7. LUCINA hace commit con mensaje claro.

## Estados de trabajo

- `Pendiente`: escrito pero aún no analizado.
- `En análisis`: interpretándose y convirtiéndose en plan.
- `En implementación`: código/documentación en cambio.
- `Bloqueado`: falta decisión, credencial, dato o aprobación.
- `Completado`: implementado, verificado y commiteado.

## Plantilla de plan técnico

```md
## Cambio: <título>

Origen:
- `docs/CAMBIOS_SOLICITADOS.md`, sección: `<nombre>`

Resumen:
- 

Archivos probablemente afectados:
- 

Criterios de aceptación técnicos:
- [ ] 
- [ ] 

Plan:
1. 
2. 
3. 

Pruebas/verificación:
- 

Riesgos:
- 

Estado:
- Pendiente
```

---

## Cambios en curso

## Cambio: Robustecer video RCP con temporal y validación

Origen:
- `docs/CAMBIOS_SOLICITADOS.md`, Fase 1, cambios 1, 2 y 3.

Resumen:
- Evitar que un MP4 incompleto o corrupto quede asociado como evidencia válida de RCP.

Archivos afectados:
- `app/routes/tablet.py`
- `.env.example`
- `docs/PROJECT_STATUS.md`

Criterios de aceptación técnicos:
- [x] La grabación escribe primero a archivo temporal.
- [x] El archivo final solo se publica con `os.replace` si pasa validación.
- [x] La validación revisa existencia, tamaño, duración con FFprobe y decodificación con FFmpeg.
- [x] Si falla la validación, la evaluación puede guardarse pero no queda asociada a evidencia falsa.
- [ ] Falta prueba integrada con cámara real/go2rtc.

Plan:
1. Crear archivo temporal para FFmpeg.
2. Centralizar cierre de FFmpeg.
3. Validar video antes de asociarlo.
4. Reportar estado en endpoint `/stop`.
5. Probar sintaxis y luego prueba funcional cuando cámara esté disponible.

Estado:
- En implementación / pendiente de prueba integrada.
