import os
import sys
import subprocess
import signal
import time
import platform
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).parent
PYTHON = sys.executable or 'python'

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Muestra el menú de opciones"""
    clear_screen()
    print("""
=== CONTROLADOR DE BOT DE DISCORD ===

1. 🚀 Iniciar el bot
2. 🛑 Detener el bot
3. ℹ️  Ver estado del bot
4. 🔧 Instalar/Actualizar dependencias
5. ❌ Salir

💡 También puedes usar:
   bot_controller.py 1 - Para iniciar
   bot_controller.py 2 - Para detener
   bot_controller.py 3 - Para ver estado
""")

def get_bot_pid():
    """Obtiene el PID del proceso del bot si está en ejecución"""
    try:
        with open('bot.pid', 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None

def is_bot_running(pid):
    """Verifica si el bot está en ejecución"""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False

def start_bot():
    """Inicia el bot"""
    print("🔍 Verificando dependencias...")
    try:
        import discord
        print("✅ discord.py está instalado")
    except ImportError:
        print("❌ Error: discord.py no está instalado. Ejecuta 'pip install -r requirements.txt'")
        return

    pid = get_bot_pid()
    if pid is not None and is_bot_running(pid):
        print(f"⚠️  El bot ya está en ejecución (PID: {pid}).")
        return
    
    print("🚀 Iniciando el bot...")
    try:
        # Asegurarse de que el directorio de trabajo sea correcto
        os.chdir(BASE_DIR)
        
        # Iniciar el bot en segundo plano
        with open('bot.log', 'w', encoding='utf-8') as log_file:
            process = subprocess.Popen(
                [PYTHON, 'main.py'],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
        
        # Pequeña pausa para verificar si hay errores de inicio
        time.sleep(2)
        
        # Verificar si el proceso sigue en ejecución
        if process.poll() is not None:
            print("❌ Error al iniciar el bot. Revisa bot.log para más detalles.")
            if os.path.exists('bot.pid'):
                os.remove('bot.pid')
            return
        
        # Guardar el PID para referencia futura
        with open('bot.pid', 'w') as f:
            f.write(str(process.pid))
        
        print(f"✅ Bot iniciado con PID: {process.pid}")
        print(f"📝 Registros: {os.path.abspath('bot.log')}")
        print("💡 Usa 'python bot_controller.py 3' para ver el estado")
        
    except Exception as e:
        print(f"❌ Error al iniciar el bot: {e}")
        if os.path.exists('bot.pid'):
            os.remove('bot.pid')

def stop_bot():
    """Detiene el bot"""
    pid = get_bot_pid()
    if pid is None:
        print("ℹ️  No se encontró información del bot en ejecución.")
        return
    
    if not is_bot_running(pid):
        print(f"ℹ️  El bot no está en ejecución (PID: {pid}). Limpiando archivo PID...")
        if os.path.exists('bot.pid'):
            os.remove('bot.pid')
        return
    
    print(f"🛑 Deteniendo el bot (PID: {pid})...")
    try:
        if platform.system() == 'Windows':
            # Usar taskkill para asegurar que se cierre correctamente
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
        else:
            os.kill(pid, signal.SIGTERM)
        
        # Esperar hasta 5 segundos a que el proceso se cierre
        for _ in range(10):
            if not is_bot_running(pid):
                break
            time.sleep(0.5)
        
        if is_bot_running(pid):
            print("⚠️  No se pudo detener el bot correctamente. Intentando forzar cierre...")
            if platform.system() == 'Windows':
                subprocess.run(['taskkill', '/F', '/PID', str(pid)])
            else:
                os.kill(pid, signal.SIGKILL)
            time.sleep(1)
        
        if os.path.exists('bot.pid'):
            os.remove('bot.pid')
            print("✅ Bot detenido correctamente.")
        else:
            print("✅ Proceso del bot finalizado.")
            
    except Exception as e:
        print(f"❌ Error al detener el bot: {e}")
        print("💡 Intenta detenerlo manualmente con: taskkill /F /PID", pid)

def bot_status():
    """Muestra el estado actual del bot"""
    pid = get_bot_pid()
    
    print("\n" + "="*50)
    print(f"{'ESTADO DEL BOT':^50}")
    print("="*50)
    
    if pid is not None and is_bot_running(pid):
        print(f"🟢 Estado: EN EJECUCIÓN")
        print(f"📌 PID: {pid}")
        
        # Mostrar información del proceso
        try:
            if platform.system() == 'Windows':
                proc_info = subprocess.run(
                    ['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'CommandLine', '/value'],
                    capture_output=True, text=True, check=True
                )
                print(f"📂 Directorio: {os.path.dirname(proc_info.stdout.split('=')[1].strip())}")
        except:
            pass
            
        # Mostrar últimas líneas del log
        log_file = BASE_DIR / 'bot.log'
        if log_file.exists():
            print(f"\n📋 Últimas líneas del registro ({log_file}):")
            print("-"*50)
            try:
                with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                    print(''.join(lines[-15:]))  # Mostrar últimas 15 líneas
            except Exception as e:
                print(f"No se pudo leer el archivo de registro: {e}")
        else:
            print("ℹ️  No se encontró el archivo de registro.")
    else:
        print("🔴 Estado: DETENIDO")
        if pid is not None and not is_bot_running(pid):
            print(f"⚠️  Se encontró un PID ({pid}) pero el proceso no está en ejecución.")
            print("   Limpiando archivo PID...")
            if os.path.exists('bot.pid'):
                os.remove('bot.pid')
    
    print("\n💡 Comandos útiles:")
    print("  python bot_controller.py 1  # Iniciar")
    print("  python bot_controller.py 2  # Detener")
    print("  python bot_controller.py 3  # Ver estado")
    print("="*50)

def install_dependencies():
    """Instala las dependencias necesarias"""
    print("🔧 Instalando dependencias...")
    try:
        result = subprocess.run(
            [PYTHON, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente.")
            print(result.stdout)
        else:
            print("❌ Error al instalar dependencias:")
            print(result.stderr or result.stdout)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def main():
    """Función principal del controlador"""
    # Asegurarse de que estamos en el directorio correcto
    os.chdir(BASE_DIR)
    
    # Crear archivo de registro si no existe
    (BASE_DIR / 'bot.log').touch(exist_ok=True)
    
    # Manejar argumentos de línea de comandos
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '1':
            start_bot()
        elif arg == '2':
            stop_bot()
        elif arg == '3':
            bot_status()
        elif arg == '4':
            install_dependencies()
        else:
            print(f"❌ Opción no válida: {arg}")
        return
    
    # Modo interactivo
    while True:
        show_menu()
        try:
            choice = input("\nSelecciona una opción (1-5): ").strip()
            
            if choice == '1':
                start_bot()
            elif choice == '2':
                stop_bot()
            elif choice == '3':
                bot_status()
            elif choice == '4':
                install_dependencies()
            elif choice == '5':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida. Por favor, elige un número del 1 al 5.")
            
            if choice in ['1', '2', '3', '4']:  # No pausar después de mostrar ayuda
                input("\nPresiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n👋 Operación cancelada por el usuario.")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Operación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
