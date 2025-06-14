@echo off
title Bot de Discord - Iniciando...

:: Cambiar al directorio del script
cd /d %~dp0

echo Verificando dependencias...
python -m pip install -r requirements.txt

if not exist .env (
    echo Creando archivo .env...
    echo DISCORD_TOKEN=tu_token_aquí > .env
    echo Por favor edita el archivo .env y agrega tu token de Discord
    pause
    exit /b
)

echo Iniciando el bot...
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error al iniciar el bot. Verifica los mensajes de error arriba.
    pause
)
