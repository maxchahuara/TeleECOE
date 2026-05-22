# TeleECOE

TeleECOE es un sistema web local para evaluación clínica por estaciones tipo ECOE/OSCE. Está pensado para una **PC maestra** y tablets o laptops conectadas en la misma red.

Versión actual: **1.1.0**. Historial y rollback: [`docs/VERSIONES.md`](docs/VERSIONES.md).

Incluye:

- administración de alumnos;
- creación/cierre de exámenes o convocatorias;
- importación masiva de alumnos desde archivo compatible con Excel;
- rúbricas por estación;
- evaluación en tablets;
- dashboard de calificaciones;
- analítica básica;
- estación RCP con video mediante go2rtc/FFmpeg cuando se configure cámara.

Nombre anterior: `SistemaEvaluacion v2`.

---

## Instalación rápida

### Windows

Abre PowerShell en la carpeta del proyecto:

```powershell
.\install.ps1
.\start.ps1
```

Si Windows bloquea scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

También puedes usar doble clic o consola con:

```bat
install.bat
start.bat
```

### Linux/macOS

```bash
chmod +x install.sh start.sh
./install.sh
./start.sh
```

Luego abre:

```text
http://localhost:5000
```

Para tablets en la misma red:

```text
http://IP_DE_LA_PC:5000/tablet
```

Guía completa: [`docs/INSTALLATION.md`](docs/INSTALLATION.md)

---

## Requisitos

- Python 3.10+
- Navegador moderno
- Opcional: go2rtc y FFmpeg para cámara/grabación RCP real

---

## Primer uso

El instalador crea:

- entorno virtual `.venv`;
- `.env` desde `.env.example`;
- `go2rtc.yaml` desde `go2rtc.example.yaml`;
- `evaluaciones.db` local con datos demo.

Puedes iniciar con:

```bash
./start.sh
```

o en Windows:

```powershell
.\start.ps1
```

---

## Funciones principales

### Exámenes / convocatorias

- Crear examen nuevo.
- Cerrar examen actual.
- Activar exámenes históricos.
- Eliminar exámenes no activos con confirmación.
- Mantener resultados separados por convocatoria.

### Alumnos

- Agregar manualmente.
- Importar masivamente desde CSV compatible con Excel.
- Descargar plantilla desde el panel.
- Retirar del examen activo sin borrar histórico.

### Estaciones

- Crear estaciones.
- Configurar categorías y criterios.
- Evaluar desde tablets.
- Corregir evaluaciones ya guardadas.

### RCP / video

- Visor con botones **HD | SD | HLS | WebRTC | Auto | MSE | Reconectar**.
- Grabación MP4 mediante go2rtc + FFmpeg si hay cámara configurada.
- Corrección posterior mostrando video grabado y preguntas debajo.

---

## Configuración de cámara

El archivo real `go2rtc.yaml` no se versiona porque puede contener credenciales, `device_id`, URLs Tuya o datos de red privada.

Crear localmente desde:

```bash
cp go2rtc.example.yaml go2rtc.yaml
```

Streams esperados:

```text
camara1     # HD/principal
camara1_sd  # SD/liviano opcional
```

---

## Archivos que no deben subirse a GitHub

- `.env`
- `go2rtc.yaml`
- `evaluaciones.db`
- grabaciones MP4
- logs
- backups
- entornos virtuales
- binarios descargados

Esto está cubierto por `.gitignore`, pero revisa antes de publicar.

---

## Verificación antes de publicar

Linux/macOS:

```bash
source .venv/bin/activate
python scripts/check_release.py
```

Windows:

```powershell
.\.venv\Scripts\python.exe scripts\check_release.py
```

Debe mostrar:

```text
release_check_ok=true
```

---

## Documentación útil

- [`docs/INSTALLATION.md`](docs/INSTALLATION.md) — instalación Windows/Linux/macOS.
- [`docs/VERSIONES.md`](docs/VERSIONES.md) — versiones publicadas y cómo volver a una versión estable anterior.
- [`docs/TELEECOE_GUIA_COMPLETA.md`](docs/TELEECOE_GUIA_COMPLETA.md) — guía completa en lenguaje natural.
- [`docs/EXAMENES_ALUMNOS_IMPORTACION_2026-05-12.md`](docs/EXAMENES_ALUMNOS_IMPORTACION_2026-05-12.md) — exámenes e importación.
- [`docs/RCP_VIDEO_CONFIG_HD_SD_2026-05-12.md`](docs/RCP_VIDEO_CONFIG_HD_SD_2026-05-12.md) — configuración RCP/video.

---

## Licencia

MIT. Ver [`LICENSE`](LICENSE).

---

## Seguridad

TeleECOE está pensado inicialmente para red local/controlada. Antes de exponerlo a internet se requiere autenticación, CSRF, configuración de producción y revisión de permisos.
