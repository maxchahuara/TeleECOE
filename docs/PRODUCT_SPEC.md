# Especificación viva del producto

Este documento describe qué debe ser **TeleECOE** como producto. No es una lista de tareas diarias; es la referencia estable del sistema.

Nombre anterior del proyecto: `SistemaEvaluacion v2`.

Para una explicación completa en lenguaje natural, leer primero `docs/TELEECOE_GUIA_COMPLETA.md`.

## Propósito

Sistema local para evaluar alumnos por estaciones mediante una PC maestra y tablets, registrando puntajes, detalles de evaluación y evidencia de video cuando aplique.

## Usuarios principales

- Evaluadores/docentes que califican estaciones desde tablets.
- Administrador/coordinador que gestiona alumnos, estaciones, rúbricas y resultados desde la PC maestra.
- Responsable técnico que configura cámara, red local, go2rtc, base de datos y respaldo.

## Módulos

### Master / Administración

Responsable de:

- Ver tablero general de alumnos y estaciones.
- Crear/editar/eliminar alumnos.
- Crear/editar/eliminar estaciones.
- Construir categorías y criterios de evaluación.
- Acceder a exportación/analítica.

### Tablet / Evaluación

Responsable de:

- Seleccionar estación.
- Seleccionar alumno.
- Completar rúbricas.
- Guardar evaluación.
- En estación RCP, iniciar y detener grabación asociada.

### Analytics / Reportes

Responsable de:

- Mostrar resumen de desempeño.
- Analizar resultados por ítem/estación/grupo.
- Exportar datos para análisis externo.

### Cámara / RCP

Estado actual esperado:

- Una sola cámara activa: `camara1`.
- Fuente vía go2rtc.
- Visor en tablet.
- Grabación mediante FFmpeg desde RTSP local.
- Warm-up configurable para descartar frames iniciales.

## Reglas funcionales conocidas

- Una evaluación pertenece a un alumno y una estación.
- Una evaluación puede tener múltiples detalles.
- Las categorías `seleccion_unica` deben sumar los puntos del criterio seleccionado.
- Las grabaciones reales no forman parte del repositorio Git.
- La base SQLite real no forma parte del repositorio Git.

## Requisitos no funcionales

- Debe poder ejecutarse en red local.
- Debe funcionar con tablets conectadas a la misma red que la PC maestra.
- Debe evitar exponer secretos en Git.
- Debe ser mantenible mediante commits pequeños y trazables.

## Pendientes de definición

- Flujo de autenticación/roles.
- Estrategia de backup de base de datos y videos.
- Retención/eliminación de grabaciones.
- Modo offline completo sin CDN.
- Empaquetado/instalación final para Windows o Linux.
- Política de publicación en GitHub: privado inicialmente recomendado.
