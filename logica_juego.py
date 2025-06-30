# logica_juego.py
# Este módulo implementa la lógica central del juego Kakuro.
# Maneja el estado del tablero, las reglas de las jugadas, y las operaciones de deshacer/rehacer.

import random # Importa el módulo random para seleccionar partidas aleatorias.
from gestion_archivos import cargar_partidas # Importa la función para cargar las definiciones de partidas.

class LogicaJuego:
    def __init__(self, configuracion):
        """
        Constructor de la clase LogicaJuego.
        Inicializa el estado del tablero, las estructuras de datos para las claves
        y las pilas de jugadas.

        Args:
            configuracion (Configuracion): Una instancia de la clase Configuracion
                                           que contiene los ajustes actuales del juego.
        """
        self.configuracion = configuracion # Almacena la referencia al objeto de configuración.
        
        # tableros para representar el estado del juego:
        # self.tablero_actual: Matriz 9x9 que guarda los números (1-9) ingresados por el jugador.
        # Los valores iniciales son None (celdas vacías).
        self.tablero_actual = [[None for _ in range(9)] for _ in range(9)]
        
        # self.tablero_claves: Matriz 9x9 que guarda la información de las claves y el tipo de cada celda.
        # Cada elemento es un diccionario con 'tipo' (clave, rellenable, no_utilizable, vacio)
        # y los valores de las claves de fila/columna y la cantidad de casillas asociadas.
        self.tablero_claves = [[{"tipo": "vacio", "clave_fila": None, "clave_columna": None, "casillas_fila": 0, "casillas_columna": 0} for _ in range(9)] for _ in range(9)]
        
        # self.partidas_disponibles: Diccionario que almacena todas las partidas cargadas,
        # organizadas por nivel de dificultad (ej. {"facil": [partida1, partida2], ...}).
        self.partidas_disponibles = {}
        
        # self.partidas_ya_jugadas_nivel: Lista para llevar un registro de las partidas
        # que ya se han jugado en el nivel actual durante la sesión, para evitar repeticiones.
        self.partidas_ya_jugadas_nivel = []
        
        # self.partida_actual_info: Diccionario que guarda los detalles de la partida
        # que está actualmente cargada y en juego.
        self.partida_actual_info = None

        # Pilas para las funcionalidades de deshacer y rehacer jugadas.
        # Cada elemento en la pila es un diccionario que describe la jugada.
        self.pila_jugadas_realizadas = [] # Almacena las jugadas que se pueden deshacer.
        self.pila_jugadas_deshechas = [] # Almacena las jugadas que se pueden rehacer.

        # Al inicializar, carga todas las partidas disponibles desde el archivo JSON.
        self.cargar_todas_las_partidas()
        # Reinicia el estado del tablero a un estado limpio (vacío).
        self.resetear_juego()

    def cargar_todas_las_partidas(self):
        """
        Carga todas las definiciones de partidas desde el archivo JSON
        y las organiza en el diccionario `self.partidas_disponibles` por nivel de dificultad.
        """
        partidas_raw = cargar_partidas() # Llama a la función de gestión de archivos para obtener todas las partidas.
        for partida in partidas_raw:
            # Si partida es una lista, conviértela a dict usando enumerate o corrige el acceso
            # Aquí asumimos que cada 'partida' es un diccionario, pero si es una lista, accede por índices
            # Por ejemplo, si partida = [id, nivel, claves, ...], ajusta así:
            # nivel = partida[1].lower()
            # Si no, deja como estaba.
            if isinstance(partida, dict):
                nivel = partida["nivel_de_dificultad"].lower()
            elif isinstance(partida, list):
                nivel = partida[1].lower()
            else:
                continue
            if nivel not in self.partidas_disponibles:
                self.partidas_disponibles[nivel] = []
            self.partidas_disponibles[nivel].append(partida)

    def resetear_juego(self):
        """
        Reinicia el estado del tablero actual y las pilas de jugadas.
        Esto prepara el juego para una nueva partida o para borrar el juego actual.
        """
        # Reinicia el tablero de valores a todos None.
        self.tablero_actual = [[None for _ in range(9)] for _ in range(9)]
        # Reinicia el tablero de claves a su estado inicial 'vacio'.
        self.tablero_claves = [[{"tipo": "vacio", "clave_fila": None, "clave_columna": None, "casillas_fila": 0, "casillas_columna": 0} for _ in range(9)] for _ in range(9)]
        # Vacía las pilas de jugadas.
        self.pila_jugadas_realizadas = []
        self.pila_jugadas_deshechas = []
        self.partida_actual_info = None # Borra la información de la partida actual.

    def cargar_nueva_partida(self):
        """
        Selecciona una nueva partida aleatoria del nivel configurado.
        Inicializa el tablero con las claves de la partida seleccionada.

        Returns:
            bool: True si se cargó una partida exitosamente, False si no hay partidas
                  disponibles para el nivel actual.
        """
        nivel_actual = self.configuracion.nivel.lower() # Obtiene el nivel de dificultad configurado.
        
        # Verifica si hay partidas para el nivel actual.
        if nivel_actual not in self.partidas_disponibles or not self.partidas_disponibles[nivel_actual]:
            return False # No hay partidas, retorna False.

        # Filtra las partidas que aún no se han jugado en esta sesión para el nivel actual.
        partidas_filtradas = [p for p in self.partidas_disponibles[nivel_actual] if p["partida"] not in self.partidas_ya_jugadas_nivel]

        if not partidas_filtradas:
            # Si todas las partidas del nivel ya se jugaron en esta sesión,
            # reinicia la lista de partidas jugadas para permitir que se repitan.
            self.partidas_ya_jugadas_nivel = []
            partidas_filtradas = self.partidas_disponibles[nivel_actual]
            if not partidas_filtradas: # Si aún después de reiniciar no hay partidas (caso improbable).
                return False

        # Selecciona una partida aleatoria de las filtradas.
        partida_elegida = random.choice(partidas_filtradas)
        # Añade el ID de la partida a la lista de partidas ya jugadas.
        self.partidas_ya_jugadas_nivel.append(partida_elegida["partida"])
        self.partida_actual_info = partida_elegida # Almacena la información de la partida elegida.

        self.resetear_juego() # Limpia el tablero antes de cargar la nueva partida.
        # Inicializa el tablero de claves con los datos de la partida elegida.
        self._inicializar_tablero_con_claves(partida_elegida["claves"])
        return True # Retorna True indicando que la partida se cargó.

    def _inicializar_tablero_con_claves(self, claves_partida):
        """
        Rellena el `self.tablero_claves` con la información de las claves numéricas
        y marca el tipo de cada celda (clave, rellenable, no_utilizable).

        Args:
            claves_partida (list): Una lista de diccionarios, cada uno representando una clave.
        """
        for clave_data in claves_partida:
            # Ajusta las coordenadas de 1-basadas a 0-basadas para índices de lista.
            fila = clave_data["fila"] - 1
            columna = clave_data["columna"] - 1
            tipo_clave = clave_data["tipo_de_clave"] # "F" para fila, "C" para columna.
            clave_valor = clave_data["clave"] # El valor numérico de la clave.
            casillas_cantidad = clave_data["casillas"] # Cantidad de casillas asociadas a la clave.

            # Determina el tipo de celda basado en los valores de clave y casillas.
            if clave_valor == 0 and casillas_cantidad == 0:
                # Si clave y casillas son 0, la celda no es utilizable (generalmente un bloque negro).
                self.tablero_claves[fila][columna]["tipo"] = "no_utilizable"
            else:
                # Si tiene valores, es una celda de clave.
                self.tablero_claves[fila][columna]["tipo"] = "clave"
                if tipo_clave == "F":
                    # Si es clave de fila, guarda su valor y cantidad de casillas.
                    self.tablero_claves[fila][columna]["clave_fila"] = clave_valor
                    self.tablero_claves[fila][columna]["casillas_fila"] = casillas_cantidad
                elif tipo_clave == "C":
                    # Si es clave de columna, guarda su valor y cantidad de casillas.
                    self.tablero_claves[fila][columna]["clave_columna"] = clave_valor
                    self.tablero_claves[fila][columna]["casillas_columna"] = casillas_cantidad

        # Después de procesar todas las claves, marca las celdas restantes como "rellenables".
        # Una celda es rellenable si no es una celda de clave ni una celda no utilizable.
        for r in range(9):
            for c in range(9):
                if self.tablero_claves[r][c]["tipo"] == "vacio":
                    self.tablero_claves[r][c]["tipo"] = "rellenable"

    def obtener_tipo_celda(self, fila, columna):
        """
        Retorna el tipo de celda en una posición específica del tablero.

        Args:
            fila (int): Índice de la fila (0-8).
            columna (int): Índice de la columna (0-8).

        Returns:
            str: El tipo de celda ("clave", "rellenable", "no_utilizable", "vacio").
        """
        return self.tablero_claves[fila][columna]["tipo"]

    def obtener_claves_celda(self, fila, columna):
        """
        Retorna los valores de las claves de fila y columna para una celda dada.

        Args:
            fila (int): Índice de la fila (0-8).
            columna (int): Índice de la columna (0-8).

        Returns:
            tuple: Una tupla (clave_fila, clave_columna). Los valores pueden ser None.
        """
        data_celda = self.tablero_claves[fila][columna]
        return data_celda["clave_fila"], data_celda["clave_columna"]

    def obtener_valor_celda(self, fila, columna):
        """
        Retorna el valor numérico actual en una celda rellenable.

        Args:
            fila (int): Índice de la fila (0-8).
            columna (int): Índice de la columna (0-8).

        Returns:
            int or None: El número en la celda, o None si está vacía.
        """
        return self.tablero_actual[fila][columna]

    def realizar_jugada(self, fila, columna, valor):
        """
        Intenta colocar un número en una celda del tablero y valida la jugada
        según las reglas de Kakuro (no repetición en grupo, suma no excedida).

        Args:
            fila (int): Índice de la fila donde se intenta colocar el número.
            columna (int): Índice de la columna donde se intenta colocar el número.
            valor (int): El número (1-9) que se intenta colocar.

        Returns:
            dict: Un diccionario con "valida" (bool) y "mensaje" (str) explicando el resultado.
        """
        # Validación básica del rango del número.
        if not (1 <= valor <= 9):
            return {"valida": False, "mensaje": "El número debe estar entre 1 y 9."}

        # Guarda el valor actual de la celda antes de la jugada para permitir deshacer.
        jugada_anterior = self.tablero_actual[fila][columna]
        
        # Realiza la jugada temporalmente para las validaciones.
        self.tablero_actual[fila][columna] = valor

        # 1. Validación de no repetición en el grupo de fila.
        # Obtiene el grupo de celdas rellenables asociadas a la clave de fila.
        grupo_fila = self._obtener_grupo_fila(fila, columna)
        if self._numero_repetido_en_grupo(valor, grupo_fila):
            # Si el número se repite, revierte la jugada y retorna un error.
            self.tablero_actual[fila][columna] = jugada_anterior
            return {"valida": False, "mensaje": f"JUGADA NO ES VÁLIDA PORQUE EL NÚMERO {valor} YA ESTÁ EN SU GRUPO DE FILA"}

        # 2. Validación de no repetición en el grupo de columna.
        # Obtiene el grupo de celdas rellenables asociadas a la clave de columna.
        grupo_columna = self._obtener_grupo_columna(fila, columna)
        if self._numero_repetido_en_grupo(valor, grupo_columna):
            # Si el número se repite, revierte la jugada y retorna un error.
            self.tablero_actual[fila][columna] = jugada_anterior
            return {"valida": False, "mensaje": f"JUGADA NO ES VÁLIDA PORQUE EL NÚMERO {valor} YA ESTÁ EN SU GRUPO DE COLUMNA"}

        # 3. Validación de la suma de fila.
        # Obtiene la información de la clave de fila asociada a esta celda.
        clave_fila_info = self._obtener_info_clave_fila_asociada(fila, columna)
        if clave_fila_info:
            # Calcula la suma actual de los números en el grupo de fila.
            suma_actual_fila = sum(v for v in clave_fila_info["valores_grupo"] if v is not None)
            # Si la suma excede la clave numérica, la jugada no es válida.
            if suma_actual_fila > clave_fila_info["clave_valor"]:
                self.tablero_actual[fila][columna] = jugada_anterior
                return {"valida": False, "mensaje": f"JUGADA NO ES VÁLIDA PORQUE LA SUMA DE LA FILA ES {suma_actual_fila} Y LA CLAVE NUMÉRICA ES {clave_fila_info['clave_valor']}"}
            # Si el grupo de fila está completo y la suma no coincide, la jugada no es válida.
            elif len([v for v in clave_fila_info["valores_grupo"] if v is not None]) == clave_fila_info["casillas_cantidad"] and suma_actual_fila != clave_fila_info["clave_valor"]:
                self.tablero_actual[fila][columna] = jugada_anterior
                return {"valida": False, "mensaje": f"JUGADA NO ES VÁLIDA PORQUE LA SUMA DE LA FILA ES {suma_actual_fila} Y LA CLAVE NUMÉRICA ES {clave_fila_info['clave_valor']}"}

        # 4. Validación de la suma de columna.
        # Obtiene la información de la clave de columna asociada a esta celda.
        clave_columna_info = self._obtener_info_clave_columna_asociada(fila, columna)
        if clave_columna_info:
            # Calcula la suma actual de los números en el grupo de columna.
            suma_actual_columna = sum(v for v in clave_columna_info["valores_grupo"] if v is not None)
            # Si la suma excede la clave numérica, la jugada no es válida.
            if suma_actual_columna > clave_columna_info["clave_valor"]:
                self.tablero_actual[fila][columna] = jugada_anterior
                return {"valida": False, "mensaje": f"JUGADA NO ES VÁLIDA PORQUE LA SUMA DE LA COLUMNA ES {suma_actual_columna} Y LA CLAVE NUMÉRICA ES {clave_columna_info['clave_valor']}"}
            # Si el grupo de columna está completo y la suma no coincide, la jugada no es válida.
            elif len([v for v in clave_columna_info["valores_grupo"] if v is not None]) == clave_columna_info["casillas_cantidad"] and suma_actual_columna != clave_columna_info["clave_valor"]:
                self.tablero_actual[fila][columna] = jugada_anterior
                return {"valida": False, "mensaje": f"JUGADA NO ES VÁLIDA PORQUE LA SUMA DE LA COLUMNA ES {suma_actual_columna} Y LA CLAVE NUMÉRICA ES {clave_columna_info['clave_valor']}"}

        # Si todas las validaciones pasan, la jugada es válida.
        # Guarda la jugada en la pila de jugadas realizadas para permitir deshacer.
        self.pila_jugadas_realizadas.append({"fila": fila, "columna": columna, "valor_anterior": jugada_anterior, "valor_nuevo": valor})
        self.pila_jugadas_deshechas = [] # Limpia la pila de rehacer, ya que se hizo una nueva jugada.
        return {"valida": True, "mensaje": "Jugada válida."}

    def _obtener_grupo_fila(self, fila, columna):
        """
        Identifica y retorna los valores de las celdas rellenables que forman
        el grupo horizontal asociado a la celda (fila, columna).
        Un grupo horizontal comienza después de una celda de clave de fila o una celda no utilizable.
        """
        grupo = []
        # Busca hacia la izquierda desde la celda actual para encontrar el inicio del grupo.
        # El inicio del grupo es la celda de clave de fila o la celda no utilizable más cercana.
        inicio_grupo_col = columna
        while inicio_grupo_col >= 0:
            tipo_celda_actual = self.tablero_claves[fila][inicio_grupo_col]["tipo"]
            if tipo_celda_actual == "clave" and self.tablero_claves[fila][inicio_grupo_col]["clave_fila"] is not None:
                # Si encuentra una clave de fila, el grupo comienza en la siguiente columna.
                inicio_grupo_col += 1
                break
            elif tipo_celda_actual == "no_utilizable":
                # Si encuentra una celda no utilizable, el grupo comienza en la siguiente columna.
                inicio_grupo_col += 1
                break
            inicio_grupo_col -= 1
        
        # Si el bucle terminó sin encontrar una clave o no utilizable a la izquierda,
        # significa que el grupo empieza en la columna 0.
        if inicio_grupo_col < 0:
            inicio_grupo_col = 0

        # Recorre las celdas desde el inicio del grupo hasta el final de la fila
        # o hasta encontrar otra celda de clave/no utilizable.
        for c in range(inicio_grupo_col, 9):
            tipo_celda_actual = self.tablero_claves[fila][c]["tipo"]
            if tipo_celda_actual == "rellenable":
                grupo.append(self.tablero_actual[fila][c])
            elif tipo_celda_actual == "clave" or tipo_celda_actual == "no_utilizable":
                break # El grupo termina aquí.
        return grupo

    def _obtener_grupo_columna(self, fila, columna):
        """
        Identifica y retorna los valores de las celdas rellenables que forman
        el grupo vertical asociado a la celda (fila, columna).
        Un grupo vertical comienza después de una celda de clave de columna o una celda no utilizable.
        """
        grupo = []
        # Busca hacia arriba desde la celda actual para encontrar el inicio del grupo.
        # El inicio del grupo es la celda de clave de columna o la celda no utilizable más cercana.
        inicio_grupo_fila = fila
        while inicio_grupo_fila >= 0:
            tipo_celda_actual = self.tablero_claves[inicio_grupo_fila][columna]["tipo"]
            if tipo_celda_actual == "clave" and self.tablero_claves[inicio_grupo_fila][columna]["clave_columna"] is not None:
                # Si encuentra una clave de columna, el grupo comienza en la siguiente fila.
                inicio_grupo_fila += 1
                break
            elif tipo_celda_actual == "no_utilizable":
                # Si encuentra una celda no utilizable, el grupo comienza en la siguiente fila.
                inicio_grupo_fila += 1
                break
            inicio_grupo_fila -= 1
        
        # Si el bucle terminó sin encontrar una clave o no utilizable arriba,
        # significa que el grupo empieza en la fila 0.
        if inicio_grupo_fila < 0:
            inicio_grupo_fila = 0

        # Recorre las celdas desde el inicio del grupo hasta el final de la columna
        # o hasta encontrar otra celda de clave/no utilizable.
        for r in range(inicio_grupo_fila, 9):
            tipo_celda_actual = self.tablero_claves[r][columna]["tipo"]
            if tipo_celda_actual == "rellenable":
                grupo.append(self.tablero_actual[r][columna])
            elif tipo_celda_actual == "clave" or tipo_celda_actual == "no_utilizable":
                break # El grupo termina aquí.
        return grupo

    def _numero_repetido_en_grupo(self, numero, grupo):
        """
        Verifica si un número ya está repetido en un grupo de celdas.
        Ignora los valores None (celdas vacías).

        Args:
            numero (int): El número a verificar.
            grupo (list): Una lista de valores de celdas (int o None) que forman un grupo.

        Returns:
            bool: True si el número se repite en el grupo (excluyendo la celda actual si es la misma),
                  False en caso contrario.
        """
        # Filtra los valores None y cuenta las ocurrencias del número.
        numeros_existentes = [val for val in grupo if val is not None]
        # Si el número aparece más de una vez, significa que hay una repetición.
        return numeros_existentes.count(numero) > 1

    def _obtener_info_clave_fila_asociada(self, fila, columna):
        """
        Encuentra la clave de fila asociada a una celda rellenable y retorna
        su valor, la cantidad de casillas y los valores actuales del grupo.

        Args:
            fila (int): Índice de la fila de la celda rellenable.
            columna (int): Índice de la columna de la celda rellenable.

        Returns:
            dict or None: Un diccionario con 'clave_valor', 'casillas_cantidad', 'valores_grupo',
                          o None si no se encuentra una clave de fila asociada.
        """
        # Busca hacia la izquierda desde la celda actual para encontrar la celda de clave de fila.
        for c_clave in range(columna, -1, -1):
            celda_info = self.tablero_claves[fila][c_clave]
            if celda_info["tipo"] == "clave" and celda_info["clave_fila"] is not None:
                clave_valor = celda_info["clave_fila"]
                casillas_cantidad = celda_info["casillas_fila"]
                valores_grupo = []
                # Recorre las casillas a la derecha de la clave para formar el grupo.
                for i in range(casillas_cantidad):
                    if c_clave + 1 + i < 9: # Asegura no salirse del tablero.
                        # Añade el valor actual de la celda al grupo.
                        valores_grupo.append(self.tablero_actual[fila][c_clave + 1 + i])
                return {"clave_valor": clave_valor, "casillas_cantidad": casillas_cantidad, "valores_grupo": valores_grupo}
            elif celda_info["tipo"] == "no_utilizable":
                break # Si encuentra una celda no utilizable, el grupo termina antes.
        return None # No se encontró una clave de fila asociada.

    def _obtener_info_clave_columna_asociada(self, fila, columna):
        """
        Encuentra la clave de columna asociada a una celda rellenable y retorna
        su valor, la cantidad de casillas y los valores actuales del grupo.

        Args:
            fila (int): Índice de la fila de la celda rellenable.
            columna (int): Índice de la columna de la celda rellenable.

        Returns:
            dict or None: Un diccionario con 'clave_valor', 'casillas_cantidad', 'valores_grupo',
                          o None si no se encuentra una clave de columna asociada.
        """
        # Busca hacia arriba desde la celda actual para encontrar la celda de clave de columna.
        for r_clave in range(fila, -1, -1):
            celda_info = self.tablero_claves[r_clave][columna]
            if celda_info["tipo"] == "clave" and celda_info["clave_columna"] is not None:
                clave_valor = celda_info["clave_columna"]
                casillas_cantidad = celda_info["casillas_columna"]
                valores_grupo = []
                # Recorre las casillas hacia abajo de la clave para formar el grupo.
                for i in range(casillas_cantidad):
                    if r_clave + 1 + i < 9: # Asegura no salirse del tablero.
                        # Añade el valor actual de la celda al grupo.
                        valores_grupo.append(self.tablero_actual[r_clave + 1 + i][columna])
                return {"clave_valor": clave_valor, "casillas_cantidad": casillas_cantidad, "valores_grupo": valores_grupo}
            elif celda_info["tipo"] == "no_utilizable":
                break # Si encuentra una celda no utilizable, el grupo termina antes.
        return None # No se encontró una clave de columna asociada.

    def verificar_juego_terminado(self):
        """
        Verifica si el juego ha sido completado correctamente.
        Esto implica que todas las celdas rellenables tienen un número
        y que todas las sumas de filas y columnas son correctas, sin repeticiones.

        Returns:
            bool: True si el juego está terminado y es válido, False en caso contrario.
        """
        # Primero, verifica que todas las celdas rellenables estén llenas.
        for r in range(9):
            for c in range(9):
                if self.tablero_claves[r][c]["tipo"] == "rellenable" and self.tablero_actual[r][c] is None:
                    return False # Si encuentra una celda rellenable vacía, el juego no ha terminado.

        # Luego, verifica todas las sumas y no repeticiones para cada grupo.
        for r in range(9):
            for c in range(9):
                celda_info = self.tablero_claves[r][c]
                if celda_info["tipo"] == "clave":
                    # Valida la clave de fila si existe.
                    if celda_info["clave_fila"] is not None:
                        # Obtiene la información del grupo de fila asociado a esta clave.
                        # Se pasa (r, c+1) porque el grupo de fila empieza a la derecha de la clave.
                        info_fila = self._obtener_info_clave_fila_asociada(r, c + 1)
                        if info_fila:
                            suma_actual = sum(v for v in info_fila["valores_grupo"] if v is not None)
                            # Verifica que la suma sea correcta y que no haya números repetidos en el grupo.
                            if suma_actual != info_fila["clave_valor"] or self._numero_repetido_en_grupo_completo(info_fila["valores_grupo"]):
                                return False # Si hay un error, el juego no es válido.

                    # Valida la clave de columna si existe.
                    if celda_info["clave_columna"] is not None:
                        # Obtiene la información del grupo de columna asociado a esta clave.
                        # Se pasa (r+1, c) porque el grupo de columna empieza debajo de la clave.
                        info_columna = self._obtener_info_clave_columna_asociada(r + 1, c)
                        if info_columna:
                            suma_actual = sum(v for v in info_columna["valores_grupo"] if v is not None)
                            # Verifica que la suma sea correcta y que no haya números repetidos en el grupo.
                            if suma_actual != info_columna["clave_valor"] or self._numero_repetido_en_grupo_completo(info_columna["valores_grupo"]):
                                return False # Si hay un error, el juego no es válido.
        return True # Si todas las celdas están llenas y todas las validaciones pasan, el juego es válido.

    def _numero_repetido_en_grupo_completo(self, grupo):
        """
        Verifica si hay números repetidos en un grupo de celdas que se asume completo.
        A diferencia de `_numero_repetido_en_grupo`, este método no ignora la celda actual
        porque se usa para la validación final de un grupo ya lleno.

        Args:
            grupo (list): Una lista de valores de celdas (int) que forman un grupo completo.

        Returns:
            bool: True si hay números repetidos, False en caso contrario.
        """
        # Convierte la lista de números a un conjunto para eliminar duplicados.
        # Si la longitud de la lista original es diferente a la del conjunto, hay duplicados.
        return len(grupo) != len(set(grupo))

    def deshacer_jugada(self):
        """
        Deshace la última jugada realizada por el jugador.
        Mueve la jugada de la pila de realizadas a la pila de deshechas.

        Returns:
            bool: True si se pudo deshacer una jugada, False si la pila está vacía.
        """
        if self.pila_jugadas_realizadas: # Verifica si hay jugadas para deshacer.
            ultima_jugada = self.pila_jugadas_realizadas.pop() # Saca la última jugada de la pila.
            fila = ultima_jugada["fila"]
            columna = ultima_jugada["columna"]
            valor_anterior = ultima_jugada["valor_anterior"] # El valor que estaba antes de la jugada.
            valor_nuevo = ultima_jugada["valor_nuevo"] # El valor que se puso en la jugada.

            self.tablero_actual[fila][columna] = valor_anterior # Restaura el valor anterior en el tablero.
            # Añade la jugada a la pila de deshechas para permitir rehacerla.
            self.pila_jugadas_deshechas.append({"fila": fila, "columna": columna, "valor_anterior": valor_nuevo, "valor_nuevo": valor_anterior})
            return True
        return False # No hay jugadas para deshacer.

    def rehacer_jugada(self):
        """
        Rehace la última jugada que fue deshecha por el jugador.
        Mueve la jugada de la pila de deshechas a la pila de realizadas.

        Returns:
            bool: True si se pudo rehacer una jugada, False si la pila está vacía.
        """
        if self.pila_jugadas_deshechas: # Verifica si hay jugadas para rehacer.
            ultima_deshecha = self.pila_jugadas_deshechas.pop() # Saca la última jugada de la pila.
            fila = ultima_deshecha["fila"]
            columna = ultima_deshecha["columna"]
            valor_anterior = ultima_deshecha["valor_anterior"] # El valor que se había puesto antes de deshacer.
            valor_nuevo = ultima_deshecha["valor_nuevo"] # El valor que se restauró al deshacer.

            self.tablero_actual[fila][columna] = valor_anterior # Vuelve a poner el valor original de la jugada.
            # Añade la jugada de nuevo a la pila de realizadas.
            self.pila_jugadas_realizadas.append({"fila": fila, "columna": columna, "valor_anterior": valor_nuevo, "valor_nuevo": valor_anterior})
            return True
        return False # No hay jugadas para rehacer.

    def borrar_juego_actual(self):
        """
        Borra todas las jugadas realizadas en el tablero actual,
        restaurando el tablero a su estado inicial con solo las claves.
        """
        self.resetear_juego() # Reinicia el tablero y las pilas.
        if self.partida_actual_info:
            # Si hay una partida cargada, reinicializa el tablero de claves con esa partida.
            self._inicializar_tablero_con_claves(self.partida_actual_info["claves"])

    def obtener_estado_tablero(self):
        """
        Retorna el estado actual del tablero (valores y claves) y la información de la partida
        para poder guardar el progreso del juego.

        Returns:
            dict: Un diccionario con el estado del tablero y la partida.
        """
        return {
            "tablero_valores": self.tablero_actual, # Los números que el jugador ha puesto.
            "tablero_claves": self.tablero_claves, # La estructura de claves y tipos de celda.
            "partida_info": self.partida_actual_info # Información de la partida cargada.
        }

    def cargar_estado_tablero(self, estado_guardado):
        """
        Carga un estado de tablero previamente guardado en la lógica del juego.

        Args:
            estado_guardado (dict): Un diccionario que contiene el estado del tablero y la partida.
        """
        self.tablero_actual = estado_guardado["tablero_valores"] # Restaura los valores del tablero.
        self.tablero_claves = estado_guardado["tablero_claves"] # Restaura la estructura de claves.
        self.partida_actual_info = estado_guardado["partida_info"] # Restaura la información de la partida.

