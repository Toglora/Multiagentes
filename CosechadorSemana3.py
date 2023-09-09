from math import dist, atan2, cos, sin
from random import randint, randrange, random
import socket
import scipy.interpolate
import json

# PGraphics es una clase que representa un lienzo de gráficos en Processing, se utiliza para crear y manipular gráficos fuera del lienzo principal.
pg, pg2 = None, None
# La clase Despacho modela una zona de carga o almacén.
despacho = None
# radio es el radio de acción de los cosechadores y recolectores.
radio = 20
# tamanoNodo es el tamaño de cada celda en la cuadrícula de nodos.
tamanoNodo = 20
# numCosechadores es el número de cosechadores en la simulación.
numCosechadores = 2
# Una lista de objetos Cosechador que representan las máquinas cosechadoras.
cosechadores = []
# Una lista de objetos Recolector que representan los remolques recolectores.
recolectores = []
# Una lista de objetos Nodo que representan celdas en una cuadrícula.
listaDeNodos = []
# Una lista de arreglos de vectores PVector, que almacenan los caminos para cada cosechador.
caminos = []
prueba = 0

width = 0
height = 0

def lerp(x, y, t):
    # y_interp = scipy.interpolate.interp1d(x, y)
    # return y_interp(t)
    return x + (y - x) * t


def generarNodos(despacho):
    global listaDeNodos
    for x in range(0, width, tamanoNodo):
        for y in range(0, height, tamanoNodo):
            nodo = Nodo(x, y)

            # Asignar un peso alto a los nodos dentro del área del despacho
            if nodo.x >= despacho.x and nodo.x <= despacho.x + despacho.longitud and nodo.y >= despacho.y and nodo.y <= despacho.y + despacho.anchura:
                nodo.peso = 9999.0

            listaDeNodos.append(nodo) # Agregar el nodo a la lista

def agregarVecinosANodos():
    for nodo in listaDeNodos:
        for otroNodo in listaDeNodos:
            if abs(nodo.x - otroNodo.x) <= tamanoNodo and abs(nodo.y - otroNodo.y) <= tamanoNodo and nodo != otroNodo:
                nodo.agregarVecino(otroNodo)
def encontrarCaminoAEstrella(nodoInicial, nodoObjetivo):
    abiertos = []
    cerrados = []
    abiertos.append(nodoInicial)
    while abiertos:
        actual = encontrarNodoMenorCostoF(abiertos)
        abiertos.remove(actual)
        cerrados.append(actual)
        # Si hemos llegado al nodo objetivo, reconstruimos el camino y lo retornamos
        if actual == nodoObjetivo:
            camino = reconstruirCamino(actual)
            return camino
        for vecino in actual.vecinos:
            if vecino in cerrados or vecino.peso == 9999.0 or actual.esDescendiente(vecino):
                continue
            nuevoCostoG = actual.costoG + dist((actual.x, actual.y), (vecino.x, vecino.y)) * vecino.peso
            if vecino not in abiertos or nuevoCostoG < vecino.costoG:
                # Solo se agrega el vecino si es un mejor camino o no está en la lista abiertos
                if vecino not in abiertos:
                    abiertos.append(vecino)
                vecino.padre = actual
                vecino.costoG = nuevoCostoG
                vecino.calcularHeuristica(nodoObjetivo)
                vecino.calcularFuncionEvaluacion()

    print("No se encontró un camino al nodo objetivo.")
    return None  # No se encontró un camino

def encontrarNodoMenorCostoF(nodos):
    menor = nodos[0]
    for nodo in nodos:
        if nodo.costoF < menor.costoF:
            menor = nodo
    return menor

def reconstruirCamino(nodo):
    camino = []
    actual = nodo
    while actual is not None:
        camino.insert(0, actual)
        actual = actual.padre
    return camino

def encontrarNodoCercano(x, y, listaNodos):
    nodoCercano = None
    distanciaMinima = float('inf')
    for nodo in listaNodos:
        distancia = dist((x, y), (nodo.x + tamanoNodo / 2, nodo.y + tamanoNodo / 2))
        if distancia < distanciaMinima:
            distanciaMinima = distancia
            nodoCercano = nodo
    return nodoCercano

def calcularNodosObjetivos(numCosechadores, indiceCosechador, despacho):
    nodosObjetivos = []

    # Calcular el tamaño de la región para cada cosechador
    regionWidth = width / numCosechadores

    # Calcular el número de nodos objetivos a lo largo de los ejes x e y
    numNodosX = width / (tamanoNodo * 2) # Divide el canvas entre el tamaño de nodos para determinar la cantidad de nodos a necesitar
    numNodosY = 2 #numCosechadores == 1 ? height / (radio * 2) : numCosechadores;  # Esto divide el eje por el numero de cosechadores

    # Generar nodos objetivos en una cuadrícula que cubra todo el canvas
    for i in range(int(numNodosX)):
        for j in range(numNodosY):
            objetivoX = i * (width / (numNodosX - 1))
            if i % 2 == 0:
                objetivoY = j * (height / (numNodosY - 1))
            else:
                objetivoY = height - j * (height / (numNodosY - 1))
            if objetivoX >= despacho.x and objetivoX <= despacho.x + despacho.longitud and objetivoY >= despacho.y and objetivoY <= despacho.y + despacho.anchura:
                # Si el despacho está en la parte superior del lienzo, mover el nodo objetivo debajo del despacho
                if despacho.y + despacho.anchura / 2 < height / 2:
                    objetivoY = despacho.y + despacho.anchura + tamanoNodo
                # Si el despacho está en la parte inferior del lienzo, mover el nodo objetivo encima del despacho
                else:
                    objetivoY = despacho.y - tamanoNodo

            # Solo agregar el nodo objetivo si está dentro de la región de este cosechador
            if objetivoX >= indiceCosechador * regionWidth and objetivoX < (indiceCosechador + 1) * regionWidth:
                nodoObjetivo = encontrarNodoCercano(objetivoX, objetivoY, listaDeNodos)
                nodosObjetivos.append(nodoObjetivo)

    print("Total de nodos objetivos generados: " + str(len(nodosObjetivos)))
    for nodo in nodosObjetivos:
        print("Objetivo: (" + str(nodo.x) + "," + str(nodo.y) + ")")

    return nodosObjetivos

# def dibujarNodosObjetivos(nodosObjetivos, indiceCosechador):
#     # Cambiar el color de la elipse en función del índice del cosechador
#     if indiceCosechador % 3 == 0:
#         fill(255, 0, 0) # Rojo para el primer cosechador
#     elif indiceCosechador % 3 == 1:
#         fill(0, 255, 0) # Verde para el segundo cosechador
#     elif indiceCosechador % 3 == 2:
#         fill(0, 0, 255) # Azul para el tercer cosechador

#     for nodo in nodosObjetivos:
#         ellipse(nodo.x, nodo.y, 10, 10) # Dibuja un círculo en la posición del nodo

class Nodo:
    """
    The Nodo class represents a cell in the grid used in the A* search algorithm.
    """
    def __init__(self, x , y ):
        """
        Constructor of the Nodo class that initializes its position and weight.

        :param x: The x coordinate of the node in the grid.
        :param y: The y coordinate of the node in the grid.
        """
        self.x = x
        self.y = y
        self.vecinos = []  # List of neighboring nodes
        self.peso = 1.0  # Node weight used to mark inaccessible areas
        self.costoG = 0.0  # Accumulated cost from the initial node
        self.costoH = 0.0  # Heuristic (estimated distance to target node)
        self.costoF = 0.0  # Evaluation value f = g + h
        self.padre = None  # Parent node in the optimal path

    def agregarVecino(self, vecino):
        """
        Adds a neighboring node to this node's list of neighbors.

        :param vecino: The neighboring node to be added.
        """
        self.vecinos.append(vecino)

    def __eq__(self, other):
        if isinstance(other, Nodo):
            return self.x == other.x and self.y == other.y
        return False

    def esDescendiente(self, posibleAncestro):
        if self == posibleAncestro:
            return True
        nodo = self.padre
        while nodo is not None:
            if nodo == posibleAncestro:
                return True
            nodo = nodo.padre
        return False

    def calcularHeuristica(self, objetivo):
        """
        Calculates the heuristic (estimated distance) from this node to a target node.

        :param objetivo: The target node to which the distance is being calculated.
        """
        self.costoH = dist((self.x, self.y), (objetivo.x, objetivo.y))

    def calcularFuncionEvaluacion(self):
        """
        Calculates the evaluation function f = g + h for this node.
        """
        self.costoF = self.costoG + self.costoH

    def calcularCostos(self, nodoInicial, nodoObjetivo):
        """
        Calculates costs (g, h and f) from this node through a specific path.

        :param nodoInicial: The initial node of the path.
        :param nodoObjetivo: The target node of the path.
        """
        self.costoG = nodoInicial.costoG + dist((self.x, self.y), (nodoInicial.x, nodoInicial.y))
        self.costoH = dist((self.x, self.y), (nodoObjetivo.x, nodoObjetivo.y))
        self.costoF = self.costoG + self.costoH

class Despacho:
    """
    The Despacho class represents a rectangular area where collectors can deposit their loads.
    It can have different sizes and positions, and can be attached to an edge of the canvas.
    """
    def __init__(self, longitud=None, anchura=None):
        """
        Constructor that creates a dispatch with random dimensions within a range.

        :param longitud: The length (width) of the dispatch.
        :param anchura: The width (height) of the dispatch.
        """
        if longitud is None or anchura is None:
            self.longitud = random() * 100 + 100
            self.anchura = random() * 100 + 100
        else:
            self.longitud = longitud
            self.anchura = anchura
        self.posicion(self.longitud, self.anchura)

    def posicion(self, longitud, anchura):
        """
        Sets the position of the dispatch based on its length and width,
        ensuring that it is attached to an edge if possible.

        :param longitud: The length (width) of the dispatch.
        :param anchura: The width (height) of the dispatch.
        """
        if longitud == anchura:
            # If the dispatch is a square
            if random() < 0.5:
                # Attached to a vertical edge
                if random() < 0.5:
                    self.x = 0
                else:
                    self.x = width - longitud
                self.y = random() * (height - anchura)
            else:
                # Attached to a horizontal edge
                self.x = random() * (width - longitud)
                if random() < 0.5:
                    self.y = 0
                else:
                    self.y = height - anchura
        elif longitud > anchura:
            # If the dispatch is a horizontal rectangle
            self.x = random() * (width - longitud)
            if random() < 0.5:
                self.y = 0
            else:
                self.y = height - anchura
        else:
            # If the dispatch is a vertical rectangle
            if random() < 0.5:
                self.x = 0
            else:
                self.x = width - longitud
            self.y = random() * (height - anchura)

    # def dibujar(self):
    #     """
    #     Draws the dispatch as a rectangle in the established position.
    #     """
    #     rect(self.x, self.y, self.longitud, self.anchura)

class Recolector:
    """
    The Recolector class represents a vehicle that follows a harvester and collects nearby crops.
    It can transport an amount of crops until it reaches its maximum capacity and deposits them in the dispatch.
    """
    def __init__(self, cosechador, despacho):
        """
        Constructor that creates a collector associated with a specific harvester and dispatch.

        :param cosechador: The harvester that this collector follows.
        :param despacho: The dispatch where the collector deposits the crops.
        """
        self.distance = 50  # Constant distance between the collector and the harvester
        self.offsetX = 20  # Lateral displacement of the collector with respect to the harvester
        self.t = 0.0
        self.x = cosechador.x
        self.y = cosechador.y
        self.targetX = 0.0
        self.targetY = 0.0
        self.prevX = 0.0
        self.prevY = 0.0  # Position and movement variables
        self.lleno = False
        self.regresando = False  # Collector status indicators
        self.almacenado = 0
        self.espera = 0  # Amount of stored crops and waiting time
        self.capacidad = 500  # Maximum capacity of the collector

        self.cosechadorToFollow = cosechador  # The harvester that this collector follows
        self.despachoToGather = despacho  # The dispatch where it will deposit the crops

    def update(self):
        """
        Updates the position of the collector and its interaction with the harvester and dispatch.
        """
        # Check if the collector is full
        if self.almacenado >= self.capacidad:
            self.lleno = True

        # If the collector is full, move it smoothly towards the dispatch
        if self.lleno:
            self.prevX = self.x
            self.prevY = self.y

            # Smooth the movement of the collector towards the dispatch using linear interpolation
            t = 0.02  # Smoothing factor (between 0 and 1)
            self.x = lerp(self.x, (self.despachoToGather.x + self.despachoToGather.longitud / 2), t)
            self.y = lerp(self.y, (self.despachoToGather.y + self.despachoToGather.anchura / 2), t)

            # Check if the collector has arrived at the dispatch
            if dist((self.x, self.y), (self.despachoToGather.x + self.despachoToGather.longitud / 2, 
                                        (self.despachoToGather.y + self.despachoToGather.anchura / 2))) < radio:
                # Decrement load counter
                self.almacenado -= 1

                # Check if the collector is empty
                if self.almacenado <= 0:
                    self.lleno = False
                    self.regresando = True
        else:
            self.prevX = self.x
            self.prevY = self.y

            # Increment collection counter only if collector is close to harvester
            if dist((self.x, self.y), (self.cosechadorToFollow.x, 
                                        (self.cosechadorToFollow.y))) < (radio + self.distance):
                if self.cosechadorToFollow.cosechando:
                    self.almacenado +=1 
                    self.cosechadorToFollow.almacen -=1 
                self.regresando = False

            # Calculate harvester's angle of movement
            angle = atan2(self.cosechadorToFollow.velY, 
                          (self.cosechadorToFollow.velX))

            # Calculate target position of collector based on angle, distance and lateral displacement
            targetX = self.cosechadorToFollow.x + cos(angle) * self.distance - sin(angle) * self.offsetX
            targetY = self.cosechadorToFollow.y + sin(angle) * self.distance + cos(angle) * self.offsetX

            # Modify smoothing factor only if collector is returning to harvester
            if self.regresando:
                t = 0.02
            else:
                t = 0.1

            self.x = lerp(self.x, targetX, t)
            self.y = lerp(self.y, targetY, t)

    # def clean(self):
    #     """
    #     Clears the trail of the collector on the secondary canvas.
    #     """
    #     pg.noStroke()
    #     pg.fill(0,128,0)
    #     pg.ellipse(self.prevX,self.prevY,radio*2.3,radio*2.3)

    # def display(self,c):
    #     """
    #      Shows the collector on the secondary canvas with a given color.

    #      :param c: The color with which the collector will be drawn.
    #     """
    #     self.clean()
    #     pg.stroke(0)
    #     pg.fill(c)
    #     pg.ellipse(self.x,self.y,radio*2,radio*2)

class Cosechador:
    def __init__(self, x, y, velX, velY, despacho):
        self.nodosCosechador = []
        for nodo in listaDeNodos:
            copiaNodo = Nodo(nodo.x, nodo.y)
            copiaNodo.vecinos = list(nodo.vecinos)
            copiaNodo.peso = nodo.peso
            copiaNodo.costoG = nodo.costoG
            copiaNodo.costoH = nodo.costoH
            copiaNodo.costoF = nodo.costoF
            copiaNodo.padre = nodo.padre
            self.nodosCosechador.append(copiaNodo)
        self.x = x
        self.y = y
        self.velX = velX
        self.velY = velY
        self.despacho = despacho
        self.nodoInicial = encontrarNodoCercano(int(x), int(y), self.nodosCosechador)
        self.almacen = 0
        self.capacidad = 1000
        # print("Nodo Inicial: (" + str(self.nodoInicial.x) + "," + str(self.nodoInicial.y) + ")")
        self.primerMovimiento = True
        self.cosechando = False
        self.objetivos = []
        self.caminoObjetivo = []
        self.currentTargetIndex = 0
        self.currentCaminoIndex = 0

    def setNodoObjetivo(self, nodosObjetivosOriginales):
        self.objetivos = []
        for nodoOriginal in nodosObjetivosOriginales:
            copiaNodo = Nodo(nodoOriginal.x, nodoOriginal.y)
            copiaNodo.vecinos = list(nodoOriginal.vecinos)
            copiaNodo.peso = nodoOriginal.peso
            copiaNodo.costoG = nodoOriginal.costoG
            copiaNodo.costoH = nodoOriginal.costoH
            copiaNodo.costoF = nodoOriginal.costoF
            copiaNodo.padre = nodoOriginal.padre
            self.objetivos.append(copiaNodo)
    def update(self):
        self.prevX = self.x
        self.prevY = self.y
        if self.almacen >= self.capacidad:
            print("El almacén está lleno.")
        else:
            if self.cosechando:
                self.almacen += 1
            if self.currentTargetIndex < len(self.objetivos):
                target = self.objetivos[self.currentTargetIndex]
                distanciaAObjetivo = dist((self.x, self.y), (target.x, target.y))
                if (self.primerMovimiento and self.caminoObjetivo == None) or distanciaAObjetivo <= radio:
                    if not self.primerMovimiento:
                        self.currentTargetIndex += 1
                    if self.currentTargetIndex < len(self.objetivos):
                        target = self.objetivos[self.currentTargetIndex]
                        if self.primerMovimiento:
                            self.caminoObjetivo = encontrarCaminoAEstrella(self.nodoInicial, target)
                            self.primerMovimiento = False
                        else:
                            self.cosechando = True
                            self.caminoObjetivo = encontrarCaminoAEstrella(self.nodoActual, target)
            speed = 0.03
            if self.caminoObjetivo != None and self.currentCaminoIndex < len(self.caminoObjetivo):
                nextNode = self.caminoObjetivo[self.currentCaminoIndex]
                self.x = lerp(self.x, nextNode.x, speed)
                self.y = lerp(self.y, nextNode.y, speed)
                if dist((self.x, self.y), (nextNode.x, nextNode.y)) <= radio:
                    self.nodoActual = nextNode
                    self.currentCaminoIndex += 1

    # def clean(self):
    #     pg.noStroke()
    #     pg.fill(0, 128, 0)
    #     pg.ellipse(self.prevX, self.prevY, radio * 2.3, radio * 2.3)

    # def display(self, c):
    #     clean()
    #     pg.stroke(0)
    #     pg.fill(c)
    #     pg.ellipse(self.x, self.y, radio * 2, radio * 2)
    #     if cosechando:
    #         pg2.fill(139, 69, 19)
    #         pg2.ellipse(prevX, prevY, radio * 2, radio * 2)

class SocketSender:
    def __init__(self):
        # print("init")
        self.host = "localhost"
        self.port = 25001
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        # print("connected")

    def send(self, data: str):
        # data = json.loads(data)
        self.sock.sendall(data.encode("utf-8"))
        # response = self.sock.recv(1024).decode("utf-8")
        # print(response)
    
    def close(self):
        self.sock.close()
        
    def _del_(self):
        self.sock.close()

# sender = SocketSender()
# print(sender.sock)

def setup():
    global pg, pg2, despacho, cosechadores, recolectores, caminos, width, height, numCosechadores
    # size(800, 600)
    
    width = 800
    height = 600
    # pg = createGraphics(width, height)
    # pg2 = createGraphics(width, height)

    # Crear un objeto Despacho y generar nodos y sus conexiones
    despacho = Despacho()
    generarNodos(despacho)
    agregarVecinosANodos()
    # Establecer un color verde como fondo
    # background(0, 128, 0)

    # Inicializar posición y velocidad de los cosechadores
    velX = randint(1, 3)
    velY = randint(1, 3)

    # Calcular la posición de inicio de los cosechadores en función de la posición del despacho
    startX = 0
    startY = 0
    if despacho.x == 0:
        startX = max(despacho.x + despacho.longitud + radio, radio)
        startY = min(max(despacho.y + despacho.anchura / 2, radio), height - radio)
    elif despacho.x == width - despacho.longitud:
        startX = min(despacho.x - radio, width - radio)
        startY = min(max(despacho.y + despacho.anchura / 2, radio), height - radio)
    elif despacho.y == 0:
        startX = min(max(despacho.x + despacho.longitud / 2, radio), width - radio)
        startY = max(despacho.y + despacho.anchura + radio, radio)
    elif despacho.y == height - despacho.anchura:
        startX = min(max(despacho.x + despacho.longitud / 2, radio), width - radio)
        startY = min(despacho.y - radio, height - radio)

    initialData = {
        "Mapa": {
            "Width": width,
            "Height": height,
        },
        "Despacho": {
            "x_min": despacho.x - despacho.anchura / 2,
            "x_max": despacho.x + despacho.anchura / 2,
            "y_min": despacho.y - despacho.longitud / 2,
            "y_max": despacho.y + despacho.longitud / 2,
        },
        "Recolectores": numCosechadores,
        "Almacenadores": numCosechadores
    }

    with open("init.json", "w") as f:
        # save initial data to init.json
        json.dump(initialData, f)
        f.close()

    # sender.send(str(initialData))
    print(initialData)

    # Crear cosechadores y asignarles sus caminos objetivos
    for i in range(numCosechadores):
        # Calcular nodos objetivos para este cosechador
        nodosObjetivos = calcularNodosObjetivos(numCosechadores, i, despacho)

        # Crear el cosechador y asignarle sus nodos objetivos
        cosechador = Cosechador(startX + (i * 2 * radio), startY, velX, velY, despacho)
        recolector = Recolector(cosechador, despacho)

        # Asignar la lista de nodos objetivos al cosechador
        cosechador.setNodoObjetivo(nodosObjetivos)

        recolectores.append(recolector)
        cosechadores.append(cosechador)
        # dibujarNodosObjetivos(nodosObjetivos,i) # Dibuja los nodos objetivos
    
    with open("Data.json", "w") as f:
        json.dump({
            "Cosechadores": [ [] for i in range(numCosechadores)],
            "Recolectores": [ [] for i in range(numCosechadores)]
        }, f)
        f.close()

    # Dibujar el despacho en el lienzo
    # despacho.dibujar()


def draw():
    global pg, pg2, despacho, cosechadores, recolectores, caminos
    # Dibujar el despacho en el lienzo principal
    # despacho.dibujar()

    # Actualizar y mostrar los tractores y trailers
    
    for i in range(numCosechadores):
        cosechadores[i].update()
        recolectores[i].update()

    # data = {
    #     "Cosechadores": [
    #         {"x":cosechador.x,  "y":cosechador.y, "almacen": 0, "capacidad": 0} for cosechador in cosechadores
    #     ],
    #     "Recolectores": [
    #         {"x": recolector.x, "y": recolector.y, "almacen": 0, "capacidad": 0} for recolector in recolectores
    #     ]
    # }
    # read Data.json at cosechadores and recolectores and append to each list
    with open("Data.json", "r") as f:
        data = json.load(f)
        f.close()
    print(data)
    cosechadoresList = data["Cosechadores"]
    recolectoresList = data["Recolectores"]
    print("cosechadoresList", cosechadoresList)
    print("recolectoresList", recolectoresList)
    for i in range(numCosechadores):
        cosechadoresList[i].append({

            "x": cosechadores[i].x,
            "z": cosechadores[i].y,
            "y": 0
        })
        recolectoresList[i].append({
            "x": recolectores[i].x,
            "z": recolectores[i].y,
            "y": 0
        })
    
    data = {
        "Cosechadores": cosechadoresList,
        "Recolectores": recolectoresList
    }
        
    with open("Data.json", "w") as f:
        json.dump(data, f)
        f.close()
    


    print(data)
    # sender.send(str(data))
    
setup()
while True:
    draw()
    # sender.send(str(data))
    # time.sleep(1)




