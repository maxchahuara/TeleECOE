# Changelog

## Sin publicar

### Preparación de repositorio

- Agregado `.gitignore` para excluir secretos, bases de datos, grabaciones, logs, entornos virtuales, backups y binarios pesados.
- Agregado `.env.example` para configuración local segura.
- Agregado `go2rtc.example.yaml` como plantilla sin credenciales.
- Agregado `README.md` con instalación, ejecución, estado actual y advertencias.
- Agregado `SECURITY.md` con lineamientos de seguridad.

### RCP / cámara

- Estación RCP orientada a una sola cámara (`camara1`).
- Grabación por FFmpeg RTSP transcode.
- Warm-up configurable para descartar frames iniciales del stream.
