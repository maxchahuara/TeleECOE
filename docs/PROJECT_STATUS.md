# Estado del proyecto

## Objetivo inmediato

Preparar `SistemaEvaluacion v2` para trabajo continuo con Git y futura publicación en GitHub sin exponer datos sensibles.

## Estado funcional conocido

- Aplicación Flask local con módulos master, tablet y analytics.
- Base SQLite local no versionada.
- Estación RCP adaptada a una sola cámara (`camara1`).
- Grabación RCP por FFmpeg desde RTSP local de go2rtc.
- Warm-up de 5 segundos integrado para descartar frames iniciales problemáticos.

## Bloqueo/prueba pendiente

La última prueba integrada con warm-up generó un MP4 inválido (`moov atom not found`) probablemente por cierre incompleto durante apagado/reinicio. No usar esa prueba como evidencia final.

Al retomar validación funcional:

1. Levantar go2rtc y Flask.
2. Iniciar grabación corta desde `/tablet/api/record/start/rcp/<alumno_prueba>`.
3. Detener con `/tablet/api/record/stop/rcp/<alumno_prueba>`.
4. Validar:
   - `returncode=0`.
   - `ffprobe` OK.
   - MP4 con átomo `moov`.
   - Decode sin warnings.
   - Frames visibles y coherentes.

## Riesgos técnicos pendientes

- Seguridad básica pendiente: autenticación, CSRF y control de rutas destructivas.
- Uso de `debug` debe estar desactivado fuera de pruebas.
- Dependencia de Tuya Cloud/go2rtc puede introducir latencia/cortes.
- Cámara Tuya por nube es fallback; una fuente local RTSP/ONVIF/USB sería más estable para evaluación formal.
- Revisar exportación analytics y flujos CRUD antes de una versión 1.0.
