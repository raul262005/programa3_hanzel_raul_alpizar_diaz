# kakuro.py
# Este archivo es el punto de inicio de la aplicación del juego Kakuro.
# Se encarga de inicializar la ventana principal de Tkinter y la interfaz gráfica.

import tkinter as tk # Importa la librería Tkinter para crear la interfaz gráfica de usuario (GUI).
from interfaz_grafica import InterfazGrafica # Importa la clase InterfazGrafica desde el módulo interfaz_grafica.
from gestion_archivos import cargar_configuracion_inicial # Importa la función para cargar la configuración inicial del juego.

def main():
    """
    Función principal que se ejecuta al iniciar el programa.
    Configura la ventana de Tkinter y lanza la interfaz del juego.
    """
    # 1. Cargar la configuración inicial del juego.
    # Esta configuración incluye el nivel de dificultad, tipo de reloj, etc.
    configuracion_actual = cargar_configuracion_inicial()

    # 2. Crear la ventana principal de la aplicación Tkinter.
    # Esta será la ventana raíz donde se mostrará todo el contenido del juego.
    ventana_principal = tk.Tk()
    ventana_principal.title("Juego Kakuro") # Establece el título de la ventana.
    ventana_principal.geometry("800x600") # Define el tamaño inicial de la ventana (ancho x alto).
    ventana_principal.resizable(False, False) # Impide que el usuario pueda redimensionar la ventana.

    # 3. Inicializar la interfaz gráfica del juego.
    # Se pasa la ventana principal y la configuración cargada a la clase InterfazGrafica.
    app = InterfazGrafica(ventana_principal, configuracion_actual)

    # 4. Iniciar el bucle principal de eventos de Tkinter.
    # Este bucle mantiene la ventana abierta y responde a las interacciones del usuario (clics, teclado, etc.).
    ventana_principal.mainloop()

# Este bloque asegura que la función 'main()' se llame solo cuando el script se ejecuta directamente.
# No se ejecutará si el módulo es importado por otro script.
if __name__ == "__main__":
    main()

