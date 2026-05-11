# TeleECOE - Guía completa del sistema

Este documento explica en lenguaje natural qué es TeleECOE, qué tiene, qué hace y cómo funciona. Está pensado para que el usuario pueda leerlo completo y luego pedir cambios con contexto, por ejemplo: “cambia esto”, “quita esto”, “mejora esta parte” o “agrega esta función”.

> Nombre anterior del proyecto: `SistemaEvaluacion v2`.
> Nombre de trabajo desde ahora: **TeleECOE**.

## 1. Qué es TeleECOE

TeleECOE es una aplicación web local para gestionar y ejecutar evaluaciones clínicas/educativas por estaciones, usando una computadora principal como servidor y tablets como dispositivos de evaluación.

El sistema permite:

- Registrar alumnos.
- Registrar estaciones de evaluación.
- Crear rúbricas por estación.
- Evaluar alumnos desde tablets.
- Guardar puntajes y detalles de cada evaluación.
- Consultar resultados desde una pantalla maestra.
- Ver analítica básica.
- En la estación RCP, grabar evidencia de video asociada a la evaluación.

La idea central es apoyar una dinámica tipo ECOE/OSCE: varios alumnos pasan por estaciones y evaluadores registran desempeño en formularios específicos.

## 2. Cómo se usa en la práctica

El escenario esperado es:

1. Una laptop o PC funciona como **computadora maestra**.
2. Esa computadora ejecuta TeleECOE.
3. Las tablets se conectan a la misma red local.
4. Desde la PC maestra se administra el sistema.
5. Desde las tablets se elige una estación, se selecciona un alumno y se registra la evaluación.
6. Los resultados quedan guardados en una base de datos SQLite local.
7. Para la estación RCP, el sistema puede iniciar grabación de cámara y asociar el video al alumno evaluado.

## 3. Usuarios del sistema

### Administrador o coordinador

Usa la PC maestra para:

- Ver el tablero general.
- Crear y editar alumnos.
- Crear y editar estaciones.
- Configurar criterios/rúbricas.
- Revisar resultados.
- Exportar o analizar información.

### Evaluador o docente

Usa una tablet para:

- Entrar a la estación asignada.
- Seleccionar al alumno.
- Completar la rúbrica.
- Guardar la evaluación.

### Responsable técnico

Configura:

- Red local.
- Cámara.
- go2rtc.
- FFmpeg.
- Base de datos.
- Backups.
- Publicación futura en GitHub.

## 4. Módulos principales

TeleECOE tiene tres grandes módulos funcionales:

1. **Master / Administración**
2. **Tablet / Evaluación**
3. **Analytics / Reportes**

Además tiene un subsistema especial para:

4. **Cámara y grabación RCP**

## 5. Módulo Master / Administración

Este módulo es la pantalla principal de control.

Permite ver el estado general de alumnos y estaciones, incluyendo qué evaluaciones ya están registradas y qué puntajes existen.

Funciones principales:

- Dashboard general.
- Gestión de alumnos.
- Gestión de estaciones.
- Constructor de rúbricas.
- Acceso a reportes/exportación.

### 5.1 Dashboard principal

Es la entrada principal del sistema.

Muestra una matriz o resumen donde se relacionan alumnos con estaciones. Sirve para saber quién ya fue evaluado, en qué estación y con qué resultado.

### 5.2 Gestión de alumnos

Permite:

- Crear alumnos.
- Editar datos de alumnos.
- Eliminar alumnos.
- Asociar alumnos a grupos.

Datos conocidos del modelo de alumno:

- Nombre.
- CMP u otro identificador similar.
- Grupo.

### 5.3 Gestión de estaciones

Permite:

- Crear estaciones.
- Editar estaciones.
- Eliminar estaciones.
- Definir orden de aparición.
- Entrar al constructor de rúbrica de cada estación.

Datos conocidos de una estación:

- ID interno.
- Nombre.
- Orden.

### 5.4 Constructor de rúbricas

Permite crear la estructura de evaluación de cada estación.

Una estación contiene categorías. Cada categoría contiene criterios.

Tipos de criterios/categorías conocidos:

- Checkbox o criterio marcado/no marcado.
- Rango numérico.
- Selección única.

El puntaje final de una evaluación se calcula sumando los puntos de criterios marcados o valores seleccionados, según el tipo.

## 6. Módulo Tablet / Evaluación

Este módulo está pensado para usarse desde tablets.

Flujo típico:

1. El evaluador abre la URL de tablets.
2. Selecciona una estación.
3. Selecciona un alumno.
4. Inicia la evaluación.
5. Completa la rúbrica.
6. Guarda la evaluación.
7. El sistema muestra una pantalla de éxito.

### 6.1 Selección de estación

La tablet muestra las estaciones disponibles. El evaluador elige la estación que le corresponde.

### 6.2 Selección de alumno

Luego se muestra la lista de alumnos. El evaluador selecciona el alumno a evaluar.

El sistema también puede indicar si un alumno ya tiene evaluación registrada para esa estación.

### 6.3 Formulario de evaluación

El formulario muestra las categorías y criterios configurados para la estación.

Según el tipo de criterio, el evaluador puede:

- Marcar/desmarcar criterios.
- Elegir un valor de rango.
- Seleccionar una opción única.

Al guardar, el sistema:

- Crea o actualiza la evaluación.
- Borra detalles anteriores si se está editando.
- Guarda los nuevos detalles.
- Calcula puntaje total.
- Redirige a pantalla de éxito.

### 6.4 Edición de evaluación existente

Si un alumno ya tiene evaluación, el sistema puede entrar en modo edición. Al guardar, reemplaza los detalles anteriores por los nuevos.

### 6.5 Reinicio de evaluación

Existe una función para borrar una evaluación de un alumno en una estación y permitir evaluarlo nuevamente.

## 7. Estación RCP y video

La estación RCP tiene comportamiento especial porque integra cámara y grabación.

Estado actual esperado:

- Usa una sola cámara: `camara1`.
- La cámara se visualiza mediante go2rtc.
- La grabación se realiza con FFmpeg desde el RTSP local de go2rtc.
- El video se guarda como MP4.
- El video se asocia al campo `video_camara1` de la evaluación.
- `video_camara2` queda en `None` porque ya no se trabaja con doble cámara.

### 7.1 Flujo de RCP

Cuando el evaluador entra a RCP:

1. Ve el nombre del alumno.
2. Ve el visor de cámara.
3. Antes de mostrar el formulario completo, aparece un botón para iniciar evaluación y grabación.
4. Al presionar iniciar, el sistema intenta arrancar FFmpeg.
5. Si la grabación inicia correctamente, se muestra la rúbrica.
6. Al guardar la evaluación, el sistema intenta detener la grabación y cerrar el MP4.
7. El archivo de video queda vinculado a la evaluación.

### 7.2 Visor de cámara

El visor usa go2rtc y una plantilla específica de auto-recarga/visualización.

La intención actual es que el video sea claro y estable, sin recargas preventivas innecesarias si la transmisión está funcionando.

### 7.3 Grabación

La ruta técnica actual es:

Tuya Smart Cloud → go2rtc `camara1` → RTSP local → FFmpeg transcode → MP4

La entrada de grabación esperada es:

`rtsp://127.0.0.1:8554/camara1`

El método actual usa FFmpeg con:

- RTSP por TCP.
- Descarte de frames corruptos.
- Ignorar ciertos errores de stream.
- FPS objetivo de 15.
- Escala 640px de ancho aproximado.
- Codificación H.264.
- `+faststart` para MP4.

### 7.4 Warm-up

Se agregó un warm-up de 5 segundos.

Razón:

La cámara Tuya/go2rtc puede entregar frames iniciales con artefactos o corrupción visual. Descartar los primeros segundos ayudó en pruebas aisladas a obtener videos más coherentes.

## 8. Módulo Analytics / Reportes

Este módulo permite revisar resultados.

Funciones conocidas:

- Dashboard analítico.
- Resumen global.
- Análisis por ítem/criterio.
- Distribución por estación.
- Exportación CSV.

El objetivo es ayudar a ver desempeño general y detectar criterios con mayor tasa de fallo/acierto.

Pendiente conocido:

- Revisar que todos los filtros funcionen correctamente.
- Revisar bug de exportación desde el dashboard principal.

## 9. Datos que maneja TeleECOE

Modelo general:

### Alumno

Representa a una persona evaluada.

Campos conocidos:

- `id`
- `nombre`
- `cmp`
- `grupo`

### Estación

Representa una estación de evaluación.

Campos conocidos:

- `id`
- `nombre`
- `orden`

### Categoría

Agrupa criterios dentro de una estación.

Campos conocidos:

- estación asociada
- nombre
- orden
- tipo

### Criterio

Elemento concreto que se evalúa.

Campos conocidos:

- texto
- puntos
- tipo
- opciones

### Evaluación

Resultado general de evaluar un alumno en una estación.

Campos conocidos:

- alumno
- estación
- puntaje total
- video cámara 1
- video cámara 2

### Detalle de evaluación

Registro de cada criterio completado dentro de una evaluación.

Campos conocidos:

- evaluación asociada
- criterio asociado
- valor registrado

## 10. Base de datos

TeleECOE usa SQLite local.

Archivo real actual:

`evaluaciones.db`

Este archivo no se versiona en Git porque contiene datos reales/operativos.

Conteo detectado previamente en la base actual:

- 34 alumnos.
- 10 estaciones.
- 44 categorías.
- 208 criterios.
- 309 evaluaciones.
- 4740 detalles.

Estos números describen el estado de una base concreta y pueden cambiar.

## 11. Archivos y carpetas importantes

### Código principal

- `run.py`: arranque de la aplicación.
- `app/__init__.py`: creación/configuración Flask.
- `extensions.py`: inicialización de SQLAlchemy.
- `app/models/models.py`: modelos de datos.

### Rutas

- `app/routes/master.py`: administración y dashboard principal.
- `app/routes/tablet.py`: flujo de tablets y grabación RCP.
- `app/routes/analytics.py`: reportes y exportación.

### Templates

- `app/templates/base.html`: plantilla base.
- `app/templates/master_dashboard.html`: dashboard principal.
- `app/templates/master_alumnos.html`: alumnos.
- `app/templates/master_estaciones.html`: estaciones.
- `app/templates/master_constructor.html`: constructor de rúbricas.
- `app/templates/tablet_index.html`: selección de estación.
- `app/templates/tablet_seleccionar.html`: selección de alumno.
- `app/templates/tablet_evaluar.html`: formulario de evaluación.
- `app/templates/tablet_exito.html`: confirmación.
- `app/templates/analytics_dashboard.html`: analítica.
- `app/templates/camera_auto_reload.html`: visor de cámara.

### Configuración segura de ejemplo

- `.env.example`: variables de entorno sin secretos.
- `go2rtc.example.yaml`: ejemplo seguro de configuración de cámara.

### Documentación de trabajo

- `docs/TELEECOE_GUIA_COMPLETA.md`: este documento.
- `docs/CAMBIOS_SOLICITADOS.md`: lugar para pedir cambios concretos.
- `docs/PRODUCT_SPEC.md`: especificación viva del producto.
- `docs/DECISION_LOG.md`: decisiones importantes.
- `docs/IMPLEMENTATION_PLAN.md`: planificación técnica.
- `docs/PROJECT_STATUS.md`: estado técnico actual.
- `docs/GITHUB_SETUP.md`: preparación Git/GitHub.

## 12. Archivos que NO deben subirse a GitHub

Por seguridad o tamaño, no deben versionarse:

- `.env`
- `go2rtc.yaml`
- archivos `go2rtc.yaml*` reales
- `evaluaciones.db`
- grabaciones MP4
- logs
- backups
- venvs
- `tools/`
- `go2rtc.exe`
- scripts locales con credenciales o IPs sensibles, como `auto_update_camaras.py`

## 13. Configuración actual del repositorio

TeleECOE ya tiene Git local inicializado.

Rama principal:

`main`

Commits base relevantes:

- `7365f9e Preparar proyecto para versionado seguro`
- `f030069 Agregar flujo de cambios en Markdown`

GitHub aún no se ha creado ni conectado. La recomendación es que el primer repositorio remoto sea privado.

## 14. Cómo se piden cambios desde ahora

El flujo acordado es:

1. Leer este documento para entender el sistema.
2. Escribir cambios concretos en `docs/CAMBIOS_SOLICITADOS.md`.
3. Avisar en el chat administrativo: “ya edité cambios”.
4. LUCINA revisa el diff contra Git.
5. LUCINA interpreta qué se pide.
6. Si hay dudas críticas, pregunta.
7. Si está claro, implementa.
8. Verifica.
9. Hace commit.

Este chat queda para instrucciones de alto nivel, administración, aprobaciones y decisiones.

## 15. Estado técnico actual conocido

### Ya preparado

- Proyecto en Git local.
- `.gitignore` protege secretos y archivos pesados.
- Documentación base creada.
- App lee varias configuraciones desde `.env`/entorno.
- RCP adaptado a una cámara.
- Grabación por FFmpeg RTSP transcode.
- Warm-up integrado.

### Pendiente funcional importante

Hay que repetir la prueba integrada final de RCP con warm-up.

La última prueba integrada generó un MP4 inválido con error `moov atom not found`. La interpretación más probable es cierre incompleto del archivo durante apagado/reinicio.

Para validar correctamente:

1. Levantar go2rtc.
2. Levantar Flask.
3. Iniciar grabación corta desde endpoint/API.
4. Detener grabación con endpoint/API.
5. Confirmar `returncode=0`.
6. Confirmar que `ffprobe` acepta el archivo.
7. Confirmar que existe átomo `moov`.
8. Confirmar decode sin warnings.
9. Extraer o revisar frames.

Si vuelve a fallar con `moov atom not found`, hay que robustecer el cierre de grabación: esperar mejor al proceso, usar archivo temporal `.part` y renombrar solo cuando el MP4 cierre correctamente, o mejorar el manejo de señales a FFmpeg.

## 16. Riesgos y deudas conocidas

### Seguridad

- Falta autenticación.
- Falta control de roles.
- Falta CSRF en formularios/rutas destructivas.
- Algunas rutas permiten eliminar datos.
- No debe exponerse a Internet en el estado actual.

### Producción

- Hay que asegurar `debug=False` fuera de pruebas.
- Falta estrategia formal de backup.
- Falta política de retención de videos.
- Falta empaquetado o instalación final clara para operación real.

### Frontend/offline

- Bootstrap/Chart.js dependen de CDN.
- Para uso sin Internet conviene vendorizarlos localmente.

### Reportes

- Revisar bug de exportación desde dashboard principal.
- Revisar filtros de analytics.

### Cámara

- Tuya Cloud puede introducir latencia, cortes o artefactos.
- Para evaluación formal robusta, una fuente local RTSP/ONVIF/USB sería mejor que nube Tuya.

### Procesos FFmpeg

- Si Flask se reinicia durante una grabación, puede perder referencia al proceso.
- Podrían quedar procesos huérfanos o archivos incompletos.

## 17. Ideas naturales de mejora

Posibles líneas de evolución:

- Renombrar visualmente toda la app a TeleECOE.
- Crear pantalla de configuración inicial.
- Crear login/admin/evaluador.
- Mejorar constructor de rúbricas.
- Agregar respaldo automático de base de datos.
- Agregar exportación completa y reportes imprimibles.
- Mejorar modo offline.
- Crear instalador o launcher para Windows.
- Crear monitoreo de cámara antes de iniciar evaluación.
- Mejorar cierre seguro de grabaciones.
- Crear página de diagnóstico técnico.
- Integrar GitHub Issues cuando el repo remoto exista.

## 18. Cómo editar este documento

Este documento también puede modificarse si algo está incompleto o incorrecto.

Si el usuario lee esta guía y quiere cambiar una descripción general del sistema, puede editar este archivo directamente.

Si quiere pedir una modificación concreta del producto, es mejor escribirla en:

`docs/CAMBIOS_SOLICITADOS.md`

Ejemplo de pedido:

> En la sección RCP dices que primero aparece el botón de iniciar grabación. Quiero que antes de ese botón haya una comprobación visual de cámara con estado “cámara conectada”. Agregar eso como mejora prioritaria.

Ese tipo de pedido debe ir a `CAMBIOS_SOLICITADOS.md` para que pueda analizarse, implementarse y commitearse.
