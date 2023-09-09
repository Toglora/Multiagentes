from math import cos, sin
import threading
import socket
import json
import os

# currPath = os.path.dirname(os.path.abspath(__file__))
# currPath = "/Users/eddy/Desktop/John Deere - Cosechadores/Final/Cosechador_pyde"
currPath = "C:\\Users\\iwell\\Downloads\\Cosechador\\Cosechador_pyde"
print(currPath)

def generarNodos(listaNodos):
    for x in range(0, width, tamanoNodo):
        for y in range(0, height, tamanoNodo):
            nodo = Nodo(x, y)

            # Asignar un peso alto a los nodos dentro del área del despacho
            if nodo.x >= despacho.x and nodo.x <= despacho.x + despacho.longitud and nodo.y >= despacho.y and nodo.y <= despacho.y + despacho.anchura:
                nodo.peso = 9999.0
                
            listaNodos.append(nodo) # Agregar el nodo a la lista

def agregarVecinosANodos(listaNodos):
    for nodo in listaNodos:
        for otroNodo in listaNodos:
            if abs(nodo.x - otroNodo.x) <= tamanoNodo and abs(nodo.y - otroNodo.y) <= tamanoNodo and nodo != otroNodo:
                nodo.agregarVecino(otroNodo)

def encontrarNodoCercano(x, y, listaNodos):
    nodoCercano = None
    distanciaMinima = float('inf')
    for nodo in listaNodos:
        distancia = dist(x, y, nodo.x + tamanoNodo / 2, nodo.y + tamanoNodo / 2)
        if distancia < distanciaMinima:
            distanciaMinima = distancia
            nodoCercano = nodo
    return nodoCercano

def calcularNodosObjetivos(numCosechadores, indiceCosechador, listaNodos, longitudDespacho):
    nodosObjetivos = []
    # Calcular el tamaño de la región para cada cosechador
    regionWidth = (width - longitudDespacho) / numCosechadores
    # Calcular el número de nodos objetivos a lo largo de los ejes x e y
    numNodosX = (width - longitudDespacho) / (tamanoNodo * 2) # Divide el canvas entre el tamaño de nodos para determinar la cantidad de nodos a necesitar
    numNodosY = 2 #numCosechadores == 1 ? height / (radio * 2) : numCosechadores;  # Esto divide el eje por el numero de cosechadores

    # Generar nodos objetivos en una cuadrícula que cubra todo el canvas
    for i in range(int(numNodosX)):
        for j in range(numNodosY):
            objetivoX = i * ((width - longitudDespacho) / (numNodosX - 1))
            if i % 2 == 0:
                objetivoY = j * (height / (numNodosY - 1))
            else:
                objetivoY = height - j * (height / (numNodosY - 1))

            # Solo agregar el nodo objetivo si está dentro de la región de este cosechador
            if objetivoX >= indiceCosechador * regionWidth and objetivoX < (indiceCosechador + 1) * regionWidth:
                nodoObjetivo = encontrarNodoCercano(objetivoX, objetivoY, listaNodos)
                nodosObjetivos.append(nodoObjetivo)

    print("Total de nodos objetivos generados: " + str(len(nodosObjetivos)))
    for nodo in nodosObjetivos:
        print("Objetivo: (" + str(nodo.x) + "," + str(nodo.y) + ")")
    return nodosObjetivos

def dibujarNodosObjetivos(nodosObjetivos, indiceCosechador):
    # Cambiar el color de la elipse en función del índice del cosechador
    if indiceCosechador % 3 == 0:
        fill(255, 0, 0) # Rojo para el primer cosechador
    elif indiceCosechador % 3 == 1:
        fill(0, 255, 0) # Verde para el segundo cosechador
    elif indiceCosechador % 3 == 2:
        fill(0, 0, 255) # Azul para el tercer cosechador

    for nodo in nodosObjetivos:
        ellipse(nodo.x + tamanoNodo/2, nodo.y + tamanoNodo/2, 10, 10) # Dibuja un círculo en la posición del nodo

        
class AEstrella:
    def __init__(self, nodos):
        self.nodos = nodos

    def encontrarCaminoAEstrella(self, nodoInicial, nodoObjetivo):
        abiertos = []
        cerrados = []
        abiertos.append(nodoInicial)
        while abiertos:
            actual = self.encontrarNodoMenorCostoF(abiertos)
            abiertos.remove(actual)
            cerrados.append(actual)
            # Si hemos llegado al nodo objetivo, reconstruimos el camino y lo retornamos
            if actual == nodoObjetivo:
                camino = self.reconstruirCamino(actual)
                return camino
            for vecino in actual.vecinos:
                if vecino in cerrados or vecino.peso == 9999.0 or actual.esDescendiente(vecino):
                    continue

                nuevoCostoG = actual.costoG + dist(actual.x, actual.y, vecino.x, vecino.y) * vecino.peso

                with mi_bloqueo:
                    if vecino not in abiertos or nuevoCostoG < vecino.costoG:
                        # Solo se agrega el vecino si es un mejor camino o no está en la lista abiertos
                        if vecino not in abiertos:
                            abiertos.append(vecino)
                        vecino.padre = actual
                        vecino.costoG = nuevoCostoG
                        vecino.calcularHeuristica(nodoObjetivo)
                        vecino.calcularFuncionEvaluacion()

        print("No se encontró un camino al nodo objetivo.")
        return []  # No se encontró un camino

    def encontrarNodoMenorCostoF(self, nodos):
        menor = nodos[0]
        for nodo in nodos:
            if nodo.costoF < menor.costoF:
                menor = nodo
        return menor

    def reconstruirCamino(self, nodo):
        camino = []
        actual = nodo
        while actual is not None:
            camino.insert(0, actual)
            actual = actual.padre
        return camino
        
class SocketSender:
    def _init_(self):
        self.host = "localhost"
        self.port = 10000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send(self, data):
        self.sock.sendall(data.encode("utf-8"))
        response = self.sock.recv(1024).decode("utf-8")
        print(response)
    
    def close(self):
        self.sock.close()
        
    def _del_(self):
        self.sock.close()


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
        self.costoH = dist(self.x, self.y, objetivo.x, objetivo.y)

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
        self.costoG = nodoInicial.costoG + dist(self.x, self.y, nodoInicial.x, nodoInicial.y)
        self.costoH = dist(self.x, self.y, nodoObjetivo.x, nodoObjetivo.y)
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
            self.longitud = random(1) * tamanoNodo + 10
            self.anchura = random(1) * ((tamanoNodo * 2) + 20)
        else:
            self.longitud = longitud
            self.anchura = anchura
        self.tipoDespacho = None
        self.posicion(self.longitud, self.anchura)

    def posicion(self, longitud, anchura):
        """
        Sets the position and type of the dispatch based on its length and width,
        ensuring that it is attached to an edge if possible.

        :param longitud: The length (width) of the dispatch.
        :param anchura: The width (height) of the dispatch.
        """
        # Attached to the right edge
        self.x = width - longitud
        self.tipoDespacho = "Right Edge"
        self.y = random(1) * (height - anchura)

    def dibujar(self):
        """
        Draws the dispatch as a rectangle in the established position.
        """
        rect(self.x, self.y, self.longitud, self.anchura)

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
        self.distance = 5  # Constant distance between the collector and the harvester
        self.offsetX = 2  # Lateral displacement of the collector with respect to the harvester
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
            if dist(self.x, self.y, (self.despachoToGather.x + self.despachoToGather.longitud / 2), 
                                        (self.despachoToGather.y + self.despachoToGather.anchura / 2)) < radio:
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
            if dist(self.x, self.y, self.cosechadorToFollow.x, 
                                        self.cosechadorToFollow.y) < (radio + self.distance):
                if self.cosechadorToFollow.cosechando:
                    self.almacenado +=1 
                    self.cosechadorToFollow.almacen -=1 
                self.regresando = False

            # Calculate harvester's angle of movement
            angle = atan2(self.cosechadorToFollow.velY, 
                          self.cosechadorToFollow.velX)


            # Calculate target position of collector based on angle, distance and lateral displacement
            targetX = self.cosechadorToFollow.x + cos(angle) * self.distance - sin(angle) * self.offsetX;
            targetY = self.cosechadorToFollow.y + sin(angle) * self.distance + cos(angle) * self.offsetX;

            # Modify smoothing factor only if collector is returning to harvester
            if self.regresando:
                t = 0.02;
            else:
                t = 0.1;

            self.x = lerp(self.x, targetX, t);
            self.y = lerp(self.y, targetY, t);

    def clean(self):
        """
        Clears the trail of the collector on the secondary canvas.
        """
        pg.noStroke()
        pg.fill(0,128,0)
        pg.ellipse(self.prevX,self.prevY,radio*2.3,radio*2.3)

    def display(self,c):
        """
         Shows the collector on the secondary canvas with a given color.

         :param c: The color with which the collector will be drawn.
        """
        self.clean()
        pg.stroke(0)
        pg.fill(c)
        pg.ellipse(self.x,self.y,radio*2,radio*2)

class Cosechador:
    def __init__(self, x, y, velX, velY, despacho, numCosechador):
        self.nodosCosechador = []
        generarNodos(self.nodosCosechador)
        agregarVecinosANodos(self.nodosCosechador)
        self.a_estrella = AEstrella(self.nodosCosechador)
        self.x = x
        self.y = y
        self.velX = velX
        self.velY = velY
        self.despacho = despacho
        self.nodoInicial = encontrarNodoCercano(self.x, self.y, self.nodosCosechador)
        self.almacen = 0
        self.capacidad = 1000
        print("Nodo Inicial: (" + str(self.nodoInicial.x) + "," + str(self.nodoInicial.y) + ")")
        self.primerMovimiento = True
        self.cosechando = False
        self.objetivos = []
        self.caminoObjetivo = []
        self.currentTargetIndex = 0
        self.currentCaminoIndex = 0
        self.setNodoObjetivo(numCosechador,self.nodosCosechador)

    def setNodoObjetivo(self, numCosechador,listaNodos):
        global numCosechadores
        self.objetivos = calcularNodosObjetivos(numCosechadores, numCosechador,listaNodos, self.despacho.longitud)
                            
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
                distanciaAObjetivo = dist(self.x, self.y, target.x, target.y)
                if (self.primerMovimiento and not self.caminoObjetivo) or distanciaAObjetivo <= radio:
                    if not self.primerMovimiento:
                        self.currentTargetIndex += 1
                    if self.currentTargetIndex < len(self.objetivos):
                        target = self.objetivos[self.currentTargetIndex]
                        if self.primerMovimiento:
                            # Llamar al método encontrarCaminoAEstrella de la instancia de la clase AEstrella
                            self.caminoObjetivo = self.a_estrella.encontrarCaminoAEstrella(self.nodoInicial, target)
                            self.primerMovimiento = False
                        else:
                            try:
                                self.cosechando = True
                                self.caminoObjetivo = self.a_estrella.encontrarCaminoAEstrella(self.nodoActual, target)
                                print("Camino para: " + str(self) + " con objetivo en nodo: (" + str(target.x) + "," + str(target.y) + ")")
                                for nodo in self.caminoObjetivo:
                                    print("     Nodo : (" + str(nodo.x) + "," + str(nodo.y) + ")")
                            except Exception as e:
                                # Código que se ejecuta si se produce una excepción
                                print("Se produjo un error:", e)
            speed = 0.03

            if self.caminoObjetivo and self.currentCaminoIndex < len(self.caminoObjetivo):
                nextNode = self.caminoObjetivo[self.currentCaminoIndex]
                self.x = lerp(self.x, nextNode.x, speed)
                self.y = lerp(self.y, nextNode.y, speed)
                if dist(self.x, self.y, nextNode.x, nextNode.y) <= radio:
                    self.nodoActual = nextNode
                    self.currentCaminoIndex += 1
            elif not self.caminoObjetivo and self.currentCaminoIndex:
                print("Recalculando camino...")
                # Llamar al método encontrarCaminoAEstrella de la instancia de la clase AEstrella
                print("Tamano camino previo:"+str(len(self.caminoObjetivo)))
                self.caminoObjetivo = self.a_estrella.encontrarCaminoAEstrella(self.nodoActual, target)
                print("Tamano camino despues:"+str(len(self.caminoObjetivo)))


    def clean(self):
        pg.noStroke()
        pg.fill(0, 128, 0)
        pg.ellipse(self.prevX, self.prevY, radio * 2.3, radio * 2.3)

    def display(self, c):
        self.clean()
        pg.stroke(0)
        pg.fill(c)
        pg.ellipse(self.x, self.y, radio * 2, radio * 2)
        if self.cosechando:
            pg2.fill(139, 69, 19)
            pg2.ellipse(self.prevX, self.prevY, radio * 2, radio * 2)


def setup():
    global pg, pg2, despacho, cosechadores, recolectores, caminos, width, height, currPath
    size(300,150)
    pg = createGraphics(150, 300)
    pg2 = createGraphics(150, 300)

    # Crear un objeto Despacho y generar nodos y sus conexiones
    despacho = Despacho()

    # Establecer un color verde como fondo
    background(0, 128, 0)
    
    # Inicializar posición y velocidad de los cosechadores
    velX = random(1, 3)
    velY = random(1, 3)

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
        "Cosechadores": numCosechadores,
        "Recolectores": numCosechadores
    }

    try:
        # sender.send(str(initialData))
        print(initialData)
        initDataFilename = os.path.join(currPath, "initialData.json")
        with open(initDataFilename, "w") as f:
            json.dump(initialData, f)
            f.close()
        with open(os.path.join(currPath, "data.json"), "w") as f:
            json.dump({
                "cosechadores": [{"path":[]} for i in range(numCosechadores)],
                "recolectores": [{"path":[]} for i in range(numCosechadores)]
            }, f)
            f.close()
    except Exception as e:
        print("Se produjo error: ",e)
    
    # Crear cosechadores y asignarles sus caminos objetivos
    for i in range(numCosechadores):
        # Crear el cosechador y asignarle sus nodos objetivos
        cosechador = Cosechador(startX + (i * 2 * radio), startY, velX, velY, despacho, i)
        recolector = Recolector(cosechador, despacho)
        recolectores.append(recolector)
        cosechadores.append(cosechador)
        dibujarNodosObjetivos(cosechador.objetivos,i) # Dibuja los nodos objetivos

    # Dibujar el despacho en el lienzo
    despacho.dibujar()

def draw():
    global pg, pg2, despacho, cosechadores, recolectores, caminos, numCosechadores
    try:
        # Dibujar el despacho en el lienzo principal
        despacho.dibujar()
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
        # sender.send(str(data))
        # print(data)
        data = {}
        with open(os.path.join(currPath, "data.json"), "r") as f:
            data = json.load(f)
            f.close()
        
        for i in range(numCosechadores):
            data["cosechadores"][i]["path"].append({"x": cosechadores[i].x, "y":0, "z": cosechadores[i].y})
        
        for i in range(numCosechadores):
            data["recolectores"][i]["path"].append({"x": recolectores[i].x, "y":0, "z": recolectores[i].y})
        
        with open(os.path.join(currPath, "data.json"), "w") as f:
            json.dump(data, f)
            f.close()
        # Dibujar el rastro de los recolectores directamente en el lienzo pg
        pg.beginDraw()
        pg.clear()
        for recolector in recolectores:
            recolector.display(color(0, 0, 255))
    
        # Dibujar los cosechadores en el lienzo principal pg2
        pg2.beginDraw()
        for cosechador in cosechadores:
            cosechador.display(color(255))
            if cosechador.caminoObjetivo:
                for nodo in cosechador.caminoObjetivo:
                    ellipse(nodo.x, nodo.y, 10, 10) # Dibuja un círculo en la posición del nodo
            else:
                print("Error: Falta un camino")
    
    
        pg.endDraw()
        pg2.endDraw()
    
        # Mostrar los lienzos en el lienzo principal
        image(pg2, 0, 0)
        image(pg, 0, 0)
    
        # Comentario: El siguiente bloque de código está comentado, ya que dibuja nodos y conexiones entre ellos.
        # Puedes descomentarlo si deseas visualizar las celdas/nodos y sus conexiones en la simulación.
    
        for nodo in cosechadores[0].nodosCosechador:
            # Dibuja un contorno de cada celda/nodo
            stroke(0)
            noFill()
            rect(nodo.x, nodo.y, tamanoNodo, tamanoNodo)
            fill(255)
    except Exception as e:
        print("Se produjo un error:", e)

sender = SocketSender()
mi_bloqueo = threading.Lock()
# PGraphics es una clase que representa un lienzo de gráficos en Processing, se utiliza para crear y manipular gráficos fuera del lienzo principal.
pg, pg2 = None, None
# La clase Despacho modela una zona de carga o almacén.
despacho = None
# radio es el radio de acción de los cosechadores y recolectores.
radio = 1
# tamanoNodo es el tamaño de cada celda en la cuadrícula de nodos.
tamanoNodo = 10
# numCosechadores es el número de cosechadores en la simulación.
numCosechadores = 3
# Una lista de objetos Cosechador que representan las máquinas cosechadoras.
cosechadores = []
# Una lista de objetos Recolector que representan los remolques recolectores.
recolectores = []
# Una lista de objetos Nodo que representan celdas en una cuadrícula.
listaDeNodos = []
# Una lista de arreglos de vectores PVector, que almacenan los caminos para cada cosechador.
caminos = []
prueba = [1,2,3,4,5]
