# Changelog

## [1.1.0] - 2026-05-22

### Agregado

- Gestión de estaciones activas/inactivas sin borrar rúbricas ni histórico.
- Selección de alumnos en tablet con grupos dinámicos, compatible con 1, 2, 3 o más grupos.
- QR y URL configurable para tablets desde el panel maestro (`TABLET_URL` opcional).
- Exportaciones Excel separadas para panel de calificaciones y dashboard analítico.
- Script USB ADB para tablets (`scripts/connect_tablet_usb.sh`).
- Script de depuración inalámbrica ADB para tablets (`scripts/connect_tablet_wireless.sh`).
- Migración idempotente para `estacion.activa`.
- Preparación de estación 5 sin cámara para pruebas de conectividad.
- Dependencia `qrcode` para generar el QR local.

### Cambiado

- Dashboard, tablet y analítica filtran estaciones activas cuando corresponde.
- La estación RCP con cámara puede deshabilitarse por configuración local sin romper estaciones sin cámara.
- El dashboard muestra una URL de tablet única, ya sea LAN/local o una URL pública temporal configurada.

### Verificado

- `scripts/check_release.py` pasa correctamente.
- Rutas locales principales responden HTTP 200: `/`, `/tablet/`, `/tablet-qr.svg`, `/estaciones`, `/analytics/`.

## [1.0.0] - 2026-05-13

### Publicado

- Primera versión pública estable en GitHub.
- Instalación multiplataforma Windows, Linux y macOS.
- Base demo reproducible, scripts de instalación/arranque/backup/verificación.
- Exámenes, alumnos, importación CSV/XLSX, estaciones, evaluación tablet, analítica y exportaciones base.
- Plantillas seguras `.env.example` y `go2rtc.example.yaml` sin credenciales.

## Historial inicial

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
