# principal.py

import tkinter as tk
from interfaz_grafica import InterfazGrafica
from gestion_archivos import cargar_configuracion_inicial

def main():
    """
    Función principal para iniciar la aplicación Kakuro.
    """
    # Cargar configuración inicial del juego
    configuracion_actual = cargar_configuracion_inicial()

    # Crear la ventana principal de Tkinter
    ventana_principal = tk.Tk()
    ventana_principal.title("Juego Kakuro")
    ventana_principal.geometry("800x600") # Tamaño de ventana inicial, ajustar según diseño

    # Inicializar la interfaz gráfica
    app = InterfazGrafica(ventana_principal, configuracion_actual)

    # Iniciar el bucle principal de Tkinter
    ventana_principal.mainloop()

if __name__ == "__main__":
    main()
