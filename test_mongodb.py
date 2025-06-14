import os
import sys
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

def print_safe(text):
    """Función para imprimir texto seguro en la consola de Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Si falla, intenta con una codificación alternativa
        print(text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

# Configurar la codificación de la consola
if sys.platform == 'win32':
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, 'utf-8')

# Cargar variables de entorno
load_dotenv()

# Obtener la cadena de conexión
try:
    MONGODB_URI = os.getenv('MONGODB_URI')
    DB_NAME = os.getenv('DB_NAME', 'discord_bot')
    
    if not MONGODB_URI:
        raise ValueError("No se encontró la variable de entorno MONGODB_URI")
    
    print_safe("[*] Intentando conectar a MongoDB...")
    print_safe(f"[i] Base de datos: {DB_NAME}")
    
    # Ocultar la contraseña en el log
    safe_uri = MONGODB_URI.split('@')
    if len(safe_uri) > 1:
        print_safe(f"[i] Servidor: {safe_uri[1]}")
    else:
        print_safe(f"[i] URI: {MONGODB_URI}")
    
    # Conectar a MongoDB
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)  # 10 segundos de timeout
    
    # Verificar la conexión
    client.server_info()
    print_safe("[+] ¡Conexión exitosa a MongoDB!")
    
    # Listar las bases de datos disponibles
    print_safe("\n[i] Bases de datos disponibles:")
    for db_name in client.list_database_names():
        print_safe(f"- {db_name}")
    
    # Verificar si la base de datos existe, si no, se creará automáticamente
    db = client[DB_NAME]
    print_safe(f"\n[i] Usando base de datos: {DB_NAME}")
    
    # Listar colecciones en la base de datos
    print_safe("\n[i] Colecciones en la base de datos:")
    collections = db.list_collection_names()
    if collections:
        for collection in collections:
            print_safe(f"- {collection}")
    else:
        print_safe("- No hay colecciones (se crearán automáticamente cuando sea necesario)")
    
    # Crear una colección de prueba
    test_collection = db.test_connection
    test_collection.insert_one({"test": "Conexión exitosa", "timestamp": datetime.datetime.now(datetime.timezone.utc)})
    test_collection.delete_many({})  # Limpiar
    
    print_safe("\n[+] Configuración de MongoDB completada correctamente.")
    
except Exception as e:
    print_safe(f"\n[!] Error al conectar a MongoDB: {e}")
    print_safe("\n[!] Solución de problemas:")
    print_safe("1. Verifica que tu conexión a Internet esté activa")
    print_safe("2. Asegúrate de que tu IP esté en la lista blanca en MongoDB Atlas")
    print_safe("3. Verifica que la cadena de conexión sea correcta")
    print_safe("4. Intenta desactivar temporalmente tu firewall o antivirus")
    
    if "timed out" in str(e).lower() or "ServerSelectionTimeoutError" in str(e):
        print_safe("\n[i] El error sugiere que no se pudo conectar al servidor de MongoDB.")
        print_safe("   Verifica que la URL de conexión sea correcta y que tu IP esté en la lista blanca.")
    
    if "Authentication failed" in str(e):
        print_safe("\n[i] Error de autenticación. Verifica tu nombre de usuario y contraseña.")
        print_safe("   Recuerda que la contraseña puede contener caracteres especiales que necesitan ser codificados en la URL.")
    
    if "SSL" in str(e):
        print_safe("\n[i] Error de SSL. Intenta agregar `tls=true` o `ssl=true` a tu cadena de conexión.")

input("\nPresiona Enter para salir...")
