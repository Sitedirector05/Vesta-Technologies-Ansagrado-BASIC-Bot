@echo off
title Deteniendo Bot de Discord...

echo Buscando procesos de Python relacionados con el bot...

:: Detener cualquier instancia de main.py
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Bot de Discord" 2>nul

echo.
if %ERRORLEVEL%==0 (
    echo Bot detenido correctamente.
) else (
    echo No se encontraron instancias del bot en ejecución.
)

echo.
pause
