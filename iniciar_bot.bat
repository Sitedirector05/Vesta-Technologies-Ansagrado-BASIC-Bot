@echo off
title Controlador del Bot de Discord
:menu
cls
echo ====================================
echo    CONTROLADOR DEL BOT DE DISCORD
echo ====================================
echo.
echo 1. Iniciar el bot
echo 2. Detener el bot
echo 3. Ver estado del bot
echo 4. Instalar dependencias
echo 5. Salir
echo.
set /p opcion=Selecciona una opción (1-5): 

if "%opcion%"=="1" goto iniciar
if "%opcion%"=="2" goto detener
if "%opcion%"=="3" goto estado
if "%opcion%"=="4" goto instalar
if "%opcion%"=="5" goto salir

echo Opción no válida. Presiona cualquier tecla para continuar...
pause >nul
goto menu

:iniciar
py bot_controller.py 1
pause
goto menu

:detener
py bot_controller.py 2
pause
goto menu

:estado
py bot_controller.py 3
pause
goto menu

:instalar
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo ¡Dependencias instaladas correctamente!
pause
goto menu

:salir
exit
