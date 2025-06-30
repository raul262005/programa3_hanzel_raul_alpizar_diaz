# interfaz_grafica.py
# Este módulo contiene la clase InterfazGrafica, responsable de construir y gestionar
# la interfaz de usuario del juego Kakuro utilizando Tkinter.
# También maneja las interacciones del usuario con los elementos de la GUI.

import tkinter as tk # Importa la librería Tkinter para la creación de la GUI.
from tkinter import messagebox # Importa el módulo messagebox para mostrar cuadros de diálogo.
from logica_juego import LogicaJuego # Importa la clase LogicaJuego para interactuar con la lógica del juego.
from gestion_archivos import ( # Importa funciones específicas para la gestión de archivos.
    guardar_records, cargar_records,
    guardar_juego_actual, cargar_juego_actual,
    guardar_configuracion
)
from configuracion import Configuracion # Importa la clase Configuracion para manejar los ajustes del juego.
from fpdf import FPDF # Importa la clase FPDF para la creación de documentos PDF.
import os # Importa el módulo os para interactuar con el sistema operativo (ej. rutas de archivos).
import subprocess # Importa subprocess para ejecutar comandos externos (ej. abrir PDFs).

class InterfazGrafica:
    def __init__(self, ventana_maestra, configuracion_inicial):
        """
        Constructor de la clase InterfazGrafica.
        Inicializa la ventana principal, la configuración del juego y la lógica del juego.

        Args:
            ventana_maestra (tk.Tk): La ventana raíz de Tkinter donde se construirá la interfaz.
            configuracion_inicial (dict): Un diccionario con la configuración inicial del juego.
        """
        self.ventana_maestra = ventana_maestra # Almacena la referencia a la ventana principal.
        # Crea una instancia de la clase Configuracion con los ajustes iniciales.
        self.configuracion = Configuracion(configuracion_inicial)
        # Crea una instancia de la clase LogicaJuego, pasándole la configuración actual.
        self.logica_juego = LogicaJuego(self.configuracion)

        # Variables de estado de la interfaz y el juego.
        self.jugador_actual = "" # Almacena el nombre del jugador actual.
        self.juego_iniciado = False # Booleano que indica si hay una partida en curso.
        self.cronometro_activo = False # Booleano que indica si el reloj está corriendo.
        self.tiempo_transcurrido = 0 # Almacena el tiempo en segundos (para cronómetro o temporizador).
        self.id_actualizacion_reloj = None # ID para cancelar la actualización periódica del reloj.
        self.numero_seleccionado = None # Almacena el número que el jugador ha seleccionado para colocar.
        self.botones_numeros = [] # Lista para almacenar los botones del panel de números (1-9).

        # Llama al método para crear el menú principal al iniciar la aplicación.
        self.crear_menu_principal()

    def crear_menu_principal(self):
        """
        Crea y muestra la pantalla del menú principal del juego.
        Destruye cualquier widget anterior en la ventana para limpiar la pantalla.
        """
        # Detiene el reloj si está activo y se está regresando al menú principal desde el juego.
        if self.id_actualizacion_reloj:
            self.ventana_maestra.after_cancel(self.id_actualizacion_reloj)
            self.id_actualizacion_reloj = None
        self.cronometro_activo = False
        self.juego_iniciado = False # Asegura que el juego no esté marcado como iniciado al volver al menú.

        # Destruye todos los widgets hijos de la ventana maestra para limpiar la interfaz.
        for widget in self.ventana_maestra.winfo_children():
            widget.destroy()

        # Crea un marco para contener los botones del menú principal.
        marco_menu = tk.Frame(self.ventana_maestra, padx=50, pady=50)
        marco_menu.pack(expand=True) # Empaqueta el marco para que se expanda y centre.

        # Etiqueta con el título del juego.
        tk.Label(marco_menu, text="K A K U R O", font=("Arial", 24, "bold")).pack(pady=20)

        # Botones del menú principal, cada uno asociado a una función.
        tk.Button(marco_menu, text="Jugar", command=self.mostrar_pantalla_juego, width=20, height=2).pack(pady=10)
        tk.Button(marco_menu, text="Configurar", command=self.mostrar_pantalla_configuracion, width=20, height=2).pack(pady=10)
        tk.Button(marco_menu, text="Ayuda", command=self.mostrar_ayuda, width=20, height=2).pack(pady=10)
        tk.Button(marco_menu, text="Acerca de", command=self.mostrar_acerca_de, width=20, height=2).pack(pady=10)
        tk.Button(marco_menu, text="Salir", command=self.salir_aplicacion, width=20, height=2).pack(pady=10)

    def mostrar_pantalla_juego(self):
        """
        Muestra la pantalla principal del juego Kakuro, incluyendo el tablero,
        el panel de números y los botones de control.
        """
        # Limpia la ventana de cualquier widget anterior.
        for widget in self.ventana_maestra.winfo_children():
            widget.destroy()

        # Marco superior para el reloj y el nivel de dificultad.
        marco_superior = tk.Frame(self.ventana_maestra)
        marco_superior.pack(pady=10)

        # Etiqueta para mostrar el tiempo (cronómetro/temporizador).
        self.etiqueta_reloj = tk.Label(marco_superior, text="00:00:00", font=("Arial", 16))
        # Muestra el reloj solo si está configurado para usarse.
        if self.configuracion.reloj_activo:
            self.etiqueta_reloj.pack(side=tk.LEFT, padx=20)

        # Etiqueta para mostrar el nivel de dificultad actual.
        self.etiqueta_nivel = tk.Label(marco_superior, text=f"NIVEL {self.configuracion.nivel.upper()}", font=("Arial", 16, "bold"))
        self.etiqueta_nivel.pack(side=tk.RIGHT, padx=20)

        # Marco principal que contendrá el tablero y los controles.
        marco_juego = tk.Frame(self.ventana_maestra)
        marco_juego.pack(expand=True, fill=tk.BOTH)

        # Marco para el tablero de Kakuro (la cuadrícula 9x9).
        self.marco_tablero = tk.Frame(marco_juego, bd=2, relief="groove")
        self.marco_tablero.pack(side=tk.LEFT, padx=20, pady=20)
        self.celdas_tablero = {} # Diccionario para almacenar las referencias a las celdas del tablero.

        # Dibuja el tablero inicialmente vacío.
        self.dibujar_tablero_vacio()

        # Marco para el panel de números y los botones de acción.
        marco_controles = tk.Frame(marco_juego)
        marco_controles.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.Y)

        # Entrada para el nombre del jugador.
        tk.Label(marco_controles, text="Jugador:").pack(pady=5)
        self.entrada_jugador = tk.Entry(marco_controles, width=30)
        self.entrada_jugador.pack(pady=5)
        # Si ya se había ingresado un nombre, lo muestra.
        self.entrada_jugador.insert(0, self.jugador_actual)

        # Panel de números (botones del 1 al 9).
        marco_numeros = tk.Frame(marco_controles, bd=2, relief="ridge")
        marco_numeros.pack(pady=10)
        self.numero_seleccionado = None # Reinicia el número seleccionado.
        self.botones_numeros = [] # Reinicia la lista de botones de números.

        # Crea los 9 botones numéricos y los organiza en una cuadrícula 3x3.
        for i in range(1, 10):
            boton = tk.Button(marco_numeros, text=str(i), width=4, height=2,
                              command=lambda num=i: self.seleccionar_numero(num))
            boton.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
            self.botones_numeros.append(boton)

        # Botones de acción del juego.
        self.boton_iniciar_juego = tk.Button(marco_controles, text="INICIAR JUEGO", command=self.iniciar_juego, width=20, height=2)
        self.boton_iniciar_juego.pack(pady=5)

        self.boton_deshacer = tk.Button(marco_controles, text="DESHACER JUGADA", command=self.deshacer_jugada, width=20, height=2, state=tk.DISABLED)
        self.boton_deshacer.pack(pady=5)

        self.boton_rehacer = tk.Button(marco_controles, text="REHACER JUGADA", command=self.rehacer_jugada, width=20, height=2, state=tk.DISABLED)
        self.boton_rehacer.pack(pady=5)

        self.boton_borrar_juego = tk.Button(marco_controles, text="BORRAR JUEGO", command=self.borrar_juego, width=20, height=2, state=tk.DISABLED)
        self.boton_borrar_juego.pack(pady=5)

        self.boton_terminar_juego = tk.Button(marco_controles, text="TERMINAR JUEGO", command=self.terminar_juego, width=20, height=2, state=tk.DISABLED)
        self.boton_terminar_juego.pack(pady=5)

        self.boton_records = tk.Button(marco_controles, text="RÉCORDS", command=self.mostrar_records, width=20, height=2)
        self.boton_records.pack(pady=5)

        self.boton_guardar_juego = tk.Button(marco_controles, text="GUARDAR JUEGO", command=self.guardar_juego, width=20, height=2, state=tk.DISABLED)
        self.boton_guardar_juego.pack(pady=5)

        self.boton_cargar_juego = tk.Button(marco_controles, text="CARGAR JUEGO", command=self.cargar_juego, width=20, height=2)
        self.boton_cargar_juego.pack(pady=5)

        # Botón para regresar al menú principal.
        tk.Button(marco_controles, text="Regresar al Menú Principal", command=self.crear_menu_principal, width=20, height=2).pack(pady=20)

    def dibujar_tablero_vacio(self):
        """
        Dibuja la cuadrícula visual del tablero de Kakuro con celdas vacías.
        Cada celda es un Frame que contiene un Canvas para dibujar contenido.
        """
        for fila in range(9):
            for columna in range(9):
                # Crea un Frame para cada celda del tablero.
                celda_frame = tk.Frame(self.marco_tablero, width=50, height=50, bd=1, relief="solid", bg="white")
                celda_frame.grid(row=fila, column=columna) # Posiciona el frame en la cuadrícula.
                celda_frame.grid_propagate(False) # Evita que el frame se ajuste al tamaño de su contenido.

                # Crea un Canvas dentro del Frame para permitir dibujos (números, líneas de clave).
                canvas_celda = tk.Canvas(celda_frame, width=50, height=50, bg="white", highlightthickness=0)
                canvas_celda.pack(fill="both", expand=True) # Empaqueta el canvas para que llene el frame.
                # Asocia un evento de clic a cada celda para manejar la interacción del jugador.
                canvas_celda.bind("<Button-1>", lambda event, r=fila, c=columna: self.clic_celda(event, r, c))
                # Almacena la referencia al frame, canvas y el valor actual de la celda.
                self.celdas_tablero[(fila, columna)] = {"frame": celda_frame, "canvas": canvas_celda, "valor": None}

    def actualizar_tablero_gui(self):
        """
        Actualiza la representación visual del tablero de Kakuro en la GUI
        basándose en el estado actual del tablero en la lógica del juego.
        """
        for fila in range(9):
            for columna in range(9):
                canvas = self.celdas_tablero[(fila, columna)]["canvas"]
                canvas.delete("all") # Limpia cualquier dibujo anterior en la celda.

                # Obtiene el tipo de celda (clave, rellenable, no_utilizable) de la lógica del juego.
                tipo_celda = self.logica_juego.obtener_tipo_celda(fila, columna)

                if tipo_celda == "clave":
                    # Si es una celda de clave, cambia el fondo a gris claro.
                    canvas.config(bg="lightgray")
                    # Obtiene los valores de las claves de fila y columna.
                    clave_fila, clave_columna = self.logica_juego.obtener_claves_celda(fila, columna)
                    
                    # Dibuja la clave de fila (si existe) en la parte inferior derecha.
                    if clave_fila is not None:
                        canvas.create_text(40, 10, text=str(clave_fila), anchor="ne", font=("Arial", 8, "bold"))
                    # Dibuja la clave de columna (si existe) en la parte superior izquierda.
                    if clave_columna is not None:
                        canvas.create_text(10, 40, text=str(clave_columna), anchor="sw", font=("Arial", 8, "bold"))
                    # Dibuja una línea diagonal para separar las claves.
                    canvas.create_line(0, 0, 50, 50, fill="black", width=2)
                elif tipo_celda == "rellenable":
                    # Si es una celda rellenable, el fondo es blanco.
                    canvas.config(bg="white")
                    # Obtiene el valor numérico actual de la celda.
                    valor = self.logica_juego.obtener_valor_celda(fila, columna)
                    if valor is not None:
                        # Si hay un valor, lo dibuja en el centro de la celda.
                        canvas.create_text(25, 25, text=str(valor), font=("Arial", 14, "bold"), fill="blue")
                else: # tipo_celda == "no_utilizable"
                    # Si la celda no es utilizable, el fondo es negro.
                    canvas.config(bg="black")

    def seleccionar_numero(self, numero):
        """
        Maneja la selección de un número en el panel numérico.
        Resalta el botón del número seleccionado y deselecciona el anterior.
        """
        # Si ya había un número seleccionado previamente, restaura su color original.
        if self.numero_seleccionado is not None:
            self.botones_numeros[self.numero_seleccionado - 1].config(bg=tk.Button().cget("bg"))

        # Establece el nuevo número seleccionado.
        self.numero_seleccionado = numero
        # Resalta el botón del número recién seleccionado con un color diferente.
        self.botones_numeros[numero - 1].config(bg="lightblue")

    def clic_celda(self, event, fila, columna):
        """
        Maneja el evento de clic en una celda del tablero.
        Realiza validaciones y, si es posible, coloca el número seleccionado.
        """
        # Verifica si el juego ha sido iniciado.
        if not self.juego_iniciado:
            messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO.")
            return

        # Verifica si la celda clicada es rellenable (no es una clave o celda no utilizable).
        if self.logica_juego.obtener_tipo_celda(fila, columna) != "rellenable":
            messagebox.showinfo("Información", "Las celdas con claves o no utilizables no se pueden modificar.")
            return

        # Verifica si el jugador ha seleccionado un número del panel.
        if self.numero_seleccionado is None:
            messagebox.showerror("Error", "FALTA QUE SELECCIONE EL NÚMERO.")
            return

        valor_a_colocar = self.numero_seleccionado # Obtiene el número a colocar.
        self.numero_seleccionado = None # Deselecciona el número después de usarlo.
        # Restaura el color del botón del número que acaba de ser usado.
        self.botones_numeros[valor_a_colocar - 1].config(bg=tk.Button().cget("bg"))

        # Intenta realizar la jugada a través de la lógica del juego.
        resultado_jugada = self.logica_juego.realizar_jugada(fila, columna, valor_a_colocar)

        if resultado_jugada["valida"]:
            # Si la jugada es válida, actualiza la GUI del tablero.
            self.actualizar_tablero_gui()
            # Habilita el botón de deshacer.
            self.boton_deshacer.config(state=tk.NORMAL)
            # Deshabilita el botón de rehacer, ya que una nueva jugada invalida las jugadas deshechas.
            self.boton_rehacer.config(state=tk.DISABLED)

            # Verifica si el juego ha terminado después de la jugada.
            if self.logica_juego.verificar_juego_terminado():
                self.terminar_juego_exito() # Llama a la función de finalización exitosa.
        else:
            # Si la jugada no es válida, muestra un mensaje de error.
            messagebox.showerror("Jugada Inválida", resultado_jugada["mensaje"])

    def iniciar_juego(self):
        """
        Inicia un nuevo juego de Kakuro.
        Carga una partida, actualiza la GUI y comienza el reloj si está configurado.
        """
        self.jugador_actual = self.entrada_jugador.get().strip() # Obtiene el nombre del jugador.
        if not self.jugador_actual:
            messagebox.showerror("Error", "Debe ingresar un nombre de jugador para iniciar el juego.")
            return

        if self.juego_iniciado:
            messagebox.showinfo("Información", "El juego ya está iniciado.")
            return

        # Carga una nueva partida aleatoria según el nivel configurado.
        partida_cargada = self.logica_juego.cargar_nueva_partida()
        if not partida_cargada:
            # Si no hay partidas para el nivel seleccionado, informa al usuario y vuelve al menú.
            messagebox.showinfo("Información", "NO HAY PARTIDAS PARA ESTE NIVEL.")
            self.crear_menu_principal()
            return

        self.actualizar_tablero_gui() # Actualiza la GUI con la nueva partida.
        self.juego_iniciado = True # Marca el juego como iniciado.
        # Deshabilita el botón de iniciar juego para evitar reinicios accidentales.
        self.boton_iniciar_juego.config(state=tk.DISABLED)
        # Habilita los botones de control del juego.
        self.boton_borrar_juego.config(state=tk.NORMAL)
        self.boton_terminar_juego.config(state=tk.NORMAL)
        self.boton_guardar_juego.config(state=tk.NORMAL)
        self.boton_cargar_juego.config(state=tk.DISABLED) # No se puede cargar mientras se juega.

        # Inicia el cronómetro o temporizador si está activo en la configuración.
        if self.configuracion.reloj_activo:
            self.tiempo_transcurrido = 0 # Reinicia el tiempo.
            if self.configuracion.tipo_reloj == "temporizador":
                # Si es temporizador, el tiempo inicial es el configurado.
                self.tiempo_transcurrido = self.configuracion.tiempo_temporizador_segundos
            self.cronometro_activo = True # Activa el reloj.
            self.actualizar_reloj() # Inicia la actualización periódica del reloj.
        else:
            # Si el reloj no está activo, oculta la etiqueta del reloj.
            self.etiqueta_reloj.pack_forget()

    def actualizar_reloj(self):
        """
        Actualiza el cronómetro o temporizador en la interfaz gráfica cada segundo.
        Maneja la lógica de tiempo y las condiciones de fin de temporizador.
        """
        if self.cronometro_activo:
            if self.configuracion.tipo_reloj == "cronometro":
                self.tiempo_transcurrido += 1 # Incrementa el tiempo para el cronómetro.
                horas = self.tiempo_transcurrido // 3600
                minutos = (self.tiempo_transcurrido % 3600) // 60
                segundos = self.tiempo_transcurrido % 60
                # Validación de horas para el cronómetro (máximo 2 horas).
                if horas > 2:
                    messagebox.showerror("Error", "El cronómetro ha excedido el límite de 2 horas.")
                    self.terminar_juego_forzado() # Termina el juego si se excede el tiempo.
                    return
            elif self.configuracion.tipo_reloj == "temporizador":
                self.tiempo_transcurrido -= 1 # Decrementa el tiempo para el temporizador.
                if self.tiempo_transcurrido <= 0:
                    # Si el temporizador llega a cero, lo detiene.
                    self.cronometro_activo = False
                    # Pregunta al usuario si desea continuar el juego como cronómetro.
                    respuesta = messagebox.askyesno("Tiempo Expirado", "¿DESEA CONTINUAR EL MISMO JUEGO (SI/NO)?")
                    if respuesta:
                        # Si el usuario elige continuar, cambia el tipo de reloj a cronómetro.
                        self.configuracion.tipo_reloj = "cronometro"
                        # El tiempo transcurrido se convierte en el punto de partida del cronómetro.
                        self.tiempo_transcurrido = self.configuracion.tiempo_temporizador_segundos
                        self.cronometro_activo = True # Reactiva el reloj como cronómetro.
                        messagebox.showinfo("Continuar", "El temporizador ha cambiado a cronómetro.")
                    else:
                        self.terminar_juego_forzado() # Si no desea continuar, termina el juego.
                        return
                horas = self.tiempo_transcurrido // 3600
                minutos = (self.tiempo_transcurrido % 3600) // 60
                segundos = self.tiempo_transcurrido % 60

            # Actualiza el texto de la etiqueta del reloj con el formato HH:MM:SS.
            self.etiqueta_reloj.config(text=f"{horas:02}:{minutos:02}:{segundos:02}")
            # Programa la próxima actualización del reloj después de 1000 ms (1 segundo).
            self.id_actualizacion_reloj = self.ventana_maestra.after(1000, self.actualizar_reloj)

    def terminar_juego_exito(self):
        """
        Maneja la finalización exitosa del juego cuando el jugador completa el tablero.
        Detiene el reloj, registra el récord y reinicia el estado del juego.
        """
        # Cancela cualquier actualización pendiente del reloj.
        if self.id_actualizacion_reloj:
            self.ventana_maestra.after_cancel(self.id_actualizacion_reloj)
            self.id_actualizacion_reloj = None
        self.cronometro_activo = False # Desactiva el reloj.
        self.juego_iniciado = False # Marca el juego como no iniciado.

        messagebox.showinfo("¡Felicidades!", "¡EXCELENTE JUGADOR! TERMINÓ EL JUEGO CON ÉXITO.")

        # Calcula el tiempo final para el récord.
        tiempo_final = self.tiempo_transcurrido
        # Guarda el récord del jugador.
        guardar_records(self.jugador_actual, tiempo_final, self.configuracion.nivel)

        # Reinicia el estado del juego en la lógica y actualiza la GUI.
        self.logica_juego.resetear_juego()
        self.actualizar_tablero_gui()
        # Restaura el estado de los botones para permitir iniciar un nuevo juego.
        self.boton_iniciar_juego.config(state=tk.NORMAL)
        self.boton_deshacer.config(state=tk.DISABLED)
        self.boton_rehacer.config(state=tk.DISABLED)
        self.boton_borrar_juego.config(state=tk.DISABLED)
        self.boton_terminar_juego.config(state=tk.DISABLED)
        self.boton_guardar_juego.config(state=tk.DISABLED)
        self.boton_cargar_juego.config(state=tk.NORMAL) # Permite cargar un juego guardado.

    def terminar_juego_forzado(self):
        """
        Termina el juego de forma no exitosa (ej. por tiempo expirado, o decisión del jugador).
        Reinicia el estado del juego y la GUI.
        """
        # Cancela cualquier actualización pendiente del reloj.
        if self.id_actualizacion_reloj:
            self.ventana_maestra.after_cancel(self.id_actualizacion_reloj)
            self.id_actualizacion_reloj = None
        self.cronometro_activo = False # Desactiva el reloj.
        self.juego_iniciado = False # Marca el juego como no iniciado.

        messagebox.showinfo("Juego Terminado", "El juego ha finalizado.")

        # Reinicia el estado del juego en la lógica y actualiza la GUI.
        self.logica_juego.resetear_juego()
        self.actualizar_tablero_gui()
        # Restaura el estado de los botones para permitir iniciar un nuevo juego.
        self.boton_iniciar_juego.config(state=tk.NORMAL)
        self.boton_deshacer.config(state=tk.DISABLED)
        self.boton_rehacer.config(state=tk.DISABLED)
        self.boton_borrar_juego.config(state=tk.DISABLED)
        self.boton_terminar_juego.config(state=tk.DISABLED)
        self.boton_guardar_juego.config(state=tk.DISABLED)
        self.boton_cargar_juego.config(state=tk.NORMAL)

    def deshacer_jugada(self):
        """
        Deshace la última jugada realizada por el jugador.
        Utiliza la pila de jugadas realizadas de la lógica del juego.
        """
        if not self.juego_iniciado:
            messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO.")
            return

        # Llama al método de la lógica del juego para deshacer la jugada.
        if self.logica_juego.deshacer_jugada():
            self.actualizar_tablero_gui() # Actualiza la GUI para reflejar el cambio.
            self.boton_rehacer.config(state=tk.NORMAL) # Habilita el botón de rehacer.
            # Si no quedan más jugadas para deshacer, deshabilita el botón de deshacer.
            if not self.logica_juego.pila_jugadas_realizadas:
                self.boton_deshacer.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Información", "No hay jugadas para deshacer.")
            self.boton_deshacer.config(state=tk.DISABLED)

    def rehacer_jugada(self):
        """
        Rehace la última jugada que fue deshecha por el jugador.
        Utiliza la pila de jugadas deshechas de la lógica del juego.
        """
        if not self.juego_iniciado:
            messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO.")
            return

        # Llama al método de la lógica del juego para rehacer la jugada.
        if self.logica_juego.rehacer_jugada():
            self.actualizar_tablero_gui() # Actualiza la GUI para reflejar el cambio.
            self.boton_deshacer.config(state=tk.NORMAL) # Habilita el botón de deshacer.
            # Si no quedan más jugadas para rehacer, deshabilita el botón de rehacer.
            if not self.logica_juego.pila_jugadas_deshechas:
                self.boton_rehacer.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Información", "No hay jugadas para rehacer.")
            self.boton_rehacer.config(state=tk.DISABLED)

    def borrar_juego(self):
        """
        Borra todas las jugadas realizadas en el juego actual, volviendo al estado inicial de la partida.
        Pide confirmación al usuario.
        """
        if not self.juego_iniciado:
            messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO.")
            return

        # Pide confirmación al usuario antes de borrar el juego.
        respuesta = messagebox.askyesno("Borrar Juego", "¿ESTÁ SEGURO DE BORRAR EL JUEGO (SI/NO)?")
        if respuesta:
            self.logica_juego.borrar_juego_actual() # Llama a la lógica para borrar el juego.
            self.actualizar_tablero_gui() # Actualiza la GUI.
            # Deshabilita los botones de deshacer/rehacer y otros controles.
            self.boton_deshacer.config(state=tk.DISABLED)
            self.boton_rehacer.config(state=tk.DISABLED)
            self.boton_iniciar_juego.config(state=tk.NORMAL) # Habilita iniciar para un nuevo juego.
            self.boton_borrar_juego.config(state=tk.DISABLED)
            self.boton_terminar_juego.config(state=tk.DISABLED)
            self.boton_guardar_juego.config(state=tk.DISABLED)
            self.boton_cargar_juego.config(state=tk.NORMAL)
            # Detiene el reloj si estaba activo.
            if self.id_actualizacion_reloj:
                self.ventana_maestra.after_cancel(self.id_actualizacion_reloj)
                self.id_actualizacion_reloj = None
            self.cronometro_activo = False
            self.juego_iniciado = False
            messagebox.showinfo("Juego Borrado", "El juego ha sido borrado. Puede iniciar uno nuevo.")
        else:
            messagebox.showinfo("Información", "El juego no ha sido borrado.")

    def terminar_juego(self):
        """
        Permite al jugador terminar el juego actual en cualquier momento.
        Pide confirmación y, si se confirma, finaliza el juego y carga una nueva partida.
        """
        if not self.juego_iniciado:
            messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO.")
            return

        # Pide confirmación al usuario.
        respuesta = messagebox.askyesno("Terminar Juego", "¿ESTÁ SEGURO DE TERMINAR EL JUEGO (SI/NO)?")
        if respuesta:
            self.terminar_juego_forzado() # Llama a la función de terminación forzada.
            messagebox.showinfo("Juego Terminado", "El juego ha sido terminado.")
            self.iniciar_juego() # Inicia automáticamente una nueva partida.
        else:
            messagebox.showinfo("Información", "El juego no ha sido terminado.")

    def mostrar_records(self):
        """
        Muestra una nueva ventana con los récords de los jugadores.
        Permite filtrar por nivel y por jugador.
        """
        # Si el reloj está activo, lo detiene temporalmente para que el tiempo no siga corriendo.
        if self.cronometro_activo and self.id_actualizacion_reloj:
            self.ventana_maestra.after_cancel(self.id_actualizacion_reloj)
            self.id_actualizacion_reloj = None
            self.cronometro_activo = False

        records = cargar_records() # Carga los récords desde el archivo.
        ventana_records = tk.Toplevel(self.ventana_maestra) # Crea una nueva ventana de nivel superior.
        ventana_records.title("Récords Kakuro")
        ventana_records.geometry("400x500")
        ventana_records.transient(self.ventana_maestra) # Hace que la ventana de récords sea hija de la principal.
        ventana_records.grab_set() # Bloquea la interacción con la ventana principal mientras esta está abierta.

        tk.Label(ventana_records, text="RÉCORDS", font=("Arial", 18, "bold")).pack(pady=10)

        # Marco para los filtros de visualización.
        marco_filtros = tk.Frame(ventana_records)
        marco_filtros.pack(pady=10)

        tk.Label(marco_filtros, text="Mostrar:").pack(side=tk.LEFT)
        # Opciones para filtrar por nivel.
        opciones_mostrar = ["Todos los niveles", "Nivel fácil", "Nivel medio", "Nivel difícil", "Nivel experto"]
        self.filtro_nivel = tk.StringVar(ventana_records)
        self.filtro_nivel.set(opciones_mostrar[0]) # Valor por defecto.
        menu_nivel = tk.OptionMenu(marco_filtros, self.filtro_nivel, *opciones_mostrar,
                                   command=lambda x: self.actualizar_lista_records(records, self.filtro_nivel.get(), self.filtro_jugador.get()))
        menu_nivel.pack(side=tk.LEFT, padx=5)

        # Opciones para filtrar por jugador.
        opciones_jugador = ["Todos los jugadores", "Yo"]
        self.filtro_jugador = tk.StringVar(ventana_records)
        self.filtro_jugador.set(opciones_jugador[0]) # Valor por defecto.
        menu_jugador = tk.OptionMenu(marco_filtros, self.filtro_jugador, *opciones_jugador,
                                     command=lambda x: self.actualizar_lista_records(records, self.filtro_nivel.get(), self.filtro_jugador.get()))
        menu_jugador.pack(side=tk.LEFT, padx=5)

        # Área de texto para mostrar los récords.
        self.area_records = tk.Text(ventana_records, wrap=tk.WORD, width=40, height=20, font=("Courier New", 10))
        self.area_records.pack(pady=10)

        # Actualiza la lista de récords inicialmente.
        self.actualizar_lista_records(records, self.filtro_nivel.get(), self.filtro_jugador.get())

        def al_cerrar_records():
            """Función que se ejecuta al cerrar la ventana de récords."""
            ventana_records.destroy() # Destruye la ventana de récords.
            self.ventana_maestra.grab_release() # Libera el bloqueo de la ventana principal.
            # Si el juego estaba iniciado y el reloj debe continuar, lo reanuda.
            if self.juego_iniciado and self.configuracion.reloj_activo:
                self.cronometro_activo = True
                self.actualizar_reloj()

        # Asocia la función 'al_cerrar_records' al evento de cierre de la ventana.
        ventana_records.protocol("WM_DELETE_WINDOW", al_cerrar_records)
        tk.Button(ventana_records, text="Cerrar", command=al_cerrar_records).pack(pady=10)

    def actualizar_lista_records(self, records, filtro_nivel, filtro_jugador):
        """
        Actualiza el contenido del área de texto de récords según los filtros seleccionados.
        """
        self.area_records.delete(1.0, tk.END) # Limpia el contenido actual del área de texto.
        records_filtrados = {} # Diccionario para almacenar los récords que cumplen los filtros.

        # Itera sobre los niveles de dificultad en los récords cargados.
        for nivel_key, lista_records in records.items(): # nivel_key es la clave normalizada (ej. "facil")
            # Normaliza el filtro de nivel para la comparación.
            # Si el filtro es "Todos los niveles", no se aplica filtro de nivel.
            # Si es "Nivel fácil", se convierte a "facil" para comparar con la clave.
            filtro_nivel_normalizado = filtro_nivel.lower().replace("nivel ", "")

            if filtro_nivel == "Todos los niveles" or nivel_key == filtro_nivel_normalizado:
                records_filtrados[nivel_key] = [] # Inicializa la lista para este nivel.
                # Itera sobre los récords dentro de cada nivel.
                for record in lista_records:
                    # Aplica el filtro de jugador.
                    if filtro_jugador == "Todos los jugadores" or (filtro_jugador == "Yo" and record["jugador"] == self.jugador_actual):
                        records_filtrados[nivel_key].append(record)
                # Ordena los récords de cada nivel por tiempo de forma ascendente.
                records_filtrados[nivel_key].sort(key=lambda x: x["tiempo_segundos"])

        # Muestra los récords filtrados en el área de texto.
        for nivel_key, lista_records in records_filtrados.items():
            if lista_records: # Si hay récords para este nivel.
                # Formatea el nombre del nivel para mostrarlo (ej. "facil" -> "FÁCIL").
                nivel_display = nivel_key.replace("_", " ").upper()
                self.area_records.insert(tk.END, f"NIVEL {nivel_display}\n", "nivel_tag") # Inserta el título del nivel.
                for i, record in enumerate(lista_records):
                    # Formatea el tiempo de segundos a HH:MM:SS.
                    horas = record["tiempo_segundos"] // 3600
                    minutos = (record["tiempo_segundos"] % 3600) // 60
                    segundos = record["tiempo_segundos"] % 60
                    tiempo_formateado = f"{horas:02}:{minutos:02}:{segundos:02}"
                    # Inserta el récord formateado.
                    self.area_records.insert(tk.END, f"{i+1} - {record['jugador']}: {tiempo_formateado}\n")
                self.area_records.insert(tk.END, "\n") # Añade un salto de línea entre niveles.
        self.area_records.tag_config("nivel_tag", font=("Arial", 12, "bold")) # Configura el estilo del título del nivel.

    def guardar_juego(self):
        """
        Guarda el estado actual del juego en un archivo.
        Detiene el reloj y pregunta al usuario si desea continuar jugando.
        """
        if not self.juego_iniciado:
            messagebox.showerror("Error", "NO SE HA INICIADO EL JUEGO PARA GUARDAR.")
            return

        # Detiene el reloj si está activo.
        if self.id_actualizacion_reloj:
            self.ventana_maestra.after_cancel(self.id_actualizacion_reloj)
            self.id_actualizacion_reloj = None
        self.cronometro_activo = False

        # Prepara el diccionario con el estado completo del juego para guardar.
        estado_juego = {
            "jugador": self.jugador_actual,
            "nivel": self.configuracion.nivel,
            "tablero_actual": self.logica_juego.obtener_estado_tablero(), # Obtiene el estado del tablero de la lógica.
            "pila_jugadas_realizadas": self.logica_juego.pila_jugadas_realizadas,
            "pila_jugadas_deshechas": self.logica_juego.pila_jugadas_deshechas,
            "tiempo_transcurrido": self.tiempo_transcurrido,
            "tipo_reloj": self.configuracion.tipo_reloj,
            "tiempo_temporizador_segundos": self.configuracion.tiempo_temporizador_segundos
        }
        guardar_juego_actual(estado_juego) # Llama a la función de gestión de archivos para guardar.
        messagebox.showinfo("Juego Guardado", "El juego ha sido guardado exitosamente.")

        # Pregunta al usuario si desea continuar jugando.
        respuesta = messagebox.askyesno("Continuar Juego", "¿VA A CONTINUAR JUGANDO (SI/NO)?")
        if not respuesta:
            self.terminar_juego_forzado() # Si no, termina el juego y vuelve al menú principal.
            self.crear_menu_principal()
        else:
            # Si sí, reanuda el reloj si estaba activo.
            if self.configuracion.reloj_activo:
                self.cronometro_activo = True
                self.actualizar_reloj()

    def cargar_juego(self):
        """
        Carga un juego previamente guardado desde un archivo.
        Actualiza la interfaz con el estado del juego cargado.
        """
        if self.juego_iniciado:
            messagebox.showerror("Error", "Ya hay un juego en curso. Termínelo o bórrelo antes de cargar uno nuevo.")
            return

        estado_cargado = cargar_juego_actual() # Carga el estado del juego desde el archivo.
        if estado_cargado:
            # Restaura el nombre del jugador.
            self.jugador_actual = estado_cargado["jugador"]
            self.entrada_jugador.delete(0, tk.END)
            self.entrada_jugador.insert(0, self.jugador_actual)

            # Restaura la configuración del juego.
            self.configuracion.nivel = estado_cargado["nivel"]
            self.configuracion.tipo_reloj = estado_cargado["tipo_reloj"]
            self.configuracion.tiempo_temporizador_segundos = estado_cargado["tiempo_temporizador_segundos"]
            self.configuracion.reloj_activo = (self.configuracion.tipo_reloj != "no_usar")

            # Carga el estado del tablero y las pilas de jugadas en la lógica del juego.
            self.logica_juego.cargar_estado_tablero(estado_cargado["tablero_actual"])
            self.logica_juego.pila_jugadas_realizadas = estado_cargado["pila_jugadas_realizadas"]
            self.logica_juego.pila_jugadas_deshechas = estado_cargado["pila_jugadas_deshechas"]
            self.tiempo_transcurrido = estado_cargado["tiempo_transcurrido"]

            self.actualizar_tablero_gui() # Actualiza la GUI del tablero.
            self.etiqueta_nivel.config(text=f"NIVEL {self.configuracion.nivel.upper()}") # Actualiza la etiqueta del nivel.
            # Actualiza la etiqueta del reloj con el tiempo cargado.
            self.etiqueta_reloj.config(text=f"{self.tiempo_transcurrido // 3600:02}:{(self.tiempo_transcurrido % 3600) // 60:02}:{self.tiempo_transcurrido % 60:02}")

            # Muestra u oculta el reloj según la configuración cargada.
            if self.configuracion.reloj_activo:
                self.etiqueta_reloj.pack(side=tk.LEFT, padx=20)
            else:
                self.etiqueta_reloj.pack_forget()

            self.juego_iniciado = False # El juego no se inicia automáticamente, espera al botón INICIAR JUEGO.
            # Habilita/deshabilita los botones según el estado cargado.
            self.boton_iniciar_juego.config(state=tk.NORMAL)
            self.boton_deshacer.config(state=tk.NORMAL if self.logica_juego.pila_jugadas_realizadas else tk.DISABLED)
            self.boton_rehacer.config(state=tk.NORMAL if self.logica_juego.pila_jugadas_deshechas else tk.DISABLED)
            self.boton_borrar_juego.config(state=tk.NORMAL)
            self.boton_terminar_juego.config(state=tk.NORMAL)
            self.boton_guardar_juego.config(state=tk.NORMAL)
            self.boton_cargar_juego.config(state=tk.DISABLED) # No se puede cargar si ya se cargó.

            messagebox.showinfo("Juego Cargado", "Juego cargado exitosamente. Presione 'INICIAR JUEGO' para continuar.")
        else:
            messagebox.showinfo("Información", "No hay juego guardado para cargar.")

    def mostrar_pantalla_configuracion(self):
        """
        Muestra la pantalla de configuración del juego, permitiendo al usuario
        ajustar el nivel de dificultad y el tipo de reloj.
        """
        # Limpia la ventana de cualquier widget anterior.
        for widget in self.ventana_maestra.winfo_children():
            widget.destroy()

        # Marco para la pantalla de configuración.
        marco_config = tk.Frame(self.ventana_maestra, padx=50, pady=50)
        marco_config.pack(expand=True)

        tk.Label(marco_config, text="Configuración del Juego", font=("Arial", 20, "bold")).pack(pady=20)

        # Sección para seleccionar el Nivel de dificultad.
        tk.Label(marco_config, text="Nivel:").pack(anchor="w", pady=5)
        niveles = ["Fácil", "Medio", "Difícil", "Experto"]
        self.var_nivel = tk.StringVar(marco_config)
        # Establece el valor inicial del Radiobutton al nivel actual de la configuración.
        self.var_nivel.set(self.configuracion.nivel.capitalize())
        for nivel in niveles:
            tk.Radiobutton(marco_config, text=nivel, variable=self.var_nivel, value=nivel.lower()).pack(anchor="w")

        # Sección para seleccionar el Tipo de reloj.
        tk.Label(marco_config, text="Reloj:").pack(anchor="w", pady=10)
        tipos_reloj = {"Cronómetro": "cronometro", "Temporizador": "temporizador", "No usar reloj": "no_usar"}
        self.var_tipo_reloj = tk.StringVar(marco_config)
        # Establece el valor inicial del Radiobutton al tipo de reloj actual.
        self.var_tipo_reloj.set(self.configuracion.tipo_reloj)

        for texto, valor in tipos_reloj.items():
            rb = tk.Radiobutton(marco_config, text=texto, variable=self.var_tipo_reloj, value=valor,
                                command=self.toggle_temporizador_entries) # Asocia una función para mostrar/ocultar entradas de tiempo.
            rb.pack(anchor="w")

        # Marco y entradas para configurar el tiempo del temporizador.
        self.marco_temporizador = tk.Frame(marco_config)
        self.marco_temporizador.pack(anchor="w", padx=20)

        tk.Label(self.marco_temporizador, text="Horas:").pack(side=tk.LEFT)
        self.entrada_horas = tk.Entry(self.marco_temporizador, width=5)
        self.entrada_horas.pack(side=tk.LEFT, padx=5)

        tk.Label(self.marco_temporizador, text="Minutos:").pack(side=tk.LEFT)
        self.entrada_minutos = tk.Entry(self.marco_temporizador, width=5)
        self.entrada_minutos.pack(side=tk.LEFT, padx=5)

        tk.Label(self.marco_temporizador, text="Segundos:").pack(side=tk.LEFT)
        self.entrada_segundos = tk.Entry(self.marco_temporizador, width=5)
        self.entrada_segundos.pack(side=tk.LEFT, padx=5)

        # Carga los valores actuales del temporizador en las entradas si están configurados.
        if self.configuracion.tiempo_temporizador_segundos > 0:
            horas = self.configuracion.tiempo_temporizador_segundos // 3600
            minutos = (self.configuracion.tiempo_temporizador_segundos % 3600) // 60
            segundos = self.configuracion.tiempo_temporizador_segundos % 60
            self.entrada_horas.insert(0, str(horas))
            self.entrada_minutos.insert(0, str(minutos))
            self.entrada_segundos.insert(0, str(segundos))

        self.toggle_temporizador_entries() # Llama para ajustar la visibilidad inicial de las entradas.

        # Botones para guardar la configuración y volver al menú.
        tk.Button(marco_config, text="Guardar Configuración", command=self.guardar_configuracion_ui, width=25, height=2).pack(pady=20)
        tk.Button(marco_config, text="Volver al Menú Principal", command=self.crear_menu_principal, width=25, height=2).pack(pady=10)

    def toggle_temporizador_entries(self):
        """
        Habilita o deshabilita (muestra/oculta) las entradas de tiempo del temporizador
        según el tipo de reloj seleccionado.
        """
        if self.var_tipo_reloj.get() == "temporizador":
            self.marco_temporizador.pack(anchor="w", padx=20) # Muestra el marco del temporizador.
        else:
            self.marco_temporizador.pack_forget() # Oculta el marco del temporizador.

    def guardar_configuracion_ui(self):
        """
        Guarda la configuración seleccionada por el usuario en el objeto de configuración
        y en el archivo de configuración. Realiza validaciones para el temporizador.
        """
        nuevo_nivel = self.var_nivel.get()
        nuevo_tipo_reloj = self.var_tipo_reloj.get()
        nuevas_horas = 0
        nuevos_minutos = 0
        nuevos_segundos = 0

        if nuevo_tipo_reloj == "temporizador":
            try:
                # Intenta obtener los valores de las entradas de tiempo.
                horas_str = self.entrada_horas.get()
                minutos_str = self.entrada_minutos.get()
                segundos_str = self.entrada_segundos.get()

                # Si todas las entradas están vacías, muestra un error.
                if not horas_str and not minutos_str and not segundos_str:
                    messagebox.showerror("Error de Configuración", "Debe ingresar al menos un valor para el temporizador.")
                    return

                # Convierte las cadenas a enteros, usando 0 si están vacías.
                nuevas_horas = int(horas_str) if horas_str else 0
                nuevos_minutos = int(minutos_str) if minutos_str else 0
                nuevos_segundos = int(segundos_str) if segundos_str else 0

                # Valida los rangos de tiempo.
                if not (0 <= nuevas_horas <= 2 and 0 <= nuevos_minutos <= 59 and 0 <= nuevos_segundos <= 59):
                    messagebox.showerror("Error de Configuración", "Valores de tiempo inválidos. Horas (0-2), Minutos (0-59), Segundos (0-59).")
                    return
                # Valida que el temporizador no sea 00:00:00.
                if nuevas_horas == 0 and nuevos_minutos == 0 and nuevos_segundos == 0:
                     messagebox.showerror("Error de Configuración", "El temporizador debe tener al menos un segundo.")
                     return

            except ValueError:
                messagebox.showerror("Error de Configuración", "Por favor, ingrese números válidos para el tiempo.")
                return

        # Actualiza los atributos del objeto de configuración.
        self.configuracion.nivel = nuevo_nivel
        self.configuracion.tipo_reloj = nuevo_tipo_reloj
        self.configuracion.reloj_activo = (nuevo_tipo_reloj != "no_usar")
        # Calcula el tiempo total del temporizador en segundos.
        self.configuracion.tiempo_temporizador_segundos = nuevas_horas * 3600 + nuevos_minutos * 60 + nuevos_segundos

        # Guarda la configuración actualizada en el archivo.
        guardar_configuracion(self.configuracion.obtener_configuracion_dict())
        messagebox.showinfo("Configuración Guardada", "La configuración ha sido guardada exitosamente.")

    def mostrar_ayuda(self):
        """
        Muestra el manual de usuario en formato PDF.
        Intenta abrir el archivo PDF existente o lo crea si no existe.
        """
        # Define la ruta del archivo PDF del manual.
        pdf_path = os.path.join(os.path.dirname(__file__), "manual_usuario.pdf")
        try:
            if not os.path.exists(pdf_path):
                # Si el manual no existe, lo crea.
                self.crear_pdf_manual(pdf_path)
                messagebox.showinfo("Manual Creado", "El manual de usuario ha sido creado. Se abrirá ahora.")

            # Intenta abrir el archivo PDF con el visor predeterminado del sistema.
            if os.name == 'nt': # Para Windows
                os.startfile(pdf_path)
            elif os.uname().sysname == 'Darwin': # Para macOS
                subprocess.call(['open', pdf_path])
            else: # Para Linux y otros sistemas Unix-like
                subprocess.call(['xdg-open', pdf_path])
        except FileNotFoundError:
            messagebox.showerror("Error", f"El archivo del manual '{pdf_path}' no se encontró o no se pudo crear.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el manual de usuario: {str(e)}")

    def crear_pdf_manual(self, ruta):
        """
        Crea un archivo PDF básico para el manual de usuario.
        """
        pdf = FPDF() # Crea una nueva instancia de FPDF.
        pdf.add_page() # Añade una nueva página al PDF.
        pdf.set_font("Arial", size=12) # Establece la fuente y el tamaño.

        # Añade el título del manual.
        pdf.cell(200, 10, txt="Manual de Usuario - Juego Kakuro", ln=True, align='C')
        pdf.ln(10) # Salto de línea.

        # Añade el contenido del manual.
        pdf.multi_cell(0, 10, txt="Bienvenido al Manual de Usuario del Juego Kakuro.")
        pdf.multi_cell(0, 10, txt="Kakuro es un pasatiempo de lógica similar a un crucigrama matemático.")
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt="1. Objetivo del Juego:")
        pdf.multi_cell(0, 10, txt="   Rellenar las casillas vacías con números del 1 al 9. La suma de los números en cada bloque horizontal o vertical debe coincidir con la clave numérica asociada. Los números no pueden repetirse dentro de un mismo bloque.")
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt="2. Cómo Jugar:")
        pdf.multi_cell(0, 10, txt="   - Seleccione la opción 'Jugar' desde el menú principal.")
        pdf.multi_cell(0, 10, txt="   - Ingrese su nombre de jugador.")
        pdf.multi_cell(0, 10, txt="   - Haga clic en el botón 'INICIAR JUEGO'.")
        pdf.multi_cell(0, 10, txt="   - Seleccione un número del panel (1-9) haciendo clic en él.")
        pdf.multi_cell(0, 10, txt="   - Haga clic en la celda del tablero donde desea colocar el número.")
        pdf.multi_cell(0, 10, txt="   - El juego validará su jugada. Si es incorrecta, recibirá un mensaje de error.")
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt="3. Controles del Juego:")
        pdf.multi_cell(0, 10, txt="   - INICIAR JUEGO: Comienza una nueva partida.")
        pdf.multi_cell(0, 10, txt="   - DESHACER JUGADA: Revierte la última jugada realizada.")
        pdf.multi_cell(0, 10, txt="   - REHACER JUGADA: Vuelve a aplicar una jugada que fue deshecha.")
        pdf.multi_cell(0, 10, txt="   - BORRAR JUEGO: Reinicia el tablero actual a su estado inicial.")
        pdf.multi_cell(0, 10, txt="   - TERMINAR JUEGO: Finaliza la partida actual y carga una nueva.")
        pdf.multi_cell(0, 10, txt="   - RÉCORDS: Muestra los mejores tiempos por nivel de dificultad.")
        pdf.multi_cell(0, 10, txt="   - GUARDAR JUEGO: Guarda el estado actual de su partida para continuar después.")
        pdf.multi_cell(0, 10, txt="   - CARGAR JUEGO: Carga la última partida guardada.")
        pdf.multi_cell(0, 10, txt="   - Regresar al Menú Principal: Vuelve a la pantalla de inicio del juego.")
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt="4. Configuración:")
        pdf.multi_cell(0, 10, txt="   - Nivel: Elija entre Fácil, Medio, Difícil o Experto.")
        pdf.multi_cell(0, 10, txt="   - Reloj: Seleccione Cronómetro (cuenta hacia arriba), Temporizador (cuenta hacia abajo) o No usar reloj.")
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt="¡Disfrute del juego Kakuro!")

        pdf.output(ruta) # Guarda el PDF en la ruta especificada.

    def mostrar_acerca_de(self):
        """
        Muestra información sobre el programa y ofrece la opción de generar
        un documento PDF con la documentación del proyecto.
        """
        info = """
        Juego Kakuro
        Versión: 1.0
        Fecha de Creación: Junio 2025
        Autor: Hanzel Raúl Alpízar Díaz
        """
        # Pregunta al usuario si desea generar un PDF de documentación.
        respuesta = messagebox.askyesno("Acerca de", info + "\n\n¿Desea generar un PDF con la documentación del proyecto?")
        if respuesta:
            doc_path = os.path.join(os.path.dirname(__file__), "documentacion_proyecto.pdf")
            try:
                self.crear_pdf_documentacion(doc_path) # Llama a la función para crear el PDF.
                messagebox.showinfo("Éxito", f"Documentación generada en:\n{doc_path}")
                # Intenta abrir el archivo PDF con el visor predeterminado del sistema.
                if os.name == 'nt': # Para Windows
                    os.startfile(doc_path)
                elif os.uname().sysname == 'Darwin': # Para macOS
                    subprocess.call(['open', doc_path])
                else: # Para Linux y otros sistemas Unix-like
                    subprocess.call(['xdg-open', doc_path])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el PDF de documentación: {str(e)}")

    def crear_pdf_documentacion(self, ruta):
        """
        Crea un archivo PDF con información básica de la documentación del proyecto.
        """
        pdf = FPDF() # Crea una nueva instancia de FPDF.
        pdf.add_page() # Añade una nueva página.
        pdf.set_font("Arial", size=16, style='B') # Establece la fuente para el título.
        pdf.cell(200, 10, txt="Documentación del Proyecto Kakuro", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", size=12) # Restablece la fuente para el contenido.
        pdf.multi_cell(0, 10, txt="Este documento proporciona una visión general del proyecto del juego Kakuro.")
        pdf.ln(5)

        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="1. Descripción del Proyecto", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt="El juego Kakuro es un pasatiempo de lógica basado en sumas cruzadas. El objetivo es rellenar una cuadrícula de 9x9 con números del 1 al 9, de modo que la suma de los números en cada bloque horizontal y vertical coincida con las claves numéricas dadas, sin repetir números dentro de un mismo bloque.")
        pdf.ln(5)

        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="2. Objetivos del Desarrollo", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt="- Aplicar la metodología de desarrollo de programas (análisis, diseño, codificación, prueba).")
        pdf.multi_cell(0, 10, txt="- Reforzar el uso de Python, incluyendo estructuras de datos (pilas), programación estructurada y manejo de archivos.")
        pdf.multi_cell(0, 10, txt="- Implementar una interfaz gráfica de usuario (GUI) con Tkinter.")
        pdf.multi_cell(0, 10, txt="- Fomentar buenas prácticas de programación (documentación, nombres significativos, reutilización de código).")
        pdf.multi_cell(0, 10, txt="- Utilizar software de control de versiones (Git).")
        pdf.ln(5)

        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="3. Estructura del Código", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt="El proyecto está modularizado en varios archivos Python para una mejor organización:")
        pdf.multi_cell(0, 10, txt="- kakuro.py: Punto de entrada principal.")
        pdf.multi_cell(0, 10, txt="- interfaz_grafica.py: Maneja la GUI y la interacción del usuario.")
        pdf.multi_cell(0, 10, txt="- logica_juego.py: Contiene la lógica central del juego (validaciones, movimientos, etc.).")
        pdf.multi_cell(0, 10, txt="- gestion_archivos.py: Funciones para la lectura y escritura de datos (partidas, récords, configuración).")
        pdf.multi_cell(0, 10, txt="- configuracion.py: Clase para gestionar los ajustes del juego.")
        pdf.ln(5)

        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="4. Archivos de Datos", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt="- kakuro_partidas.json: Almacena las definiciones de los tableros de Kakuro por nivel de dificultad.")
        pdf.multi_cell(0, 10, txt="- kakuro_records.txt: Guarda los récords de los jugadores (nombre y tiempo).")
        pdf.multi_cell(0, 10, txt="- kakuro_juego_actual.txt: Permite guardar y cargar el progreso de una partida.")
        pdf.multi_cell(0, 10, txt="- kakuro_configuracion.txt: Almacena la configuración persistente del usuario.")
        pdf.ln(5)

        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="5. Uso de Herramientas y Tecnologías", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt="- Lenguaje de Programación: Python 3.x")
        pdf.multi_cell(0, 10, txt="- Interfaz Gráfica: Tkinter")
        pdf.multi_cell(0, 10, txt="- Gestión de Versiones: Git")
        pdf.multi_cell(0, 10, txt="- Generación de PDF: FPDF")
        pdf.ln(5)

        pdf.set_font("Arial", size=12, style='I')
        pdf.cell(0, 10, txt="Este documento es parte de la entrega del Proyecto 3 de Taller de Programación, I Semestre 2025.", ln=True, align='C')

        pdf.output(ruta) # Guarda el PDF en la ruta especificada.

    def salir_aplicacion(self):
        """
        Cierra la aplicación después de pedir confirmación al usuario.
        """
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir del juego?"):
            self.ventana_maestra.destroy() # Cierra la ventana principal de Tkinter.

