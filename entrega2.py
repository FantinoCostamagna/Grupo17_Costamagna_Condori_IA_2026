# entrega2.py
from itertools import combinations
from simpleai.search import CspProblem, backtrack

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    rows, cols = camp_size
    craters_set = set(craters)

    # generación de identificadores únicos para variables
    vHabs = [f"hab_{i}" for i in range(habs)]
    vGens = [f"gen_{i}" for i in range(generators)]
    vLabs = [f"lab_{i}" for i in range(labs)]
    vDeps = [f"dep_{i}" for i in range(deposits)]
    vAirs = [f"air_{i}" for i in range(airlocks)]

    # si hay laboratorios pero ningún depósito, la restricción de suministro es imposible de cumplir
    if labs > 0 and deposits == 0:
        return None

    variables = vHabs + vGens + vLabs + vDeps + vAirs

    # definición de Dominios con restricciones geográficas unarias aplicadas en el origen
    domains = {}
    for var in variables:
        validCoords = []
        for r in range(rows):
            for c in range(cols):
                coord = (r, c)
                
                # R2: ningún módulo en cráteres
                if coord in craters_set:
                    continue
                
                isBorder = (r == 0 or r == rows - 1 or c == 0 or c == cols - 1)
                
                # R4: habitacionales estrictamente al interior
                if var.startswith("hab") and isBorder:
                    continue
                
                # R3: esclusas de aire estrictamente en el borde
                if var.startswith("air") and not isBorder:
                    continue
                
                validCoords.append(coord)
        
        if not validCoords:
            return None
        domains[var] = validCoords

    # modelado de Restricciones Binarias y N-arias optimizadas
    constraints = []

    # auxiliar de adyacencia ortogonal
    def are_adjacent(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    # R1: sin superposición (Todas las variables entre sí deben tener posiciones diferentes)
    for v1, v2 in combinations(variables, 2):
        constraints.append(((v1, v2), lambda vars, vals: vals[0] != vals[1]))

    # R5: seguridad energética (Generador no adyacente a habitacional)
    for g in vGens:
        for h in vHabs:
            constraints.append(((g, h), lambda vars, vals: not are_adjacent(vals[0], vals[1])))

    # R6: aislamiento entre generadores (No adyacentes entre sí)
    for g1, g2 in combinations(vGens, 2):
        constraints.append(((g1, g2), lambda vars, vals: not are_adjacent(vals[0], vals[1])))

    # R7: cadena de suministro científico (Cada laboratorio adyacente a AL MENOS un depósito)
    # se optimiza pasando únicamente el laboratorio y la lista de depósitos disponibles
    def lab_supply_constraint(vars, vals):
        labPos = vals[0]
        depPositions = vals[1:]
        return any(are_adjacent(labPos, dep_pos) for dep_pos in depPositions)

    if vDeps:
        for lab in vLabs:
            constraints.append(([lab] + vDeps, lab_supply_constraint))

    # R8: ruta de evacuación (Cada habitacional debe tener al menos una celda libre)
    # optimizamos pasando el habitacional contra absolutamente todos los demás componentes del mapa
    def evacuation_route_constraint(vars, vals):
        habPos = vals[0]
        otherPositions = set(vals[1:])
        
        # generar vecinos válidos dentro de los límites de la grilla marciana
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = habPos[0] + dr, habPos[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = (nr, nc)
                # Si el vecino no es un cráter ni está ocupado por otra variable, hay ruta libre
                if neighbor not in craters_set and neighbor not in otherPositions:
                    return True
        return False

    otherVarsThan = lambda target: [v for v in variables if v != target]
    for h in vHabs:
        constraints.append(([h] + otherVarsThan(h), evacuation_route_constraint))

    # resolución del problema con SimpleAI
    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)

    if solution is None:
        return None

    # formateo de salida exacto al requerido por la cátedra
    formatedSolution = []
    for varName, coord in solution.items():
        prefix = varName.split("_")[0]
        # Mapeo del prefijo interno al tipo solicitado por el enunciado
        moduleType = "air" if prefix == "air" else prefix
        formatedSolution.append((moduleType, coord[0], coord[1]))

    return formatedSolution