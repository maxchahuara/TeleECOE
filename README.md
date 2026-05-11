# TeleECOE

Sistema web local para evaluación por estaciones, orientado a tablets y una PC maestra. Incluye administración de alumnos/estaciones/rúbricas, registro de evaluaciones, analítica básica y grabación de video para la estación RCP.

Nombre anterior del proyecto: `SistemaEvaluacion v2`.

Para entender todo el proyecto en lenguaje natural antes de pedir cambios, leer:

`docs/TELEECOE_GUIA_COMPLETA.md`

## Estado actual

Versión en preparación para control de versiones.

Trabajo reciente:

- Estación 5/RCP adaptada a **una sola cámara** (`camara1`).
- Visor de cámara vía go2rtc.
- Grabación RCP mediante FFmpeg desde RTSP local de go2rtc.
- Descarte inicial configurable del stream (`WARMUP_SECONDS`) para reducir artefactos iniciales.
- Endpoints de control de grabación: start/status/stop.
- Puntaje de categorías `seleccion_unica` corregido para sumar puntos.

Pendiente funcional principal:

- Repetir prueba integrada de grabación con warm-up y validar que el MP4 final tenga `moov`, pase `ffprobe`, decodifique sin warnings y tenga frames coherentes.

## Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite
- Jinja2 / Bootstrap
- go2rtc
- FFmpeg

## Instalación local

```bash
python3 -m venv .venv-linux
source .venv-linux/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Editar `.env` con valores locales. No subir `.env` al repositorio.

## Configuración de cámara

El archivo real `go2rtc.yaml` no se versiona porque puede contener credenciales, `device_id`, URLs Tuya o datos de red privada.

Crear una copia local desde el ejemplo:

```bash
cp go2rtc.example.yaml go2rtc.yaml
```

Luego completar `go2rtc.yaml` con la fuente real de cámara.

## Ejecución

Con el entorno virtual activo:

```bash
python run.py
```

Accesos habituales:

- PC maestra: `http://localhost:5000`
- Tablets: `http://<IP_DE_LA_PC>:5000/tablet`
- go2rtc: `http://localhost:1984`
- RTSP local esperado: `rtsp://127.0.0.1:8554/camara1`

## Datos y archivos no versionados

Por seguridad y tamaño, el repositorio excluye:

- `.env` y variantes locales.
- `go2rtc.yaml` real.
- `evaluaciones.db` y bases SQLite reales.
- Grabaciones MP4 y logs.
- Entornos virtuales.
- Backups locales.
- Binarios pesados como `go2rtc.exe` y herramientas descargadas.

## Flujo de cambios en lenguaje natural

Para no mezclar instrucciones técnicas fragmentadas en el chat, los cambios concretos del producto se escriben en Markdown dentro de `docs/`:

- `docs/CAMBIOS_SOLICITADOS.md`: pedidos concretos editables por el usuario.
- `docs/PRODUCT_SPEC.md`: especificación viva del producto.
- `docs/DECISION_LOG.md`: decisiones importantes y razones.
- `docs/IMPLEMENTATION_PLAN.md`: traducción técnica de pedidos a tareas verificables.

Flujo recomendado:

1. Editar `docs/CAMBIOS_SOLICITADOS.md`.
2. Avisar en el chat administrativo: `ya edité CAMBIOS_SOLICITADOS.md`.
3. Revisar el diff contra Git.
4. Implementar, verificar y commitear cambios.

## Preparación para GitHub

Este proyecto está preparado para Git local y futura publicación en GitHub, pero antes de hacer `push` se debe revisar:

1. Que no haya secretos en archivos versionados.
2. Que `git status` solo muestre archivos esperados.
3. Que `go2rtc.yaml`, `.env`, bases de datos y grabaciones estén ignorados.
4. Que exista una prueba funcional mínima documentada.

## Advertencia de seguridad

La versión actual está pensada para red local/controlada. Antes de exponerla fuera de una red privada hay que añadir autenticación, CSRF, manejo seguro de sesiones, configuración de producción y revisión de rutas destructivas.
