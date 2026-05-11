@echo off
echo Creando estructura del proyecto SistemaEvaluacion...

:: Crear carpeta principal si no existe (aunque deberias estar dentro de ella)
if not exist "app" mkdir app
if not exist "app\routes" mkdir app\routes
if not exist "app\models" mkdir app\models
if not exist "app\static" mkdir app\static
if not exist "app\static\css" mkdir app\static\css
if not exist "app\templates" mkdir app\templates

echo Creando archivos vacios iniciales para evitar errores de importacion...
type NUL > app\__init__.py
type NUL > app\routes\__init__.py
type NUL > app\routes\master.py
type NUL > app\routes\tablet.py
type NUL > app\models\__init__.py

echo.
echo Estructura creada exitosamente.
echo Ahora sigue los pasos en el chat para crear el entorno virtual.
pause