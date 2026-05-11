@echo off
setlocal enabledelayedexpansion
title Panel de Control - Sistema de Evaluacion OSCE
color 0A

cd /d "%~dp0"

:menu
cls
echo =================================================================
echo        SISTEMA DE EVALUACION MEDICA OSCE - PANEL DE CONTROL
echo =================================================================
echo.

REM Comprobar estado del servidor (busca el proceso ligado al titulo de la ventana)
tasklist /FI "WINDOWTITLE eq Servidor_OSCE*" 2>NUL | find /I "cmd.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo   ESTADO: [ EN LINEA ] El servidor esta en ejecucion.
) else (
    echo   ESTADO: [ APAGADO  ] El servidor no esta activo.
)
echo.
echo   [1] Iniciar Sistema (Abre la consola de registro del servidor)
echo   [2] Detener Sistema (Cierra el servidor de forma segura)
echo   [3] Ver si hay errores (Muestra salida del ultimo intento si aplicase)
echo   [4] Salir del Panel
echo.
echo =================================================================
set /p opcion=" Seleccione una opcion (1-4): "

if "%opcion%"=="1" goto iniciar
if "%opcion%"=="2" goto detener
if "%opcion%"=="3" goto avisos
if "%opcion%"=="4" goto salir
goto menu

:iniciar
echo.
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual en 'venv'.
    echo Asegurese de instalar las dependencias con: pip install -r requirements.txt
    pause
    goto menu
)
echo Iniciando servidor Web OSCE...
REM Abrir en una nueva ventana con titulo especifico para no bloquear el panel
start "Servidor_OSCE" cmd /k "title Servidor_OSCE & venv\Scripts\activate.bat & echo Iniciando aplicacion Flask... & python run.py"

echo.
echo Buscando y actualizando IPs de camaras ONVIF en la red...
venv\Scripts\python.exe auto_update_camaras.py
echo.

echo Iniciando servidor de Camaras (go2rtc)...
start "Servidor_Camaras" cmd /k "title Servidor_Camaras & go2rtc.exe"
echo El servidor se esta iniciando en nuevas ventanas de registro.
timeout /t 3 >nul
goto menu

:detener
echo.
echo Deteniendo servidores...
taskkill /FI "WINDOWTITLE eq Servidor_OSCE*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Servidor_Camaras*" /T /F >nul 2>&1
taskkill /IM "go2rtc.exe" /F >nul 2>&1
echo El sistema ha sido detenido por completo.
timeout /t 2 >nul
goto menu

:avisos
echo.
echo ATENCION: El archivo `app\__init__.py` tiene 0 bytes o fue vaciado.
echo Si al intentar arrancar el servidor (Opcion 1) este muestra el error:
echo   ImportError: cannot import name 'create_app' from 'app'
echo Sera necesario restaurar o escribir de nuevo la definicion de create_app() en app\__init__.py.
echo.
pause
goto menu

:salir
exit
