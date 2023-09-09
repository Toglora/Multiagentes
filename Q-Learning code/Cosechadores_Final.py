import agentpy as ap
import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import csv
import json

# Clase base para todos los agentes
class AgenteBase(ap.Agent):
    def setup(self):
        # Inicializa los atributos comunes a todos los agentes
        self.velocidad = 0  # Velocidad de movimiento
        self.entorno = None  # Entorno en el que se encuentra el agente
        self.x = 0  # Posición x del agente
        self.y = 0  # Posición y del agente

    def mover_a_objetivo(self, x, y):
        """
        Mueve al agente hacia el objetivo especificado por las coordenadas x e y.
        :param x: Coordenada x del objetivo.
        :param y: Coordenada y del objetivo.
        """
        t = 0.02
        self.x = x #self.x + t * (x - self.x)
        self.y = y #self.y + t * (y - self.y)

# Clase para el Cosechador
class Cosechador(AgenteBase):
    def setup(self):
        # Llama al método setup de la clase base
        super().setup()
        # Inicializa los atributos específicos del Cosechador
        self.encendido = True  # Indicador de si está encendido
        self.almacen = 0  # Cantidad de trigo almacenado
        self.direccion = "arriba"  # Dirección inicial del Cosechador
        self.nodo_actual = None  # Nodo actual del Cosechador
        self.paths = []  # Lista de nodos visitados por el Cosechador

    def step(self):
        """
        Agrega el nodo actual a la lista de nodos visitados.
        """
        self.paths.append(self.nodo_actual)

    def realizar_accion(self, accion, objetivo):
        """
        Realiza la acción seleccionada.
        :param accion: Acción a realizar.
        :param objetivo: Objetivo a alcanzar.
        :return: Tupla con el objetivo actualizado y un indicador de si la acción fue válida.
        """
        accion_valida = True
        # Implementa la lógica para realizar la acción seleccionada
        if accion == "mover_adelante":
            (objetivo,accion_valida) = self.mover_adelante(objetivo)
        elif accion == "mover_atras":
            (objetivo,accion_valida) = self.mover_atras(objetivo)
        elif accion == "girar_izquierda":
            self.girar_izquierda()
        elif accion == "girar_derecha":
            self.girar_derecha()
        # Lógica para recolectar trigo si está encendido y pasa por un nodo con trigo
        if self.encendido and self.hay_trigo_en_nodo_actual():
            self.cosechar_trigo()
        return (objetivo,accion_valida)


    def mover_adelante(self, objetivo):
        """
        Mueve al Cosechador hacia adelante en la dirección en la que está mirando.
        :param objetivo: Objetivo a alcanzar.
        :return: Tupla con el objetivo actualizado y un indicador de si la acción fue válida.
        """
        # Implementa la lógica para mover el Cosechador hacia adelante
        accion_valida = True
        if self.encendido:
            if self.direccion == "arriba":
                if self.y - 1 >= 0:
                    self.y -= 1
                    objetivo = self.entorno.obtener_nodo_actual(objetivo.x, objetivo.y - 1)
                else:
                    accion_valida = False
            elif self.direccion == "abajo":
                if self.y + 1 < self.entorno.alto_campo:
                    self.y += 1
                    objetivo = self.entorno.obtener_nodo_actual(objetivo.x, objetivo.y + 1)
                else:
                    accion_valida = False
            elif self.direccion == "izquierda":
                if self.x - 1 >= 0:
                    self.x -= 1
                    objetivo = self.entorno.obtener_nodo_actual(objetivo.x - 1, objetivo.y)
                else:
                    accion_valida = False
            elif self.direccion == "derecha":
                if self.x + 1 < self.entorno.ancho_campo:
                    self.x += 1
                    objetivo = self.entorno.obtener_nodo_actual(objetivo.x + 1, objetivo.y)
                else:
                    accion_valida = False
        return (objetivo, accion_valida)

    def mover_atras(self, objetivo):
        """
        Mueve al Cosechador hacia atrás en la dirección opuesta a la que está mirando.
        :param objetivo: Objetivo a alcanzar.
        :return: Tupla con el objetivo actualizado y un indicador de si la acción fue válida.
        """
        # Implementa la lógica para mover el Cosechador hacia atrás
        accion_valida = True
        if self.encendido:
            if self.direccion == "arriba":
                if self.y + 1 < self.entorno.alto_campo:
                    self.y += 1
                    objetivo = self.entorno.obtener_nodo_actual(objetivo.x, objetivo.y + 1)
                else:
                    accion_valida = False
            elif self.direccion == "abajo":
                if self.y - 1 >= 0:
                    self.y -= 1
                    objetivo = self.entorno.obtener_nodo_actual(objetivo.x, objetivo.y - 1)
                else:
                    accion_valida = False
            elif self.direccion == "izquierda":
                if self.x + 1 < self.entorno.ancho_campo:
                    self.x += 1
                    objetivo = self.entorno.obtener_nodo_actual(objetivo.x + 1, objetivo.y)
                else:
                    accion_valida = False
            elif self.direccion == "derecha":
                if self.x - 1 >= 0:
                    self.x -= 1
                    objetivo = self.entorno.obtener_nodo_actual(objetivo.x - 1, objetivo.y)
                else:
                    accion_valida = False
        return (objetivo, accion_valida)


    def girar_izquierda(self):
        """
        Gira al Cosechador hacia la izquierda.
        """
        # Implementa la lógica para girar el Cosechador hacia la izquierda
        if self.encendido:
            if self.direccion == "arriba":
                self.direccion = "izquierda"
            elif self.direccion == "abajo":
                self.direccion = "derecha"
            elif self.direccion == "izquierda":
                self.direccion = "abajo"
            elif self.direccion == "derecha":
                self.direccion = "arriba"

    def girar_derecha(self):
        """
        Gira al Cosechador hacia la derecha.
        """
        # Implementa la lógica para girar el Cosechador hacia la derecha
        if self.encendido:
            if self.direccion == "arriba":
                self.direccion = "derecha"
            elif self.direccion == "abajo":
                self.direccion = "izquierda"
            elif self.direccion == "izquierda":
                self.direccion = "arriba"
            elif self.direccion == "derecha":
                self.direccion = "abajo"

    def eficiencia(self):
        """
        Calcula la eficiencia del conductor.
        """
        # Implementa la lógica para calcular la eficiencia del conductor
        # Por ejemplo, se podria tener en cuenta factores como:
        # - Cantidad de trigo cosechado
        # - Distancia recorrida para llegar al objetivo
        # - Tiempo que tardó en llegar al objetivo
        # ...
        pass

    def hay_trigo_en_nodo_actual(self):
        """
        Verifica si hay trigo en el nodo actual en el que se encuentra el Cosechador.
        :return: Verdadero si hay trigo en el nodo actual, falso en caso contrario.
        """
        # Obtiene el nodo actual en el que se encuentra el cosechador
        nodo_actual = self.entorno.obtener_nodo_actual(self.x, self.y)
        # Verifica si el nodo actual tiene trigo
        return nodo_actual.tiene_trigo()

    def cosechar_trigo(self):
        """
        Cosecha el trigo en el nodo actual en el que se encuentra el Cosechador (si hay trigo).
        :return: Verdadero si se cosechó trigo, falso en caso contrario.
        """
        # Obtiene el nodo actual en el que se encuentra el cosechador
        nodo_actual = self.entorno.obtener_nodo_actual(self.x, self.y)
        # Cosecha el trigo en el nodo actual (si hay trigo)
        if nodo_actual.tiene_trigo():
            self.almacen += nodo_actual.cosechar_trigo()
            return True
        else:
            return False


# Clase para el Conductor
class Conductor(AgenteBase):
    def setup(self,cosechador_a_conducir):
        """
        Inicializa los atributos del Conductor.
        :param cosechador_a_conducir: Cosechador al cual dirige el conductor.
        """
        # Llama al método setup de la clase base
        super().setup()
        # Inicializa los atributos específicos del Conductor
        self.cosechador = cosechador_a_conducir # Cosechador al cual dirige el conductor
        self.nodo_actual = None  # Nodo en el que se encuentra el cosechador
        self.nodo_anterior = None # Nodo previo en el que se encontraba el cosechador
        self.experiencia = 0  # Nivel de experiencia del conductor
        self.objetivos = []  # Lista de objetivos a seguir
        self.q_table = {}  # Tabla Q para el Conductor, inicialmente vacía
        self.cambio_objetivo_antes_de_llegar = False  # Indica si el conductor intentó cambiar de objetivo antes de llegar al anterior
        self.mensajes_recibidos = []  # Lista de mensajes recibidos por el conductor
        self.nodos_actuales_conductores = {}  # Información sobre el nodo actual de otros conductores
        self.objetivos_conductores = {}  # Información sobre los objetivos de otros conductores
        self.nombre = None  # Nombre del conductor

    def step(self):
        """
        Realiza un paso en el entorno.
        """
        try:
            # Actualiza el nodo anterior y el nodo actual del Cosechador
            self.nodo_anterior = self.nodo_actual
            self.cosechador.nodo_actual = self.nodo_actual

            # Recibir y procesar los mensajes
            mensajes = self.recibir_mensajes()
            for mensaje in mensajes:
                # Procesa el mensaje
                self.procesar_mensaje(mensaje)

            # Observar el entorno
            observaciones = self.observar_entorno()

            # Seleccionar una acción basada en Q-learning
            accion = self.seleccionar_accion(observaciones)

            # Realizar la acción seleccionada y obtener la recompensa
            recompensa = self.realizar_accion(accion)

            # Obtener las nuevas observaciones después de la acción
            observaciones_siguiente = self.observar_entorno()

            # Actualizar la tabla Q usando Q-learning
            self.actualizar_q_table(observaciones, observaciones_siguiente, accion, recompensa)
        except Exception as e:
            print("El error encontrado es:",e)


    def crear_q_table(self):
        """
        Crea una tabla Q inicial para el Conductor.
        """
        # Valor por defecto para los elementos de la tabla Q
        default_q_value = 0
        # Obtiene las acciones posibles
        actions = self.obtener_acciones_posibles()
        # Obtiene los estados posibles (todas las posiciones en el campo)
        states = [(x, y) for x in range(self.entorno.ancho_campo) for y in range(self.entorno.alto_campo)]
        # Crea una tabla Q con todos los valores inicializados en 0
        self.q_table = {s: {a: default_q_value for a in actions} for s in states}

    def exportar_q_table(self):
        """
        Exporta la tabla Q del Conductor a un archivo CSV.
        """
        # Abre un archivo CSV en modo escritura
        with open('q_table_' + str(self.nombre) + '.csv', 'w', newline='') as csvfile:
            # Crea un objeto csv.DictWriter para escribir en el archivo
            fieldnames = ['estado', 'mover_adelante', 'mover_atras', 'girar_izquierda', 'girar_derecha', 'esperar', 'seleccionar_objetivo']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Escribe la cabecera del archivo
            writer.writeheader()
            # Recorre la tabla Q y escribe cada estado y sus acciones en una fila del archivo
            for estado, acciones in self.q_table.items():
                fila = {'estado': estado}
                fila.update(acciones)
                writer.writerow(fila)

    def importar_q_table(self):
        """
        Importa la tabla Q del Conductor desde un archivo CSV.
        """
        # Nombre del archivo CSV
        archivo_q_table = 'q_table_' + str(self.nombre) + '.csv'
        try:
            # Abre el archivo CSV en modo lectura
            with open(archivo_q_table, 'r') as csvfile:
                # Crea un objeto csv.DictReader para leer el archivo
                reader = csv.DictReader(csvfile)
                # Recorre cada fila del archivo
                for row in reader:
                    # Obtiene el estado y las acciones de la fila
                    estado = tuple(map(int, row['estado'][1:-1].split(',')))
                    acciones = {a: float(row[a]) for a in row if a != 'estado'}
                    # Actualiza la tabla Q con los valores leídos
                    self.q_table[estado] = acciones
        except FileNotFoundError:
            # El archivo no existe
            print(f"El archivo {archivo_q_table} no existe. No se pudo importar la q_table.")

    def enviar_mensaje(self, destinatario, mensaje):
        """
        Envía un mensaje al destinatario.
        :param destinatario: Destinatario del mensaje.
        :param mensaje: Mensaje a enviar.
        """
        # Envía el mensaje al destinatario
        destinatario.recibir_mensaje(mensaje)

    def recibir_mensaje(self, mensaje):
        """
        Recibe un mensaje.
        :param mensaje: Mensaje recibido.
        """
        # Agrega el mensaje a la lista de mensajes recibidos
        self.mensajes_recibidos.append(mensaje)

    def recibir_mensajes(self):
        """
        Devuelve la lista de mensajes recibidos y la vacía.
        :return: Lista de mensajes recibidos.
        """
        # Devuelve la lista de mensajes recibidos y la vacía
        mensajes = self.mensajes_recibidos
        self.mensajes_recibidos = []
        return mensajes

    def procesar_mensaje(self, mensaje):
        """
        Procesa un mensaje recibido.
        :param mensaje: Mensaje recibido.
        """
        # Actualiza el estado interno del conductor en función del mensaje recibido
        if 'nodo_actual' in mensaje:
            # Actualiza la información sobre el nodo actual de otros conductores
            self.nodos_actuales_conductores[mensaje['emisor']] = mensaje['nodo_actual']
        if 'objetivo' in mensaje:
            # Actualiza la información sobre los objetivos de otros conductores
            self.objetivos_conductores[mensaje['emisor']] = mensaje['objetivo']


    def observar_entorno(self):
        """
        Devuelve las observaciones del entorno para el Conductor.
        :return: Diccionario con las observaciones del entorno.
        """
        # Observaciones del entorno para el Conductor
        observaciones = {
            'posicion_x': self.x,
            'posicion_y': self.y,
            'experiencia': self.experiencia,
            'objetivos': self.objetivos,
            'nodo_actual_x:': self.nodo_actual.x,
            'nodo_actual_y:': self.nodo_actual.y
        }
        return observaciones

    def seleccionar_accion(self, observaciones):
        """
        Selecciona una acción para el Conductor utilizando una política epsilon-greedy.
        :param observaciones: Observaciones del entorno.
        :return: Acción seleccionada.
        """
        # Convierte las observaciones a un estado discreto
        estado_actual = self.convertir_observaciones_a_estado(observaciones)

        # Parámetro epsilon para la política epsilon-greedy
        epsilon = 0.1

        if random.uniform(0, 1) < epsilon:
            # Acción aleatoria con probabilidad epsilon (exploración)
            acciones_posibles = self.obtener_acciones_posibles()
            return random.choice(acciones_posibles)
        else:
            # Acción óptima según los valores Q (explotación)
            accion_optima = self.obtener_accion_optima(estado_actual)

            # Verifica si la acción óptima causaría una colisión con otros conductores
            if self.verificar_colision(accion_optima):
                # Elige una acción diferente para evitar la colisión
                acciones_posibles = self.obtener_acciones_posibles()
                acciones_posibles.remove(accion_optima)
                return random.choice(acciones_posibles)
            else:
                return accion_optima

    def convertir_observaciones_a_estado(self, observaciones):
        """
        Convierte las observaciones a un estado discreto.
        :param observaciones: Observaciones del entorno.
        :return: Estado discreto que representa las observaciones.
        """
        # Definimos cómo mapear las observaciones a un estado discreto

        # Consideramos la posición del Cosechador
        posicion_x = observaciones['posicion_x']
        posicion_y = observaciones['posicion_y']

        # Combina las observaciones en un estado discreto
        estado = (posicion_x, posicion_y)

        return estado


    def obtener_acciones_posibles(self):
        """
        Define las acciones posibles que el Conductor puede tomar.
        :return: Lista de acciones posibles.
        """
        acciones_posibles = ["mover_adelante", "mover_atras", "girar_izquierda", "girar_derecha", "esperar", "seleccionar_objetivo"]
        return acciones_posibles

    def obtener_accion_optima(self, estado):
        """
        Encuentra la acción óptima según los valores Q para el estado dado.
        :param estado: Estado actual.
        :return: Acción óptima.
        """
        # Recorre las acciones posibles y elige la que tiene el mayor valor Q
        acciones_posibles = self.obtener_acciones_posibles()
        mejor_accion = None
        mejor_valor_q = float('-inf')

        for accion in acciones_posibles:
            if (estado, accion) in self.q_table:
                valor_q = self.q_table[(estado, accion)]
                if valor_q > mejor_valor_q:
                    mejor_accion = accion
                    mejor_valor_q = valor_q

        # Si no hay valores Q para las acciones posibles, elige una aleatoria
        if mejor_accion is None:
            return random.choice(acciones_posibles)
        else:
            return mejor_accion

    def realizar_accion(self, accion):
        """
        Realiza la acción seleccionada y calcula la recompensa.
        :param accion: Acción seleccionada.
        :return: Recompensa obtenida al realizar la acción.
        """
        accion_valida = True
        # Implementa la lógica para realizar la acción seleccionada
        if accion == "seleccionar_objetivo":
            if self.objetivos and self.nodo_actual != self.objetivos[-1]:
                # El conductor intenta seleccionar un nuevo objetivo antes de llegar al anterior
                self.cambio_objetivo_antes_de_llegar = True
            else:
                # Selecciona uno de los vecinos del nodo actual como objetivo
                self.objetivos.append(self.nodo_actual.seleccionar_vecino_con_mas_trigo())
                self.cambio_objetivo_antes_de_llegar = False
        elif accion != "esperar":
            # Lógica para realizar accion en el cosechador
            (self.nodo_actual, accion_valida) = self.cosechador.realizar_accion(accion, self.nodo_actual)
            # Mueve al agente hacia el objetivo
            self.mover_a_objetivo(self.nodo_actual.x,self.nodo_actual.y)

        # Calcula y devuelve la recompensa
        recompensa = self.calcular_recompensa(accion, accion_valida)  # Debes implementar esta función
        return recompensa


    def calcular_recompensa(self, accion, accion_valida):
        """
        Calcula la recompensa en función de la acción.
        :param accion: Acción realizada.
        :param accion_valida: Indicador de si la acción fue válida.
        :return: Recompensa obtenida al realizar la acción.
        """
        # Define las constantes para las recompensas y penalizaciones
        recompensa_positiva_recoleccion = 1
        penalizacion_colision = 0.5
        incentivo_eficiencia = 0.1
        incentivo_cercania_objetivo = 0.2
        recompensa_seleccion_objetivo = 0.1
        penalizacion_cambio_objetivo = 0.1
        penalizacion_accion_no_valida = 0.1
        recompensa = 0

        # Verifica si el cosechador realizo una cosecha
        recoleccion_exitosa = self.cosechador.cosechar_trigo()
        # Verifica si el valor de cosecha es el mejor de los vecinos del trigo
        llego_eficientemente = self.cosechador.eficiencia()

        if not accion_valida:
            recompensa -= penalizacion_accion_no_valida

        if recoleccion_exitosa:
            recompensa += recompensa_positiva_recoleccion  # Asigna una recompensa positiva por recolección exitosa

        # Añade una penalización por colisiones o situaciones no deseadas
        if self.verificar_colision():
            recompensa -= penalizacion_colision  # Penaliza colisiones

        # Añade un incentivo por eficiencia
        if llego_eficientemente:
            recompensa += incentivo_eficiencia  # Recompensa la eficiencia

        # Añade un incentivo por acercarse al objetivo
        if self.se_acerca_al_objetivo():
            recompensa += incentivo_cercania_objetivo  # Recompensa acercarse al objetivo

        # Añade un incentivo por seleccionar un objetivo con trigo
        if accion == "seleccionar_objetivo" and self.objetivos[-1].tiene_trigo():
            recompensa += recompensa_seleccion_objetivo

        # Añade una penalización por intentar cambiar de objetivo antes de llegar al anterior
        if self.cambio_objetivo_antes_de_llegar:
            recompensa += penalizacion_cambio_objetivo

        return recompensa

    def se_acerca_al_objetivo(self):
        """
        Verifica si el Conductor se está acercando a su objetivo.
        :return: Verdadero si el Conductor se está acercando a su objetivo, falso en caso contrario.
        """
        # Calcula la distancia entre el nodo anterior y el objetivo
        distancia_anterior = self.calcular_distancia(self.nodo_anterior, self.objetivos[-1])
        # Calcula la distancia entre el nodo actual y el objetivo
        distancia_actual = self.calcular_distancia(self.nodo_actual, self.objetivos[-1])
        # Devuelve True si la distancia actual es menor que la distancia anterior
        return distancia_actual < distancia_anterior

    def calcular_distancia(self, nodo1, nodo2):
        """
        Calcula la distancia euclidiana entre dos nodos.
        :param nodo1: Primer nodo.
        :param nodo2: Segundo nodo.
        :return: Distancia euclidiana entre los dos nodos.
        """
        dx = nodo1.x - nodo2.x
        dy = nodo1.y - nodo2.y
        return math.sqrt(dx**2 + dy**2)

    def verificar_colision(self, accion_optima=None):
        """
        Verifica si hay colisiones con otros conductores.
        :param accion_optima: Acción óptima seleccionada (opcional).
        :return: Verdadero si hay colisiones, falso en caso contrario.
        """
        # Verifica si hay colisiones con otros conductores
        for conductor, nodo in self.nodos_actuales_conductores.items():
            if self.nodo_actual == nodo:
                # Verifica si la acción óptima causaría una colisión con otros conductores
                if accion_optima is not None:
                    # Elige una acción diferente para evitar la colisión
                    acciones_posibles = self.obtener_acciones_posibles()
                    acciones_posibles.remove(accion_optima)
                    return random.choice(acciones_posibles)
                else:
                    return True
        return False


    def actualizar_q_table(self, observaciones, observaciones_siguiente, accion, recompensa):
        """
        Actualiza la tabla Q del agente Conductor utilizando el algoritmo Q-learning.
        :param observaciones: Observaciones actuales del entorno.
        :param observaciones_siguiente: Observaciones siguientes del entorno.
        :param accion: Acción realizada.
        :param recompensa: Recompensa obtenida al realizar la acción.
        """
        # Define las constantes para la tasa de aprendizaje y el factor de descuento
        tasa_aprendizaje = 0.7
        factor_descuento = 0.95

        # Convierte las observaciones en estados
        estado_actual = self.convertir_observaciones_a_estado(observaciones)
        estado_siguiente = self.convertir_observaciones_a_estado(observaciones_siguiente)

        # Verifica si el estado y la acción actuales existen en la tabla Q
        if estado_actual not in self.q_table:
            self.q_table[estado_actual] = {}
        if accion not in self.q_table[estado_actual]:
            self.q_table[estado_actual][accion] = 0  # Valor predeterminado

        # Calcula el valor Q actual para el estado y la acción actuales
        valor_q_actual = self.q_table[estado_actual][accion]

        # Encuentra el mejor valor Q posible para el siguiente estado
        if estado_siguiente not in self.q_table:
            self.q_table[estado_siguiente] = {}
            for accion in self.obtener_acciones_posibles():
                self.q_table[estado_siguiente][accion] = 0

        mejor_valor_q_siguiente = max(self.q_table[estado_siguiente].values())

        # Aplica la fórmula de actualización de Q-learning
        nuevo_valor_q = valor_q_actual + tasa_aprendizaje * (recompensa + (factor_descuento * mejor_valor_q_siguiente) - valor_q_actual)

        # Actualiza la tabla Q con el nuevo valor
        self.q_table[estado_actual][accion] = nuevo_valor_q

# Clase para el Recolector
class Recolector(AgenteBase):
    def setup(self, cosechador_a_seguir, despacho_a_utilizar):
        """
        Inicializa los atributos del Recolector.
        :param cosechador_a_seguir: Cosechador al cual seguir.
        :param despacho_a_utilizar: Despacho al cual depositar la carga.
        """
        # Llama al método setup de la clase base
        super().setup()
        # Inicializa los atributos específicos del Recolector
        self.direccion = "arriba"
        self.despacho = despacho_a_utilizar # Despacho al cual depositar la carga
        self.cosechador = cosechador_a_seguir # Cosechador al cual seguir
        self.lleno = False  # Indicador de si está lleno de trigo
        self.carga = 0 # Cantidad de trigo almacenado
        self.capacidad = 500  # Capacidad máxima de almacenamiento
        self.q_table = {}
        self.offset_para_X = 1
        self.offset_para_Y = 1
        self.nombre = None
        self.recolectando = False
        self.objetivo = None
        self.nodo_anterior = None
        self.nodo_actual = None
        self.paths = []

    def crear_q_table(self):
        """
        Crea una tabla Q inicial para el Recolector.
        """
        # Valor por defecto para los elementos de la tabla Q
        default_q_value = 0
        # Obtiene las acciones posibles
        actions = self.obtener_acciones_posibles()
        # Obtiene los estados posibles (todas las posiciones en el campo y si está lleno o no)
        states = [(x, y, lleno) for x in range(self.entorno.ancho) for y in range(self.entorno.alto) for lleno in [True, False]]
        # Crea una tabla Q con todos los valores inicializados en 0
        self.q_table = {s: {a: default_q_value for a in actions} for s in states}

    def exportar_q_table(self):
        """
        Exporta la tabla Q del Recolector a un archivo CSV.
        """
        # Abre un archivo CSV en modo escritura
        with open('q_table_'+ str(self.nombre) + '.csv', 'w', newline='') as csvfile:
            # Crea un objeto csv.DictWriter para escribir en el archivo
            fieldnames = ['estado', 'mover_adelante', 'mover_atras', 'girar_izquierda', 'girar_derecha', 'esperar']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Escribe la cabecera del archivo
            writer.writeheader()
            # Recorre la tabla Q y escribe cada estado y sus acciones en una fila del archivo
            for estado, acciones in self.q_table.items():
                fila = {'estado': estado}
                fila.update(acciones)
                writer.writerow(fila)
    
    def importar_q_table(self):
        """
        Importa la tabla Q del Recolector desde un archivo CSV.
        """
        # Construye el nombre del archivo a partir del nombre del Recolector
        archivo_q_table = 'q_table_' + str(self.nombre) + '.csv'
        try:
            # Intenta abrir el archivo en modo lectura
            with open(archivo_q_table, 'r') as csvfile:
                # Crea un objeto csv.DictReader para leer el contenido del archivo
                reader = csv.DictReader(csvfile)
                # Recorre cada fila del archivo
                for row in reader:
                    # Extrae la información sobre el estado y las acciones
                    estado_str = row['estado'][1:-1].split(',')
                    estado = tuple(int(x) if x.isdigit() else x == ' True' for x in estado_str)
                    acciones = {a: float(row[a]) for a in row if a != 'estado'}
                    # Actualiza la tabla Q con la información leída
                    self.q_table[estado] = acciones
        except FileNotFoundError:
            # El archivo no existe, puedes manejar esto según tus necesidades
            print(f"El archivo {archivo_q_table} no existe. No se pudo importar la q_table.")

    def step(self):
        """
        Realiza un paso en el ciclo de vida del Recolector.
        """
        # Guarda el nodo anterior
        self.nodo_anterior = self.nodo_actual
        # Agrega el nodo anterior a la lista de caminos
        self.paths.append(self.nodo_anterior)
        # Calcula el objetivo
        self.calcular_objetivo()
        # Aumenta la carga
        self.aumentar_carga()
        # Descarga la carga
        self.descargar_carga()
        # Observa el entorno
        observaciones = self.observar_entorno()
        # Selecciona una acción basada en Q-learning
        accion = self.seleccionar_accion(observaciones)
        # Realiza la acción seleccionada y obtiene la recompensa
        recompensa = self.realizar_accion(accion)
        # Obtener las nuevas observaciones después de la acción
        observaciones_siguiente = self.observar_entorno()
        # Actualiza la tabla Q usando Q-learning
        self.actualizar_q_table(observaciones, observaciones_siguiente, accion, recompensa)

    def aumentar_carga(self):
        """
        Aumenta la carga del Recolector si está en su objetivo y está recolectando.
        """
        if self.nodo_actual == self.objetivo and self.recolectando:
            # Calcula la cantidad de trigo que puede transferir del Cosechador al Recolector
            cantidad_transferir = min(250, self.cosechador.almacen)
            # Resta esa cantidad del almacenamiento del Cosechador
            self.cosechador.almacen -= cantidad_transferir
            # Aumenta la carga del Recolector en esa cantidad
            self.carga += cantidad_transferir

    def descargar_carga(self):
        """
        Descarga la carga del Recolector si está dentro del despacho.
        """
        if self.esta_dentro_despacho():
            # Reduce la carga en 20 unidades (hasta un mínimo de 0)
            self.carga = max(0, self.carga - 20)

    def observar_entorno(self):
        """
        Devuelve las observaciones del entorno para el Recolector.
        :return: Diccionario con las observaciones del entorno.
        """
        # Observaciones del entorno para el Conductor
        observaciones = {
            'posicion_x': self.x,
            'posicion_y': self.y,
            'lleno': self.lleno,
            'cosechador_x': self.cosechador.x,
            'cosechador_y': self.cosechador.y
        }
        return observaciones

    def seleccionar_accion(self, observaciones):
        """
        Selecciona una acción para el Recolector utilizando una política epsilon-greedy.
        :param observaciones: Observaciones del entorno.
        :return: Acción seleccionada.
        """
        # Convierte las observaciones a un estado discreto
        estado_actual = self.convertir_observaciones_a_estado(observaciones)

        # Parámetro epsilon para la política epsilon-greedy
        epsilon = 0.1

        if random.uniform(0, 1) < epsilon:
            # Acción aleatoria con probabilidad epsilon (exploración)
            acciones_posibles = self.obtener_acciones_posibles()
            return random.choice(acciones_posibles)
        else:
            # Acción óptima según los valores Q (explotación)
            return self.obtener_accion_optima(estado_actual)

    def convertir_observaciones_a_estado(self, observaciones):
        """
        Convierte las observaciones a un estado discreto.
        :param observaciones: Observaciones del entorno.
        :return: Estado discreto que representa las observaciones.
        """
        # Definimos cómo mapear las observaciones a un estado discreto

        # Consideramos la posición del recolector y si está lleno o no
        posicion_x = observaciones['posicion_x']
        posicion_y = observaciones['posicion_y']
        lleno = observaciones['lleno']

        # Combina las observaciones en un estado discreto
        estado = (posicion_x, posicion_y, lleno)

        return estado

    
    def obtener_acciones_posibles(self):
        """
        Devuelve las acciones posibles que el Recolector puede tomar.
        :return: Lista de acciones posibles.
        """
        # Define las acciones posibles que el Conductor puede tomar
        acciones_posibles = ["mover_adelante", "mover_atras", "girar_izquierda", "girar_derecha", "esperar"]
        return acciones_posibles

    def obtener_accion_optima(self, estado):
        """
        Encuentra la acción óptima según los valores Q para el estado dado.
        :param estado: Estado actual.
        :return: Acción óptima.
        """
        # Recorre las acciones posibles y elige la que tiene el mayor valor Q
        acciones_posibles = self.obtener_acciones_posibles()
        mejor_accion = None
        mejor_valor_q = float('-inf')

        for accion in acciones_posibles:
            if (estado, accion) in self.q_table:
                valor_q = self.q_table[(estado, accion)]
                if valor_q > mejor_valor_q:
                    mejor_accion = accion
                    mejor_valor_q = valor_q

        # Si no hay valores Q para las acciones posibles, elige una aleatoria
        if mejor_accion is None:
            return random.choice(acciones_posibles)
        else:
            return mejor_accion

    def calcular_objetivo(self):
        """
        Calcula el objetivo del Recolector.
        """
        if self.recolectando or self.carga == 0:
            # Calcula la mejor posición
            self.objetivo = self.calcular_mejor_posicion()
            # Establece recolectando en True y lleno en False
            self.recolectando = True
            self.lleno = False
        elif self.lleno or self.carga == self.capacidad:
            # Establece el objetivo en el nodo del despacho
            self.objetivo = self.despacho.nodo
            # Establece recolectando en False y lleno en True
            self.recolectando = False
            self.lleno = True

    def realizar_accion(self, accion):
        """
        Realiza la acción seleccionada y devuelve la recompensa.
        :param accion: Acción seleccionada.
        :return: Recompensa obtenida al realizar la acción.
        """
        # Inicializa una variable para indicar si la acción es válida
        accion_valida = True 
        # Verifica qué acción se seleccionó y llama al método correspondiente
        if accion == "mover_adelante":
            accion_valida = self.mover_adelante()
        elif accion == "mover_atras":
            accion_valida = self.mover_atras()
        elif accion == "girar_izquierda":
            self.girar_izquierda()
        elif accion == "girar_derecha":
            self.girar_derecha()
        # Mueve al Recolector hacia su objetivo
        self.mover_a_objetivo(self.nodo_actual.x,self.nodo_actual.y)   
        # Calcula y devuelve la recompensa
        recompensa = self.calcular_recompensa(accion, accion_valida)
        return recompensa

    def mover_adelante(self):
        """
        Mueve el Recolector hacia adelante.
        :return: Verdadero si la acción fue válida, falso en caso contrario.
        """
        # Inicializa una variable para indicar si la acción es válida
        accion_valida = True
        # Verifica en qué dirección está mirando el Recolector
        if self.direccion == "arriba":
            # Verifica si puede moverse hacia adelante sin salirse del entorno
            if self.y - 1 >= 0:
                # Actualiza su nodo actual
                self.nodo_actual = self.entorno.obtener_nodo_actual(self.nodo_actual.x, self.nodo_actual.y - 1)
            else:
                # No puede moverse hacia adelante, la acción no es válida
                accion_valida = False
        elif self.direccion == "abajo":
            if self.y + 1 < self.entorno.alto:
                self.nodo_actual = self.entorno.obtener_nodo_actual(self.nodo_actual.x, self.nodo_actual.y + 1)
            else:
                accion_valida = False
        elif self.direccion == "izquierda":
            if self.x - 1 >= 0:
                self.nodo_actual = self.entorno.obtener_nodo_actual(self.nodo_actual.x - 1, self.nodo_actual.y)
            else:
                accion_valida = False
        elif self.direccion == "derecha":
            if self.x + 1 < self.entorno.ancho:
                self.nodo_actual = self.entorno.obtener_nodo_actual(self.nodo_actual.x + 1, self.nodo_actual.y)
            else:
                accion_valida = False
        # Devuelve si la acción fue válida o no
        return accion_valida

    def mover_atras(self):
        """
        Mueve el Recolector hacia atrás.
        :return: Verdadero si la acción fue válida, falso en caso contrario.
        """
        # Inicializa una variable para indicar si la acción es válida
        accion_valida = True
        # Verifica en qué dirección está mirando el Recolector
        if self.direccion == "arriba":
            # Verifica si puede moverse hacia atrás sin salirse del entorno
            if self.y + 1 < self.entorno.alto_campo:
                # Actualiza su nodo actual
                self.nodo_actual = self.entorno.obtener_nodo_actual(self.nodo_actual.x, self.nodo_actual.y + 1)
            else:
                # No puede moverse hacia atrás, la acción no es válida
                accion_valida = False
        elif self.direccion == "abajo":
            if self.y - 1 >= 0:
                self.nodo_actual = self.entorno.obtener_nodo_actual(self.nodo_actual.x, self.nodo_actual.y - 1)
            else:
                accion_valida = False
        elif self.direccion == "izquierda":
            if self.x + 1 < self.entorno.ancho_campo:
                self.nodo_actual = self.entorno.obtener_nodo_actual(self.nodo_actual.x + 1, self.nodo_actual.y)
            else:
                accion_valida = False
        elif self.direccion == "derecha":
            if self.x - 1 >= 0:
                self.nodo_actual = self.entorno.obtener_nodo_actual(self.nodo_actual.x - 1, self.nodo_actual.y)
            else:
                accion_valida = False
        # Devuelve si la acción fue válida o no
        return accion_valida

    def girar_izquierda(self):
        """
        Gira el Recolector hacia la izquierda.
        """
        # Verifica en qué dirección está mirando el Recolector y actualiza su dirección
        if self.direccion == "arriba":
            self.direccion = "izquierda"
        elif self.direccion == "abajo":
            self.direccion = "derecha"
        elif self.direccion == "izquierda":
            self.direccion = "abajo"
        elif self.direccion == "derecha":
            self.direccion = "arriba"

    def girar_derecha(self):
        """
        Gira el Recolector hacia la derecha.
        """
        # Verifica en qué dirección está mirando el Recolector y actualiza su dirección
        if self.direccion == "arriba":
            self.direccion = "derecha"
        elif self.direccion == "abajo":
            self.direccion = "izquierda"
        elif self.direccion == "izquierda":
            self.direccion = "arriba"
        elif self.direccion == "derecha":
            self.direccion = "abajo"

    def calcular_recompensa(self, accion, accion_valida):
        """
        Calcula la recompensa en función de la acción realizada.
        :param accion: Acción realizada.
        :param accion_valida: Verdadero si la acción fue válida, falso en caso contrario.
        :return: Recompensa obtenida al realizar la acción.
        """
        # Define las constantes para las penalizaciones e incentivos
        penalizacion_colision = 0.1
        penalizacion_distancia = 0.1
        incentivo_eficiencia = 0.1
        incentivo_distancia = 0.1
        incentivo_seguimiento = 0.1
        incentivo_descarga = 0.1
        
        # Inicializa una variable para la recompensa
        recompensa = 0

        # Verifica si el Recolector se está acercando a su objetivo
        se_acerca_al_objetivo = self.se_acerca_al_objetivo()
        if se_acerca_al_objetivo:
            # Aumenta la recompensa en el valor del incentivo de seguimiento
            recompensa += incentivo_seguimiento
        else:
            # Disminuye la recompensa en el valor del incentivo de seguimiento
            recompensa -= incentivo_seguimiento

        # Añade una penalización por colisiones o situaciones no deseadas
        if self.verificar_colision():
            # Penaliza colisiones
            recompensa -= penalizacion_colision

        if self.esta_dentro_despacho() and self.carga == 0:
            # Aumenta la recompensa en el valor del incentivo de descarga
            recompensa += incentivo_descarga
        elif not self.esta_dentro_despacho() and self.carga == self.capacidad:
            # Disminuye la recompensa en el valor del incentivo de descarga
            recompensa -= incentivo_descarga
        
        if not se_acerca_al_objetivo and self.carga == self.capacidad:
            # Disminuye la recompensa en el valor de la penalización por distancia
            recompensa -= penalizacion_distancia

        if not se_acerca_al_objetivo and self.carga == 0 and self.recolectando:
            # Disminuye la recompensa en el valor de la penalización por distancia
            recompensa -= penalizacion_distancia
        
        if self.recolectando and self.carga == 0:
            # Aumenta la recompensa en el valor del incentivo de eficiencia
            recompensa += incentivo_eficiencia

        if se_acerca_al_objetivo:
            # Aumenta la recompensa en el valor del incentivo de distancia
            recompensa += incentivo_distancia

        return recompensa


    def esta_dentro_despacho(self):
        """
        Verifica si el Recolector está dentro del despacho.
        :return: Verdadero si está dentro del despacho, falso en caso contrario.
        """
        # Calcula los límites del despacho en las coordenadas x e y
        x_min = self.despacho.x - self.despacho.ancho / 2
        x_max = self.despacho.x + self.despacho.ancho / 2
        y_min = self.despacho.y - self.despacho.alto / 2
        y_max = self.despacho.y + self.despacho.alto / 2
        # Verifica si la posición del Recolector está dentro de esos límites
        return x_min <= self.x <= x_max and y_min <= self.y <= y_max

    def se_acerca_al_objetivo(self):
        """
        Devuelve True si el Recolector se está acercando a su objetivo.
        :return: Verdadero si se está acercando a su objetivo, falso en caso contrario.
        """
        # Calcula la distancia entre el nodo anterior y el objetivo
        distancia_anterior = self.calcular_distancia(self.nodo_anterior.x, self.nodo_anterior.y, self.objetivo.x, self.objetivo.y)
        # Calcula la distancia entre el nodo actual y el objetivo
        distancia_actual = self.calcular_distancia(self.nodo_actual.x, self.nodo_actual.y, self.objetivo.x, self.objetivo.y)
        # Compara las dos distancias
        return distancia_actual < distancia_anterior

    def calcular_distancia(self, nodo1_x,nodo1_y, nodo2_x,nodo2_y):
        """
        Calcula la distancia entre dos nodos.
        :param nodo1_x: Coordenada x del primer nodo.
        :param nodo1_y: Coordenada y del primer nodo.
        :param nodo2_x: Coordenada x del segundo nodo.
        :param nodo2_y: Coordenada y del segundo nodo.
        :return: Distancia entre los dos nodos.
        """
        # Calcula la diferencia en las coordenadas x e y entre los dos nodos
        dx = nodo1_x - nodo2_x
        dy = nodo1_y - nodo2_y
        # Utiliza el teorema de Pitágoras para calcular la distancia euclidiana entre los dos nodos
        return math.sqrt(dx**2 + dy**2)

    def verificar_colision(self):
        """
        Verifica si hay una colisión con el cosechador o con el entorno.
        :return: Verdadero si hay una colisión, falso en caso contrario.
        """
        # Verifica si hay una colisión con el cosechador
        if (self.x, self.y) == (self.cosechador.x, self.cosechador.y):
            return True

        # Verifica si hay una colisión con el entorno
        return self.entorno.verificar_colision((self.x, self.y))

    def calcular_mejor_posicion(self):
        """
        Calcula la mejor posición para seguir al cosechador.
        :return: Nodo correspondiente a la mejor posición.
        """
        # Inicializa las variables para guardar la mejor posición y la mejor métrica
        mejor_x = None
        mejor_y = None
        mejor_metrica = float('inf')

        # Obtiene el nodo en el que está el cosechador
        nodo_cosechador = self.entorno.obtener_nodo_actual(self.cosechador.x, self.cosechador.y)

        # Evalúa solo las posiciones vecinas al nodo en el que está el cosechador
        for vecino in nodo_cosechador.vecinos:
            # Calcula la métrica para esta posición
            metrica = self.calcular_metrica(vecino.x, vecino.y)

            # Si la métrica es mejor que la mejor métrica actual, actualiza la mejor posición
            if metrica < mejor_metrica:
                mejor_x = vecino.x
                mejor_y = vecino.y
                mejor_metrica = metrica

        # Obtiene el nodo correspondiente a la mejor posición
        MejorNodo = self.entorno.obtener_nodo_actual(mejor_x, mejor_y)

        return MejorNodo

    def calcular_metrica(self, x, y):
        """
        Calcula una métrica para evaluar la calidad de una posición (x, y).
        :param x: Coordenada x de la posición.
        :param y: Coordenada y de la posición.
        :return: Métrica para evaluar la calidad de la posición.
        """
        # Inicializa una variable para guardar la distancia total y define un factor de preferencia por la izquierda
        distancia_total = 0
        factor_preferencia_izquierda = 1

        # Recorre todos los nodos del entorno
        for nodo in self.entorno.nodos:
            # Calcula la distancia entre cada nodo y la posición (x, y) utilizando la distancia de Manhattan
            distancia = abs(x - nodo.x) + abs(y - nodo.y)
            # Suma esa distancia a la distancia total
            distancia_total += distancia

        # Calcula la métrica como la distancia total dividida por el número de nodos
        metrica = distancia_total / len(self.entorno.nodos)

        # Si la posición está a la izquierda del cosechador, reduce la métrica en el valor del factor de preferencia por la izquierda
        if x < self.cosechador.x:
            metrica -= factor_preferencia_izquierda

        return metrica

    def actualizar_q_table(self, observaciones, observaciones_siguiente, accion, recompensa):
        """
        Actualiza la tabla Q del agente Recolector utilizando el algoritmo Q-learning.
        :param observaciones: Observaciones actuales.
        :param observaciones_siguiente: Observaciones siguientes.
        :param accion: Acción realizada.
        :param recompensa: Recompensa obtenida.
        """
        # Define las constantes para controlar la tasa de aprendizaje y el factor de descuento
        tasa_aprendizaje = 0.7
        factor_descuento = 0.95

        # Convertir las observaciones en estados
        estado_actual = self.convertir_observaciones_a_estado(observaciones)
        estado_siguiente = self.convertir_observaciones_a_estado(observaciones_siguiente)

        # Verifica si el estado y la acción actuales existen en la tabla Q
        if estado_actual not in self.q_table:
            print(estado_actual)
            self.q_table[estado_actual] = estado_actual
        if accion not in self.q_table[estado_actual]:
            self.q_table[estado_actual][accion] = 0  # Valor predeterminado

        # Calcula el valor Q actual para el estado y la acción actuales
        valor_q_actual = self.q_table[estado_actual][accion]

        # Encuentra el mejor valor Q posible para el siguiente estado
        if estado_siguiente not in self.q_table:
            print(estado_siguiente)
            self.q_table[estado_siguiente] = estado_siguiente
        if accion not in self.q_table[estado_siguiente]:
            #print(accion)
            self.q_table[estado_siguiente][accion] = 0  # Valor predeterminado

        mejor_valor_q_siguiente = max(self.q_table[estado_siguiente].values())

        # Aplica la fórmula de actualización de Q-learning
        nuevo_valor_q = valor_q_actual + tasa_aprendizaje * (recompensa + (factor_descuento * mejor_valor_q_siguiente) - valor_q_actual)

        # Actualiza la tabla Q con el nuevo valor
        self.q_table[estado_actual][accion] = nuevo_valor_q

# Clase para el Despacho
class Despacho(AgenteBase):
    def setup(self, ancho , alto):
        """
        Configura el despacho.
        :param ancho: Anchura del despacho.
        :param alto: Altura del despacho.
        """
        super().setup()
        self.ancho = ancho # Anchura del despacho
        self.alto = alto # Altura del despacho
        self.trigo_almacenado = 0  # Cantidad de trigo almacenado en el despacho
        self.nodo = Nodo(self.x, self.y)

    def step(self):
        """
        Lógica específica del Despacho.
        """
        pass

# Clase para el Trigo
class Trigo(ap.Agent):
    def setup(self):
        """
        Configura el trigo.
        """
        self.crecido = False  # Indicador de si el trigo ha crecido
        self.cantidad = 100  # Cantidad de trigo disponible en el nodo
        self.cosechado = False

    def step(self):
        """
        Lógica específica del Trigo (puede incluir el crecimiento).
        """
        pass

class Nodo:
    def __init__(self, x, y, trigo=None, peso=1):
        """
        Constructor del Nodo.
        :param x: Coordenada x del nodo.
        :param y: Coordenada y del nodo.
        :param trigo: Objeto de Trigo en el nodo (None si no hay trigo).
        :param peso: Peso del nodo (por defecto es 1).
        """
        self.x = x  # Coordenada x del nodo
        self.y = y  # Coordenada y del nodo
        self.trigo = trigo  # Objeto de Trigo en el nodo (None si no hay trigo)
        self.peso = peso  # Peso del nodo (por defecto es 1)
        self.vecinos = []

    def agregar_vecino(self,nodoVecino):
        """
        Agrega un vecino al nodo.
        :param nodoVecino: Nodo vecino a agregar.
        """
        self.vecinos.append(nodoVecino)
    
    def seleccionar_vecino_con_mas_trigo(self):
         """
         Devuelve el vecino con más trigo.
         :return: Vecino con más trigo.
         """
         vecino_con_mas_trigo = None
         max_trigo = 0
         for vecino in self.vecinos:
             if vecino.tiene_trigo() and vecino.trigo.cantidad >= max_trigo:
                 vecino_con_mas_trigo = vecino
                 max_trigo = vecino.trigo.cantidad
         return vecino_con_mas_trigo
    
    def tiene_trigo(self):
         """
         Devuelve True si el nodo tiene trigo, False en caso contrario.
         :return: Verdadero si tiene trigo, falso en caso contrario.
         """
         if self.trigo is not None and not self.trigo.cosechado:
             return True
         else:
             return False

    def cosechar_trigo(self):
        """
        Cosecha el trigo en el nodo (si hay trigo).
        :return: Cantidad de trigo cosechado.
        """
        # Verifica si el nodo tiene trigo
        if self.tiene_trigo():
            # Guarda la cantidad de trigo cosechado
            trigo_cosechado = self.trigo.cantidad
            # Establece la cantidad de trigo del nodo en 0
            self.trigo.cantidad = 0
            # Marca el trigo como cosechado
            self.trigo.cosechado = True
            # Devuelve la cantidad de trigo cosechado
            return trigo_cosechado
        else:
            # No hay trigo para cosechar
            return 0

class EntornoRecolecta(ap.Model):
    def setup(self):
        """
        Configura el entorno.
        """
        self.ancho = self.p.ancho  # Ancho del campo
        self.alto = self.p.alto  # Alto del campo
        self.ancho_campo = self.ancho - 1
        self.alto_campo = self.alto
        self.nodos = []     # Lista de nodos en el campo
        self.tamano_nodo = self.p.tamano_nodo  # Tamaño de los nodos
        self.agentes = []  # Lista de agentes en el campo
        self.contador_pasos = 0  # Contador de pasos
        self.aprendizaje_activado = self.p.aprendizaje_activado
        self.limite_pasos = self.p.limite_pasos  # Límite de pasos para exportar la tabla Q

        # Inicializa los nodos
        self.inicializar_nodos()
        # Inicializa los agentes
        self.crear_agentes()

    def inicializar_nodos(self):
        """
        Inicializa los nodos del entorno.
        """

        # Crea una matriz para almacenar los nodos
        matriz_nodos = [[None for j in range(self.alto)] for i in range(self.ancho)]
        for i in range(self.ancho):
            for j in range(self.alto):
                if i < self.ancho_campo and j < self.alto_campo:
                    trigo = Trigo(self)  # Crea un objeto Trigo con una referencia al modelo
                    nodo = Nodo(i, j, trigo)  # Crea un nodo con el objeto Trigo
                else:
                    nodo = Nodo(i, j)  # Crea un nodo sin objeto Trigo
                matriz_nodos[i][j] = nodo  # Almacena el nodo en la matriz
                self.nodos.append(nodo)  # Agrega el nodo a la lista de nodos

        # Agrega los vecinos de cada nodo
        for i in range(self.ancho):
            for j in range(self.alto):
                nodo = matriz_nodos[i][j]
                if i > 0: nodo.agregar_vecino(matriz_nodos[i-1][j])  # Vecino a la izquierda
                if i < self.ancho - 1: nodo.agregar_vecino(matriz_nodos[i+1][j])  # Vecino a la derecha
                if j > 0: nodo.agregar_vecino(matriz_nodos[i][j-1])  # Vecino arriba
                if j < self.alto - 1: nodo.agregar_vecino(matriz_nodos[i][j+1])  # Vecino abajo
            
        # Crea el despacho en la columna del menos 1 (el lado derecho)
        despacho = Despacho(self, self.tamano_nodo, self.tamano_nodo * 2)
        y_max = self.alto - despacho.alto
        y = random.randint(0, y_max)
        self.agregar_agente(despacho, self.ancho - 1, y)
        despacho.nodo = self.obtener_nodo_actual(despacho.x,despacho.y)

    def crear_agentes(self):
        """
        Crea los agentes del entorno.
        """
        for i in range(self.p.numeroCosechadores):
            # Selecciona una posición aleatoria para el Cosechador dentro del rango de los nodos existentes
            nodo_aleatorio = random.choice(self.nodos)
            x_cosechador = nodo_aleatorio.x
            y_cosechador = nodo_aleatorio.y

            # Crea un Cosechador en la posición aleatoria
            cosechador = Cosechador(self)
            self.agregar_agente(cosechador, x_cosechador, y_cosechador)

            # Crea un Conductor para el Cosechador en la misma posición
            conductor = Conductor(self, cosechador)
            self.agregar_agente(conductor, x_cosechador, y_cosechador)
            conductor.nodo_actual = self.obtener_nodo_actual(x_cosechador,y_cosechador)
            cosechador.nodo_actual = conductor.nodo_actual
            conductor.objetivos.append(conductor.nodo_actual)
            conductor.crear_q_table()
            conductor.nombre = "Conductor " + str(i)

            # Los Recolectores deben aparecer en el Despacho
            for agente in self.agentes:
                if isinstance(agente, Despacho):
                    x_despacho = agente.x
                    y_despacho = agente.y
                    recolector = Recolector(self,cosechador, agente)
                    self.agregar_agente(recolector, x_despacho, y_despacho)
                    recolector.nodo_actual = recolector.despacho.nodo
                    recolector.crear_q_table()
            recolector.nombre = "Recolector " + str(i)
        if self.aprendizaje_activado:
            self.importar_q_table()
    
    def agregar_agente(self, agente, x, y):
        """
        Agrega un agente al campo en la posición (x, y).
        :param agente: Agente a agregar.
        :param x: Coordenada x del agente.
        :param y: Coordenada y del agente.
        """
        # Asigna una referencia al entorno al agente
        agente.entorno = self
        # Establece las coordenadas del agente
        agente.x = x
        agente.y = y
        # Agrega el agente a la lista de agentes
        self.agentes.append(agente)

    def verificar_colision(self, posicion):
        """
        Verifica si hubo una colisión en la posición dada.
        :param posicion: Posición a verificar.
        :return: Verdadero si hubo colisión, falso en caso contrario.
        """
        # Recorre los nodos en la lista de nodos
        for nodo in self.nodos:
            # Verifica si las coordenadas del nodo coinciden con la posición dada
            if (nodo.x, nodo.y) == posicion:
                # Hubo colisión
                return True
        # No hubo colisión
        return False

    def obtener_nodo_actual(self, posicionX, posicionY):
        """
        Busca el nodo en la posición (posicionX, posicionY).
        :param posicionX: Coordenada x de la posición.
        :param posicionY: Coordenada y de la posición.
        :return: Nodo en la posición dada o None si no se encuentra.
        """
        # Recorre los nodos en la lista de nodos
        for nodo in self.nodos:
            # Verifica si las propiedades x e y del nodo coinciden con posicionX y posicionY
            if nodo.x == posicionX and nodo.y == posicionY:
                # Devuelve el nodo
                return nodo
        # Si no se encuentra el nodo, devuelve None
        return None

    def step(self):
        """
        Actualiza el estado del modelo en cada paso de la simulación.
        """
        # Llama al método step de cada agente en la lista de agentes
        for agente in self.agentes:
            agente.step()

        # Verifica si todos los nodos tienen su trigo cosechado
        todos_cosechados = True
        for nodo in self.nodos:
            if nodo.trigo and not nodo.trigo.cosechado:
                todos_cosechados = False
                break

        if todos_cosechados:
            # Todos los nodos tienen su trigo cosechado, detener la simulación
            self.stop()
        else:
            # Dibuja el grafo
            self.dibujar_grafo()
        
        self.contador_pasos += 1  # Incrementa el contador de pasos
        if self.aprendizaje_activado and self.contador_pasos >= self.limite_pasos:
            # Se alcanzó el límite de pasos, exportar la tabla Q
            self.exportar_q_table()
            self.exportar_JSON()
            self.stop()

    def exportar_q_table(self):
        """
        Exporta la tabla Q de cada agente que tenga una tabla Q.
        """
        # Recorre los agentes en la lista de agentes
        for agente in self.agentes:
            # Verifica si el agente tiene una tabla Q
            if hasattr(agente, 'q_table'):
                # Exporta la tabla Q del agente
                agente.exportar_q_table()

    def importar_q_table(self):
        """
        Importa tablas Q para agentes que las tengan.
        """
        # Recorre los agentes en la lista de agentes
        for agente in self.agentes:
            # Verifica si el agente tiene una tabla Q
            if hasattr(agente, 'q_table'):
                # Importa la tabla Q del agente
                agente.importar_q_table()

    def exportar_JSON(self):
        """
        Exporta datos a un archivo JSON.
        """
        data = {"cosechadores": [], "recolectores": []}
        for agente in self.agentes:
            if hasattr(agente, 'paths'):
                agente_data = {"path": []}
                for nodo in agente.paths:
                    agente_data["path"].append({"x": nodo.x, "y": 0, "z": nodo.y})
                if isinstance(agente, Cosechador):
                    data["cosechadores"].append(agente_data)
                elif isinstance(agente, Recolector):
                    data["recolectores"].append(agente_data)
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

    def dibujar_grafo(self):
        """
        Dibuja un grafo que representa el entorno de simulación.
        """
        # Crea un objeto de grafo vacío
        G = nx.Graph()

        # Añade los nodos al grafo
        for nodo in self.nodos:
            G.add_node((nodo.x, nodo.y))

        # Crea un diccionario con las coordenadas de cada nodo
        pos = {}
        for nodo in self.nodos:
            pos[(nodo.x, nodo.y)] = (nodo.x, nodo.y)

        # Dibuja el grafo
        colors = [G.nodes[n].get('color', 'blue') for n in G.nodes]
        nx.draw(G, pos, node_color=colors, with_labels=False)

        # Dibuja el despacho como un rectángulo
        for agente in self.agentes:
            if isinstance(agente, Despacho):
                x0 = agente.x
                y0 = agente.y
                x1 = x0 + agente.ancho
                y1 = y0 + agente.alto
                plt.fill_between([x0, x1], y0, y1, color='red')
            elif isinstance(agente, Cosechador):
                # Dibuja el Cosechador como un círculo azul
                plt.plot(agente.x, agente.y, 'o', color='yellow')
            elif isinstance(agente, Recolector):
                # Dibuja el Recolector como un círculo verde
                plt.plot(agente.x, agente.y, 'o', color='green')

        #plt.show()

parametros = {
    'numeroCosechadores': 2,
    'ancho': 30,
    'alto': 15,
    'tamano_nodo': 2,
    'aprendizaje_activado': True,
    'limite_pasos': 10000
}

num_iteraciones = 1  # Número de iteraciones que quieres realizar

for i in range(num_iteraciones):
    print("Numero de iteracion: ", i)
    modelo = EntornoRecolecta(parametros)
    results = modelo.run()
    modelo.dibujar_grafo()
