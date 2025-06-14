# Bot de Discord con Python

Un bot de Discord simple creado con Python y discord.py que puedes desplegar fácilmente en Replit.

## Características
- Responde al comando `!hola`
- Muestra información del servidor con `!info`
- Muestra ayuda con `!ayuda`

## Configuración

1. **Clona este repositorio o crea un nuevo proyecto en Replit**
   - Si usas Replit, crea un nuevo proyecto Python y sube estos archivos

2. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura el token de tu bot**
   - Abre el archivo `.env`
   - Reemplaza `tu_token_aqui` con el token de tu bot de Discord
     - Obtén el token en: [Portal de Desarrolladores de Discord](https://discord.com/developers/applications)

4. **Invita el bot a tu servidor**
   - Ve al portal de desarrolladores de Discord
   - Ve a "OAuth2" > "URL Generator"
   - Selecciona los siguientes permisos:
     - `bot`
     - `Send Messages`
     - `Read Messages/View Channels`
   - Copia la URL generada y ábrela en tu navegador
   - Selecciona el servidor donde quieres agregar el bot

5. **Ejecuta el bot**
   ```bash
   python main.py
   ```
   
   En Replit, simplemente haz clic en "Run"

## Comandos disponibles
- `!hola` - El bot te saluda
- `!info` - Muestra información del servidor
- `!ayuda` - Muestra todos los comandos disponibles

## Personalización
Puedes agregar más comandos editando el archivo `main.py`. Para más información sobre discord.py, consulta la [documentación oficial](https://discordpy.readthedocs.io/).
