# Preparación para Git y GitHub

## Repositorio local

Este proyecto debe versionarse desde esta carpeta:

```bash
cd "SistemaEvaluacion v2"
git status
```

No inicializar Git desde la raíz global del workspace de OpenClaw.

## Primer commit recomendado

```bash
git init
git add .
git status
git commit -m "Preparar proyecto para versionado seguro"
```

Antes del commit verificar que NO aparezcan:

- `.env`
- `go2rtc.yaml`
- `evaluaciones.db`
- `app/static/grabaciones/`
- `logs/`
- `backups/`
- `.venv/`, `.venv-linux/`, `venv/`
- `tools/`
- `go2rtc.exe`

## GitHub remoto

Cuando el usuario confirme publicación:

```bash
gh repo create SistemaEvaluacion-v2 --private --source=. --remote=origin --push
```

Recomendación inicial: crear el repositorio como **privado**. Puede volverse público después de una auditoría completa de secretos, datos personales y licencias.

## Ramas sugeridas

- `main`: versión estable.
- `develop`: integración de mejoras.
- `feature/<nombre>`: cambios puntuales.
- `fix/<nombre>`: correcciones.

## Checklist antes de publicar

- [ ] `git status` limpio.
- [ ] `git ls-files` no muestra secretos, base de datos ni videos.
- [ ] `.env.example` existe y no contiene secretos reales.
- [ ] `go2rtc.example.yaml` existe y no contiene secretos reales.
- [ ] README actualizado.
- [ ] Prueba mínima ejecutada o bloqueo documentado.
