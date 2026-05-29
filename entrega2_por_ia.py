# entrega2_por_ia.py
from simpleai.search import CspProblem, backtrack

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    rows, cols = camp_size
    
    # Lista plana de todos los módulos requeridos
    modules = (["hab"] * habs + 
               ["gen"] * generators + 
               ["lab"] * labs + 
               ["dep"] * deposits + 
               ["air"] * airlocks)
    
    # Asignamos índices numéricos planos como variables únicas
    variables = [i for i in range(len(modules))]
    
    # Dominios globales idénticos para todas las variables
    all_cells = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in craters]
    domains = {v: all_cells for v in variables}
    
    constraints = []
    
    def son_vecinos(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1

    def es_borde(p):
        return p[0] == 0 or p[0] == rows - 1 or p[1] == 0 or p[1] == cols - 1

    # Restricciones globales evaluadas por pares de variables
    def constreñir_modulos(vars, vals):
        v1, v2 = vars
        p1, p2 = vals
        t1, t2 = modules[v1], modules[v2]
        
        # R1: Sin superposición
        if p1 == p2:
            return False
        # R5: Generador no adyacente a habitacional
        if ((t1 == "gen" and t2 == "hab") or (t1 == "hab" and t2 == "gen")) and son_vecinos(p1, p2):
            return False
        # R6: Generadores no adyacentes entre sí
        if t1 == "gen" and t2 == "gen" and son_vecinos(p1, p2):
            return False
            
        return True

    # Aplicar restricciones binarias por pares de índices
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            constraints.append(((i, j), constreñir_modulos))
            
    # Restricciones Unarias (Bordes e Interiores) evaluadas en ejecución
    for i, t in enumerate(modules):
        if t == "air":
            constraints.append(([i], lambda vars, vals: es_borde(vals[0])))
        elif t == "hab":
            constraints.append(([i], lambda vars, vals: not es_borde(vals[0])))

    # R7 y R8 complejas aplicadas sobre el alcance completo del sistema
    def validar_global(vars, vals):
        positions = {modules[v]: [] for v in vars}
        for v, p in zip(vars, vals):
            positions[modules[v]].append(p)
            
        occupied = set(vals) | set(craters)
        
        # Validar laboratorios
        if "lab" in positions:
            for lp in positions["lab"]:
                if not any(son_vecinos(lp, dp) for dp in positions.get("dep", [])):
                    return False
                    
        # Validar evacuación
        if "hab" in positions:
            for hp in positions["hab"]:
                has_exit = False
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    np = (hp[0] + dr, hp[1] + dc)
                    if 0 <= np[0] < rows and 0 <= np[1] < cols:
                        if np not in occupied:
                            has_exit = True
                            break
                if not has_exit:
                    return False
        return True

    if variables:
        constraints.append((variables, validar_global))

    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)
    
    if solution is None:
        return None
        
    return [(modules[v], pos[0], pos[1]) for v, pos in solution.items()]