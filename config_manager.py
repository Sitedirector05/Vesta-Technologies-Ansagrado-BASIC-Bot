import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa el gestor de configuración"""
        self.local_config = {}
        self.last_update = datetime.now(timezone.utc)
        self.db = None
        self._init_database()
    
    def _init_database(self):
        """Inicializa la conexión a MongoDB"""
        try:
            mongo_uri = os.getenv('MONGODB_URI')
            if not mongo_uri:
                print("[!] No se encontro MONGODB_URI en las variables de entorno")
                return
                
            # Configuración de conexión con tiempo de espera más corto
            self.client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,  # 5 segundos de timeout
                connectTimeoutMS=10000,        # 10 segundos para conectar
                socketTimeoutMS=30000,         # 30 segundos para operaciones
                retryWrites=True,
                w='majority'
            )
            
            # Forzar una conexión para verificar
            self.client.admin.command('ping')
            
            # Configurar la base de datos
            self.db = self.client.get_database('ansagrado_bot')
            
            # Crear colección de configuración si no existe
            if 'config' not in self.db.list_collection_names():
                self.db.create_collection('config')
                self.db.config.insert_one({
                    '_id': 'bot_config',
                    'last_updated': datetime.now(timezone.utc),
                    'settings': {
                        'bloquear_programacion': True,
                        'palabras_clave_programacion': [
                            'programa', 'código', 'script', 'python', 'javascript',
                            'java', 'c++', 'c#', 'php', 'html', 'css', 'desarrollar',
                            'desarrollo', 'aplicación', 'app', 'web', 'página web',
                            'página', 'sitio web', 'backend', 'frontend', 'fullstack',
                            'base de datos', 'sql', 'mysql', 'mongodb', 'api', 'endpoint',
                            'función', 'método', 'clase', 'objeto', 'variable', 'constante',
                            'bucle', 'ciclo', 'condicional', 'if', 'else', 'for', 'while',
                            'switch', 'case', 'break', 'continue', 'return', 'import',
                            'from', 'as', 'def', 'function', 'class', 'try', 'except',
                            'finally', 'raise', 'throw', 'catch', 'debug', 'depurar',
                            'compilar', 'compilación', 'ejecutar', 'ejecución', 'correr',
                            'terminal', 'consola', 'comando', 'línea de comandos', 'cli',
                            'sdk', 'framework', 'librería', 'biblioteca', 'módulo',
                            'paquete', 'dependencia', 'instalar', 'instalación', 'gestor',
                            'gestión de paquetes', 'pip', 'npm', 'yarn', 'composer',
                            'git', 'github', 'gitlab', 'bitbucket', 'repositorio', 'fork',
                            'pull request', 'merge', 'commit', 'push', 'pull', 'clonar',
                            'descargar', 'subir', 'actualizar', 'actualización', 'versión',
                            'release', 'rama', 'branch', 'tag', 'versión estable', 'beta',
                            'alfa', 'desarrollo', 'producción', 'entorno', 'ambiente',
                            'dev', 'prod', 'staging', 'testing', 'pruebas', 'test',
                            'unittest', 'pytest', 'cobertura', 'coverage', 'integración',
                            'continua', 'ci/cd', 'devops', 'despliegue', 'deploy',
                            'servidor', 'servicio', 'contenedor', 'docker', 'kubernetes',
                            'nube', 'cloud', 'aws', 'azure', 'google cloud', 'firebase',
                            'autenticación', 'autorización', 'jwt', 'oauth', 'openid',
                            'token', 'sesión', 'cookie', 'cache', 'caché', 'memoria',
                            'procesamiento', 'hilo', 'thread', 'proceso', 'process',
                            'asíncrono', 'asincrónico', 'síncrono', 'sincrónico',
                            'paralelo', 'paralelismo', 'concurrencia', 'concurrente',
                            'event loop', 'bucle de eventos', 'callback', 'promesa',
                            'futuro', 'async/await', 'then/catch', 'then/finally',
                            'then/catch/finally', 'try/catch', 'try/except', 'try/finally',
                            'try/except/finally', 'throw', 'throws', 'raise', 'raise from',
                            'except as', 'except Exception as e', 'except (Exception1, Exception2) as e',
                            'finally', 'else', 'pass', 'continue', 'break', 'return',
                            'yield', 'yield from', 'generator', 'generador', 'iterador',
                            'iterable', 'iteración', 'recursión', 'recursivo', 'recursiva',
                            'algoritmo', 'estructura de datos', 'lista', 'array', 'arreglo',
                            'tupla', 'diccionario', 'conjunto', 'hash', 'tabla hash',
                            'árbol', 'grafo', 'nodo', 'hoja', 'raíz', 'padre', 'hijo',
                            'hermano', 'hermana', 'ancestro', 'descendiente', 'hoja',
                            'nodo hoja', 'nodo interno', 'nodo raíz', 'nodo padre',
                            'nodo hijo', 'nodo hermano', 'nodo hoja', 'nodo interno',
                            'nodo raíz', 'nodo padre', 'nodo hijo', 'nodo hermano',
                            'nodo hoja', 'nodo interno', 'nodo raíz', 'nodo padre',
                            'nodo hijo', 'nodo hermano', 'nodo hoja', 'nodo interno',
                            'nodo raíz', 'nodo padre', 'nodo hijo', 'nodo hermano',
                            'nodo hoja', 'nodo interno', 'nodo raíz', 'nodo padre',
                            'nodo hijo', 'nodo hermano', 'nodo hoja', 'nodo interno',
                            'nodo raíz', 'nodo padre', 'nodo hijo', 'nodo hermano',
                            'nodo hoja', 'nodo interno', 'nodo raíz', 'nodo padre',
                            'nodo hijo', 'nodo hermano', 'nodo hoja', 'nodo interno',
                            'nodo raíz', 'nodo padre', 'nodo hijo', 'nodo hermano'
                        ],
                        'mensaje_bloqueo_programacion': (
                            "🚫 *Mensaje bloqueado por el sistema de seguridad de Ansagrado Intelligence Pro+*\n\n"
                            "🔒 **¡Esta función está disponible solo en la versión premium!**\n"
                            "*Desbloquea la versión premium de Ansagrado Intelligence Pro+ para poder utilizar esta función.\n"
                            "AntiBlocker by Vestá Technologies*"
                        )
                    }
                })
            
            print("[+] Configuracion de MongoDB inicializada correctamente")
            return True
            
        except Exception as e:
            print(f"[!] Error al conectar a MongoDB: {e}")
            self.client = None
            self.db = None
            return False
    
    async def get_config(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración"""
        try:
            if self.db:
                config = self.db.config.find_one({'_id': 'bot_config'})
                if config and key in config.get('settings', {}):
                    return config['settings'][key]
            return self.local_config.get(key, default)
        except Exception as e:
            print(f"Error al obtener configuración: {e}")
            return default
    
    async def set_config(self, key: str, value: Any) -> bool:
        """Establece un valor de configuración"""
        try:
            self.local_config[key] = value
            if self.db:
                self.db.config.update_one(
                    {'_id': 'bot_config'},
                    {'$set': {
                        f'settings.{key}': value,
                        'last_updated': datetime.now(timezone.utc)
                    }},
                    upsert=True
                )
            self.last_update = datetime.now(timezone.utc)
            return True
        except Exception as e:
            print(f"Error al actualizar configuración: {e}")
            return False
    
    async def reload_config(self):
        """Recarga la configuración desde la base de datos"""
        try:
            if self.db:
                config = self.db.config.find_one({'_id': 'bot_config'})
                if config and 'settings' in config:
                    self.local_config.update(config['settings'])
                    self.last_update = config.get('last_updated', datetime.now(timezone.utc))
                    return True
            return False
        except Exception as e:
            print(f"Error al recargar configuración: {e}")
            return False

# Instancia global del gestor de configuración
config_manager = ConfigManager()
