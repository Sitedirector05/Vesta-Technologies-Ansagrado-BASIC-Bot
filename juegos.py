import random
import asyncio
from typing import Dict, List, Optional, Tuple
import httpx
import os
from enum import Enum

class EstadoJuego(Enum):
    EN_ESPERA = "en_espera"
    EN_CURSO = "en_curso"
    TERMINADO = "terminado"
    CANCELADO = "cancelado"

class JuegoAhorcado:
    def __init__(self, palabra: str, pistas: List[str] = None):
        self.palabra = palabra.upper()
        self.palabra_oculta = ['_' if letra.isalpha() else letra for letra in self.palabra]
        self.letras_intentadas = set()
        self.intentos_restantes = 6
        self.estado = EstadoJuego.EN_ESPERA
        self.ganador = None
        self.pistas = pistas or []
        self.pistas_mostradas = 0
        self.max_pistas = 2 if pistas else 0
    
    def intentar_letra(self, letra: str) -> bool:
        """Intenta adivinar una letra. Devuelve True si la letra está en la palabra."""
        letra = letra.upper()
        if letra in self.letras_intentadas:
            return None  # Ya se intentó esta letra
        
        self.letras_intentadas.add(letra)
        
        if letra in self.palabra:
            # Actualizar palabra oculta
            for i, l in enumerate(self.palabra):
                if l == letra:
                    self.palabra_oculta[i] = letra
            
            # Verificar si ganó
            if '_' not in self.palabra_oculta:
                self.estado = EstadoJuego.TERMINADO
                self.ganador = True
            return True
        else:
            self.intentos_restantes -= 1
            if self.intentos_restantes <= 0:
                self.estado = EstadoJuego.TERMINADO
                self.ganador = False
            return False
    
    def intentar_palabra(self, palabra: str) -> bool:
        """Intenta adivinar la palabra completa. Devuelve True si es correcta."""
        if palabra.upper() == self.palora:
            self.palabra_oculta = list(self.palabra)
            self.estado = EstadoJuego.TERMINADO
            self.ganador = True
            return True
        else:
            self.intentos_restantes = max(0, self.intentos_restantes - 1)
            if self.intentos_restantes <= 0:
                self.estado = EstadoJuego.TERMINADO
                self.ganador = False
            return False
    
    def obtener_pista(self) -> Optional[str]:
        """Devuelve una pista si hay disponibles."""
        if self.pistas and self.pistas_mostradas < self.max_pistas:
            pista = self.pistas[self.pistas_mostradas]
            self.pistas_mostradas += 1
            return pista
        return None
    
    def obtener_estado(self) -> str:
        """Devuelve una representación del estado actual del juego."""
        # Dibujo del ahorcado
        dibujo = [
            "  ____\n  |  |\n  |  \n  |  \n  |  \n__|__",
            "  ____\n  |  |\n  |  O\n  |  \n  |  \n__|__",
            "  ____\n  |  |\n  |  O\n  |  |\n  |  \n__|__",
            "  ____\n  |  |\n  |  O\n  | /|\n  |  \n__|__",
            "  ____\n  |  |\n  |  O\n  | /|\\n  |  \n__|__",
            "  ____\n  |  |\n  |  O\n  | /|\\n  | / \n__|__",
            "  ____\n  |  |\n  |  O\n  | /|\\n  | / \\n__|__"
        ]
        
        intentos_restantes = min(max(0, self.intentos_restantes), 6)
        return f"```{dibujo[6 - intentos_restantes]}\n\n{' '.join(self.palabra_oculta)}\n" \
               f"\nLetras intentadas: {', '.join(sorted(self.letras_intentadas)) if self.letras_intentadas else 'Ninguna'}" \
               f"\nIntentos restantes: {self.intentos_restantes}```"

class JuegoPiedraPapelTijeras:
    OPCIONES = ["piedra", "papel", "tijeras"]
    RESULTADOS = {
        "piedra": {"piedra": 0, "papel": -1, "tijeras": 1},
        "papel": {"piedra": 1, "papel": 0, "tijeras": -1},
        "tijeras": {"piedra": -1, "papel": 1, "tijeras": 0}
    }
    
    def __init__(self):
        self.jugador1 = None
        self.jugador2 = None
        self.eleccion1 = None
        self.eleccion2 = None
        self.estado = EstadoJuego.EN_ESPERA
        self.ganador = None
    
    def unirse(self, jugador_id: int) -> bool:
        """Un jugador se une al juego. Devuelve True si el juego está listo para comenzar."""
        if self.jugador1 is None:
            self.jugador1 = jugador_id
            return False
        elif self.jugador2 is None and jugador_id != self.jugador1:
            self.jugador2 = jugador_id
            self.estado = EstadoJuego.EN_CURSO
            return True
        return False
    
    def jugar(self, jugador_id: int, eleccion: str) -> bool:
        """Registra la elección de un jugador. Devuelve True si ambos jugadores han jugado."""
        eleccion = eleccion.lower()
        if eleccion not in self.OPCIONES:
            return False
            
        if jugador_id == self.jugador1 and self.eleccion1 is None:
            self.eleccion1 = eleccion
        elif jugador_id == self.jugador2 and self.eleccion2 is None:
            self.eleccion2 = eleccion
        else:
            return False
            
        if self.eleccion1 is not None and self.eleccion2 is not None:
            self._calcular_ganador()
            return True
        return False
    
    def _calcular_ganador(self):
        """Calcula el ganador basado en las elecciones de los jugadores."""
        resultado = self.RESULTADOS[self.eleccion1][self.eleccion2]
        if resultado == 1:
            self.ganador = self.jugador1
        elif resultado == -1:
            self.ganador = self.jugador2
        else:
            self.ganador = 0  # Empate
        self.estado = EstadoJuego.TERMINADO

class JuegoTrivia:
    def __init__(self, pregunta: str, opciones: List[str], respuesta_correcta: int, categoria: str = "General", dificultad: str = "Media"):
        self.pregunta = pregunta
        self.opciones = opciones
        self.respuesta_correcta = respuesta_correcta
        self.categoria = categoria
        self.dificultad = dificultad
        self.respuestas = {}
        self.estado = EstadoJuego.EN_CURSO
        self.temporizador = None
    
    def responder(self, jugador_id: int, respuesta: int) -> bool:
        """Registra la respuesta de un jugador. Devuelve True si la respuesta es correcta."""
        if self.estado != EstadoJuego.EN_CURSO:
            return False
            
        self.respuestas[jugador_id] = respuesta
        return respuesta == self.respuesta_correcta
    
    def obtener_resultados(self) -> Dict[int, bool]:
        """Devuelve un diccionario con los resultados de los jugadores."""
        return {jugador: (respuesta == self.respuesta_correcta) 
                for jugador, respuesta in self.respuestas.items()}

async def generar_palabra_ahorcado() -> Tuple[str, List[str]]:
    """Genera una palabra y pistas usando la API de DeepSeek."""
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if not openrouter_key:
        # Si no hay API key, usamos una lista de palabras predefinidas
        palabras_predefinidas = [
            ("PYTHON", ["Lenguaje de programación", "Creado por Guido van Rossum"]),
            ("JAVA", ["Lenguaje de programación", "Desarrollado por Sun Microsystems"]),
            ("JAVASCRIPT", ["Lenguaje de programación", "Usado en navegadores web"]),
            ("PROGRAMACION", ["Proceso de crear software", "Involucra escribir código"]),
            ("ALGORITMO", ["Secuencia de pasos", "Usado para resolver problemas"]),
        ]
        return random.choice(palabras_predefinidas)
    
    temas = [
        "ciudades del mundo", "animales", "frutas", "países", "deportes",
        "películas famosas", "libros clásicos", "inventos importantes",
        "elementos químicos", "instrumentos musicales"
    ]
    tema = random.choice(temas)
    
    prompt = f"""
    Necesito una palabra para un juego del ahorcado sobre {tema}.
    La palabra debe tener entre 5 y 12 letras y ser común en español.
    También necesito 2 pistas cortas (máximo 20 caracteres cada una) que ayuden a adivinarla.
    
    Por favor, responde SOLO con el siguiente formato, sin explicaciones adicionales:
    PALABRA|Pista 1|Pista 2
    
    Ejemplo:
    ELEFANTE|Animal grande|Tiene trompa
    """
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek/deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 100
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                resultado = response.json()
                contenido = resultado['choices'][0]['message']['content'].strip()
                if '|' in contenido:
                    partes = [p.strip() for p in contenido.split('|')]
                    if len(partes) >= 3:
                        return partes[0].upper(), partes[1:3]
    except Exception as e:
        print(f"Error al generar palabra con DeepSeek: {e}")
    
    # En caso de error, usar una palabra predefinida
    palabras_predefinidas = [
        ("PYTHON", ["Lenguaje de programación", "Creado por Guido van Rossum"]),
        ("JAVA", ["Lenguaje de programación", "Desarrollado por Sun Microsystems"]),
        ("JAVASCRIPT", ["Lenguaje de programación", "Usado en navegadores web"]),
        ("PROGRAMACION", ["Proceso de crear software", "Involucra escribir código"]),
        ("ALGORITMO", ["Secuencia de pasos", "Usado para resolver problemas"]),
    ]
    return random.choice(palabras_predefinidas)
