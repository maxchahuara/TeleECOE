# Seguridad

## Secretos

No versionar ni compartir públicamente:

- `.env`
- `go2rtc.yaml`
- Credenciales Tuya/Smart Life
- URLs firmadas o tokens de cámara
- Bases de datos reales
- Grabaciones de evaluaciones
- Logs con rutas, tokens o datos personales

Usar `.env.example` y `go2rtc.example.yaml` como plantillas seguras.

## Alcance actual

La aplicación está diseñada para uso en red local/controlada. No debe exponerse a Internet sin endurecimiento previo.

Pendientes antes de producción:

- Autenticación y roles.
- Protección CSRF en formularios/rutas destructivas.
- `SECRET_KEY` fuerte desde variable de entorno.
- `debug=False` en uso real.
- Manejo de backups y retención de videos.
- Revisión de datos personales en exports y logs.
