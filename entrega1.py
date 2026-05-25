
from simpleai.search import SearchProblem, astar

BATERIA_MAX = 20

class Ares1MarsRover(SearchProblem):
    def __init__(self, initial_state, zonas_sombra):
        # Almacenamos las zonas de sombra en el objeto para no arrastrarlas en el estado
        self.zonas_sombra = frozenset(zonas_sombra)
        super().__init__(initial_state)

    def actions(self, state):
        accionesPosibles = []
        (
            posicionRover,
            bateria,
            taladroEquipado,
            cantidadAlmacenada,
            muestrasIgneas,
            muestrasSedimentarias,
        ) = state

        muestras_restantes = len(muestrasIgneas) + len(muestrasSedimentarias)

        # 1 Recolectar (consume 3 batería, requiere espacio y taladro correcto)
        if bateria - 3 > 0 and cantidadAlmacenada < 2:
            if posicionRover in muestrasIgneas and taladroEquipado == "termico":
                accionesPosibles.append(("recolectar", "ignea"))
            if posicionRover in muestrasSedimentarias and taladroEquipado == "percusion":
                accionesPosibles.append(("recolectar", "sedimentaria"))

        # 2 Depositar (consume 1 bateria. Regla: 2 muestras, o 1 si es la última del mapa)
        if bateria - 1 > 0 and cantidadAlmacenada > 0:
            if cantidadAlmacenada == 2 or (cantidadAlmacenada == 1 and muestras_restantes == 0):
                accionesPosibles.append(("depositar", None))

        # 3 Acciones de taladro (solo si hay muestras de ese tipo en el mapa y no lo tiene equipado)
        if bateria - 1 > 0:
            if len(muestrasIgneas) > 0 and taladroEquipado != "termico":
                accionesPosibles.append(("equipar", "termico"))
            if len(muestrasSedimentarias) > 0 and taladroEquipado != "percusion":
                accionesPosibles.append(("equipar", "percusion"))

        # 4 movimientos simples (consume 1 bateria)
        if bateria - 1 > 0:
            r, c = posicionRover
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                accionesPosibles.append(("moverse", (nr, nc)))

        # 5 sobremarcha (consume 4 bateria)
        if bateria - 4 > 0:
            r, c = posicionRover
            for nr, nc in ((r + 2, c), (r - 2, c), (r, c + 2), (r, c - 2)):
                accionesPosibles.append(("sobremarcha", (nr, nc)))

        # 6 recargar (no consume, suma hasta 20. Prohibido en sombras)
        if posicionRover not in self.zonas_sombra and bateria < BATERIA_MAX:
            accionesPosibles.append(("recargar", None))

        return accionesPosibles

    def result(self, state, action):
        (
            posicionRover,
            bateria,
            taladroEquipado,
            cantidadAlmacenada,
            muestrasIgneas,
            muestrasSedimentarias,
        ) = state

        tipoAccion, parametro = action

        if tipoAccion == "moverse":
            return (parametro, bateria - 1, taladroEquipado, cantidadAlmacenada, muestrasIgneas, muestrasSedimentarias)
        
        elif tipoAccion == "sobremarcha":
            return (parametro, bateria - 4, taladroEquipado, cantidadAlmacenada, muestrasIgneas, muestrasSedimentarias)
        
        elif tipoAccion == "equipar":
            return (posicionRover, bateria - 1, parametro, cantidadAlmacenada, muestrasIgneas, muestrasSedimentarias)
        
        elif tipoAccion == "recolectar":
            if parametro == "ignea":
                return (posicionRover, bateria - 3, taladroEquipado, cantidadAlmacenada + 1, muestrasIgneas - {posicionRover}, muestrasSedimentarias)
            else:
                return (posicionRover, bateria - 3, taladroEquipado, cantidadAlmacenada + 1, muestrasIgneas, muestrasSedimentarias - {posicionRover})
        
        elif tipoAccion == "depositar":
            return (posicionRover, bateria - 1, taladroEquipado, 0, muestrasIgneas, muestrasSedimentarias)
        
        elif tipoAccion == "recargar":
            return (posicionRover, min(bateria + 10, BATERIA_MAX), taladroEquipado, cantidadAlmacenada, muestrasIgneas, muestrasSedimentarias)

        return state

    def cost(self, state1, action, state2):
        tipoAccion, _ = action
        if tipoAccion == "depositar":
            return state1[3]  # cantidadAlmacenada del estado de origen
        
        costos = {
            "moverse": 1,
            "sobremarcha": 1,
            "recolectar": 2,
            "equipar": 3,
            "recargar": 4
        }
        return costos.get(tipoAccion, 0)

    def is_goal(self, state):
        return len(state[4]) == 0 and len(state[5]) == 0 and state[3] == 0 and state[1] > 0

    def heuristic(self, state):

        posicionRover, bateria, taladroEquipado, cantidadAlmacenada, muestrasIgneas, muestrasSedimentarias = state
        
        nIgn = len(muestrasIgneas)
        nSed = len(muestrasSedimentarias)
        totalMuestras = nIgn + nSed

        if totalMuestras == 0 and cantidadAlmacenada == 0:
            return 0

        if totalMuestras == 0:
            return cantidadAlmacenada

        # 1. Estimación optimista de tiempos de herramientas
        if nIgn > 0 and nSed > 0:
            equipoTiempo = 6 if taladroEquipado is None or taladroEquipado == "ninguno" else 3
            equipoBateria = 2 if taladroEquipado is None or taladroEquipado == "ninguno" else 1
        elif (nIgn > 0 and taladroEquipado != "termico") or (nSed > 0 and taladroEquipado != "percusion"):
            equipoTiempo = 3
            equipoBateria = 1
        else:
            equipoTiempo = 0
            equipoBateria = 0

        # 2. Cálculo del Árbol de Expansión Mínima (MST) usando algoritmo de Prim
        allPos = [posicionRover] + list(muestrasIgneas) + list(muestrasSedimentarias)
        n = len(allPos)
        inTree = [False] * n
        minEdge = [float("inf")] * n
        minEdge[0] = 0
        mstDist = 0
        
        for _ in range(n):
            u = -1
            for i in range(n):
                if not inTree[i] and (u == -1 or minEdge[i] < minEdge[u]):
                    u = i
            inTree[u] = True
            mstDist += minEdge[u]
            
            for v in range(n):
                if not inTree[v]:
                    d = abs(allPos[u][0] - allPos[v][0]) + abs(allPos[u][1] - allPos[v][1])
                    if d < minEdge[v]:
                        minEdge[v] = d

        # 3. Costos fijos e inevitables en acciones operativas
        collectTiempo = totalMuestras * 2
        collectBateria = totalMuestras * 3
        depositTiempo = totalMuestras + cantidadAlmacenada
        depositBateria = (totalMuestras + cantidadAlmacenada + 1) // 2

        otherTiempo = equipoTiempo + collectTiempo + depositTiempo
        otherBateria = equipoBateria + collectBateria + depositBateria + 1

        # 4. Simulación del balance óptimo entre sobremarchas y movimientos simples
        best_h = float("inf")
        max_overdrives = mstDist // 2

        for k in range(max_overdrives + 1):
            travelTiempo = mstDist - k
            travelBateria = 2 * k + mstDist
            totalBateriaNeeded = travelBateria + otherBateria
            extraBateria = totalBateriaNeeded - bateria
            recharges = (extraBateria + 9) // 10 if extraBateria > 0 else 0
            
            hActual = travelTiempo + otherTiempo + recharges * 4
            if hActual < best_h:
                best_h = hActual

        return best_h

def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    # Definimos el estado inicial usando frozenset para las muestras
    estado_inicial = (
        rover_inicio,
        bateria_inicial,
        "ninguno", # taladroEquipado
        0,         # cantidadAlmacenada
        frozenset(muestras_igneas),
        frozenset(muestras_sedimentarias),
    )

    problema = Ares1MarsRover(estado_inicial, zonas_sombra)
    resultado = astar(problema, graph_search=True)
    
    if resultado is None:
        return []
        
    acciones = [accion for accion, _ in resultado.path() if accion is not None]
    return acciones