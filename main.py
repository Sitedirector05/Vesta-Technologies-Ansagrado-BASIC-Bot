# Configurar la codificación estándar a UTF-8
import sys
import io
import os
import logging
import asyncio
import traceback
from datetime import datetime, timezone

import discord
from discord.ext import commands
from discord import app_commands
import pytz
from dotenv import load_dotenv

# Agregar el directorio actual al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Configuración de la zona horaria
TIMEZONE_ARG = pytz.timezone('America/Argentina/Buenos_Aires')

def now_argentina():
    """Obtiene la fecha y hora actual en la zona horaria de Argentina."""
    return datetime.now(timezone.utc).astimezone(TIMEZONE_ARG)

def format_dt_argentina(dt):
    """Formatea una fecha a la zona horaria de Argentina."""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(TIMEZONE_ARG)

# Importar módulos locales
try:
    from datastore import ProvisionalDataStore as DataStore
    from commands.ahorcado import AhorcadoCog
    from commands.ping import PingCog
    from commands.rbxlookup import RobloxLookupCog
    from commands.deepseek import DeepSeekCog
except ImportError as e:
    logger.error(f"Error al importar módulos: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

class MiBot(commands.Bot):
    """Clase principal del bot que extiende la funcionalidad base."""
    
    def __init__(self):
        # Configurar intenciones
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=intents,
            activity=discord.Game(name="¡Usa /ayuda para ver los comandos!"),
            status=discord.Status.online
        )
        
        self.start_time = datetime.now(timezone.utc)
        self.datastore = DataStore()
        self.logger = logging.getLogger('bot')
    
    async def setup_hook(self):
        """Configura los cogs y comandos al iniciar el bot."""
        try:
            self.logger.info("Iniciando carga de cogs...")
            
            # Cargar cogs
            self.logger.info("Cargando AhorcadoCog...")
            await self.add_cog(AhorcadoCog(self))
            
            self.logger.info("Cargando PingCog...")
            await self.add_cog(PingCog(self))
            
            self.logger.info("Cargando RobloxLookupCog...")
            await self.add_cog(RobloxLookupCog(self))
            
            # Cargar DeepSeek solo si está configurada la API key
            if os.getenv("DEEPSEEK_API_KEY"):
                self.logger.info("Cargando DeepSeekCog...")
                await self.add_cog(DeepSeekCog(self))
            else:
                self.logger.warning("DEEPSEEK_API_KEY no configurada. El comando de DeepSeek no estará disponible.")
            
            self.logger.info("Cogs cargados correctamente")
            
            # Sincronizar comandos
            self.logger.info("Sincronizando comandos...")
            synced = await self.tree.sync()
            
            # Listar comandos sincronizados
            self.logger.info(f"Comandos sincronizados ({len(synced)}):")
            for cmd in synced:
                self.logger.info(f"- /{cmd.name}")
            
        except Exception as e:
            self.logger.error(f"Error en setup_hook: {e}")
            self.logger.error(traceback.format_exc())
    
    async def on_ready(self):
        """Evento que se dispara cuando el bot está listo."""
        self.logger.info(f'Conectado como {self.user.name} (ID: {self.user.id})')
        self.logger.info(f'Conectado a {len(self.guilds)} servidores')
        self.logger.info('¡Bot listo y funcionando!')
        
        # Establecer estado personalizado
        await self.change_presence(
            activity=discord.Game(name="¡Usa /ayuda"),
            status=discord.Status.online
        )
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Maneja errores de comandos de barra."""
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ ¡Espera {error.retry_after:.1f} segundos antes de usar este comando de nuevo!",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ No tienes permisos para usar este comando.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message(
                "❌ No tengo los permisos necesarios para ejecutar este comando.",
                ephemeral=True
            )
        else:
            self.logger.error(f'Error en el comando {interaction.command}: {error}', exc_info=error)
            try:
                await interaction.response.send_message(
                    f"❌ Ocurrió un error al ejecutar el comando: {str(error)}",
                    ephemeral=True
                )
            except:
                pass

def main():
    """Función principal para iniciar el bot."""
    # Crear instancia del bot
    bot = MiBot()
    
    # Configurar el manejador de excepciones global
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Maneja excepciones no capturadas."""
        logger.error("Excepción no capturada:", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception
    
    # Obtener el token y ejecutar el bot
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        logger.error("No se encontró el token de Discord. Asegúrate de tener un archivo .env con DISCORD_TOKEN=tu_token")
        sys.exit(1)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("Token de Discord inválido. Verifica tu token en el archivo .env")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado al iniciar el bot: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
