import os

# Directorios a crear
directorios = [
    "juegos/precision",
    "juegos/azar",
    "juegos/sociales",
    "juegos/comandos",
    "juegos/economia",
    "juegos/visuales",
    "juegos/mascotas"
]

# Crear cada directorio
for directorio in directorios:
    try:
        os.makedirs(directorio, exist_ok=True)
        print(f"Directorio creado: {directorio}")
    except Exception as e:
        print(f"Error al crear {directorio}: {e}")

print("\nEstructura de directorios creada exitosamente.")
