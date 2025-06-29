# gestion_archivos.py
# Este módulo maneja todas las operaciones de lectura y escritura de archivos
# para la persistencia de datos del juego Kakuro (partidas, récords, juego actual, configuración).

import json # Importa la librería json para trabajar con archivos JSON.
import os # Importa el módulo os para interactuar con el sistema de archivos (ej. verificar existencia de archivos).

# Definición de los nombres de los archivos utilizados por el juego.
# Se usan constantes para facilitar el mantenimiento y evitar errores de escritura.
ARCHIVO_PARTIDAS = "kakuro_partidas.json"
ARCHIVO_RECORDS = "kakuro_records.txt" # Aunque es .txt, se guardará como JSON para estructura.
ARCHIVO_JUEGO_ACTUAL = "kakuro_juego_actual.txt" # Aunque es .txt, se guardará como JSON.
ARCHIVO_CONFIGURACION = "kakuro_configuracion.txt" # Aunque es .txt, se guardará como JSON.

def cargar_partidas():
    """
    Carga las definiciones de las partidas de Kakuro desde el archivo JSON.
    Si el archivo no existe o es inválido, retorna una lista vacía.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa una partida.
    """
    # Verifica si el archivo de partidas existe.
    if not os.path.exists(ARCHIVO_PARTIDAS):
        print(f"Advertencia: El archivo de partidas '{ARCHIVO_PARTIDAS}' no se encontró. Creando uno vacío.")
        # Si no existe, crea un archivo JSON vacío para evitar errores posteriores.
        with open(ARCHIVO_PARTIDAS, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4) # Escribe una lista JSON vacía con formato legible.
        return [] # Retorna una lista vacía.
    try:
        # Intenta abrir y cargar el contenido del archivo JSON.
        with open(ARCHIVO_PARTIDAS, 'r', encoding='utf-8') as f:
            return json.load(f) # Carga el contenido JSON y lo retorna como un objeto Python.
    except json.JSONDecodeError:
        # Captura errores si el archivo no es un JSON válido.
        print(f"Error: El archivo '{ARCHIVO_PARTIDAS}' no es un JSON válido. Retornando lista vacía.")
        return []
    except Exception as e:
        # Captura cualquier otro error durante la carga del archivo.
        print(f"Error al cargar partidas de '{ARCHIVO_PARTIDAS}': {e}")
        return []

def guardar_records(nombre_jugador, tiempo_segundos, nivel):
    """
    Guarda un nuevo récord de jugador en el archivo de récords.
    Los récords se organizan por nivel de dificultad.

    Args:
        nombre_jugador (str): El nombre del jugador que logró el récord.
        tiempo_segundos (int): El tiempo en segundos que tardó el jugador.
        nivel (str): El nivel de dificultad en el que se logró el récord.
    """
    records = cargar_records() # Carga todos los récords existentes para actualizarlos.

    # Si el nivel no existe en el diccionario de récords, lo inicializa con una lista vacía.
    if nivel not in records:
        records[nivel] = []

    # Añade el nuevo récord a la lista del nivel correspondiente.
    records[nivel].append({
        "jugador": nombre_jugador,
        "tiempo_segundos": tiempo_segundos
    })

    # Opcional: Ordena los récords de este nivel por tiempo de forma ascendente antes de guardar.
    # Esto asegura que los récords siempre estén ordenados.
    records[nivel].sort(key=lambda x: x["tiempo_segundos"])

    try:
        # Intenta abrir el archivo de récords en modo escritura y guardar el diccionario actualizado como JSON.
        with open(ARCHIVO_RECORDS, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=4) # Guarda el diccionario como JSON con formato legible.
    except Exception as e:
        # Captura cualquier error durante el guardado.
        print(f"Error al guardar récords en '{ARCHIVO_RECORDS}': {e}")

def cargar_records():
    """
    Carga los récords de los jugadores desde el archivo.

    Returns:
        dict: Un diccionario donde las claves son los niveles de dificultad
              y los valores son listas de diccionarios de récords.
              Retorna un diccionario vacío si el archivo no existe o es inválido.
    """
    # Verifica si el archivo de récords existe.
    if not os.path.exists(ARCHIVO_RECORDS):
        return {} # Si no existe, retorna un diccionario vacío.
    try:
        # Intenta abrir y cargar el contenido del archivo JSON.
        with open(ARCHIVO_RECORDS, 'r', encoding='utf-8') as f:
            return json.load(f) # Carga el contenido JSON.
    except json.JSONDecodeError:
        # Captura errores si el archivo no es un JSON válido.
        print(f"Error: El archivo '{ARCHIVO_RECORDS}' no es un JSON válido. Retornando diccionario vacío.")
        return {}
    except Exception as e:
        # Captura cualquier otro error.
        print(f"Error al cargar récords de '{ARCHIVO_RECORDS}': {e}")
        return {}

def guardar_juego_actual(estado_juego):
    """
    Guarda el estado actual de la partida en un archivo.
    Este archivo solo contendrá la última partida guardada por el jugador.

    Args:
        estado_juego (dict): Un diccionario que representa el estado completo del juego.
    """
    try:
        # Abre el archivo de juego actual en modo escritura y guarda el estado como JSON.
        with open(ARCHIVO_JUEGO_ACTUAL, 'w', encoding='utf-8') as f:
            json.dump(estado_juego, f, indent=4) # Guarda el diccionario como JSON con formato legible.
    except Exception as e:
        # Captura cualquier error durante el guardado.
        print(f"Error al guardar juego actual en '{ARCHIVO_JUEGO_ACTUAL}': {e}")

def cargar_juego_actual():
    """
    Carga el estado de la última partida guardada desde el archivo.

    Returns:
        dict or None: Un diccionario con el estado del juego si se carga exitosamente,
                      o None si el archivo no existe o es inválido.
    """
    # Verifica si el archivo de juego actual existe.
    if not os.path.exists(ARCHIVO_JUEGO_ACTUAL):
        return None # Si no existe, no hay juego guardado.
    try:
        # Intenta abrir y cargar el contenido del archivo JSON.
        with open(ARCHIVO_JUEGO_ACTUAL, 'r', encoding='utf-8') as f:
            return json.load(f) # Carga el contenido JSON.
    except json.JSONDecodeError:
        # Captura errores si el archivo no es un JSON válido.
        print(f"Error: El archivo '{ARCHIVO_JUEGO_ACTUAL}' no es un JSON válido. Retornando None.")
        return None
    except Exception as e:
        # Captura cualquier otro error.
        print(f"Error al cargar juego actual de '{ARCHIVO_JUEGO_ACTUAL}': {e}")
        return None

def guardar_configuracion(configuracion_dict):
    """
    Guarda la configuración actual del juego en un archivo.

    Args:
        configuracion_dict (dict): Un diccionario con los parámetros de configuración.
    """
    try:
        # Abre el archivo de configuración en modo escritura y guarda el diccionario como JSON.
        with open(ARCHIVO_CONFIGURACION, 'w', encoding='utf-8') as f:
            json.dump(configuracion_dict, f, indent=4) # Guarda el diccionario como JSON con formato legible.
    except Exception as e:
        # Captura cualquier error durante el guardado.
        print(f"Error al guardar configuración en '{ARCHIVO_CONFIGURACION}': {e}")

def cargar_configuracion_inicial():
    """
    Carga la configuración del juego desde el archivo.
    Si el archivo no existe o es inválido, retorna una configuración por defecto.

    Returns:
        dict: Un diccionario con la configuración del juego.
    """
    # Verifica si el archivo de configuración existe.
    if not os.path.exists(ARCHIVO_CONFIGURACION):
        # Si no existe, retorna una configuración por defecto.
        return {
            "nivel": "facil",
            "tipo_reloj": "cronometro",
            "tiempo_temporizador_segundos": 0 # 0 significa que no hay tiempo preestablecido para temporizador.
        }
    try:
        # Intenta abrir y cargar el contenido del archivo JSON.
        with open(ARCHIVO_CONFIGURACION, 'r', encoding='utf-8') as f:
            return json.load(f) # Carga el contenido JSON.
    except json.JSONDecodeError:
        # Captura errores si el archivo no es un JSON válido.
        print(f"Error: El archivo '{ARCHIVO_CONFIGURACION}' no es un JSON válido. Retornando configuración por defecto.")
        return {
            "nivel": "facil",
            "tipo_reloj": "cronometro",
            "tiempo_temporizador_segundos": 0
        }
    except Exception as e:
        # Captura cualquier otro error.
        print(f"Error al cargar configuración de '{ARCHIVO_CONFIGURACION}': {e}")
        return {
            "nivel": "facil",
            "tipo_reloj": "cronometro",
            "tiempo_temporizador_segundos": 0
        }

