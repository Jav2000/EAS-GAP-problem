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
    def __init__(self, matriz_coste, vector_tiempo_tareas, vector_tiempo_operadores, objetivo, num_hormigas, num_hormigas_elitistas, alpha, beta, ratio_evaporacion) -> None:
        # Datos problema
        self.matriz_coste = matriz_coste
        self.num_tareas, self.num_operadores = self.matriz_coste.shape
        self.vector_tiempo_tareas = vector_tiempo_tareas
        self.vector_tiempo_operadores = vector_tiempo_operadores
        self.objetivo = objetivo

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
                    self.tau[i][j] = 1/self.nodos[j].coste

        # Inicialización de información heurística
        self.eta = np.full((len(self.nodos), len(self.nodos)), 1, dtype=float)
        for i in range(len(self.nodos)):
            for j in range(len(self.nodos)):
                if i == j:
                    self.eta[i][j] = 0
                else:
                    self.eta[i][j] = 1/self.nodos[j].coste
        self.mejor_solucion = None
        self.coste_mejor_solucion = 999999999

    def start(self, num_iteraciones):
        # Hasta que se cumpla el número de iteraciones
        mejor_iteracion = 0
        for iteracion in range(num_iteraciones):
            self.hormigas = []
            mejor_sol = False
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
                    if not mejor_sol:
                        mejor_sol = True
                        mejor_iteracion = iteracion
                    if self.coste_mejor_solucion <= self.objetivo:
                        break
            if self.coste_mejor_solucion <= self.objetivo:
                break
            # Actualización de las feromonas
            self.actualizar_feromonas()

        return self.mejor_solucion, mejor_iteracion
    
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
matriz_coste_1 = np.array([
    [2, 3, 2, 3, 2],
    [3, 2, 2, 3, 1],
    [4, 3, 1, 3, 2],
    [1, 2, 2, 3, 2]
])
num_tareas_1, num_operadores_1 = matriz_coste_1.shape
vector_tiempo_tareas_1 = [3, 2, 2, 3]
vector_tiempo_operadores_1 = [4, 5, 3, 4, 4]

matriz_coste_2_transpuesta = np.array([
    [8, 18, 22, 5, 11, 11, 22, 11, 17, 22, 11, 20, 13, 13, 7, 22, 15, 22, 24, 8, 8, 24, 18, 8],
    [24, 14, 11, 15, 24, 8, 10, 15, 19, 25, 6, 13, 10, 25, 19, 24, 13, 12, 5, 18, 10, 24, 8, 5],
    [22, 22, 21, 22, 13, 16, 21, 5, 25, 13, 12, 9, 24, 6, 22, 24, 11, 21, 11, 14, 12, 10, 20, 6],
    [13, 8, 19, 12, 19, 18, 10, 21, 5, 9, 11, 9, 22, 8, 12, 13, 9, 25, 19, 24, 22, 6, 19, 14],
    [25, 16, 13, 5, 11, 8, 7, 8, 25, 20, 24, 20, 11, 6, 10, 10, 6, 22, 10, 10, 13, 21, 5, 19],
    [19, 19, 5, 11, 22, 24, 18, 11, 6, 13, 24, 24, 22, 6, 22, 5, 14, 6, 16, 11, 6, 8, 18, 10],
    [24, 10, 9, 10, 6, 15, 7, 13, 20, 8, 7, 9, 24, 9, 21, 9, 11, 19, 10, 5, 23, 20, 5, 21],
    [6, 9, 9, 5, 12, 10, 16, 15, 19, 18, 20, 18, 16, 21, 11, 12, 22, 16, 21, 25, 7, 14, 16, 10]
])
matriz_coste_2 = np.transpose(matriz_coste_2_transpuesta)

num_tareas_2, num_operadores_2 = matriz_coste_2.shape
vector_tiempo_tareas_2 = [8, 9, 13, 9, 10, 9, 10, 6, 4, 8, 7, 4, 8, 13, 8, 6, 9, 12, 9, 4, 9, 12, 10, 5]
vector_tiempo_operadores_2 = [36, 35, 38, 34, 32, 34, 31, 34]

numero_hormigas = [1, 2, 4, 8, 16, 32]
numero_hormigas_elitistas = [1, 2, 4, 8, 10, 12, 16]
for i in numero_hormigas:
    for j in numero_hormigas_elitistas:
        resultados = []
        iteraciones = []
        if j > i:
            continue
        else:
            for k in range(5):
                sistema = EAS(matriz_coste_1, vector_tiempo_tareas_1, vector_tiempo_operadores_1, 5, i, j, 1, 3, 0.5)
                mejor_solucion, mejor_iteracion = sistema.start(25)
                resultados.append(mejor_solucion.coste)
                iteraciones.append(mejor_iteracion)
            print("Resultados " + str(i) +  " hormigas y " + str(j) + " de elite: " + str(resultados))
            print("Iteraciones " + str(i) +  " hormigas y " + str(j) + " de elite: " + str(iteraciones))