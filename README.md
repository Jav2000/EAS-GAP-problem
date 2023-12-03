# EAS-GAP-problem
Problema de asignación generalizado: Para realizar un conjunto de tareas Ti, i = {1,2,3,4} se dispone de un conjunto de operarios Oj, j ={1,2,3,4,5}. Cada operario dispone de un tiempo dj para realizar actividades, mientras que cada actividad requiere un tiempo ri para su correcta finalización. Cada una de las tareas debe ser llevadas a cabo por un único operario, pero un operario puede llevar a cabo varias tareas. Además, existe un coste resultante de la asignación de cada operario a cada tarea, cij, véase la tabla.
El objetivo es encontrar la asignación con coste mínimo entre los operarios y las tareas de forma que todas las tareas se completen.
<p align="center">
  <img width="389" alt="Captura de pantalla 2023-12-03 a las 12 04 50" src="https://github.com/Jav2000/EAS-GAP-problem/assets/92857248/97d505b2-abdb-43de-b9ac-05b570571d02">
</p>

# Formato entrada
  - Matriz de coste: (Columnas igual a operadores, filas igual a tareas)
        2 3 2 3 2
        3 2 2 3 1
        4 3 1 3 2
        1 2 2 3 2
  - Vector de tiempo requerido por tarea:
        3 2 2 3
  - Vector de tiempo disponible por operador:
        4 5 3 4 4

# Parámetros del algoritmo
  - Número de hormigas
  - Número de hormigas elitistas
  - Alpha
  - Beta
  - Ratio de evaporación

# Inicialización de feromonas
La matriz de feromonas representa la cantidad que hay de ella en cada camino entre los nodos. Se inializan sus valores a 1/c_{ij} excepto para los caminos entre el mismo nodo.

# Inicialización de información heurística

# Selección del nuevo nodo
\[
p_{ij}=
\begin{cases}
    \frac{[\tau_{ij}]^\alpha[\eta_{ij}]^\beta}{\sum_{u\in J_k(r)}[\tau_{iu}]^\alpha[\eta_{iu}]^\beta} & \text{if } j \text{ is reachable from } i \\
    0 & \text{otherwise}
\end{cases}
\]

