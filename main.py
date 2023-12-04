import random
import numpy as np

# Formato entrada: 
    # Matriz de coste: (Columnas igual a operadores, filas igual a tareas)
        # 2 3 2 3 2
        # 3 2 2 3 1
        # 4 3 1 3 2
        # 1 2 2 3 2
    # Vector de tiempo requerido por tarea:
        # 3 2 2 3
    # Vector de tiempo disponible por operador:
        # 4 5 3 4 4

# Clases
class Nodo:
    def __init__(self, tarea, operador, coste):
        self.tarea = tarea
        self.operador = operador
        self.coste = coste
    
    def __str__(self) -> str:
        return "(" + str(self.tarea) + ", " + str(self.operador) + ")"

class Hormiga:
    def __init__(self, nodos, vector_tiempo_operadores, vector_tiempo_tareas, tau, eta, alpha, beta, nodo_inicial):
        self.nodos = nodos.copy()
        self.tau = tau
        self.eta = eta
        self.alpha = alpha
        self.beta = beta
        self.vector_tiempo_tareas = vector_tiempo_tareas.copy()
        self.vector_tiempo_operadores = vector_tiempo_operadores.copy()

        self.nodo_actual = nodo_inicial
        self.solucion = [nodo_inicial]
        self.coste = self.solucion[-1].coste
        self.vector_tiempo_operadores[nodo_inicial.operador] -= self.vector_tiempo_tareas[nodo_inicial.tarea]
        self.vector_tiempo_tareas[nodo_inicial.tarea] = 0

        self.nodos_disponibles = []
        for nodo in nodos:
            if nodo.tarea != nodo_inicial.tarea:
                if self.vector_tiempo_operadores[nodo.operador] > self.vector_tiempo_tareas[nodo.tarea]:
                    self.nodos_disponibles.append(nodo)
    
    def avanzar(self):
        # Elige un nodo según las siguientes probabilidades
        probabilidades = []
        if len(self.nodos_disponibles) == 1:
            probabilidades.append(1)
        else:
            for nodo in self.nodos_disponibles:
                nodo_origen = self.nodos.index(self.nodo_actual)
                nodo_destino = self.nodos.index(nodo)
                numerador = ((self.tau[nodo_origen][nodo_destino]**self.alpha)*(self.eta[nodo_origen][nodo_destino])**self.beta)
                denominador = sum((self.tau[nodo_origen][u]**self.alpha)*(self.eta[nodo_origen][u]**self.beta) for u in self.posicion_nodos_disponibles())
                probabilidades.append(numerador / denominador)
        siguiente_nodo = random.choices(self.nodos_disponibles, probabilidades)[0]
        self.actualizar_hormiga(siguiente_nodo)

    def actualizar_hormiga(self, nodo_anadido):
        self.solucion.append(nodo_anadido)
        self.coste += nodo_anadido.coste
        self.vector_tiempo_operadores[nodo_anadido.operador] -= self.vector_tiempo_tareas[nodo_anadido.tarea]
        self.vector_tiempo_tareas[nodo_anadido.tarea] = 0

        self.nodos_disponibles = []
        for nodo1 in self.nodos:
            if not any(nodo2.tarea == nodo1.tarea for nodo2 in self.solucion):
                if self.vector_tiempo_operadores[nodo1.operador] > self.vector_tiempo_tareas[nodo1.tarea]:
                    self.nodos_disponibles.append(nodo1)

    def caminos(self):
        return [(self.nodos.index(self.solucion[i]), self.nodos.index(self.solucion[i + 1])) for i in range(len(self.solucion) - 1)]
    
    def posicion_nodos_disponibles(self):
        lista = []
        for nodo in self.nodos_disponibles:
            lista.append(self.nodos.index(nodo))
        return lista            

class EAS:
    def __init__(self, matriz_coste, vector_tiempo_tareas, vector_tiempo_operadores, num_hormigas, num_hormigas_elitistas, alpha, beta, ratio_evaporacion) -> None:
        # Datos problema
        self.matriz_coste = matriz_coste
        self.num_tareas, self.num_operadores = self.matriz_coste.shape
        self.vector_tiempo_tareas = vector_tiempo_tareas
        self.vector_tiempo_operadores = vector_tiempo_operadores

        # Parámetros algoritmo EAS
        self.num_hormigas = num_hormigas
        self.num_hormigas_elitistas = num_hormigas_elitistas
        self.alpha = alpha
        self.beta = beta
        self.ratio_evaporacion = ratio_evaporacion

        # Inicialización nodos
        self.nodos = []
        for i in range(0, self.num_tareas):
            for j in range(0, self.num_operadores):
                self.nodos.append(Nodo(i, j, self.matriz_coste[i][j]))

        # Inicialización feromonas
        # La matriz de feromonas representa la cantidad que hay en cada camino entre los nodos
        # se inializan sus valores a 1/c_{ij}
        self.tau = np.full((len(self.nodos), len(self.nodos)), 1, dtype=float)
        for i in range(len(self.nodos)):
            for j in range(len(self.nodos)):
                if i == j:
                    self.tau[i][j] = 0
                else:
                    self.tau[i][j] = self.num_hormigas/self.nodos[j].coste

        # Inicialización de información heurística
        self.eta = np.full((len(self.nodos), len(self.nodos)), 1)

        self.mejor_solucion = None
        self.coste_mejor_solucion = 999999999

    def start(self, num_iteraciones):
        # Hasta que se cumpla el número de iteraciones
        for iteracion in range(num_iteraciones):
            self.hormigas = []
            for _ in range(self.num_hormigas):
                # Inicialización de hormigas en un nodo aleatorio
                hormiga = Hormiga(self.nodos, self.vector_tiempo_operadores, self.vector_tiempo_tareas, self.tau, self.eta, self.alpha, self.beta, random.choice(self.nodos))
                self.hormigas.append(hormiga)
                
                # Construcción de las soluciones
                for _ in range(self.num_tareas - 1):
                    hormiga.avanzar()

                # Actualización de la mejor solución
                if hormiga.coste < self.coste_mejor_solucion:
                    self.mejor_solucion = hormiga
                    self.coste_mejor_solucion = hormiga.coste

            # Actualización de las feromonas
            self.actualizar_feromonas()

        return self.mejor_solucion
    
    # Actualización de las feromonas
    def actualizar_feromonas(self):
        # Evaporación de la feromona
        self.eta = self.eta * (1 - self.ratio_evaporacion)

        # Adición de feromonas por las hormigas
        for hormiga in self.hormigas:
            caminos_recorridos = hormiga.caminos()
            mejor_solucion = self.mejor_solucion.caminos()
            for camino in caminos_recorridos:
                if camino in mejor_solucion:
                    self.eta[camino[0]][camino[1]] += 1/hormiga.coste + self.num_hormigas_elitistas*(1/self.mejor_solucion.coste)
                    self.eta[camino[1]][camino[0]] += 1/hormiga.coste + self.num_hormigas_elitistas*(1/self.mejor_solucion.coste)
                else:
                    self.eta[camino[0]][camino[1]] += 1/hormiga.coste
                    self.eta[camino[1]][camino[0]] += 1/hormiga.coste

# Problema a resolver
matriz_coste = np.array([
    [2, 3, 2, 3, 2],
    [3, 2, 2, 3, 1],
    [4, 3, 1, 3, 2],
    [1, 2, 2, 3, 2]
])
num_tareas, num_operadores = matriz_coste.shape
vector_tiempo_tareas = [3, 2, 2, 3]
vector_tiempo_operadores = [4, 5, 3, 4, 4]

sistema = EAS(matriz_coste, vector_tiempo_tareas, vector_tiempo_operadores, 10, 10, 1, 3, 0.5)
mejor_solucion = sistema.start(20)
print("Mejor solución con coste " + str(mejor_solucion.coste))
for nodo in mejor_solucion.solucion:
    print("\t" + str(nodo))