# configuracion.py
# Este módulo define la clase Configuracion, que encapsula los ajustes del juego Kakuro.
# Permite un acceso y gestión centralizados de la configuración actual.

class Configuracion:
    def __init__(self, config_dict):
        """
        Constructor de la clase Configuracion.
        Inicializa los atributos de configuración del juego a partir de un diccionario.

        Args:
            config_dict (dict): Un diccionario que contiene los parámetros de configuración.
                                 Ej: {"nivel": "facil", "tipo_reloj": "cronometro", ...}
        """
        # Asigna el nivel de dificultad. Si no está en el diccionario, usa "facil" por defecto.
        self.nivel = config_dict.get("nivel", "facil")
        
        # Asigna el tipo de reloj. Si no está, usa "cronometro" por defecto.
        self.tipo_reloj = config_dict.get("tipo_reloj", "cronometro")
        
        # Determina si el reloj debe estar activo. Es activo si no es "no_usar".
        self.reloj_activo = (self.tipo_reloj != "no_usar")
        
        # Asigna el tiempo del temporizador en segundos. 0 por defecto si no está presente.
        self.tiempo_temporizador_segundos = config_dict.get("tiempo_temporizador_segundos", 0)

    def obtener_configuracion_dict(self):
        """
        Retorna la configuración actual del juego como un diccionario.
        Útil para guardar la configuración en un archivo.

        Returns:
            dict: Un diccionario que representa el estado actual de la configuración.
        """
        return {
            "nivel": self.nivel, # Nivel de dificultad actual.
            "tipo_reloj": self.tipo_reloj, # Tipo de reloj configurado.
            "tiempo_temporizador_segundos": self.tiempo_temporizador_segundos # Tiempo del temporizador.
        }

