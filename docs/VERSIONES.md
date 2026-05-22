# Versiones de TeleECOE

TeleECOE usa versionado semántico:

- `MAJOR`: cambios incompatibles o reestructuración grande.
- `MINOR`: funciones nuevas compatibles.
- `PATCH`: correcciones pequeñas o mantenimiento.

## Versiones publicadas

| Versión | Fecha | Referencia Git | Estado | Resumen |
| --- | --- | --- | --- | --- |
| `v1.1.0` | 2026-05-22 | tag `v1.1.0` | Actual | Estaciones activas/inactivas, grupos dinámicos, QR tablets, export Excel separado y scripts de conexión tablet. |
| `v1.0.0` | 2026-05-13 | tag `v1.0.0` | Estable anterior | Primera publicación pública: instalación multiplataforma, base demo, exámenes, alumnos, estaciones, tablet, analítica y verificación de release. |

## Volver a una versión anterior

Para revisar una versión estable sin modificar la rama principal:

```bash
git fetch --tags
git switch --detach v1.0.0
```

Para volver a la rama actual:

```bash
git switch main
git pull
```

Para crear una rama de recuperación desde una versión anterior:

```bash
git fetch --tags
git switch -c recuperacion-v1.0.0 v1.0.0
```

## Regla operativa

Antes de publicar una nueva versión:

1. Actualizar `VERSION`.
2. Actualizar `CHANGELOG.md`.
3. Ejecutar `scripts/check_release.py`.
4. Crear commit.
5. Crear tag anotado `vX.Y.Z`.
6. Subir rama y tags a GitHub.
